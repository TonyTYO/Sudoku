""" Define all buttons and the game state machine """

import sys
from PyQt5.QtCore import (QRectF, Qt, QState, QFinalState, QStateMachine,
                          pyqtSignal, QObject)
from PyQt5.QtGui import (QPixmap, QLinearGradient, QPainterPath)
from PyQt5.QtWidgets import (QGraphicsWidget, QGraphicsItem,
                             QGraphicsRectItem, QStyle)

import Constants as Cons
import qstates


class Button(QGraphicsWidget):
    """ Defines standard buttons """

    pressed = pyqtSignal()  # signal for button pressed

    def __init__(self, pixmap, size, parent=None):
        super(Button, self).__init__(parent)

        self._pix = pixmap.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.setAcceptHoverEvents(True)
        self.setCacheMode(QGraphicsItem.DeviceCoordinateCache)
        self.size = size

    def boundingRect(self):
        """ Return bounding rectangle """
        return QRectF(-1 * self.size, -1 * self.size, 2 * self.size, 2 * self.size)

    def shape(self):
        """ Return shape as path """
        path = QPainterPath()
        path.addEllipse(self.boundingRect())
        return path

    def paint(self, painter, option, _widget=None):
        """ Paint button """
        down = option.state & QStyle.State_Sunken

        r = self.boundingRect()

        grad = QLinearGradient(r.topLeft(), r.bottomRight())
        if option.state & QStyle.State_MouseOver:
            color_0 = Qt.white
        else:
            color_0 = Qt.lightGray

        color_1 = Qt.darkGray
        if down:
            color_0, color_1 = color_1, color_0

        grad.setColorAt(0, color_0)
        grad.setColorAt(1, color_1)

        painter.setPen(Qt.darkGray)
        painter.setBrush(grad)
        painter.drawEllipse(r)

        color_0 = Qt.darkGray
        color_1 = Qt.lightGray
        if down:
            color_0, color_1 = color_1, color_0

        grad.setColorAt(0, color_0)
        grad.setColorAt(1, color_1)

        painter.setPen(Qt.NoPen)
        painter.setBrush(grad)

        if down:
            painter.translate(2, 2)
        painter.drawEllipse(r.adjusted(5, 5, -5, -5))
        painter.drawPixmap(-self._pix.width() / 2, -self._pix.height() / 2,
                           self._pix)

    def mousePressEvent(self, _ev):
        """ Emit pressed signal and redraw on mouse press """
        self.pressed.emit()
        self.update()

    def mouseReleaseEvent(self, _ev):
        """ Redraw on mouse release """
        self.update()


# noinspection PyPep8Naming
class Setbuttons(QObject):
    """ Setup all buttons for the game """

    def __init__(self, scene):
        super(Setbuttons, self).__init__()

        self.scene = scene
        self.buttons = {}  # Register of buttons as {name: button}

        self.setupButton, self.checkButton, self.loadButton, self.saveButton = None, None, None, None
        self.clearButton, self.playButton, self.printButton, self.solveButton = None, None, None, None
        self.printButton, self.solveButton, self.stepButton, self.quitButton = None, None, None, None
        self.hintButton, self.restartButton = None, None

        buttonParent = QGraphicsRectItem()
        self.playButton = None
        self.checkButton = None
        self.setup_buttons(buttonParent)
        self.set_button_pos()
        self.reset_tips()
        buttonParent.setScale(0.75)
        buttonParent.setPos(Cons.BUTTON_X, Cons.BUTTON_Y)
        buttonParent.setZValue(65)
        self.scene.addItem(buttonParent)

    def setup_buttons(self, buttonParent):
        """ Define buttons """

        # Buttons for playing screen
        self.solveButton = Button(QPixmap('tiles/calculator.png'), Cons.SMALL_BUTTON, buttonParent)
        self._add_button("solveButton", self.solveButton)
        self.stepButton = Button(QPixmap('tiles/step2.png'), Cons.SMALL_BUTTON, buttonParent)
        self._add_button("stepButton", self.stepButton)
        self.setupButton = Button(QPixmap('tiles/setup.png'), Cons.SMALL_BUTTON, buttonParent)
        self._add_button("setupButton", self.setupButton)
        self.checkButton = Button(QPixmap('tiles/complete.png'), Cons.SMALL_BUTTON, buttonParent)
        self._add_button("checkButton", self.checkButton)
        self.loadButton = Button(QPixmap('tiles/load.png'), Cons.SMALL_BUTTON, buttonParent)
        self._add_button("loadButton", self.loadButton)
        self.saveButton = Button(QPixmap('tiles/save.png'), Cons.SMALL_BUTTON, buttonParent)
        self._add_button("saveButton", self.saveButton)
        self.playButton = Button(QPixmap('tiles/play.png'), Cons.SMALL_BUTTON, buttonParent)
        self._add_button("playButton", self.playButton)
        self.hintButton = Button(QPixmap('tiles/hint.png'), Cons.SMALL_BUTTON, buttonParent)
        self._add_button("hintButton", self.hintButton)
        self.restartButton = Button(QPixmap('tiles/restart.png'), Cons.SMALL_BUTTON, buttonParent)
        self._add_button("restartButton", self.restartButton)
        self.clearButton = Button(QPixmap('tiles/clear.png'), Cons.SMALL_BUTTON, buttonParent)
        self._add_button("clearButton", self.clearButton)
        self.printButton = Button(QPixmap('tiles/printer.png'), Cons.SMALL_BUTTON, buttonParent)
        self._add_button("printButton", self.printButton)
        self.quitButton = Button(QPixmap('tiles/quit.png'), Cons.SMALL_BUTTON, buttonParent)
        self._add_button("quitButton", self.quitButton)

    def _add_button(self, name, button):
        """ Register button in dictionary """
        self.buttons[name] = button

    def set_button_pos(self):
        """ Set default button positions """

        self.solveButton.setPos(Cons.SOLVE_BUTTON[0], Cons.SOLVE_BUTTON[1])
        self.stepButton.setPos(Cons.STEP_BUTTON[0], Cons.STEP_BUTTON[1])
        self.setupButton.setPos(Cons.SETUP_BUTTON[0], Cons.SETUP_BUTTON[1])
        self.checkButton.setPos(Cons.CHECK_BUTTON[0], Cons.CHECK_BUTTON[1])
        self.loadButton.setPos(Cons.LOAD_BUTTON[0], Cons.LOAD_BUTTON[1])
        self.saveButton.setPos(Cons.SAVE_BUTTON[0], Cons.SAVE_BUTTON[1])
        self.playButton.setPos(Cons.PLAY_BUTTON[0], Cons.PLAY_BUTTON[1])
        self.hintButton.setPos(Cons.HINT_BUTTON[0], Cons.HINT_BUTTON[1])
        self.restartButton.setPos(Cons.RESTART_BUTTON[0], Cons.RESTART_BUTTON[1])
        self.clearButton.setPos(Cons.CLEAR_BUTTON[0], Cons.CLEAR_BUTTON[1])
        self.printButton.setPos(Cons.PRINT_BUTTON[0], Cons.PRINT_BUTTON[1])
        self.quitButton.setPos(Cons.QUIT_BUTTON[0], Cons.QUIT_BUTTON[1])

    def reset_tips(self):
        """ Set tooltip text to correct language """
        self.playButton.setToolTip("play")
        self.hintButton.setToolTip("hint")
        self.restartButton.setToolTip("restart")
        self.checkButton.setToolTip("check")
        self.solveButton.setToolTip("solve")
        self.stepButton.setToolTip("step")
        self.loadButton.setToolTip("load")
        self.saveButton.setToolTip("save")
        self.setupButton.setToolTip("setup")
        self.clearButton.setToolTip("clear")
        self.printButton.setToolTip("print")
        self.quitButton.setToolTip("quit")


# noinspection PyUnresolvedReferences
class SetupMachine(QStateMachine):
    """ Setup game state machine """

    action_complete = pyqtSignal()  # emitted when action completed

    def __init__(self, scene):
        super(SetupMachine, self).__init__()

        self.st_code = qstates.States(scene, self)

        self.rootState, self.waitState, self.setupState, self.loadState = None, None, None, None
        self.saveState, self.solveState, self.stepState, self.clearState = None, None, None, None
        self.playState, self.checkState, self.hintState, self.restartState = None, None, None, None
        self.printState, self.quitState = None, None

        buttons = scene.buttons.buttons
        self.set_states()
        self.set_signal_transitions()
        self.set_button_transitions(buttons)
        states = self.assign_name()
        self.assign_visibility(states, buttons)
        self.assign_enabled(states, buttons)
        self.set_structure()
        self.set_connections()
        self.start()  # start state machine

    def set_states(self):
        """ Create state machine states """

        self.rootState = QState()
        # Initial setup states
        self.waitState = QState(self.rootState)
        self.setupState = QState(self.rootState)
        self.loadState = QState(self.rootState)
        self.saveState = QState(self.rootState)
        self.solveState = QState(self.rootState)
        self.stepState = QState(self.rootState)
        self.clearState = QState(self.rootState)
        self.playState = QState(self.rootState)
        self.checkState = QState(self.rootState)
        self.hintState = QState(self.rootState)
        self.restartState = QState(self.rootState)
        self.printState = QState(self.rootState)

        # End state
        self.quitState = QFinalState()

    def set_signal_transitions(self):
        """ pyqtSignal transitions from states """

        self.setupState.addTransition(self.action_complete, self.waitState)
        self.solveState.addTransition(self.action_complete, self.waitState)
        self.stepState.addTransition(self.action_complete, self.waitState)
        self.loadState.addTransition(self.action_complete, self.waitState)
        self.saveState.addTransition(self.action_complete, self.waitState)
        self.clearState.addTransition(self.action_complete, self.waitState)
        self.hintState.addTransition(self.action_complete, self.waitState)
        self.restartState.addTransition(self.action_complete, self.waitState)
        self.printState.addTransition(self.action_complete, self.waitState)
        self.checkState.addTransition(self.action_complete, self.waitState)

    def set_button_transitions(self, buttons):
        """ Button transitions from states """

        self.waitState.addTransition(buttons["setupButton"].pressed, self.setupState)
        self.setupState.addTransition(buttons["setupButton"].pressed, self.waitState)
        self.waitState.addTransition(buttons["solveButton"].pressed, self.solveState)
        self.waitState.addTransition(buttons["stepButton"].pressed, self.stepState)
        self.waitState.addTransition(buttons["loadButton"].pressed, self.loadState)
        self.waitState.addTransition(buttons["saveButton"].pressed, self.saveState)
        self.waitState.addTransition(buttons["clearButton"].pressed, self.clearState)
        self.waitState.addTransition(buttons["playButton"].pressed, self.playState)
        self.playState.addTransition(buttons["playButton"].pressed, self.waitState)
        self.waitState.addTransition(buttons["hintButton"].pressed, self.hintState)
        self.hintState.addTransition(buttons["hintButton"].pressed, self.waitState)
        self.waitState.addTransition(buttons["restartButton"].pressed, self.restartState)
        self.waitState.addTransition(buttons["printButton"].pressed, self.printState)
        self.waitState.addTransition(buttons["checkButton"].pressed, self.checkState)
        self.checkState.addTransition(buttons["checkButton"].pressed, self.checkState)
        self.rootState.addTransition(buttons["quitButton"].pressed, self.quitState)

    def assign_name(self):
        """ Assign name to property 'state' for each state """

        states = {}
        self.rootState.assignProperty(self, "state", "root")
        states["root"] = self.rootState
        self.waitState.assignProperty(self, "state", "wait")
        states["wait"] = self.waitState
        self.setupState.assignProperty(self, "state", "setup")
        states["setup"] = self.setupState
        self.loadState.assignProperty(self, "state", "load")
        states["load"] = self.loadState
        self.saveState.assignProperty(self, "state", "save")
        states["save"] = self.saveState
        self.clearState.assignProperty(self, "state", "clear")
        states["clear"] = self.clearState
        self.solveState.assignProperty(self, "state", "solve")
        states["solve"] = self.solveState
        self.stepState.assignProperty(self, "state", "step")
        states["step"] = self.stepState
        self.playState.assignProperty(self, "state", "play")
        states["play"] = self.playState
        self.hintState.assignProperty(self, "state", "hint")
        states["hint"] = self.hintState
        self.restartState.assignProperty(self, "state", "restart")
        states["restart"] = self.restartState
        self.printState.assignProperty(self, "state", "print")
        states["print"] = self.printState
        self.checkState.assignProperty(self, "state", "check")
        states["check"] = self.checkState

        return states

    @staticmethod
    def assign_visibility(states, buttons):
        """ Assign visibility property for each button in each state """

        visibility = {"wait": ["setupButton", "checkButton", "loadButton", "saveButton", "clearButton",
                               "playButton", "printButton", "solveButton", "stepButton", "quitButton",
                               "hintButton", "restartButton"],
                      "load": ["setupButton", "checkButton", "loadButton", "saveButton", "printButton",
                               "clearButton", "playButton", "solveButton", "stepButton", "quitButton",
                               "hintButton", "restartButton"],
                      "save": ["setupButton", "checkButton", "loadButton", "saveButton", "printButton",
                               "clearButton", "playButton", "solveButton", "stepButton", "quitButton",
                               "hintButton", "restartButton"],
                      "setup": ["setupButton", "checkButton", "loadButton", "saveButton", "printButton",
                                "clearButton", "playButton", "solveButton", "stepButton", "quitButton",
                                "hintButton", "restartButton"],
                      "solve": ["setupButton", "checkButton", "loadButton", "saveButton", "printButton",
                                "clearButton", "playButton", "solveButton", "stepButton", "quitButton",
                                "hintButton", "restartButton"],
                      "step": ["setupButton", "checkButton", "loadButton", "saveButton", "printButton",
                               "clearButton", "playButton", "solveButton", "stepButton", "quitButton",
                               "hintButton", "restartButton"],
                      "play": ["setupButton", "checkButton", "loadButton", "saveButton", "printButton",
                               "clearButton", "playButton", "solveButton", "stepButton", "quitButton",
                               "hintButton", "restartButton"],
                      "hint": ["setupButton", "checkButton", "loadButton", "saveButton", "printButton",
                               "clearButton", "playButton", "solveButton", "stepButton", "quitButton",
                               "hintButton", "restartButton"],
                      "print": ["setupButton", "checkButton", "loadButton", "saveButton", "printButton",
                                "clearButton", "playButton", "solveButton", "stepButton", "quitButton",
                                "hintButton", "restartButton"],
                      "check": ["setupButton", "checkButton", "loadButton", "saveButton", "printButton",
                                "clearButton", "playButton", "solveButton", "stepButton", "quitButton",
                                "hintButton", "restartButton"]}

        for name, state in states.items():
            button_list = []
            if name in visibility:
                button_list = visibility[name]
            for k, b in buttons.items():
                if k in button_list:
                    state.assignProperty(b, "visible", "True")
                else:
                    state.assignProperty(b, "visible", "False")

    @staticmethod
    def assign_enabled(states, buttons):
        """ Assign enabled property for each button in each state """

        enabled = {"wait": ["setupButton", "checkButton", "loadButton", "saveButton", "clearButton",
                            "playButton", "printButton", "solveButton", "stepButton", "quitButton",
                            "hintButton", "restartButton"],
                   "load": ["setupButton", "checkButton", "loadButton", "saveButton", "printButton",
                            "clearButton", "playButton", "solveButton", "stepButton", "quitButton",
                            "hintButton", "restartButton"],
                   "save": ["setupButton", "checkButton", "loadButton", "saveButton", "printButton",
                            "clearButton", "playButton", "solveButton", "stepButton", "quitButton",
                            "hintButton", "restartButton"],
                   "setup": ["setupButton", "loadButton", "saveButton", "printButton",
                             "clearButton", "quitButton", "hintButton", "restartButton"],
                   "solve": ["setupButton", "checkButton", "loadButton", "saveButton", "printButton",
                             "clearButton", "playButton", "solveButton", "stepButton", "quitButton",
                             "hintButton", "restartButton"],
                   "step": ["setupButton", "checkButton", "loadButton", "saveButton", "printButton",
                            "clearButton", "playButton", "solveButton", "stepButton", "quitButton",
                            "hintButton", "restartButton"],
                   "play": ["checkButton", "saveButton", "playButton", "printButton",
                            "clearButton", "solveButton", "stepButton", "quitButton",
                            "hintButton", "restartButton"],
                   "hint": ["setupButton", "checkButton", "loadButton", "saveButton", "printButton",
                            "clearButton", "playButton", "solveButton", "stepButton", "quitButton",
                            "hintButton", "restartButton"],
                   "print": ["setupButton", "checkButton", "loadButton", "saveButton", "printButton",
                             "clearButton", "playButton", "solveButton", "stepButton", "quitButton",
                             "hintButton", "restartButton"],
                   "check": ["setupButton", "checkButton", "loadButton", "saveButton", "printButton",
                             "clearButton", "playButton", "solveButton", "stepButton", "quitButton",
                             "hintButton", "restartButton"]}

        for name, state in states.items():
            button_list = []
            if name in enabled:
                button_list = enabled[name]
            for k, b in buttons.items():
                if k in button_list:
                    state.assignProperty(b, "enabled", "True")
                else:
                    state.assignProperty(b, "enabled", "False")

    def set_structure(self):
        """ Set initial anf final states """

        self.addState(self.rootState)
        self.addState(self.quitState)
        self.setInitialState(self.rootState)
        self.rootState.setInitialState(self.waitState)
        self.finished.connect(self.end_m)

    def set_connections(self):
        """ Set enter and exit connections for states """

        self.waitState.entered.connect(self.st_code.s_enter_wait)
        self.waitState.exited.connect(self.st_code.s_exit_wait)
        self.setupState.entered.connect(self.st_code.s_enter_setup)
        self.setupState.exited.connect(self.st_code.s_exit_setup)
        self.loadState.entered.connect(self.st_code.s_enter_load)
        self.loadState.exited.connect(self.st_code.s_exit_load)
        self.saveState.entered.connect(self.st_code.s_enter_save)
        self.saveState.exited.connect(self.st_code.s_exit_save)
        self.solveState.entered.connect(self.st_code.s_enter_solve)
        self.solveState.exited.connect(self.st_code.s_exit_solve)
        self.stepState.entered.connect(self.st_code.s_enter_step)
        self.stepState.exited.connect(self.st_code.s_exit_step)
        self.clearState.entered.connect(self.st_code.s_enter_clear)
        self.clearState.exited.connect(self.st_code.s_exit_clear)
        self.playState.entered.connect(self.st_code.s_enter_play)
        self.playState.exited.connect(self.st_code.s_exit_play)
        self.hintState.entered.connect(self.st_code.s_enter_hint)
        self.hintState.exited.connect(self.st_code.s_exit_hint)
        self.restartState.entered.connect(self.st_code.s_enter_restart)
        self.restartState.exited.connect(self.st_code.s_exit_restart)
        self.printState.entered.connect(self.st_code.s_enter_print)
        self.printState.exited.connect(self.st_code.s_exit_print)
        self.checkState.entered.connect(self.st_code.s_enter_check)
        self.checkState.exited.connect(self.st_code.s_exit_check)

    @staticmethod
    def end_m():
        """ State machine quit """

        sys.exit(0)
