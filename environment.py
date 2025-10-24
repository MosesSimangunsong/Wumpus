# environment.py
class WumpusWorld:
    def __init__(self, size=4):
        self.size = size
        self.agent_pos = (1, 1)  # Posisi awal agen selalu di [1,1]
        self.agent_dir = 'E'  # Arah awal agen (East/Timur)
        # Inisialisasi lingkungan
        self.wumpus_pos = (1, 3)  # Contoh posisi Wumpus
        self.gold_pos = (2, 3)  # Contoh posisi Emas
        self.pits_pos = [(3, 1), (3, 3), (4, 4)]  # Contoh posisi Pit

        print("=" * 30)
        print(f"Lingkungan Wumpus World {size}x{size} dibuat.")
        print(f"Wumpus di: {self.wumpus_pos}")
        print(f"Emas di: {self.gold_pos}")
        print(f"Pit di: {self.pits_pos}")
        print("=" * 30)

    def get_adjacent_squares(self, pos):
        """Mendapatkan kotak di sekitar posisi (x,y)"""
        x, y = pos
        adj = []
        if x > 1:
            adj.append((x - 1, y))
        if x < self.size:
            adj.append((x + 1, y))
        if y > 1:
            adj.append((x, y - 1))
        if y < self.size:
            adj.append((x, y + 1))
        return adj
    
    def shoot_arrow(self, pos):
    """Agen menembak ke arah pos"""
    if not self.wumpus_alive:
        return : False
    
    if pos == self.wumpus_pos:
        self.wumpus_alive = False
        self.wumpus_pos = None
        return True
    return False


    def get_percepts(self, pos):
        """Mendapatkan persepsi agen di posisi saat ini"""
        percepts = {
            'stench': False,
            'breeze': False,
            'glitter': False,
            'bump': False,
            'scream': False
        }

        # Cek Stench (Bau Wumpus)
        if self.wumpus_alive and self.wumpus_pos in self.get_adjacent_squares(pos): [cite: 78]
     percepts['stench'] = True

        # Cek Breeze (Angin dari Pit)
        for pit in self.pits_pos:
            if pit in self.get_adjacent_squares(pos):
                percepts['breeze'] = True
                break

        # Cek Glitter (Kilau Emas)
        if pos == self.gold_pos:
            percepts['glitter'] = True

        return percepts
