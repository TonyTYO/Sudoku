""" Startup script for game
    sets window, scene, view """

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QPainter, QTransform
from PyQt5.QtWidgets import (QApplication, QMainWindow,
                             QGraphicsScene, QGraphicsView, QGraphicsRectItem)

import Constants as Cons
import qbwtwm
import qbwrdd


class GraphicsScene(QGraphicsScene):
    """ Main graphics screen for the game """

    move_complete = pyqtSignal(object, int, int)  # Signal for end of cursor move
    active_scene = False

    def __init__(self, parent=None):
        super(GraphicsScene, self).__init__(parent)

        self.state = None  # Holds current state of FSM
        self.active = []  # List of active tiles
        # cleared in ActiveTiles class
        self.item = None  # Item under mouse press
        self.move = False  # Flag set to True if mouse is moved

        self.buttons = qbwtwm.Setbuttons(self)  # Setup all on-screen buttons
        self.machine = qbwtwm.SetupMachine(self)  # Setup and start FSM
        self.states = self.machine.st_code
        self.board = self.states.board

        GraphicsScene.active_scene = True

    def mousePressEvent(self, event):
        """ Handle mouse pressed event """

        # modifiers = event.modifiers()
        self.item = self.itemAt(event.scenePos(), QTransform())
        self.state = self.machine.property("state")
        self.move = False

        if event.button() == Qt.LeftButton and hasattr(self.item, 'tile'):
            cell = None
            if self.state in ["setup", "play"]:
                teil = self.item.tile
                if self.state == "play":
                    cell = self.board.user_tile(teil)
                    if cell:
                        teil.set_colour("red")
                if teil.cell == "new":
                    tile = qbwrdd.Tile(teil.letter, self)
                    tile.cell = "new"
                    tile.draw_tile(teil.pos)
                    teil.cell = None
                self.item.setCursor(Qt.PointingHandCursor)
                self.board.lift_tile(teil, cell)
        super(GraphicsScene, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """ Handle mouse released event """

        self.item = self.itemAt(event.scenePos(), QTransform())

        if event.button() == Qt.LeftButton and hasattr(self.item, 'tile'):
            self.clearSelection()
            self.item.setCursor(Qt.ArrowCursor)
            if self.state in ["setup", "play"]:
                collisions = self.item.collidingItems()
                if collisions:
                    row, col = self.process_collisions(collisions)
                    if row + col >= 0:
                        self.board.drop_tile(self.item.tile, row, col)
        super(GraphicsScene, self).mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        """ Handle mouse move event """
        self.item = self.itemAt(event.scenePos(), QTransform())
        if event.buttons() == Qt.LeftButton:
            self.move = True  # required for exchange
        super(GraphicsScene, self).mouseMoveEvent(event)

    def process_collisions(self, collisions):
        """ Jump tile to nearest board cell """

        row, col = -1, -1
        cells = [(r.rect(), r.cell) for r in collisions if isinstance(r, QGraphicsRectItem) and hasattr(r, 'cell')]
        rects = [[r.x(), r.y(), r.width(), r.height()] for (r, w) in cells]
        tilerect = [self.item.x(), self.item.y(), Cons.WIDTH, Cons.HEIGHT]
        overlaps = [self.overlap(tilerect, r) for r in rects]
        if overlaps:
            index = max(range(len(overlaps)), key=overlaps.__getitem__)
            row, col = cells[index][1]
            row, col = self.get_empty_cell(row, col)
            rect = self.board.cells[row * self.board.board_size + col]
            self.item.setPos(rect.x(), rect.y())
        return row, col

    def get_empty_cell(self, row, col):
        """ Find nearest empty square 
            empty_cells is [(row, col) of all empty cells
            distances is list of Manhatton distance from empty cell to present cell
            set row, col to first empty cell nearest present cell """

        if self.board.content[row][col] != "0":
            empty_cells = [(x, y) for x, nos in enumerate(self.board.content) for y in
                           [c for c, no in enumerate(nos) if no == "0"]]
            distances = [abs(row - r) + abs(col - c) for (r, c) in empty_cells]
            row, col = empty_cells[distances.index(min(distances))]
        return row, col

    @staticmethod
    def overlap(rect1, rect2):
        """ Calculate overlap between two rectangles - return size of overlap """

        rect1 = [rect1[0], rect1[1], rect1[0] + rect1[2], rect1[1] + rect1[3]]
        rect2 = [rect2[0], rect2[1], rect2[0] + rect2[2], rect2[1] + rect2[3]]
        if rect2[0] > rect1[2] or rect1[0] > rect2[2] or rect2[1] > rect1[3] or rect1[1] > rect2[3]:
            return 0
        x_overlap = max(0, min(rect1[2], rect2[2]) - max(rect1[0], rect2[0]))
        y_overlap = max(0, min(rect1[3], rect2[3]) - max(rect1[1], rect2[1]))
        return x_overlap * y_overlap

    # -------------------------------------------------------------------------


class MainWindow(QMainWindow):
    """ Main window for the game """

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.resize(Cons.WINDOW_SIZE[0], Cons.WINDOW_SIZE[1])
        self.center()

        self.setWindowTitle("Scrabble")
        self.view = MainView()
        self.setCentralWidget(self.view)

    def center(self):
        """ Centre window on screen """

        frameGm = self.frameGeometry()
        screen = QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())
        centerPoint = QApplication.desktop().screenGeometry(screen).center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())

    def reset_window(self, size=None, title=None):
        """ Resize and/or retitle window
            size as tuple (l, w) """

        if size is not None:
            self.resize(size[0], size[1])
        if title is not None:
            self.setWindowTitle(title)


# pylint: disable=too-few-public-methods
class MainView(QGraphicsView):
    """ Main graphics view for the game """

    def __init__(self, parent=None):
        super(MainView, self).__init__(parent)

        self.scene = GraphicsScene(self)
        self.scene.setSceneRect(0, 0, Cons.WINDOW_SIZE[0], Cons.WINDOW_SIZE[1])

        self.setScene(self.scene)
        self.setCacheMode(QGraphicsView.CacheBackground)
        self.setViewportUpdateMode(QGraphicsView.BoundingRectViewportUpdate)
        self.setBackgroundBrush(QColor(230, 200, 167))
        self.setCacheMode(QGraphicsView.CacheBackground)
        self.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
        self.setFrameStyle(0)
