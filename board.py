import numpy as np
import math

class Board:
    """
    Board class that represents a Sudoku board as a numpy array of size NxN.
    This includes getters and setters for rows, columns, and subgrids.
    """
    def __init__(self, puzzle):
        """
        Initialize the board with a np.array representing an NxN sudoku puzzle.
        args:
            puzzle(list): a list of integers, where 0 represents an empty cell
        """
        # Define as dimensões N (ex: 9) e subgrid_size (ex: 3) dinamicamente
        self.N = int(math.sqrt(len(puzzle)))
        self.subgrid_size = int(math.sqrt(self.N))
        
        self.grid = np.array(puzzle).reshape((self.N, self.N))
        board_copy = self.grid.copy()
        self.fixedValues = np.where(board_copy != 0, 1, board_copy)

    def __repr__(self):
        """
        Create a formatted string representation of the board dynamically.
        returns:
            (str) a formatted string representation of the board
        """
        # Calcula o tamanho da linha dinamicamente para os traços
        line_length = self.N * 2 + self.subgrid_size * 2 + 1
        lines = ["-" * line_length]
        for i in range(self.N):
            line = "| "
            for j in range(self.N):
                line += str(self.grid[i][j]) + " "
                if j % self.subgrid_size == self.subgrid_size - 1:
                    line += "| "
            lines.append(line)
            if i % self.subgrid_size == self.subgrid_size - 1:
                lines.append("-" * line_length)
        return "\n".join(lines)

    def getVal(self, row, col):
        """Get the value at a given row and column."""
        try:
            return self.grid[row][col]
        except IndexError:
            raise IndexError(f"Invalid row or column: {row}, {col}")

    def setVal(self, row, col, val):
        """Set the value at a given row and column."""
        self.grid[row][col] = val

    def getRow(self, row):
        """Get the values in a given row."""
        try:
            return self.grid[row]
        except IndexError:
            raise IndexError(f"Invalid row: {row}")

    def getCol(self, col):
        """Get the values in a given column."""
        return self.grid[:, col]

    def getSubgrid(self, row, col, fixed=False):
        """Get the subgrid containing the given row and column."""
        row_start = row - (row % self.subgrid_size)
        col_start = col - (col % self.subgrid_size)
        if fixed:
            return self.fixedValues[row_start : row_start + self.subgrid_size, col_start : col_start + self.subgrid_size]
        return self.grid[row_start : row_start + self.subgrid_size, col_start : col_start + self.subgrid_size]

    def getSubgridSum(self, subgrid):
        """Get the sum of the values in a given subgrid."""
        return np.sum(subgrid)