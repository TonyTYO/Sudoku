""" Algorithms for solving square """

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QLabel

import Constants as Cons
import qbwrdd


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

    def initialize(self):

        self.content = self.board.content
        self.board_size, self.r_size, self.c_size = self.board.get_board_size()
        self.digits = self.board.digits
        self.squares = self.list_squares()
        self.poss_tiles = [[None] * self.board_size for _ in range(self.board_size)]
        self.possibles = [[set()] * self.board_size for _ in range(self.board_size)]

        self.change = False
        self.set_possible()

        print("Sudoku", self.board.sudoku)
        print("Content", self.board.content)

    # -------------------------------------------------------------------------
    # Routines to get lists of entries in row, column, square

    def list_squares(self):
        """ Return list of lists of cells in squares """
        squares_lst = []
        row, col = 0, 0
        while row < self.board_size:
            while col < self.board_size:
                square = self.add_square(row, col)
                squares_lst.append(square)
                col += self.c_size
            row += self.r_size
            col = 0
        return squares_lst

    def add_square(self, row, col):
        """ Return list of cells in one square """
        square = []
        r, c = row, col
        while r < row + self.r_size:
            while c < col + self.c_size:
                square.append((r, c))
                c += 1
            r += 1
            c = col
        return square

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

    def get_square_list(self, squ):
        """ get list of elements in square by cell list """
        square = []
        for cell in squ:
            square.append(self.content[cell[0]][cell[1]])
        return square

    @staticmethod
    def transpose(lst):
        """ Transpose rows and columns """
        return list(zip(*lst))

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
                            self.possibles[row][col].remove(num)
                else:
                    self.possibles[row][col] = set()

    def reset_possible(self, num, row, col):
        """ Reset possibles after num in (row, col) """
        self.possibles[row][col] = []
        for c in range(self.board_size):
            print(num, row, c)
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
                    teil = qbwrdd.Tile(poss, self.board.scene)
                    teil.cell = "poss"
                    cell = row * self.board_size + col
                    pos_x, pos_y = self.board.cells[cell].x(), self.board.cells[cell].y()
                    if col % 3 > 0:
                        pos_x += 2
                    self.poss_tiles[row][col] = teil
                    teil.draw_tile_at(pos_x, pos_y)

    def redo_possibles(self):
        """ Refresh possible values on board """
        self.remove_possibles()
        self.set_possible()
        self.show_possibles()

    def remove_possibles(self):
        """ Remove possible values from board """
        for row in range(self.board_size):
            for col in range(self.board_size):
                self.remove_poss(row, col)

    def remove_poss(self, row, col):
        """ Remove possible values from one cell """
        if self.poss_tiles[row][col] is not None:
            self.poss_tiles[row][col].remove()
            self.poss_tiles[row][col] = None

    # -------------------------------------------------------------------------
    # Routines to solve board

    def naked_singles(self):
        """ Check for naked singles """
        self.change = True
        while self.change:
            self.naked_round()

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
        while self.change:
            self.hidden_round()

    def hidden_round(self):
        """ Go through rowa, columns and squares checking
            if only one cell can hold a particular value """
        self.change = False
        for row in range(self.board_size):
            hidden = self.find_singles(self.possibles[row])
            hidden = [[num, (row, pos)] for num, pos in hidden]
            if hidden:
                self.set_hidden(hidden)
        for col in range(self.board_size):
            hidden = self.find_singles([self.possibles[row][col] for row in range(self.board_size)])
            hidden = [[num, (pos, col)] for num, pos in hidden]
            if hidden:
                self.set_hidden(hidden)
        for index in range(self.board_size):
            squ = self.squares[index]
            hidden = self.find_singles([self.possibles[cell[0]][cell[1]] for cell in squ])
            hidden = [[num, squ[pos]] for num, pos in hidden]
            if hidden:
                self.set_hidden(hidden)

    def set_hidden(self, lst):
        """ Set any hidden singles found in board """
        for item in lst:
            self.set_number(item[0], item[1][0], item[1][1], "HS")

    def find_singles(self, rhes):
        """ Count no of occurrences of digits from nos in nested list rhes
            Return value and cell for value that only occurs once in lists in rhes """
        digit_count = self.count_dict(rhes)
        found = [num for num, val in digit_count.items() if val == 1]
        return [[number, pos] for pos, lst in enumerate(rhes) for number in found if number in lst]

    def check_pointing_pair(self):
        """ Look for numbers only possible in one row or column of square
            If found remove that number for all other cells in that row or column """

        for index in range(self.board_size):
            squ = self.squares[index]
            nos = self.get_numbers([self.possibles[cell[0]][cell[1]] for cell in squ])

            for num in nos:
                s_row, s_col, found = self.same_row_col(num, squ)
                if s_row:
                    row = found[0][0]
                    for c in range(self.board_size):
                        if (row, c) not in squ:
                            if num in self.possibles[row][c]:
                                self.possibles[row][c].remove(num)
                if s_col:
                    col = found[0][1]
                    for r in range(self.board_size):
                        if (r, col) not in squ:
                            if num in self.possibles[r][col]:
                                self.possibles[r][col].remove(num)

    def same_row_col(self, num, squ):
        """ Check if num only in one row or column in squ """
        found = [pos for pos in squ if num in self.possibles[pos[0]][pos[1]]]
        if found:
            row = found[0][0]
            col = found[0][1]
            all_same_row = all(pos[0] == row for pos in found)
            all_same_col = all(pos[1] == col for pos in found)
            if all_same_row ^ all_same_col:
                return all_same_row, all_same_col, found
        return [], [], []

    def check_block_block(self):
        block_horiz, block_vert = self.board_size // self.c_size, self.board_size // self.r_size
        row_poss, col_poss = self.poss_block_byrc()
        row_squares = dict()
        row_bb = dict()
        # row_squares : Dictionary by square of numbers that appear in only two rows in that square
        # {square: {num: [rows]}}
        for square in range(self.board_size):
            rows = row_poss[square]
            digits = rows[0].union(*rows)
            res = [(no, row + self.c_size * (square // self.r_size)) for no in digits for row, lst in enumerate(rows) if
                   no in lst]
            res = [[tup[0], [tup2[1] for tup2 in res if tup2[0] == tup[0]]] for tup in res]
            result = []
            [result.append({x[0]: x[1] for x in res if x[0] not in result if len(x[1]) == 2})]
            row_squares[square] = result[0]
        # row_bb : Dictionary by row block of numbers that appear in the same two rows in two squares
        # {block: ({squares}, no, [rows])}
        for block in range(block_vert):
            start = block * block_horiz
            row_poss = {key: val for key, val in row_squares.items() if key in range(start, start + block_horiz)}
            res = [({k, k2}, num, lst) for (k2, v2) in row_poss.items() for num2, lst2 in v2.items()
                   for k, v in row_poss.items() for num, lst in v.items() if num2 == num and lst2 == lst and k2 != k]
            result = []
            [result.append(x) for x in res if x not in result]
            row_bb[block] = result
        for block in row_bb:
            if row_bb[block]:
                for item in row_bb[block]:
                    squ, num, rows = item
                    for row in rows:
                        for col in range(self.board_size):
                            if self.get_square_index((row, col)) not in squ and num in self.possibles[row][col]:
                                self.possibles[row][col].remove(num)

        col_squares = dict()
        col_bb = dict()
        # col_squares : Dictionary by square of numbers that appear in only two columns in that square
        # {square: {num: [cols]}}
        for square in range(self.board_size):
            cols = col_poss[square]
            digits = cols[0].union(*cols)
            res = [(no, col + self.r_size * (square // self.c_size)) for no in digits for col, lst in enumerate(cols) if
                   no in lst]
            res = [[tup[0], [tup2[1] for tup2 in res if tup2[0] == tup[0]]] for tup in res]
            result = []
            [result.append({x[0]: x[1] for x in res if x[0] not in result if len(x[1]) == 2})]
            col_squares[square] = result[0]
        # col_bb : Dictionary by col block of numbers that appear in the same two columns in two squares
        # {block: ({squares}, no, [cols])}
        for block in range(block_horiz):
            start = block * block_vert
            col_poss = {key: val for key, val in col_squares.items() if key in range(start, start + block_vert)}
            res = [({k, k2}, num, lst) for (k2, v2) in col_poss.items() for num2, lst2 in v2.items()
                   for k, v in col_poss.items() for num, lst in v.items() if num2 == num and lst2 == lst and k2 != k]
            result = []
            [result.append(x) for x in res if x not in result]
            col_bb[block] = result
        for block in col_bb:
            if col_bb[block]:
                for item in col_bb[block]:
                    squ, num, cols = item
                    for col in cols:
                        for row in range(self.board_size):
                            if self.get_square_index((row, col)) not in squ and num in self.possibles[row][col]:
                                self.possibles[row][col].remove(num)

    def poss_block_byrc(self):
        """ Possible values by block and row/ col within block
            for each block [{possible values by row/col}]"""
        block_horiz, block_vert = self.board_size // self.c_size, self.board_size // self.r_size
        lpos = [self.c_size * no for no in range(block_horiz)]
        vpos = [self.r_size * no for no in range(block_vert)]
        row_poss, col_poss = self.poss_by_block()
        row_poss = [row_poss[x:x + self.c_size] for x in vpos]
        row_poss = [[subset[no] for subset in r] for r in row_poss for no in range(self.r_size)]
        col_poss = [col_poss[x:x + self.r_size] for x in lpos]
        col_poss = [[subset[no] for subset in r] for r in col_poss for no in range(self.c_size)]
        # Rearrange to get blocks in right order (across-down)
        col_poss = [col_poss[i + j * block_vert] for i in range(block_vert) for j in range(block_vert)]
        return row_poss, col_poss

    def poss_by_block(self):
        """ Possible values by row/col and block within row/col
            for each row/col [{possible values by block}]"""
        block_horiz, block_vert = self.board_size // self.c_size, self.board_size // self.r_size
        lpos = [self.c_size * no for no in range(block_horiz)]
        vpos = [self.r_size * no for no in range(block_vert)]
        row_poss, col_poss = [], []
        for row in range(self.board_size):
            poss = self.possibles[row]
            poss = [poss[x:x + self.r_size] for x in lpos]
            poss = [{d for subset in p for d in subset} for p in poss]
            row_poss.append(poss)
        for col in range(self.board_size):
            poss = [self.possibles[row][col] for row in range(self.board_size)]
            poss = [poss[x:x + self.c_size] for x in vpos]
            poss = [{d for subset in p for d in subset} for p in poss]
            col_poss.append(poss)
        return row_poss, col_poss

    def check_hidden_tuples(self):
        print("Rows")
        for row in range(self.board_size):
            print(self.get_row_dict(row))
        print("Cols")
        for col in range(self.board_size):
            print(self.get_col_dict(col))
        print("Blocks")
        for index in range(self.board_size):
            print(self.get_squ_dict(index))

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

    # -------------------------------------------------------------------------
    # Set number in board

    def set_number(self, num, row, col, where=""):
        """ Insert number on board """
        print(where, num, "(", row, ",", col, ")", self.possibles[row][col])
        self.content[row][col] = num
        self.possibles[row][col] = set()
        self.board.set_num(num, row, col)
        self.reset_possible(num, row, col)
        self.change = True

    # -------------------------------------------------------------------------
    # Dictionary functions

    def count_num(self, lst):
        """ Count no of occurrences of digits from nos in list lst """
        nos = list(self.digits)
        nos.append("0")
        digit_count = dict([(digit, 0) for digit in nos])
        for num in lst:
            digit_count[num] += 1
        return digit_count

    #
    # @staticmethod
    # def dups_count(rhes, digit_count):
    #     """ Count no of occurrences of digits from nos in nested list l """
    #     found = [num for num, val in digit_count.items() if val == 1]
    #     return [[number, pos] for pos, lst in enumerate(rhes) for number in found if number in lst]

    def count_dict(self, lst):
        """ Count no of occurrences of digits from nos in nested list lst """
        nos = list(self.digits)
        digit_count = dict([(digit, 0) for digit in nos])
        for item in lst:
            for num in item:
                digit_count[num] += 1
        return digit_count

    def get_numbers(self, lst):
        """ Return list of possible values in lst """
        digit_count = self.count_dict(lst)
        return [num for num, val in digit_count.items() if val > 0]

    # -------------------------------------------------------------------------
    # Utiity functions

    @staticmethod
    def print_list(lst):
        """ Print list of lists in rows """
        i = 0
        while i < len(lst):
            print(lst[i])
            i += 1


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
