""" Enter and exit procedures for all states
    in game state machine """

import math
import os

from PyQt5 import QtPrintSupport
from PyQt5 import QtSvg
from PyQt5.QtCore import Qt, QObject, QPoint, QCoreApplication, QByteArray
from PyQt5.QtGui import QPainter, QTextCursor
from PyQt5.QtWidgets import (QWidget, QTextEdit, QPushButton, QDialog,
                             QFileDialog, QInputDialog, QGridLayout, QGraphicsScene, QGraphicsView,
                             QMenu)

import Constants as Cons
import qbwrdd
import qsolver


class States(QObject):
    """ Class holding all entry and exit actions for states """

    def __init__(self, scene, machine):
        super(States, self).__init__()

        self.scene = scene
        self.machine = machine
        # result - Passes values between states as tuple (description, value) Holds the error if state exited on error
        self.result = (None,)
        self.current_state = None  # Holds current state
        self.choice, self.log = None, None
        self.view, self.editor = None, None
        self.buttonCancel, self.buttonPreview, self.buttonPrint = None, None, None
        self.step = False  # True if step pressed
        self.gen = None  # Generator for next function in step

        self.board = qbwrdd.Board(self.scene, self)
        self.board.draw_board()
        self.board_size = self.board.board_size
        self.digits = self.board.digits
        self.solver = qsolver.Solver(self.board)
        self.msg = qsolver.Msg(self.scene)
        self.solver.initialize()

    # -------------------------------------------------------------------------
    def s_enter_wait(self):
        """ Enter wait state """

        self.current_state = self.machine.property("state")
        print("DEBUG", self.current_state)
        # self.solver.check_hidden_tuples()

    def s_exit_wait(self):
        """ Exit wait state """
        pass

    # -------------------------------------------------------------------------
    def s_enter_setup(self):
        """ Enter setup board state """

        self.current_state = self.machine.property("state")
        print("DEBUG", self.current_state)
        self.msg.show_msg(self.current_state)

        # If board empty ask for size
        if all(x == self.board.sudoku[0] for x in self.board.sudoku):
            menu = QMenu("Choose Size")
            fourAction = menu.addAction("4 x 4")
            sixAction = menu.addAction("6 x 6")
            eightAction = menu.addAction("8 x 8")
            nineAction = menu.addAction("9 x 9")
            tenAction = menu.addAction("10 x 10")
            twelveAction = menu.addAction("12 x 12")
            board_size = {fourAction: 4, sixAction: 6, eightAction: 8, nineAction: 9, tenAction: 10, twelveAction: 12}
            action = menu.exec_(
                QPoint(Cons.BUTTON_X + Cons.SETUP_BUTTON[0] - 5, Cons.BUTTON_Y + Cons.SETUP_BUTTON[1] - 30))
            size = board_size.get(action, 9)
            self.reset_board(size)
        # Board not empty but in original state
        elif self.board.sudoku == self.board.content:
            self.board.free_sudoku()
        # Not doable if moves on board
        else:
            self.result = ("error",)
            self.machine.action_complete.emit()

    def s_exit_setup(self):
        """ Exit setup board state """

        print("enter exit setup")
        if self.result[0] != "error":
            self.board.clear_area()
            self.board.set_sudoku()
            self.board.freeze_sudoku()
            self.solver.initialize()
            self.step = False
        self.result = (None,)
        self.msg.clear_msg()

    # -------------------------------------------------------------------------
    def s_enter_load(self):
        """ Enter load saved board state """

        self.current_state = self.machine.property("state")
        print("DEBUG", self.current_state)
        self.msg.show_msg(self.current_state)

        cancel, new_sudoku, new_content = self.load_file()
        if not cancel:
            self.reset_board(len(new_sudoku))
            self.board.sudoku = list(new_sudoku)
            self.board.content = list(new_content)
            self.board.load_board()
            self.board.freeze_sudoku()
            self.solver.initialize()
            self.step = False

        self.machine.action_complete.emit()

    def load_file(self):
        """ Load contents from file """
        filename, _ = QFileDialog.getOpenFileName(QCoreApplication.instance().activeWindow(), 'Open file',
                                                  '.\data', '*.txt', options=QFileDialog.DontUseNativeDialog)
        cancel = True
        new_sudoku, new_content = None, None
        if filename:
            cancel = False
            datafile = open(filename, "r")
            data = datafile.readlines()
            datafile.close()

            # Check if there are multiple entries and if so
            # Store list of start lines in indexes
            indexes = None
            size = len(data[0]) - 1
            if size in Cons.SIZE_DICT:
                no_lines = size
                # If there is a separator between squares use to get positions
                # Otherwise use size of square - accommadates different sizes in same file
                if len(data) > no_lines and data[no_lines][0] not in Cons.DIGITS + ".0":
                    separator = data[no_lines]
                    indexes = [index + 1 for index, line in enumerate(data) if line == separator]
                    indexes.insert(0, 0)
                else:
                    indexes = [0]
                    pos = 0
                    while pos < len(data):
                        size = len(data[pos]) - 1
                        pos += size
                        indexes.append(pos)
            # Each square is on one long line of data
            else:
                size = int(math.sqrt(size))
                no_lines = 1

            # Get number of entries in data file
            # And ask user for entry to load
            # If line 2 says CONTENT this is a saved game
            if "CONTENT" not in data[1]:
                if indexes:
                    total = len(indexes)
                else:
                    total = len(data) // no_lines
                no = self.get_integer(total) - 1
                # Invalid input or window closed
                if no < 0:
                    cancel = True
            else:
                no = 0

            if not cancel:
                if no_lines > 1:
                    start = indexes[no]
                    size = len(data[start]) - 1
                    new_data = ""
                    for row in range(start, start + size):
                        new_data = new_data + data[row].strip()
                else:
                    new_data = data[no].strip()
                new_sudoku = self.get_list(size, new_data)
                new_content = [row[:] for row in new_sudoku]
                if data[1] == "CONTENT\n":
                    new_content = self.get_list(size, data[2])
        return cancel, new_sudoku, new_content

    def get_list(self, size, data):
        new_list = []
        for i in range(size):
            new_list.append(self.load_row(size, i * size, data))
        return new_list

    @staticmethod
    def load_row(size, start, data):
        new_row = []
        for i in range(start, start + size):
            if data[i] == ".":
                new_row.append("0")
            else:
                new_row.append(data[i])
        return new_row

    @staticmethod
    def get_integer(maximum):
        num, ok_pressed = QInputDialog.getInt(QCoreApplication.instance().activeWindow(), "Enter Number", "Number:", 1,
                                              1, maximum, 1)
        if ok_pressed:
            return num
        else:
            return 0

    def s_exit_load(self):
        """ Exit load saved board state """
        self.msg.clear_msg()
        pass

    # -------------------------------------------------------------------------
    def s_enter_save(self):
        """ Enter save board state """

        self.current_state = self.machine.property("state")
        print("DEBUG", self.current_state)
        self.msg.show_msg(self.current_state)

        filename, _ = QFileDialog.getSaveFileName(QCoreApplication.instance().activeWindow(), 'Save Game',
                                                  '.\data', '*.txt', options=QFileDialog.DontUseNativeDialog)
        _, f_extension = os.path.splitext(filename)
        if filename:
            if not f_extension:
                filename = filename + '.txt'
            try:
                with open(filename, 'w') as f:
                    f.write(self.convert_board(self.board.sudoku))
                    if self.board.content != self.board.sudoku:
                        f.write("\nCONTENT\n")
                        f.write(self.convert_board(self.board.content))
            except (IOError, OSError) as inst:
                print("IO/OSError", inst.errno, "-", os.strerror(inst.errno))
            else:
                print("Error")
        self.machine.action_complete.emit()

    def convert_board(self, lst):
        new_data = ""
        for row in lst:
            new_data += self.convert(row)
        return new_data

    @staticmethod
    def convert(row):
        new_row = ""
        for no in row:
            if no == "0":
                new_row += "."
            else:
                new_row += no
        return new_row

    def s_exit_save(self):
        """ Exit save board state """
        self.msg.clear_msg()
        pass

    # -------------------------------------------------------------------------
    def s_enter_solve(self):
        """ Enter solve board state """

        self.current_state = self.machine.property("state")
        print("DEBUG", self.current_state)
        self.msg.show_msg(self.current_state)

        self.solver.solve()
        # solved = self.solver.solve_grid(self.solver.content)
        # self.board.load_board()

        self.machine.action_complete.emit()

    def s_exit_solve(self):
        """ Exit solve board state """
        self.msg.clear_msg()
        pass

    # -------------------------------------------------------------------------
    def s_enter_step(self):
        """ Enter step in solution state """

        self.current_state = self.machine.property("state")
        print("DEBUG", self.current_state)
        self.msg.show_msg(self.current_state)

        self.msg.clear_msg()
        if self.board.hint:
            self.solver.remove_possibles()
        if not self.step:
            self.gen = self.solver.get_next()
            self.step = True
        num_func = self.solver.solve_step(self.gen)
        self.msg.show_msg(Cons.FUNC_MSGS[num_func])
        if self.board.hint:
            self.solver.show_possibles()

        self.machine.action_complete.emit()

    def s_exit_step(self):
        """ Exit step in solution state """
        pass

    # -------------------------------------------------------------------------
    def s_enter_clear(self):
        """ Enter clear board state """

        self.current_state = self.machine.property("state")
        print("DEBUG", self.current_state)
        self.msg.show_msg(self.current_state)

        self.board.clear_board_area()
        self.board.draw_board()
        self.step = False
        self.machine.action_complete.emit()

    def s_exit_clear(self):
        """ Exit clear board state """
        self.msg.clear_msg()
        pass

    # -------------------------------------------------------------------------
    def s_enter_play(self):
        """ Enter play state """

        self.current_state = self.machine.property("state")
        print("DEBUG", self.current_state)
        self.msg.show_msg(self.current_state)
        self.board.free_user_tiles()

    def s_exit_play(self):
        """ Exit play state """
        self.msg.clear_msg()
        pass

    # -------------------------------------------------------------------------
    def s_enter_hint(self):
        """ Enter hint state """

        self.current_state = self.machine.property("state")
        print("DEBUG", self.current_state)
        self.msg.show_msg(self.current_state)

        if not self.board.hint:
            self.solver.show_possibles()
        self.machine.action_complete.emit()

    def s_exit_hint(self):
        """ Exit hint state """
        if not self.board.hint:
            self.board.hint = True
        else:
            self.solver.remove_possibles()
            self.board.hint = False
        self.msg.clear_msg()
        pass

    # -------------------------------------------------------------------------

    def s_enter_restart(self):
        """ Enter restart state """

        self.current_state = self.machine.property("state")
        print("DEBUG", self.current_state)
        self.msg.show_msg(self.current_state)

        self.board.clear_board()
        self.solver.initialize()
        self.step = False
        self.machine.action_complete.emit()

    def s_exit_restart(self):
        """ Exit restart state """
        self.msg.clear_msg()
        pass

    # -------------------------------------------------------------------------

    def s_enter_print(self):
        """ Enter print state """

        self.current_state = self.machine.property("state")
        print("DEBUG", self.current_state)
        self.msg.show_msg(self.current_state)

        byte_array = self.create_svg()

        self.choice = QWidget()
        self.choice.setWindowFlags(Qt.FramelessWindowHint)
        self.choice.move(Cons.WINDOW_SIZE[0] / 2, Cons.WINDOW_SIZE[1] / 2)
        self.editor = QtSvg.QSvgWidget()
        self.editor.load(byte_array)
        self.buttonPrint = QPushButton('Print', self.choice)
        self.buttonPrint.clicked.connect(self.handle_print)
        self.buttonPreview = QPushButton('Preview', self.choice)
        self.buttonPreview.clicked.connect(self.handle_preview)
        self.buttonCancel = QPushButton('Cancel', self.choice)
        self.buttonCancel.clicked.connect(self.end_print)

        self.scene = QGraphicsScene()
        self.scene.addWidget(self.editor)
        self.view = QGraphicsView()
        self.view.setScene(self.scene)

        layout = QGridLayout(self.choice)
        layout.addWidget(self.view, 0, 0, 1, 3)
        layout.addWidget(self.buttonPrint, 1, 0)
        layout.addWidget(self.buttonPreview, 1, 1)
        layout.addWidget(self.buttonCancel, 1, 2)

        self.choice.show()
        self.machine.action_complete.emit()

    def create_svg(self):
        c_size, r_size = Cons.SIZE_DICT[self.board_size]
        v_lines_bold, h_lines_bold = [], []
        v_lines_light, h_lines_light = [], []
        box = 326
        margin = 10
        rect = box - 2 * margin
        cell = rect // self.board_size
        font = 24
        font_size = round(font * 1.333)  # 20 pt in pxs
        y_adjust = round(font_size * 0.5) // 2 - cell // 2  # descenders approx 20-30% of font height
        c_num, r_num = [margin + cell // 2], []
        for line in range(1, self.board_size):
            if line % c_size == 0:
                v_lines_bold.append(margin + line * cell)
            else:
                v_lines_light.append(margin + line * cell)
            c_num.append(margin + line * cell + cell // 2)
        for line in range(1, self.board_size):
            if line % r_size == 0:
                h_lines_bold.append(margin + line * cell)
            else:
                h_lines_light.append(margin + line * cell)
            r_num.append(margin + line * cell + y_adjust)
        r_num.append(rect + margin + y_adjust)

        b_array = QByteArray()
        b_array.append(Cons.SVG_PRINT_1.format(box=box))
        b_array.append(Cons.SVG_PRINT_2.format(box=box, rect=rect, margin=margin))
        for line in h_lines_bold:
            b_array.append(Cons.SVG_PRINT_3.format(start_x=margin, start_y=line, end_x=rect, end_y=0))
        for line in v_lines_bold:
            b_array.append(Cons.SVG_PRINT_3.format(start_x=line, start_y=margin, end_x=0, end_y=rect))
        for line in h_lines_light:
            b_array.append(Cons.SVG_PRINT_4.format(start_x=margin, start_y=line, end_x=rect, end_y=0))
        for line in v_lines_light:
            b_array.append(Cons.SVG_PRINT_4.format(start_x=line, start_y=margin, end_x=0, end_y=rect))
        b_array.append(Cons.SVG_PRINT_5.format(box=box, rect=rect))

        for r in range(self.board_size):
            for c in range(self.board_size):
                num = self.board.content[r][c]
                if num != "0":
                    if self.board.sudoku[r][c] != "0":
                        col = "black"
                    else:
                        col = "red"
                    x = c_num[c]
                    y = r_num[r]
                    b_array.append(Cons.SVG_PRINT_6.format(x=x, y=y, font_size=font, col=col, num=num))
        b_array.append("</svg>")
        return b_array

        # Using svg subelements not available in svg Tiny (as used in qt)
        # <svg x={x} y={y} width={cell} height={cell}>
        # <rect x="0" y="0" width={cell} height={cell} stroke="transparent" stroke-opacity="0" fill="none"/>
        # <text x="50%" y="50%" dy="0.4em" font-family="Arial, sans-serif"
        #  font-size="20pt" text-anchor="middle" fill={col}>{num}</text>

    def handle_print(self):
        printer = QtPrintSupport.QPrinter(QtPrintSupport.QPrinter.HighResolution)
        dialog = QtPrintSupport.QPrintDialog(printer)
        if dialog.exec_() == QDialog.Accepted:
            self.handle_paint_request(printer)
        self.end_print()

    def handle_preview(self):
        printer = QtPrintSupport.QPrinter(QtPrintSupport.QPrinter.HighResolution)
        dialog = QtPrintSupport.QPrintPreviewDialog(printer)
        dialog.paintRequested.connect(self.handle_paint_request)
        dialog.exec_()
        self.end_print()

    def handle_paint_request(self, printer):
        # self.view.render(QtGui.QPainter(printer))
        painter = QPainter(printer)
        painter.setViewport(self.view.rect())
        painter.setWindow(self.view.rect())
        self.view.render(painter)
        painter.end()

    def end_print(self):
        self.choice.hide()
        self.choice.deleteLater()
        self.machine.action_complete.emit()

    def s_exit_print(self):
        """ Exit print state """
        self.msg.clear_msg()
        pass

    # -------------------------------------------------------------------------
    def s_enter_check(self):
        """ Enter check state """

        if self.choice is not None:
            self.end_check()
            return

        self.current_state = self.machine.property("state")
        print("DEBUG", self.current_state)
        self.msg.show_msg(self.current_state)

        self.check = self.get_checks()
        self.solver.initialize()
        self.choice = QWidget()
        self.choice.setWindowFlags(Qt.FramelessWindowHint)
        self.choice.setFixedSize(300, 350)
        self.choice.move(Cons.WINDOW_SIZE[0] / 2 - 410, Cons.WINDOW_SIZE[1] / 2 - 120)
        self.log = QTextEdit()
        self.buttonCancel = QPushButton('Cancel', self.choice)
        self.buttonCancel.clicked.connect(self.end_check)

        layout = QGridLayout(self.choice)
        layout.addWidget(self.log, 0, 0, 1, 3)
        layout.addWidget(self.buttonCancel, 1, 1)

        self.choice.show()

        nos = list(Cons.DIGITS)[:self.board_size]
        self.error = False

        if self.check == 1:
            self.write_log(self.log, "\nChecking for blank cells ...\n\n")
            for r_no in range(self.board_size):
                for c_no in range(self.board_size):
                    if self.board.content[r_no][c_no] == '0':
                        self.write_log(self.log,
                                       "Blank at row " + str(r_no + 1) + " column " + str(c_no + 1) + "\n")
                        self.error = True

        elif self.check == 2:
            self.write_log(self.log, "\nChecking for missing nos ...\n\n")
            self.write_log(self.log, "\nChecking rows...\n\n")
            for r_no in range(self.board_size):
                row = self.solver.get_row(r_no)
                if not ((len(set(row)) == len(row) == max(row)) and min(row) == 1):
                    self.test_list(row, nos, r_no, "Row")

            self.write_log(self.log, "\nChecking columns...\n\n")
            for c_no in range(self.board_size):
                col = self.solver.get_column(c_no)
                if not ((len(set(col)) == len(col) == max(col)) and min(col) == 1):
                    self.test_list(col, nos, c_no, "Column")

            self.write_log(self.log, "\nChecking squares...\n\n")
            squares = self.solver.squares
            for s_no in range(len(squares)):
                squ = self.solver.get_square(s_no)
                if not ((len(set(squ)) == len(squ) == max(squ)) and min(squ) == 1):
                    self.test_list(squ, nos, s_no, "Square")

        elif self.check == 3:
            self.write_log(self.log, "\nChecking for duplicates ...\n\n")
            self.write_log(self.log, "\nChecking rows...\n\n")
            for r_no in range(self.board_size):
                row = self.solver.get_row(r_no)
                if not ((len(set(row)) == len(row) == max(row)) and min(row) == 1):
                    self.test_list(row, nos, r_no, "Row")

            self.write_log(self.log, "\nChecking columns...\n\n")
            for c_no in range(self.board_size):
                col = self.solver.get_column(c_no)
                if not ((len(set(col)) == len(col) == max(col)) and min(col) == 1):
                    self.test_list(col, nos, c_no, "Column")

            self.write_log(self.log, "\nChecking squares...\n\n")
            squares = self.solver.squares
            for s_no in range(len(squares)):
                squ = self.solver.get_square(s_no)
                if not ((len(set(squ)) == len(squ) == max(squ)) and min(squ) == 1):
                    self.test_list(squ, nos, s_no, "Square")

        elif self.check == 4:
            self.write_log(self.log, "\nChecking numbers...\n\n")
            solution = [[item for item in lst] for lst in self.board.sudoku]
            self.solver.solve_grid(solution)
            for r_no in range(self.board_size):
                for c_no in range(self.board_size):
                    if (self.board.content[r_no][c_no] != '0' and
                            self.board.content[r_no][c_no] != solution[r_no][c_no]):
                        self.write_log(self.log,
                                       "Entry at row " + str(r_no + 1) + " column " + str(c_no + 1) + " incorrect\n")
                        self.error = True

        else:
            self.end_check()

        if not self.error:
            self.write_log(self.log, "\nNo errors found\n\n")

    def test_list(self, lst, nos, l_no, txt):
        counter = self.dups_count_dict(lst, nos)
        if self.check == 2:
            empty = [key for key, val in counter.items() if val == 0]
            if empty:
                self.write_log(self.log, txt + " " + str(l_no + 1) + ": " + ','.join(str(n) for n in empty) + "\n")
                self.error = True
        if self.check == 3:
            dups = [key for key, val in counter.items() if val > 1]
            if dups:
                self.write_log(self.log,
                               txt + " " + str(l_no + 1) + ": " + ','.join(str(n) for n in dups) + " duplicated\n")
                self.error = True

    @staticmethod
    def dups_count_dict(lst, nos):
        nos.append("0")
        digit_count = dict([(digit, 0) for digit in nos])
        for item in lst:
            digit_count[item] += 1
        del digit_count["0"]
        return digit_count

    @staticmethod
    def write_log(log, msg):
        """ Write to log """
        log.moveCursor(QTextCursor.End)
        log.insertPlainText(msg)
        log.verticalScrollBar().setValue(log.verticalScrollBar().maximum())

    def get_checks(self):
        menu = QMenu("Choose check")
        blankAction = menu.addAction("Blank cells")
        missAction = menu.addAction("Missing nos")
        dupAction = menu.addAction("Duplicates")
        numAction = menu.addAction("Entries")
        check_type = {blankAction: 1, missAction: 2, dupAction: 3, numAction: 4}
        action = menu.exec_(
            QPoint(Cons.BUTTON_X + Cons.PLAY_BUTTON[0] - 5, Cons.BUTTON_Y + Cons.CHECK_BUTTON[1] + 50))
        return check_type.get(action, 0)

    def end_check(self):
        self.choice.hide()
        self.choice.deleteLater()
        self.choice = None
        self.machine.action_complete.emit()

    def s_exit_check(self):
        """ Exit check state """
        self.msg.clear_msg()
        pass

    # -------------------------------------------------------------------------
    def reset_board(self, size):
        """ Reset board """
        self.result = (None,)
        self.board.clear_board_area()
        self.board.draw_board(size)
        self.board_size = self.board.board_size
        self.digits = self.board.digits
        self.step = False
