import random
from copy import deepcopy
from math import inf


class Player:
    def __init__(self, player_id: int):
        self.player_id = player_id  # Tu identificador (1 o 2)

    def play(self, board: HexBoard) -> tuple:
        raise NotImplementedError("¡Implementa este método!")


class HexDisjointSet:
    def __init__(self, board):      
        self.board = board
        self.size = len(board)

        # Disjoint Set con nodos virtuales en 0 y 1 para Jugador1 (bordes izquierdo/derecho), en 2 y 3 para Jugador2 (superior/inferior)
        self.ds = [-1] * (self.size ** 2 + 4) 

        # Procesar cada celda del tablero para construir el DisjointSet
        for row in range(self.size):
            for col in range(self.size):
                player_id = self.board[row][col]
                if player_id == 0:
                    continue  # Ignorar celdas vacías
                self.update_ds(row,col,player_id)            

    def clone(self):
        return deepcopy(self)

    def get_possible_moves(self) -> list:
        """Devuelve todas las casillas vacías como tuplas (fila, columna)."""
        return [(x, y) for x in range(self.size) for y in range(self.size) if self.board[x][y] == 0] 

    def place_piece(self, row: int, col: int, player_id: int):        
        self.board[row][col] = player_id
        self.update_ds(row,col,player_id) 


    def update_ds(self,row,col,player_id):

        pos = self._to_index(row, col)
        
        # Conectar con bordes del jugador
        if player_id == 1:
            if col == 0: 
                self._union(0, pos)
            elif col == self.size - 1: 
                self._union(1, pos)
        else:
            if row == 0: 
                self._union(2, pos)
            elif row == self.size - 1: 
                self._union(3, pos)
        
        # Conectar vecinos del mismo jugador
        for (x,y) in self.neighbours(row,col):
            if self.board[x][y] == player_id:
                self._union(self._to_index(x, y), pos)


    def check_connection(self, player_id: int) -> bool:
        """Verifica si el jugador ha conectado sus dos lados"""
        if player_id == 1:
            return self._root(0) == self._root(1)
        else:
            return self._root(2) == self._root(3)


    def check_inside(self, x, y):
        return 0 <= x < self.size and 0 <= y < self.size

    def neighbours(self, x, y):
        neighborhood = [
            (0,-1), #Izquierda
            (0,1), #Derecha
            (-1,0), #Arriba
            (1,0), #Abajo
            (-1,1), #Arriba derecha
            (1,-1) #Abajo izquierda
        ]

        for neig in neighborhood:
            nx, ny = x + neig[0], y + neig[1]
            if self.check_inside(nx, ny):
                yield nx, ny

    # ----- Métodos auxiliares de Disjoint-Set -----

    def _to_index(self, row: int, col: int) -> int:
        """Convierte (fila, columna) a índice en el arreglo ds."""
        return row * self.size + col + 4 

    def _root(self, a: int) -> int:
        """Encuentra la raíz con compresión de camino."""
        if self.ds[a] < 0:
            return a
        self.ds[a] = self._root(self.ds[a])
        return self.ds[a]

    def _union(self, a: int, b: int):
        """Une dos conjuntos. Retorna si hubo conexión."""
        a, b = self._root(a), self._root(b)
        if a == b:
            return False
        self.ds[a] = b
        return True  

    

class RandomPlayer(Player):
    def play(self, board: HexBoard) -> tuple:
        return random.choice(board.get_possible_moves())
        
        
class HeuristicAlphaBetaPlayer(Player):
    def __init__(self, player_id: int, cutoff, h):
        super().__init__(player_id)
        self.cutoff = cutoff
        self.h = h

    def play(self, board: HexBoard) -> tuple:

        player = self.player_id
        opponent = 3 - player
        board = HexDisjointSet(board.board)

        def max_value(board: HexBoard, alpha, beta, depth):
            if board.check_connection(opponent):
                return -1, None  
            if self.cutoff(board, depth):
                return self.h(board, player), None

            value, move = -inf, None
            for row,col in board.get_possible_moves():
                new_board = board.clone()
                new_board.place_piece(row, col, player)                
                new_value, _ = min_value(new_board, alpha, beta, depth+1)
                if new_value > value:
                    value, move = new_value, (row, col)
                    alpha = max(alpha, value)
                if value >= beta:
                    return value, move
            return value, move

        def min_value(board: HexBoard, alpha, beta, depth):
            if board.check_connection(player):
                return 1, None     
            if self.cutoff(board, depth):
                return self.h(board, player), None       
            value, move = +inf, None
            for row,col in board.get_possible_moves():
                new_board = board.clone()
                new_board.place_piece(row, col, opponent)                
                new_value, _ = max_value(new_board, alpha, beta, depth+1)
                if new_value < value:
                    value, move = new_value, (row, col)
                    beta = min(beta, value)
                if value <= alpha:
                    return value, move
            return value, move

        value, move = max_value(board, -inf, +inf, 0)
        return move


def three_depth_cutoff(board, depth):
    return depth == 2   

 

def evaluate(board, player):

    player_moves = min_plays_to_win(board, player)
    opponent_moves = min_plays_to_win(board, 3-player)
    
    return opponent_moves - player_moves


from heapq import heappush, heappop

def min_plays_to_win(board, player):
      
    start_nodes = [(i,0) if player == 1 else (0,i) for i in range(board.size)]
    end_nodes = [(i,board.size-1) if player == 1 else (board.size-1,i) for i in range(board.size)]
    
    # Inicializar matriz de distancias
    dist = [[float('inf')] * board.size for _ in range(board.size)]
    heap = []
    
    # Inicializar bordes de inicio
    for (i, j) in start_nodes:
        if board.board[i][j] == player:
            dist[i][j] = 0
            heappush(heap, (0, i, j))
        elif board.board[i][j] == 0:
            dist[i][j] = 1
            heappush(heap, (1, i, j))
    
    # Dijkstra
    while heap:
        cost, i, j = heappop(heap)
        if (i, j) in end_nodes:
            return cost
        for (ni, nj) in board.neighbours(i, j):
            if board.board[ni][nj] == player:
                new_cost = cost
            elif board.board[ni][nj] == 0:
                new_cost = cost + 1
            else:
                continue  # Celda bloqueada
            
            if new_cost < dist[ni][nj]:
                dist[ni][nj] = new_cost
                heappush(heap, (new_cost, ni, nj))
    
    return float('inf')  # Si no hay camino
