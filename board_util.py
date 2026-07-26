import numpy as np
import random
from board import Board
from copy import deepcopy
import math

def sanitize_board(board):
    """
        Generates a clean version of the board for submission to the API. 
        Scans mutable cells and replaces those with duplicate values ​​
        in their respective rows or columns with 0.

        args:
        board (Board): the current state of the board
        returns:
        (list): A two-dimensional matrix
        
    """ 
    clean_grid = deepcopy(board.grid)
    
    for r in range(board.N):
        for c in range(board.N):
            if board.fixedValues[r][c] == 0:
                val = board.getVal(r, c)
                
                # The expected value for a valid state is exactly 1;
                row_occurrences = np.count_nonzero(board.getRow(r) == val)
                col_occurrences = np.count_nonzero(board.getCol(c) == val)
                
                # If it is greater than 1, there is a collision. The cell is cleared.
                if row_occurrences > 1 or col_occurrences > 1:
                    clean_grid[r][c] = 0
                    
    return clean_grid.tolist()


def randomizeSudoku(board):
    """
    Fill mutable cells on the board with random values between 1-N that are not already in the subgrid.
    """
    random_board = deepcopy(board)
    for r in range(board.N):
        for c in range(board.N):
            if random_board.getVal(r, c) == 0:
                rand_val = random.choice(
                    [i for i in range(1, board.N + 1) if i not in random_board.getSubgrid(r, c)]
                )
                random_board.setVal(r, c, rand_val)
    return random_board

def notFixedInSubgrid(board, row, col):
    """Find all the cells in a subgrid that are not fixed (mutable)."""
    not_fixed_in_subgrid = []
    fixed_board = board.fixedValues
    row_start = row - (row % board.subgrid_size)
    col_start = col - (col % board.subgrid_size)
    
    for r in range(row_start, row_start + board.subgrid_size):
        for c in range(col_start, col_start + board.subgrid_size):
            if fixed_board[r][c] == 0:
                not_fixed_in_subgrid.append([r, c])
    return not_fixed_in_subgrid

def selectTwoCells(board):
    """Select two random mutable cells from a random subgrid of the board."""
    subgrid_indices = [i for i in range(0, board.N, board.subgrid_size)]
    chosen_subgrid_idx = [random.choice(subgrid_indices), random.choice(subgrid_indices)]
    
    not_fixed_values = notFixedInSubgrid(board, *chosen_subgrid_idx)
    
    if len(not_fixed_values) < 2:
        return None, None
        
    cell_1 = random.choice(not_fixed_values)
    not_fixed_values.remove(cell_1)
    cell_2 = random.choice(not_fixed_values)
    return cell_1, cell_2 

def flipCells(board, cell_1, cell_2):
    """Interchange the values of two cells on the board in place."""
    new_board = deepcopy(board)
    tmp = new_board.getVal(cell_1[0], cell_1[1])
    new_board.setVal(cell_1[0], cell_1[1], new_board.getVal(cell_2[0], cell_2[1]))
    new_board.setVal(cell_2[0], cell_2[1], tmp)
    return new_board

def rowColCost(board, r, c):
    """Calculate the sum of the cost of given row and column of the board."""
    return (board.N - len(np.unique(board.getRow(r))) + (board.N - len(np.unique(board.getCol(c)))))

def boardCost(board):
    """Calculate sum of duplicate values in each row and column of the board."""
    cost = 0
    for i in range(board.N):
        cost += rowColCost(board, i, i)
    return cost

def initialTemp(board):
    """Calculate the initial temperature for the simulated annealing algorithm."""
    costs = []
    for _ in range(200):
        cell_1, cell_2 = selectTwoCells(board)
        if cell_1 is None or cell_2 is None:
            continue # Pula a iteração se não foi possível escolher 2 células
            
        board_proposed = flipCells(board, cell_1, cell_2)
        costs.append(boardCost(board_proposed))
        
    if not costs:
        return 0.1 # Fallback caso o tabuleiro seja quase completo
    return np.std(costs)

def totalIterations(board):
    """Calculate the total number of iterations for the simulated annealing algorithm."""
    return int(np.count_nonzero(board.grid == 0) ** 0.5)

def proposedState(current_board, initial_board):
    subgrid_indices = [i for i in range(0, current_board.N, current_board.subgrid_size)]
    random_row = random.choice(subgrid_indices)
    random_col = random.choice(subgrid_indices)
    
    subgrid_sum = current_board.getSubgridSum(
        initial_board.getSubgrid(random_row, random_col, fixed=True)
    )
    
    if subgrid_sum > (current_board.N - 2):
        return current_board, (None, None)
        
    cell_1, cell_2 = selectTwoCells(current_board)
    
    if cell_1 is None or cell_2 is None:
        return current_board, (None, None)
        
    board_proposed = flipCells(current_board, cell_1, cell_2)
    return board_proposed, (cell_1, cell_2)

def chooseNewBoard(current_board, initial_board, cost, temp):
    """Choose a new board based on current board and temperature."""
    board_proposed, cells = proposedState(current_board, initial_board)
    
    if cells[0] is None or cells[1] is None:
        return current_board, 0
        
    cell_1, cell_2 = cells
    
    current_cost = rowColCost(current_board, cell_1[0], cell_1[1]) + rowColCost(current_board, cell_2[0], cell_2[1])
    cost_proposed = rowColCost(board_proposed, cell_1[0], cell_1[1]) + rowColCost(board_proposed, cell_2[0], cell_2[1])
    
    delta_cost = cost_proposed - current_cost
    
    try:
        prob = math.exp(-delta_cost / temp)
    except OverflowError:
        prob = 0
        
    if np.random.uniform(1, 0, 1) < prob:
        return board_proposed, delta_cost
    else:
        return current_board, 0