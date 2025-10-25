# agent.py
from environment import WumpusWorld

class KnowledgeBase:
    def __init__(self):
        # KB akan menyimpan fakta sebagai string, contoh: "P_2_3", "~W_1_2"
        # Kita menggunakan set untuk efisiensi pengecekan dan menghindari duplikat.
        self.facts = set()

    def tell(self, fact):
        """Menambahkan fakta baru ke KB."""
        self.facts.add(fact)
        print(f"TELL: Menambahkan fakta '{fact}' ke KB.")

    def ask(self, query):
        """Memeriksa apakah sebuah query (fakta) ada di KB."""
        return query in self.facts


class Agent:
    def __init__(self, world):
        self.world = world
        self.kb = KnowledgeBase()
        self.pos = (1, 1)
        self.visited = set()
        self.safe_squares = set()
        

        self.has_arrow = True

        # Fakta awal: Posisi [1,1] pasti aman
        self.kb.tell("OK_1_1")  # OK_x_y berarti kotak (x,y) aman
        self.safe_squares.add((1, 1))
        self.visited.add((1, 1))

        self.has_gold = False
        self.goal = 'find_gold' # Tujuan awal: cari emas
        self.path_history = [(1,1)]

    def process_percepts(self, percepts):
        """Memproses persepsi dan menambahkan fakta baru ke KB (TELL)."""
        x, y = self.pos

        # Jika tidak ada Breeze, semua tetangga aman dari Pit
        if not percepts['breeze']:
            print("Persepsi: Tidak ada Breeze.")
            for adj_pos in self.world.get_adjacent_squares(self.pos):
                ax, ay = adj_pos
                if f"~P_{ax}_{ay}" not in self.kb.facts:
                    self.kb.tell(f"~P_{ax}_{ay}")  # ~P_x_y -> Tidak ada Pit di (x,y)
        else:
            print(f"Persepsi: Ada Breeze di {self.pos}")
            if f"B_{x}_{y}" not in self.kb.facts:
                self.kb.tell(f"B_{x}_{y}") # B_x_y -> Ada Breeze di (x,y)

        # Jika tidak ada Stench, semua tetangga aman dari Wumpus
        if not percepts['stench']:
            print("Persepsi: Tidak ada Stench.")
            for adj_pos in self.world.get_adjacent_squares(self.pos):
                ax, ay = adj_pos
                if f"~W_{ax}_{ay}" not in self.kb.facts:
                    self.kb.tell(f"~W_{ax}_{ay}")  # ~W_x_y -> Tidak ada Wumpus di (x,y)
        else:
            print(f"Persepsi: Ada Stench di {self.pos}")
            if f"S_{x}_{y}" not in self.kb.facts:
                self.kb.tell(f"S_{x}_{y}") # B_x_y -> Ada Stench di (x,y)
        
        if percepts['glitter']:
            print("Persepsi: Melihat *GLITTER*! Mengambil Emas!")
            self.has_gold = True
            self.goal = 'go_home' # Ganti tujuan: pulang! [cite: 252]
            # (Aksi 'grab' bisa jadi metode terpisah jika mau)
            # Kita anggap 'grab' terjadi otomatis saat 'glitter'
            self.kb.tell("GRAB_GOLD")

    def update_safe_squares(self):
        """Menggunakan KB untuk menyimpulkan kotak mana yang aman."""
        for x in range(1, self.world.size + 1):
            for y in range(1, self.world.size + 1):
                # Sebuah kotak aman jika kita tahu tidak ada Pit DAN tidak ada Wumpus
                if self.kb.ask(f"~P_{x}_{y}") and self.kb.ask(f"~W_{x}_{y}"):
                    if (x, y) not in self.safe_squares:
                        print(f"INFERENSI: Kotak ({x},{y}) disimpulkan aman!")
                        self.safe_squares.add((x, y))

        # ... di dalam update_safe_squares, setelah loop yang ada
        # TUGAS 1 (Tantangan): Inferensi untuk menemukan Wumpus/Pit
        for x in range(1, self.world.size + 1):
            for y in range(1, self.world.size + 1):
                # Cek jika kita merasakan Stench di (x,y)
                if self.kb.ask(f"S_{x}_{y}"):
                    adj_squares = self.world.get_adjacent_squares((x, y))
                    possible_wumpus_locs = []

                    for ax, ay in adj_squares:
                        # Jika kita TIDAK TAHU status Wumpus di (ax, ay)
                        if not self.kb.ask(f"~W_{ax}_{ay}") and not self.kb.ask(f"W_{ax}_{ay}"):
                            possible_wumpus_locs.append((ax, ay))
                        # Jika kita tahu tetangga aman, kurangi dari kemungkinan
                        if self.kb.ask(f"~W_{ax}_{ay}"):
                            # Ini bagian Disjunctive Syllogism
                            pass 

                    # Jika hanya tersisa SATU kemungkinan, kita 100% yakin
                    if len(possible_wumpus_locs) == 1:
                        w_x, w_y = possible_wumpus_locs[0]
                        if not self.kb.ask(f"W_{w_x}_{w_y}"):
                            print(f"INFERENSI (Tugas 1): Wumpus PASTI di ({w_x},{w_y})!")
                            self.kb.tell(f"W_{w_x}_{w_y}")

        # ... di dalam update_safe_squares, setelah loop yang ada
        # TUGAS 1 (Tantangan): Inferensi untuk menemukan Wumpus/Pit
        for x in range(1, self.world.size + 1):
            for y in range(1, self.world.size + 1):
                # Cek jika kita merasakan Breeze di (x,y)
                if self.kb.ask(f"B_{x}_{y}"):
                    adj_squares = self.world.get_adjacent_squares((x, y))
                    possible_pits_locs = []

                    for ax, ay in adj_squares:
                        # Jika kita TIDAK TAHU status Wumpus di (ax, ay)
                        if not self.kb.ask(f"~P_{ax}_{ay}") and not self.kb.ask(f"P_{ax}_{ay}"):
                            possible_pits_locs.append((ax, ay))
                        # Jika kita tahu tetangga aman, kurangi dari kemungkinan
                        if self.kb.ask(f"~P_{ax}_{ay}"):
                            # Ini bagian Disjunctive Syllogism
                            pass 

                    # Jika hanya tersisa SATU kemungkinan, kita 100% yakin
                    if len(possible_pits_locs) == 1:
                        w_x, w_y = possible_pits_locs[0]
                        if not self.kb.ask(f"P_{w_x}_{w_y}"):
                            print(f"INFERENSI (Tugas 1): Pits PASTI di ({w_x},{w_y})!")
                            self.kb.tell(f"P_{w_x}_{w_y}")


    def decide_next_move(self):
        """Memutuskan gerakan selanjutnya berdasarkan kotak aman yang belum dikunjungi."""
        
        # TUGAS 3: Logika berdasarkan tujuan
        if self.goal == 'go_home':
            # Tujuan: Pulang ke (1,1) 
            print("AKSI (Tugas 3): Tujuan adalah pulang ke (1,1).")
            if self.pos == (1,1):
                print("AKSI: Berhasil keluar dari gua dengan Emas! Menang!")
                return 'exit' # Sinyal untuk menghentikan simulasi

            # Ambil langkah terakhir dari jejak 
            if len(self.path_history) > 1:
                # Kita perlu pop langkah saat ini untuk dapat langkah sebelumnya
                self.path_history.pop() 
                target_pos = self.path_history[-1] 
                print(f"AKSI: Mundur ke {target_pos} melalui jalur aman.")
                return target_pos
            else:
                return None # Sudah di (1,1) atau buntu

        else: # self.goal == 'find_gold'
            # TUGAS 2: Logika Menembak
            # Agen hanya berpikir untuk menembak jika sedang mencari emas
            if self.has_arrow:
                for x in range(1, self.world.size + 1):
                    for y in range(1, self.world.size + 1):
                        # Jika inferensi (dari Tugas 1) yakin ada Wumpus
                        if self.kb.ask(f"W_{x}_{y}"): 
                            self.shoot_at((x, y))
                            return None # 'None' berarti tidak bergerak langkah ini

            # Logika Asli: Cari kotak aman terdekat
            adj_squares = self.world.get_adjacent_squares(self.pos)
            unvisited_safe_squares = [
                sq for sq in adj_squares if sq in self.safe_squares and sq not in self.visited
            ]

            if unvisited_safe_squares:
                # Jika ada, pilih salah satu sebagai tujuan
                target_pos = unvisited_safe_squares[0]
                print(f"AKSI: Memutuskan untuk pindah ke kotak aman terdekat: {target_pos}")
                return target_pos
            else:
                # Bagian ini (Tugas 3): jika buntu, mundur
                print("AKSI: Buntu, tidak ada kotak aman terdekat. Mundur...")
                if len(self.path_history) > 1:
                    self.path_history.pop()
                    target_pos = self.path_history[-1]
                    print(f"AKSI: Mundur ke {target_pos}")
                    return target_pos
                else:
                    print("AKSI: Tidak bisa mundur lagi. Terjebak.")
                    return None
        


    def move_to(self, new_pos):
        """Menggerakkan agen ke posisi baru."""
        if new_pos:
            self.pos = new_pos
            self.visited.add(self.pos)
            print(f"Agen sekarang berada di {self.pos}")


            # TUGAS 3: Catat jejak untuk pulang
            # Hanya tambahkan jika itu langkah maju (bukan mundur)
            if self.pos not in self.path_history:
                     self.path_history.append(self.pos)

            print(f"Agen sekarang berada di {self.pos}")

    def run_simulation(self, steps=15):
        """Menjalankan simulasi langkah demi langkah."""
        for step in range(steps):
            print(f"\n--- LANGKAH {step + 1} ---")
            print(f"Agen di Posisi: {self.pos}")

            # 1. Agen merasakan lingkungan
            current_percepts = self.world.get_percepts(self.pos)

            # 2. Agen memproses persepsi (TELL)
            self.process_percepts(current_percepts)

            # 3. Agen melakukan inferensi (ASK & TELL)
            self.update_safe_squares()

            # 4. Agen memutuskan gerakan selanjutnya
            next_pos = self.decide_next_move()

            # 5. Agen bergerak --- URUTAN DIPERBAIKI ---
            
            # PERIKSA 'exit' DULU
            if next_pos == 'exit':
                print("Simulasi selesai. Agen berhasil keluar.")
                break

            # KEMUDIAN, PERIKSA JIKA ADA GERAKAN
            if next_pos:
                self.move_to(next_pos)
            
            # JIKA TIDAK ADA GERAKAN (None)
            else:
                # Ini terjadi jika agen menembak (Tugas 2) atau buntu total
                # Kita tidak 'break' agar simulasi lanjut (untuk mendengar 'scream')
                print("AKSI: Tidak ada gerakan di langkah ini (menembak atau buntu).")
                
                # Jika Anda ingin simulasi berhenti jika buntu total:
                # (Logika opsional, tapi bagus)
                # if self.goal != 'find_gold' or not self.has_arrow:
                #    print("Simulasi berhenti, agen tidak bisa menentukan langkah aman.")
                #    break
                pass # Biarkan simulasi lanjut

            print(f"KB saat ini berisi {len(self.kb.facts)} fakta.")
    
    # ... di dalam kelas Agent di agent.py
    def shoot_at(self, pos):
        """Mencoba menembak Wumpus di pos"""
        if self.has_arrow:
            print(f"AKSI: Menembak panah ke {pos}")
            self.has_arrow = False
            hit = self.world.shoot_arrow(pos)

            if hit:
                print("Persepsi: Mendengar *SCREAM*!")
                # Wumpus mati, semua fakta Stench yang lama tidak valid
                # (Ini opsional tapi bagus)
                # Kita juga bisa menambahkan fakta bahwa Wumpus mati
                self.kb.tell("~WUMPUS_ALIVE")

                # Hapus semua fakta Stench dari KB karena Wumpus mati
                # (Cara sederhana: buat set baru tanpa fakta 'S_')
                facts_to_remove = {f for f in self.kb.facts if f.startswith('S_')}
                for f in facts_to_remove:
                    self.kb.facts.remove(f)

                # Wumpus di pos itu sudah mati, jadi ~W
                self.kb.tell(f"~W_{pos[0]}_{pos[1]}")
            else:
                print("AKSI: Tembakan meleset.")
        else:
            print("AKSI: Sudah tidak punya panah.")


# --- Main Program ---
if __name__ == "__main__":
    # Buat dunia dan agen
    wumpus_world = WumpusWorld(size=4)
    agent = Agent(wumpus_world)

    # Jalankan simulasi
    agent.run_simulation(steps=15)
