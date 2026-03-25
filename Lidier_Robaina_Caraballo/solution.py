"""
Hex game AI implementation with efficient connection checking and minimax algorithm.
"""

from copy import deepcopy
from heapq import heappush, heappop
from math import inf as infinity
import random
from time import perf_counter

from board import HexBoard
from player import Player


class HexDisjointSet:
    """
    Disjoint set data structure for efficient Hex board connection checking.

    Uses virtual nodes for board edges to detect player connections.
    """

    def __init__(self, board: list[list[int]]):
        """
        Initialize disjoint set for the given board.

        Args:
            board: 2D list representing the Hex board state.
        """
        self.board = board
        self.size = len(board)
        # Disjoint set with virtual nodes: 0=left, 1=right for player 1; 2=top, 3=bottom for player 2
        self.ds = [-1] * (self.size ** 2 + 4)

        # Initialize disjoint set for all occupied cells
        for row in range(self.size):
            for col in range(self.size):
                player_id = self.board[row][col]
                if player_id != 0:
                    self.update_ds(row, col, player_id)

    def clone(self) -> 'HexDisjointSet':
        """Return a deep copy of this disjoint set."""
        return deepcopy(self)

    def get_possible_moves(self) -> list[tuple[int, int]]:
        """Return list of empty cells as (row, col) tuples."""
        return [(x, y) for x in range(self.size) for y in range(self.size) if self.board[x][y] == 0]

    def place_piece(self, row: int, col: int, player_id: int) -> None:
        """
        Place a piece on the board and update disjoint set.

        Args:
            row: Row index
            col: Column index
            player_id: Player identifier (1 or 2)
        """
        self.board[row][col] = player_id
        self.update_ds(row, col, player_id)

    def update_ds(self, row: int, col: int, player_id: int) -> None:
        """
        Update disjoint set after placing a piece.

        Args:
            row: Row index
            col: Column index
            player_id: Player identifier
        """
        pos = self._to_index(row, col)

        # Connect to player's virtual edge nodes
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

        # Connect to same-player neighbors
        for nx, ny in self.neighbours(row, col):
            if self.board[nx][ny] == player_id:
                self._union(self._to_index(nx, ny), pos)

    def check_connection(self, player_id: int) -> bool:
        """
        Check if player has connected their sides.

        Args:
            player_id: Player to check (1 or 2)

        Returns:
            True if connected, False otherwise
        """
        if player_id == 1:
            return self._root(0) == self._root(1)
        return self._root(2) == self._root(3)

    def check_inside(self, x: int, y: int) -> bool:
        """Check if coordinates are within board bounds."""
        return 0 <= x < self.size and 0 <= y < self.size

    def neighbours(self, x: int, y: int) -> list[tuple[int, int]]:
        """Return list of valid neighboring cell coordinates."""
        deltas = [(-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0)]
        return [(x + dx, y + dy) for dx, dy in deltas if self.check_inside(x + dx, y + dy)]

    def _to_index(self, row: int, col: int) -> int:
        """Convert (row, col) to disjoint set array index."""
        return row * self.size + col + 4

    def _root(self, a: int) -> int:
        """Find root with path compression."""
        if self.ds[a] < 0:
            return a
        self.ds[a] = self._root(self.ds[a])
        return self.ds[a]

    def _union(self, a: int, b: int) -> bool:
        """
        Union two sets by rank.

        Returns:
            True if sets were merged, False if already connected.
        """
        a_root, b_root = self._root(a), self._root(b)
        if a_root == b_root:
            return False
        self.ds[a_root] = b_root
        return True


class SmartPlayer(Player):
    """
    AI player using minimax with alpha-beta pruning and heuristic evaluation.

    Attributes:
        max_move_time (float): maximum allowed seconds per move.
    """

    max_move_time = 4.8

    def play(self, board: HexBoard) -> tuple[int, int]:
        """
        Choose the best move for the current player under a fixed time budget.

        Uses alpha-beta minimax with depth cutoff and a timeout guard to ensure no play exceeds 5 seconds.

        Args:
            board: Current game board

        Returns:
            Tuple (row, col) of selected move
        """
        player = self.player_id
        opponent = 3 - player
        state = HexDisjointSet(board.board)

        start_time = perf_counter()

        def time_exceeded() -> bool:
            return (perf_counter() - start_time) >= self.max_move_time

        def max_value(node: HexDisjointSet, alpha: float, beta: float, depth: int):

            if node.check_connection(opponent):
                return -1_000_000, None
            if cutoff(node, depth):
                return evaluate(node, player), None

            value, best_move = -infinity, None
            for row, col in node.get_possible_moves():
                if time_exceeded():     
                    print("Time exceeded during minimax search, returning best move found so far.")                             
                    break   
                child = node.clone()
                child.place_piece(row, col, player)
                child_value, _ = min_value(child, alpha, beta, depth + 1)
                if child_value > value:
                    value, best_move = child_value, (row, col)
                    alpha = max(alpha, value)
                if value >= beta:
                    break
            return value, best_move

        def min_value(node: HexDisjointSet, alpha: float, beta: float, depth: int):
            if node.check_connection(player):
                return 1_000_000, None
            if cutoff(node, depth):
                return evaluate(node, player), None

            value, best_move = infinity, None
            for row, col in node.get_possible_moves():
                if time_exceeded():      
                    print("Time exceeded during minimax search, returning best move found so far.")              
                    break
                child = node.clone()
                child.place_piece(row, col, opponent)
                child_value, _ = max_value(child, alpha, beta, depth + 1)
                if child_value < value:
                    value, best_move = child_value, (row, col)
                    beta = min(beta, value)
                if value <= alpha:
                    break
            return value, best_move

        value, move = max_value(state, -infinity, infinity, 0)
        return move


class RandomPlayer(Player):
    """
    Player that makes random valid moves.
    """

    def play(self, board: HexBoard) -> tuple[int, int]:
        """Return a random empty cell."""
        return random.choice(board.get_possible_moves())


def cutoff(board: HexDisjointSet, depth: int) -> bool:
    """
    Adaptive search cutoff based on board size and remaining moves.

    This function is designed to keep SmartPlayer within a 5 second per-move limit,
    especially for moderate-sized boards where branching is high.

    - Small boards (size <=7): higher max depth because branching is smaller.
    - Medium boards (8<=size<=13): start with shallow depth 2, then allow deeper search
      as the number of empty cells decreases.
    - Large boards (size >13): remain conservative, with smaller depth even in midgame.

    Args:
        board: Current board state.
        depth: Current minimax depth.

    Returns:
        True if search should stop at this depth.
    """
    total_moves = board.size ** 2
    remaining_moves = len(board.get_possible_moves())

    if board.size <= 7:
        # Small board: allow more depth as game progresses
        if remaining_moves > total_moves / 2:
            max_depth = 2
        elif remaining_moves > total_moves / 5:
            max_depth = 4
        else:
            max_depth = 6
    elif board.size <= 13:
        # Medium board: start conservative
        if remaining_moves > total_moves / 3:
            max_depth = 2
        else:
            max_depth = 3
    else:
        max_depth = 2  # Large board: keep depth low to ensure timely response

    return depth >= max_depth



def evaluate(board: HexDisjointSet, player: int) -> float:
    """
    Heuristic evaluation based on minimum moves to win.

    Args:
        board: Current board state
        player: Player to evaluate for        

    Returns:
        Evaluation score (higher is better for player)
    """


    player_moves = min_plays_to_win(board, player)
    opponent_moves = min_plays_to_win(board, 3 - player)
    return opponent_moves - player_moves


def min_plays_to_win(board: HexDisjointSet, player: int) -> float:
    """
    Calculate minimum moves needed for player to win using Dijkstra.

    Args:
        board: Current board state
        player: Player to calculate for        
    Returns:
        Minimum moves to connect sides (infinity if impossible)
    """
    start_nodes = [(i, 0) if player == 1 else (0, i) for i in range(board.size)]
    end_nodes = [(i, board.size - 1) if player == 1 else (board.size - 1, i) for i in range(board.size)]

    # Distance matrix
    dist = [[infinity] * board.size for _ in range(board.size)]
    heap = []

    # Initialize starting edges
    for i, j in start_nodes:
        if board.board[i][j] == player:
            dist[i][j] = 0
            heappush(heap, (0, i, j))
        elif board.board[i][j] == 0:
            dist[i][j] = 1
            heappush(heap, (1, i, j))

    # Dijkstra's algorithm
    while heap:
        cost, i, j = heappop(heap)
        if (i, j) in end_nodes:
            return cost
        for ni, nj in board.neighbours(i, j):
            if board.board[ni][nj] == player:
                new_cost = cost
            elif board.board[ni][nj] == 0:
                new_cost = cost + 1
            else:
                continue  # Blocked cell

            if new_cost < dist[ni][nj]:
                dist[ni][nj] = new_cost
                heappush(heap, (new_cost, ni, nj))

    return infinity  # No path found




        