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

        # Fakta awal: Posisi [1,1] pasti aman
        self.kb.tell("OK_1_1")  # OK_x_y berarti kotak (x,y) aman
        self.safe_squares.add((1, 1))
        self.visited.add((1, 1))

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
        # Cari kotak aman yang berdekatan dan belum dikunjungi
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
            print("AKSI: Tidak ada kotak aman terdekat yang belum dikunjungi. Mundur atau eksplorasi lebih jauh diperlukan.")
            return None

    def move_to(self, new_pos):
        """Menggerakkan agen ke posisi baru."""
        if new_pos:
            self.pos = new_pos
            self.visited.add(self.pos)
            print(f"Agen sekarang berada di {self.pos}")

    def run_simulation(self, steps=5):
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

            # 5. Agen bergerak
            if next_pos:
                self.move_to(next_pos)
            else:
                print("Simulasi berhenti, agen tidak bisa menentukan langkah aman.")
                break

        print(f"KB saat ini berisi {len(self.kb.facts)} fakta.")


# --- Main Program ---
if __name__ == "__main__":
    # Buat dunia dan agen
    wumpus_world = WumpusWorld(size=4)
    agent = Agent(wumpus_world)

    # Jalankan simulasi
    agent.run_simulation(steps=3)
