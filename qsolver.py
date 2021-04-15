""" Algorithms for solving square """

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QLabel
import itertools

import Constants as Cons


class Solver:

    def __init__(self, board):

        self.board = board
        self.possibles = None

        self.content = None
        self.board_size, self.r_size, self.c_size = None, None, None
        self.digits = None
        self.squares = None
        self.poss_tiles = None
        self.possibles = None
        self.change = False
        self.solv_func = [self.naked_singles, self.hidden_singles, self.block_rc, self.block_block,
                          self.naked_subset, self.hidden_subset, self.solve_grid]

    def initialize(self):

        self.content = self.board.content
        self.board_size, self.r_size, self.c_size = self.board.get_board_size()
        self.digits = self.board.digits
        self.squares = self.list_squares_rc()
        self.poss_tiles = [[None] * self.board_size for _ in range(self.board_size)]
        self.possibles = [[set()] * self.board_size for _ in range(self.board_size)]

        self.change = False
        self.set_possible()

        # print("Sudoku", self.board.sudoku)
        # print("Content", self.board.content)

    # -------------------------------------------------------------------------
    # Solutions

    def solve(self):
        """ Complete solution """
        tot_func = len(self.solv_func) - 1
        num_func = -1
        count = 0

        while any(item for sublist in self.possibles for item in sublist):
            num_func = (num_func + 1) % tot_func
            if num_func == 0:
                if count == tot_func:
                    self.solve_grid(self.content)
                    self.board.load_board()
                    break
                count = 0
            count += self.solv_func[num_func]()

    # def get_next(self):
    #     """ Generator to give next function to call
    #         Needs to be called first to restart """
    #     tot_func = len(self.solv_func)
    #     num_func = -1
    #     while True:
    #         num_func = (num_func + 1) % tot_func
    #         yield num_func

    def get_next(self):
        """ Generator to give next function to call
            Needs to be called first to restart """
        tot_func = len(self.solv_func) - 1
        count = 0
        while True:
            num_func = count % tot_func
            if count // tot_func >= 2:
                num_func = tot_func
            count += 1
            yield num_func

    def solve_step(self, gen):
        """ Perform next step in solution """
        num_func = next(gen)
        if num_func == len(self.solv_func) - 1:
            self.solv_func[num_func](self.content)
            self.board.load_board()
        else:
            self.solv_func[num_func]()
        return num_func

    # -------------------------------------------------------------------------
    # Routines to solve board

    def naked_singles(self):
        """ Check for naked singles """
        self.change = True
        count = 0
        while self.change:
            count += 1
            self.naked_round()
        return count

    def naked_round(self):
        """ Go through cells checking
            if only one value possible in cell """
        self.change = False
        for row in range(self.board_size):
            for col in range(self.board_size):
                if len(self.possibles[row][col]) == 1:
                    num = self.possibles[row][col].pop()
                    self.set_number(num, row, col, "NS")

    def hidden_singles(self):
        """ Check for hidden singles """
        self.change = True
        count = 0
        while self.change:
            count += 1
            self.hidden_round()
        return count

    def hidden_round(self):
        """ Go through rowa, columns and squares checking
            if only one cell can hold a particular value """
        self.change = False
        hidden = []
        for index in range(self.board_size):
            self.extend_list(hidden, [[num, pos[0]] for num, pos in self.get_row_dict(index).items() if len(pos) == 1])
            self.extend_list(hidden, [[num, pos[0]] for num, pos in self.get_col_dict(index).items() if len(pos) == 1])
            self.extend_list(hidden, [[num, pos[0]] for num, pos in self.get_squ_dict(index).items() if len(pos) == 1])
        for item in hidden:
            self.set_number(item[0], item[1][0], item[1][1], "HS")

    @staticmethod
    def extend_list(lst1, lst2):
        for item in lst2:
            if item not in lst1:
                lst1.append(item)
        return lst1

    def block_rc(self):
        """ Check for block and column/row interactions """
        self.change = True
        count = 0
        while self.change:
            count += 1
            self.block_rc_round()
        return count

    def block_rc_round(self):
        """ Go through blocks checking for numbers only possible in single row or column
            if found remove as possible from other blocks in that row or column """
        n_row, n_col = [], []
        self.change = False
        for index in range(self.board_size):
            poss = self.get_squ_dict(index)
            n_col = [[num, index, pos[0][1]] for num, pos in poss.items()
                     if all([cell[1] == pos[0][1] for cell in pos])]
            n_row = [[num, index, pos[0][0]] for num, pos in poss.items()
                     if all([cell[0] == pos[0][0] for cell in pos])]

        for item in n_row:
            digit, square, row = item
            squ = self.squares[square]
            for col in range(self.board_size):
                self.check_possibles(digit, row, col, squ)
        for item in n_col:
            digit, square, col = item
            squ = self.squares[square]
            for row in range(self.board_size):
                self.check_possibles(digit, row, col, squ)

    def check_possibles(self, digit, row, col, squ):
        """ Check for item in possibles """
        if (row, col) not in squ:
            if digit in self.possibles[row][col]:
                self.remove_possible(digit, row, col, "BRC Remove Possible", "")

    def block_block(self):
        """ Check for block and block interactions """
        self.change = True
        count = 0
        while self.change:
            count += 1
            self.block_block_round()
        return count

    def block_block_round(self):
        """ Go through blocks checking for numbers only possible in two rows or columns
            if found in two blocks remove as possible from other blocks in that row or column """
        self.change = False
        block_horiz, block_vert = self.board_size // self.c_size, self.board_size // self.r_size
        # For each block in column get digits and cells as dictionary {digit: [(row, col)]
        # only if they occur in two columns in the block
        for hblock in range(block_horiz):
            col_poss = dict()
            for vblock in range(block_vert):
                index = hblock + vblock * block_horiz
                col_poss[index] = {digit: cells for (digit, cells) in self.get_squ_dict(index).items()
                                   if len(set([tup[1] for tup in cells])) == 2}
            block_cols = self.process_bb(col_poss, 1)
            for key, val in block_cols.items():
                blocks, cols = val[0], val[1]
                self.check_squares(key, blocks, cols, 1)
        # For each block in row get digits and cells as dictionary {digit: [(row, col)]
        # only if they occur in two rows in the block
        for vblock in map(lambda x: x * block_horiz, range(block_vert)):
            row_poss = dict()
            for hblock in range(block_horiz):
                index = vblock + hblock
                row_poss[index] = {digit: cells for (digit, cells) in self.get_squ_dict(index).items()
                                   if len(set([tup[0] for tup in cells])) == 2}
            block_rows = self.process_bb(row_poss, 0)
            for key, val in block_rows.items():
                blocks, rows = val[0], val[1]
                self.check_squares(key, blocks, rows, 0)

    def check_squares(self, key, blocks, r_c_list, r_c):
        """ key: digit to look for
            blocks: list of blocks
            r_c_list: set of rows or columns
            r_c: 0 for rows and 1 for columns """
        squares = self.get_squares_col(next(iter(r_c_list), None))
        for squ in squares:
            if squ not in blocks:
                cells = self.get_square_rc(squ)
                for cell in cells:
                    if cell[r_c] in r_c_list and key in self.possibles[cell[0]][cell[1]]:
                        self.remove_possible(key, cell[0], cell[1], "BB Remove Possible", "r" if r_c == 0 else "c")

    @staticmethod
    def process_bb(poss, rowcol):
        """ poss: dictionary of digits in blocks { block index: {digit: [(row, col)]
            returns list of digits that occur in two rows/columns as [[digit, block1, block2, r/c1, r/c2]] """
        # Get all different digits in poss as a set
        digits = set([item for sublist in [[*dct] for index, dct in poss.items()] for item in sublist])
        # Rearrange occurrences of digits as list of lists [[digit, block_index, [(row, col)]]
        comp = [[[dig, index, dct[dig]] for index, dct in poss.items() if dig in dct] for dig in digits]
        # Reaarange as [[digit, block_index, {set of row/col nos}]] for digits in more than two row/col in block
        comp = [[item[0], item[1], set([tup[rowcol] for tup in item[2]])]
                for lst in comp for item in lst if len(item) >= 2]
        # Remove all instances of digits only in one block
        comp = [item for item in comp if sum(x.count(item[0]) for x in comp) > 1]
        # Remove occurrences of digit in block but not in correct row/col pair
        comp = [item for item in comp if [pos[2] for pos in comp if pos[0] == item[0]].count(item[2]) == 2]
        # Convert to dictionary {digit: [[block_indices],{row/col nos]]
        comp = dict((item[0], [[pos[1] for pos in comp if pos[0] == item[0]], item[2]]) for item in comp)
        return comp

    def naked_subset(self):
        """ Check for naked subsets """
        self.change = True
        count = 0
        while self.change:
            count += 1
            self.naked_subset_round()
        return count

    def naked_subset_round(self):
        """ Go through rows, columns, checking for subsets of numbers in possibles
            if found remove from other cells in row, column or block  """
        self.change = False
        for row in range(self.board_size):
            subsets = enumerate(self.possibles[row])
            self.process_list(row, subsets, "r")
        for col in range(self.board_size):
            subsets = enumerate([self.possibles[row][col] for row in range(self.board_size)])
            self.process_list(col, subsets, "c")
        for index in range(self.board_size):
            squ = self.squares[index]
            subsets = enumerate([self.possibles[cell[0]][cell[1]] for cell in squ])
            self.process_list(index, subsets, "s")

    def process_list(self, index, subsets, r_c_s):
        """ Check for subsets in subsets
            index: row, col, squ number
            r_c_s: 'r' row, 'c' col, 's' square"""
        for no in range(2, 1 + self.board_size // 2):
            subset = [(n, s) for n, s in subsets if s and len(s) <= no]
            if subset:
                digits = subset[0][1].union(*[s[1] for s in subset])
                possets = [set(s) for s in itertools.combinations(digits, no)]
                for dig in possets:
                    sets = []
                    for item in subset:
                        if item[1].issubset(dig):
                            sets.append(item[0])
                    if len(sets) == no:
                        self.edit_poss(index, dig, sets, r_c_s)

    def edit_poss(self, index, dig, sets, r_c_s):
        """ Check for and remove relevant possibilities from self.possibles """
        if r_c_s == "r":
            for col in range(self.board_size):
                if col not in sets:
                    for no in dig:
                        self.remove_possible(no, index, col, "NS Remove Possible", "r")
        elif r_c_s == "c":
            for row in range(self.board_size):
                if row not in sets:
                    for no in dig:
                        self.remove_possible(no, row, index, "NS Remove Possible", "c")
        elif r_c_s == "s":
            squ = enumerate(self.squares[index])
            for item in squ:
                pos, cell = item 
                if pos not in sets:
                    for no in dig:
                        self.remove_possible(no, cell[0], cell[1], "NS Remove Possible", "s")

    def hidden_subset(self):
        """ Check for hidden subsets """
        self.change = True
        count = 0
        while self.change:
            count += 1
            self.hidden_subset_round()
        return count

    def hidden_subset_round(self):
        """ Go through rows, columns, checking for hidden subsets of numbers in possibles
            if found remove other values from these cells in row, column or block  """
        self.change = False
        for row in range(self.board_size):
            subsets = enumerate(self.possibles[row])
            self.process_hidden(row, subsets, "r")
        for col in range(self.board_size):
            subsets = enumerate([self.possibles[row][col] for row in range(self.board_size)])
            self.process_hidden(col, subsets, "c")
        for index in range(self.board_size):
            squ = self.squares[index]
            subsets = enumerate([self.possibles[cell[0]][cell[1]] for cell in squ])
            self.process_hidden(index, subsets, "s")

    def process_hidden(self, index, subsets, r_c_s):
        """ Check for subsets in subsets
            index: row, col, squ number
            r_c_s: 'r' row, 'c' col, 's' square"""
        for no in range(2, 1 + self.board_size // 2):
            subset = [(n, s) for n, s in subsets if s]
            if subset:
                digits = subset[0][1].union(*[s[1] for s in subset])
                possets = [set(s) for s in itertools.combinations(digits, no)]
                for dig in possets:
                    sets = []
                    for item in subset:
                        if item[1].intersection(dig):
                            sets.append(item[0])
                    if len(sets) == no:
                        self.edit_hidden(index, dig, sets, r_c_s)

    def edit_hidden(self, index, dig, sets, r_c_s):
        """ Check for and remove relevant possibilities from self.possibles """
        if r_c_s == "r":
            for col in sets:
                poss_nos = self.possibles[index][col].copy()
                for no in poss_nos:
                    if no not in dig:
                        self.remove_possible(no, index, col, "HS Remove Possible", "r")
        elif r_c_s == "c":
            for row in sets:
                poss_nos = self.possibles[row][index].copy()
                for no in poss_nos:
                    if no not in dig:
                        self.remove_possible(no, row, index, "HS Remove Possible", "c")
        elif r_c_s == "s":
            squ = enumerate(self.squares[index])
            for item in squ:
                pos, cell = item
                if pos in sets:
                    poss_nos = self.possibles[cell[0]][cell[1]].copy()
                    for no in poss_nos:
                        if no not in dig:
                            self.remove_possible(no, cell[0], cell[1], "HS Remove Possible", "s")

    def remove_possible(self, no, row, col, text, r_c_s):
        """ Remove digit no from self.possibles[row][co] """
        if no in self.possibles[row][col]:
            self.possibles[row][col].discard(no)
            self.change = True

    def solve_grid(self, grid):
        """ A backtracking/recursive function to check all possible combinations of numbers until solution is found """
        # Find next empty cell
        row, col = 0, 0
        for i in range(0, self.board_size ** 2):
            row = i // self.board_size
            col = i % self.board_size
            if grid[row][col] == '0':
                for value in self.digits:
                    # Check that this value has not already been used on this row
                    if value not in grid[row]:
                        # Check that this value has not already been used on this column
                        if value not in [grid[row][col] for row in range(self.board_size)]:
                            # Check that this value has not already been used on this square
                            if value not in (self.get_square_cell_grid((row, col), grid)):
                                grid[row][col] = value
                                if self.check_grid(grid):
                                    return True
                                else:
                                    if self.solve_grid(grid):
                                        return True
                break
        grid[row][col] = '0'

    def check_grid(self, grid):
        """ Check for completely filled grig """
        for row in range(0, self.board_size):
            for col in range(0, self.board_size):
                if grid[row][col] == '0':
                    return False
        return True

    # -------------------------------------------------------------------------
    # Routines to get list of possible entries for each cell

    def set_possible(self):
        """ Fill in all initial possibilities """
        for row in range(self.board_size):
            for col in range(self.board_size):
                if self.content[row][col] == "0":
                    self.possibles[row][col] = set(self.digits)
                    poss = set(self.possibles[row][col])
                    r_num = self.get_row(row)
                    c_num = self.get_column(col)
                    s_num = self.get_square_cell((row, col))
                    for num in poss:
                        if num in r_num or num in c_num or num in s_num:
                            self.possibles[row][col].discard(num)
                else:
                    self.possibles[row][col] = set()

    def reset_possible(self, num, row, col):
        """ Reset possibles after num in (row, col) """
        self.possibles[row][col] = set()
        for c in range(self.board_size):
            if num in self.possibles[row][c]:
                self.possibles[row][c].discard(num)
        for r in range(self.board_size):
            if num in self.possibles[r][col]:
                self.possibles[r][col].discard(num)
        index = self.get_square_index((row, col))
        squ = self.squares[index]
        for cell in squ:
            if num in self.possibles[cell[0]][cell[1]]:
                self.possibles[cell[0]][cell[1]].discard(num)

    def show_possibles(self):
        """ Show possible values on board
            Used by Hint """
        for row in range(self.board_size):
            for col in range(self.board_size):
                poss = list(self.possibles[row][col])
                if poss:
                    self.board.show_poss_tile(poss, row, col)

    def redo_possibles(self):
        """ Refresh possible values on board """
        self.remove_possibles()
        self.set_possible()
        self.show_possibles()

    def remove_possibles(self):
        """ Remove possible values from board """
        for row in range(self.board_size):
            for col in range(self.board_size):
                self.board.remove_poss_tile(row, col)

    # -------------------------------------------------------------------------
    # Set number in board

    def set_number(self, num, row, col, where=""):
        """ Insert number on board """
        self.content[row][col] = num
        self.possibles[row][col] = set()
        self.board.set_num(num, row, col)
        self.reset_possible(num, row, col)
        self.change = True

    # -------------------------------------------------------------------------
    # Dictionary functions

    def get_row_dict(self, row):
        """ Return dictionary of possible digits in row """
        return self.get_dict(self.possibles[row], "R", row)

    def get_col_dict(self, col):
        """ Return dictionary of possible digits in column """
        return self.get_dict([self.possibles[row][col] for row in range(self.board_size)], "C", col)

    def get_squ_dict(self, index):
        """ Return dictionary of possible digits in square """
        squ = self.squares[index]
        return self.get_dict([self.possibles[cell[0]][cell[1]] for cell in squ], "S", squ)

    @staticmethod
    def get_dict(lst, rcs=None, pos=None):
        """ Create dictionary of all possible values in row/col/square
            lst: list of sets, rcs: type R,C or S, pos: row no, col no, list of square cells
            returns {digit: [list of cell positions as (row, col)]} """
        digits = lst[0].union(*lst)
        no_digits = dict()
        for dig in digits:
            where = []
            for s in enumerate(lst):
                if dig in s[1]:
                    if rcs == "S":
                        where.append(pos[s[0]])
                    elif rcs == "R":
                        where.append((pos, s[0]))
                    elif rcs == "C":
                        where.append((s[0], pos))
                    else:
                        where.append(s[0])
            no_digits[dig] = where
        return no_digits

    @staticmethod
    def get_numbers(fnct, index):
        """ Return list of possible values in lst """
        digit_count = fnct(index)
        return [num for num, val in digit_count.items() if val > 0]

    # -------------------------------------------------------------------------
    # Routines to get lists of entries in row, column, square

    def list_squares_rc(self):
        """ Return list of lists of cells in squares
            [[list of cells in squ n as (row, col) tuples] """
        squ = []
        for block in range(self.board_size):
            squ.append(self.get_square_rc(block))
        return squ

    def get_square_rc(self, index):
        """ Return list of cells in one square as [(row,col) tuples] """
        squ = []
        start_r = index // self.r_size * self.r_size
        start_c = index % self.r_size * self.c_size
        for row in range(start_r, start_r + self.r_size):
            for col in range(start_c, start_c + self.c_size):
                squ.append((row, col))
        return squ

    def get_row(self, row):
        """ Return whole row  """
        return self.content[row]

    def get_column(self, col):
        """ Return whole column """
        return [self.content[row][col] for row in range(self.board_size)]

    def get_square(self, index):
        """ get list of elements in square by index """
        square = []
        for cell in self.squares[index]:
            square.append(self.content[cell[0]][cell[1]])
        return square

    def get_square_index(self, cell):
        """ Return index of square containing cell """
        return next(s for s, square in enumerate(self.squares) if cell in square)

    def get_square_cell(self, cell):
        """ get list of elements in square containing cell """
        index = self.get_square_index(cell)
        square = []
        for cell in self.squares[index]:
            square.append(self.content[cell[0]][cell[1]])
        return square

    def get_square_cell_grid(self, cell, grid):
        """ get list of elements in square containing cell """
        index = self.get_square_index(cell)
        square = []
        for cell in self.squares[index]:
            square.append(grid[cell[0]][cell[1]])
        return square

    def get_square_list(self, squ):
        """ get list of elements in square by cell list """
        square = []
        for cell in squ:
            square.append(self.content[cell[0]][cell[1]])
        return square

    def get_squares_row(self, row):
        """ Generates indices of blocks in a row  """
        for squ in range(self.board_size // self.c_size):
            yield row // self.r_size + squ

    def get_squares_col(self, col):
        """ Generates indices of blocks in a column  """
        for squ in range(self.board_size // self.r_size):
            yield col // self.c_size + squ * (self.board_size // self.c_size)

    @staticmethod
    def transpose(lst):
        """ Transpose rows and columns """
        return list(zip(*lst))


class Msg(QLabel):
    """ Class defines showing of messages """

    def __init__(self, scene, parent=None):
        super(Msg, self).__init__(parent)

        self.scene = scene
        self.setLineWidth(5)
        self.setMidLineWidth(5)
        self.setStyleSheet("background-color:rgb(230, 200, 167); color : black;")
        self.move(Cons.INSTR_RECT[0], Cons.INSTR_RECT[1])
        self.resize(Cons.INSTR_RECT[2], Cons.INSTR_RECT[3])
        self.setFont(QFont("Arial", 18))
        self.setAlignment(Qt.AlignCenter)
        self.setWordWrap(True)
        self.setTextFormat(Qt.PlainText)
        self.proxy = self.scene.addWidget(self)

    def show_msg(self, text):
        """ Show message """

        self.setText(text)
        self.show()

    def clear_msg(self):
        """ Clear message """

        self.clear()
