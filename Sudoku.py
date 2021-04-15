""" Startup and loading script for game
    sets splashscreen and loads game """

import sys
import time
import logging
import traceback
from collections import namedtuple
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import (QApplication, QSplashScreen, QProgressBar,
                             QLabel, QDesktopWidget, QDialog,
                             QVBoxLayout, QPushButton)
import qffenestr


class ErrorWindow(QDialog):
    """ Class to handle all errors 
        sys.excepthook will be set to an instance of this class """

    fake_tb = namedtuple(
        'fake_tb', ('tb_frame', 'tb_lasti', 'tb_lineno', 'tb_next')
    )

    def __init__(self):
        super().__init__()

        self.resize(250, 150)
        self.move(300, 300)
        self.setWindowTitle('Error')
        self.setWindowIcon(QIcon(r'Scrabble\tiles\error.png'))
        self.setWindowModality(Qt.ApplicationModal)
        self.error_trace = QLabel()
        qbtn = QPushButton('Quit', self)
        qbtn.setStyleSheet('QPushButton {color: red;}')
        qbtn.clicked.connect(QApplication.instance().quit)
        self.centre()
        layout = QVBoxLayout()
        layout.addWidget(self.error_trace)
        layout.addWidget(qbtn)
        self.setLayout(layout)
        self.setWindowFlags(
            Qt.Window |
            Qt.CustomizeWindowHint |
            Qt.WindowTitleHint |
            Qt.WindowStaysOnTopHint
        )
        self.hide()

    def centre(self):
        """ Centre window """
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def set_error_trace(self, name):
        """ Set error text in window """
        with open(name, 'rt') as f:
            body = f.read()
        self.error_trace.setText(body)
        self.exec_()

    def excepthook(self, exc_type, exc_value, exc_tb):
        """ Exception handler - All errors/exceptions come here """
        enriched_tb = self._add_missing_frames(exc_tb) if exc_tb else exc_tb
        # Note: sys.__excepthook__(...) would not work here.
        # We need to use print_exception(...):
        # traceback.print_exception(exc_type, exc_value, enriched_tb)
        logging.critical(''.join(traceback.format_tb(enriched_tb)))
        logging.critical('%s: %s', exc_type, exc_value)

        self.set_error_trace('file.log')

    def _add_missing_frames(self, tb):
        """ Create new traceback with pyQt data installed """
        result = self.fake_tb(tb.tb_frame, tb.tb_lasti, tb.tb_lineno, tb.tb_next)
        frame = tb.tb_frame.f_back
        while frame:
            result = self.fake_tb(frame, frame.f_lasti, frame.f_lineno, result)
            frame = frame.f_back
        return result


if __name__ == '__main__':

    game = QApplication(sys.argv)
    sshFile = "utility.stylesheet"
    with open(sshFile, "r") as fh:
        game.setStyleSheet(fh.read())

    # Create and display the splash screen
    splash_pix = QPixmap('tiles/sudoku.png', 'png')
    splash_pix = splash_pix.scaled(500, 250, Qt.KeepAspectRatio)
    splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
    splash.setMaximumSize(500, 250)
    splash.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
    splash.setEnabled(False)
    progressBar = QProgressBar(splash)
    progressBar.setRange(0, 0)
    progressBar.setGeometry(20, splash.height() - 10, splash.width(), 5)
    splash.show()

    logging.basicConfig(
        level=logging.DEBUG,
        filename='file.log',
        filemode='w')
    catch_error = ErrorWindow()
    # sys.excepthook = catch_error.excepthook

    gamewindow = None
    i = 0
    while not getattr(qffenestr.GraphicsScene, 'active_scene', False):
        if i == 10:
            gamewindow = qffenestr.MainWindow()
        i += 1
        t = time.time()
        while time.time() < t + 0.2:
            game.processEvents()

    progressBar.setRange(0, 1)
    gamewindow.show()
    splash.finish(gamewindow)

    sys.exit(game.exec_())
