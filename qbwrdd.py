# pylint: disable=locally-disabled,no-member,no-name-in-module,invalid-name
""" Sets up the game playboard """

from PyQt5.QtCore import (QPointF, Qt, QObject, QPoint, pyqtProperty, QRectF, pyqtSignal)
from PyQt5.QtGui import (QColor, QPixmap, QTransform, QImage)
from PyQt5.QtWidgets import (QGraphicsItem, QGraphicsPixmapItem, QGraphicsRectItem,
                             QLabel, QGraphicsProxyWidget)

import Constants as Cons


# PyQt doesn't support deriving from more than one wrapped class so we use
# composition and delegate the property.
class Pixmap(QObject):
    """ Wrapper class for PixmapItem """

    def __init__(self, pix):
        super(Pixmap, self).__init__()

        self.pixmap_item = QGraphicsPixmapItem(pix)
        self.pixmap_item.setFlag(QGraphicsItem.ItemIsMovable)
        self.pixmap_item.setCacheMode(QGraphicsItem.DeviceCoordinateCache)

    def __del__(self):
        self.deleteLater()

    def _set_pos(self, pos):
        self.pixmap_item.setPos(pos)

    def _get_pos(self):
        return self.pixmap_item.pos()

    def _set_opacity(self, op):
        self.pixmap_item.setOpacity(op)

    def _get_opacity(self):
        self.pixmap_item.opacity()

    pos = pyqtProperty(QPointF, fset=_set_pos, fget=_get_pos)  # Position property
    opacity = pyqtProperty(float, fset=_set_opacity, fget=_get_opacity)  # Opacity property

    def get_pixmap(self):
        """ Return pixmap item """
        return self.pixmap_item

    def set_pixmap(self, pix):
        """ Set pixmap item """
        self.pixmap_item.setPixmap(pix)

    def movable(self, on):
        if on:
            self.pixmap_item.setFlag(QGraphicsItem.ItemIsSelectable)
            self.pixmap_item.setFlag(QGraphicsItem.ItemIsMovable)
        else:
            self.pixmap_item.setFlag(QGraphicsItem.ItemIsSelectable, False)
            self.pixmap_item.setFlag(QGraphicsItem.ItemIsMovable, False)


class Board:
    """ Setup the board for the game """

    def __init__(self, scene, states):
        self.scene = scene
        self.states = states

        self.cells = []  # Coordinates of each cell (x, y, width, height)
        self.buttons = None
        self.background_item = None

        self.content = None  # All digits on board by row, col
        self.sudoku = None  # Original digits on board by row, col
        self.tiles = None  # Tiles on board by row, col
        self.poss_tiles = None  # Possibles tiles on board by row, col
        self.board_size = Cons.SIZE  # Size of board
        self.c_size, self.r_size = None, None  # Size of sub squares
        self.digits = None  # All digits available
        self.hint = False  # True to show possibles

    def draw_board(self, size=Cons.SIZE):
        """ Draw playing board """

        self.board_size = size
        self.c_size, self.r_size = Cons.SIZE_DICT[self.board_size]
        self.digits = Cons.DIGITS[:self.board_size]
        Tile.board_size = self.board_size
        Tile.digits = self.digits

        self.content = [["0"] * self.board_size for _ in range(self.board_size)]
        self.sudoku = [["0"] * self.board_size for _ in range(self.board_size)]
        self.tiles = [[None] * self.board_size for _ in range(self.board_size)]
        self.poss_tiles = [[None] * self.board_size for _ in range(self.board_size)]

        board_w = self.board_size * (Cons.WIDTH + Cons.MARGIN) + Cons.MARGIN  # width of playing board
        board_h = self.board_size * (Cons.HEIGHT + Cons.MARGIN) + Cons.MARGIN  # height of playing board
        board_x = (Cons.WINDOW_SIZE[0] - board_w) / 2  # x-coordinate of scrabble board
        board_y = (Cons.WINDOW_SIZE[1] - board_h) / 2  # y-coordinate of scrabble board
        board = [board_x, board_y, board_w, board_h]  # board rect details

        self.cells = []
        self.background_item = QGraphicsRectItem(board[0], board[1],
                                                 board[2], board[3])
        self.background_item.persistent = False
        self.background_item.setBrush(Qt.black)

        for row in range(self.board_size):
            for col in range(self.board_size):
                left_adj = Cons.INT_CELLS if col % self.c_size else 0
                top_adj = Cons.INT_CELLS if row % self.r_size else 0
                width_adj = Cons.INT_CELLS if col % self.c_size else 0
                height_adj = Cons.INT_CELLS if row % self.r_size else 0
                square = QGraphicsRectItem(board[0] + (Cons.MARGIN + Cons.WIDTH) * col +
                                           Cons.MARGIN - left_adj, board[1] + (Cons.MARGIN + Cons.HEIGHT) * row +
                                           Cons.MARGIN - top_adj, Cons.WIDTH + width_adj, Cons.HEIGHT + height_adj,
                                           parent=self.background_item)
                self.cells.append(square.rect())
                setattr(square, 'cell', (row, col))
                colour = Cons.NORMAL_COLOUR
                square.setBrush(QColor(colour[0], colour[1], colour[2]))
                square.setToolTip("Square")
                square.persistent = False

        self.scene.addItem(self.background_item)
        self.set_digits()

    def set_digits(self):
        """ Draw side number tiles """

        for i in range(0, 12):
            if i <= self.board_size - 1:
                xpos = Cons.RACK_XTILE[0]
                ypos = Cons.RACK_YTILE + i * 55 + (12 - self.board_size) * 55 // 2
                box = QLabel()
                box.setGeometry(xpos, ypos, Cons.TILE_WIDTH, Cons.TILE_HEIGHT)
                box.setStyleSheet("border: 2px solid black")
                box.setAlignment(Qt.AlignCenter)
                proxy = QGraphicsProxyWidget()
                proxy.persistent = False
                proxy.setWidget(box)
                proxy.digit = Cons.DIGITS[i]
                proxy.setPos(xpos, ypos)
                self.scene.addItem(proxy)
                proxy.show()
                tile = Tile(self.digits[i], self.scene)
                tile.cell = "new"
                tile.draw_tile(QPoint(xpos, ypos))

    def load_board(self):
        """ Load new board """
        for row in range(self.board_size):
            for col in range(self.board_size):
                num = self.content[row][col]
                if num != "0":
                    if self.sudoku[row][col] != "0":
                        lliw = "black"
                    else:
                        lliw = "red"
                    teil = Tile(num, self.scene, lliw)
                    teil.cell = (row, col)
                    cell = self.cells[(row * self.board_size) + col]
                    if self.tiles[row][col] is not None:
                        self.tiles[row][col].remove()
                    self.tiles[row][col] = teil
                    teil.draw_tile(QPoint(cell.x(), cell.y()))
        self.hint = False

    def set_sudoku(self):
        """ Copy working board into original board """
        for row in range(self.board_size):
            for col in range(self.board_size):
                self.sudoku[row][col] = self.content[row][col]

    def freeze_sudoku(self):
        """ Set all initial tiles """
        for row in range(self.board_size):
            for col in range(self.board_size):
                if self.sudoku[row][col] != "0":
                    self.set_in_board(self.tiles[row][col])

    def free_sudoku(self):
        """ Free all initial tiles """
        for row in range(self.board_size):
            for col in range(self.board_size):
                if self.sudoku[row][col] != "0":
                    self.free_in_board(self.tiles[row][col])

    def free_user_tiles(self):
        """ Free all initial tiles """
        for row in range(self.board_size):
            for col in range(self.board_size):
                if self.sudoku[row][col] == "0" and self.content[row][col] != "0":
                    self.free_in_board(self.tiles[row][col])

    def set_num(self, num, row, col):
        """ Set red numbered tile at row, col """

        teil = Tile(num, self.scene, "red")
        cell = self.cells[(row * self.board_size) + col]
        if self.tiles[row][col] is not None:
            self.tiles[row][col].remove()
        self.tiles[row][col] = teil
        teil.draw_tile(QPoint(cell.x(), cell.y()))

    def get_board_size(self):
        """ Return dimensions of board
            board size, square size """
        return self.board_size, self.r_size, self.c_size

    def get_rc(self, rectf):
        """ Convert rectangle to row/col """
        row, col = -1, -1
        if isinstance(rectf, QRectF) and rectf in self.cells:
            no = self.cells.index(rectf)
            row, col = no // self.board_size, no % self.board_size
        return row, col

    def user_tile(self, teil):
        """ Returns True if tile can be used by user in game
            Returns pos on board if cell on board """
        cell = next(((row, col.index(teil)) for row, col in enumerate(self.tiles) if teil in col), True)
        if isinstance(cell, tuple) and self.sudoku[cell[0]][cell[1]] != "0":
            cell = False
        return cell

    def clear_area(self):
        """ Clear all tiles not on board """
        for item in self.scene.items():
            if hasattr(item, 'tile') and item.tile.cell is None:
                self.scene.removeItem(item)
        self.set_digits()

    def clear_board(self):
        """ Clear all tiles from board """
        for row in range(self.board_size):
            for col in range(self.board_size):
                if self.sudoku[row][col] == "0" and self.content[row][col] != "0":
                    self.tiles[row][col].remove()
                    self.tiles[row][col] = None
                    self.content[row][col] = "0"
                self.remove_poss_tile(row, col)
        self.hint = False

    def clear_board_area(self):
        """ Clear graphics items from scene
            Items with attribute 'persistent' cleared """

        for item in self.scene.items():
            if hasattr(item, 'tile') or hasattr(item, 'persistent'):
                self.scene.removeItem(item)
        self.content = [["0"] * self.board_size for _ in range(self.board_size)]
        self.sudoku = [["0"] * self.board_size for _ in range(self.board_size)]
        self.tiles = [[None] * self.board_size for _ in range(self.board_size)]
        self.poss_tiles = [[None] * self.board_size for _ in range(self.board_size)]
        self.hint = False

    def lift_tile(self, teil, cell=None):
        """ Remove tile from board """
        teil.movable(True)
        teil.setZValue(3000)
        if isinstance(cell, tuple):
            row, col = cell[0], cell[1]
            teil.cell = None
            self.content[row][col] = "0"
            self.tiles[row][col] = None

    def drop_tile(self, teil, row, col):
        """ Set tile on board """
        self.content[row][col] = teil.letter
        self.tiles[row][col] = teil
        if self.hint:
            self.states.solver.redo_possibles()

    def show_poss_tile(self, poss, row, col):
        """ Show possible values on board
            Used by Hint """
        teil = Tile(poss, self.scene)
        teil.cell = "poss"
        cell = self.cells[(row * self.board_size) + col]
        self.poss_tiles[row][col] = teil
        teil.draw_tile(QPoint(cell.x(), cell.y()))

    def remove_poss_tile(self, row, col):
        """ Remove possible values from one cell """
        if self.poss_tiles[row][col] is not None:
            self.poss_tiles[row][col].remove()
            self.poss_tiles[row][col] = None

    @staticmethod
    def set_in_board(tile):
        """ Set tile in board
            No longer moveable """
        tile.activate(False)

    @staticmethod
    def free_in_board(tile):
        """ Free tile in board
            Make moveable """
        tile.activate(True)

    @staticmethod
    def num_factors(n):
        """ Get all factors of num """
        results = set()
        for i in range(1, int(n ** 0.5) + 1):
            if n % i == 0:
                results.update([i, int(n / i)])
        return results


# Class of letter tile sprites
class Tile(Pixmap):
    """ Tile class defines on screen tiles """

    anim_complete = pyqtSignal()  # Signal for completion of animation
    board_size = Cons.SIZE  # Board size set by draw_board()
    digits = Cons.DIGITS  # Digits in use set by draw_board()

    def __init__(self, letter, scene, lliw="black"):

        self.image = QPixmap.fromImage(self.set_tile(letter, lliw))
        super(Tile, self).__init__(self.image)

        self.letter = letter
        self.colour = lliw
        self.scene = scene

        self.pixmap_item.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsMovable)
        self.pixmap_item.setTransform(QTransform())
        self.pixmap_item.setAcceptedMouseButtons(Qt.LeftButton)
        self.pixmap_item.setZValue(1000)
        self.pixmap_item.tile = self
        self.pixmap_item.hide()
        self.scene.addItem(self.pixmap_item)

        self.cell = None
        self.fade = None
        self.movable(False)

    def set_tile(self, lett, lliw="black"):
        """ Draw letter on tile """
        if isinstance(lett, list):
            new_data = self.set_hint(lett)
        else:
            new_data = bytearray(Cons.SVG_DATA_1.format(one=lett, col=lliw), 'utf-8')
        return QImage.fromData(new_data, 'SVG')

    def set_colour(self, lliw):
        """ Set colour of letter on tile """
        self.colour = lliw
        self.image = QPixmap.fromImage(self.set_tile(self.letter, self.colour))
        self.set_pixmap(self.image)

    def draw_tile(self, position):
        """ Draw tile at QPoint """
        self.pos = position
        self.pixmap_item.show()

    def draw_tile_at(self, xpos, ypos):
        """ Draw tile at (xpos, ypos) """
        self.pos = QPoint(xpos, ypos)
        self.pixmap_item.show()

    def hand_cursor(self):
        """ Change cursor to hand cursor """
        self.pixmap_item.setCursor(Qt.PointingHandCursor)

    def reset_cursor(self):
        """ Change cursor to pointer cursor """
        self.pixmap_item.setCursor(Qt.ArrowCursor)

    def activate(self, activate):
        """ Accept mouse presses if activate is True """
        if activate:
            self.pixmap_item.setAcceptedMouseButtons(Qt.LeftButton)
        else:
            self.pixmap_item.setAcceptedMouseButtons(Qt.NoButton)

    def dim(self, activate):
        """ Dim tile if activate is True """
        if activate:
            self.pixmap_item.setOpacity(0.4)
        else:
            self.pixmap_item.setOpacity(1)

    def hide(self):
        """ Hide tile """
        self.pixmap_item.hide()

    def remove(self):
        self.scene.removeItem(self.pixmap_item)
        del self

    def setZValue(self, val):
        """ set ZValue for image """
        self.pixmap_item.setZValue(val)

    def set_hint(self, lett):
        """ Draw all possible letters on tile """
        num = list(type(self).digits)
        vals = [x if x in lett else "" for x in num]
        return self.create_svg(vals)

    def create_svg(self, letts):
        """ Create SVG for tile and return as byte array """
        c_size, r_size = Cons.SIZE_DICT[type(self).board_size]
        cell_w, cell_h = Cons.WIDTH, Cons.HEIGHT
        x_pos = [0]  # x coordinates of grid lines
        y_pos = []  # y coordinates of grid lines
        b_array = bytearray(Cons.SVG_HINT_1, 'utf-8')

        # Draw grid lines and store coordinates in above
        for line in range(1, c_size):
            start_x = line * cell_w // c_size
            x_pos.append(start_x)
            b_array += bytearray(Cons.SVG_HINT_2.format(start_x=start_x, start_y=0, end_x=start_x, end_y=cell_h),
                                 'utf-8')
        for line in range(1, r_size):
            start_y = line * cell_h // r_size
            y_pos.append(start_y)
            b_array += bytearray(Cons.SVG_HINT_2.format(start_x=0, start_y=start_y, end_x=cell_w, end_y=start_y),
                                 'utf-8')
        y_pos.append(cell_h)
        mid_x, mid_y = x_pos[1] // 2, y_pos[0] // 2  # Centre of each section

        # Draw digit in ection if it is a possibility for that tile
        no = 0
        for num in letts:
            row, col = no // c_size, no % c_size
            x, y = x_pos[col] + mid_x, y_pos[row] - (mid_y // 2)
            b_array += bytearray(Cons.SVG_HINT_3.format(x=x, y=y, num=num),
                                 'utf-8')
            no += 1
        b_array += bytearray("</svg>", 'utf-8')
        return b_array
