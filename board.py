from copy import deepcopy
import sys

class HexBoard:
    def __init__(self, size: int):
        self.size = size  # Tamaño N del tablero (NxN)
        self.board = [[0 for _ in range(size)] for _ in range(size)]  # Matriz NxN (0=vacío, 1=Jugador1, 2=Jugador2)

    def clone(self) -> 'HexBoard':
        """Devuelve una copia del tablero actual."""
        return deepcopy(self)

    def place_piece(self, row: int, col: int, player_id: int) -> bool:
        """Coloca una ficha si la casilla está vacía."""
        if self.board[row][col] != 0 or not (0 <= row < self.size and 0 <= col < self.size):
            return False
        self.board[row][col] = player_id
        return True


    def get_possible_moves(self) -> list:
        """Devuelve todas las casillas vacías como tuplas (fila, columna)."""
        return [(x, y) for x in range(self.size) for y in range(self.size) if self.board[x][y] == 0]        
    
    def check_connection(self, player_id: int) -> bool:
        """Verifica si el jugador ha conectado sus dos lados"""
        visited = [[False] * self.size for _ in range(self.size)]
        stack = []

        # Determina los lados a conectar según el jugador
        if player_id == 1:
            for i in range(self.size):
                if self.board[i][0] == player_id:
                    stack.append((i, 0))
                    visited[i][0] = True    
        else:
            for i in range(self.size):
                if self.board[0][i] == player_id:
                    stack.append((0, i))
                    visited[0][i] = True

        neighborhood = [
            (0,-1), #Izquierda
            (0,1), #Derecha
            (-1,0), #Arriba
            (1,0), #Abajo
            (-1,1), #Arriba derecha
            (1,-1) #Abajo izquierda
        ]

        # DFS para verificar la conexión    
        while stack:
            x, y = stack.pop()
            if (player_id == 1 and y == self.size - 1) or (player_id == 2 and x == self.size - 1):
                return True
            for dx, dy in neighborhood:
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.size and 0 <= ny < self.size and not visited[nx][ny] and self.board[nx][ny] == player_id:
                    visited[nx][ny] = True
                    stack.append((nx, ny))
        return False


    def __repr__(self):
        ans = ""
        for i in range(self.size):
            ans += " " * i
            for j in range(self.size):
                match self.board[i][j]:
                    case 0:
                        ans += " ⚪️"
                    case 1:
                        ans += " 🔴"
                    case 2:
                        ans += " 🔵"                
            ans += "\n"
        return ans
    

    def play_game(self, player1, player2, verbose=False):

        current_player, id = None, 0

        while True:
            try:
                current_player = player2 if id == player1.player_id else player1
                id = current_player.player_id

                row, col = current_player.play(self) 
                valid = self.place_piece(row, col, id)
                if not valid:
                    raise ValueError("Invalid play made by player.")
                if verbose:
                    print(f"Player {id} play ({row},{col})")
                    print(self) 

                if self.check_connection(id):   
                    if verbose:
                        print(f"Player {id} wins!")
                    return id                        
                
            except KeyboardInterrupt:
                print("\nGame interrupted. Exiting...")
                sys.exit(0)
        





