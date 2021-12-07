from __future__ import division, print_function
import qtawesome as qta
import sys
from pathlib import Path
import json

""" some magic to prevent PyQt5 from swallowing exceptions """
# Back up the reference to the exceptionhook
#sys._excepthook = sys.excepthook
# Set the exception hook to our wrapping function
#sys.excepthook = lambda *args: sys._excepthook(*args)

import sys, os, ctypes
from qtpy import QtCore, QtGui, QtWidgets

from qimage2ndarray import array2qimage

import time
import numpy as np
import matplotlib.pyplot as plt
from includes.QExtendedGraphicsView import QExtendedGraphicsView
from includes.MemMap import MemMap
import configparser
from includes.module_livedisplay import QLiveDisplay
from includes.module_liveanalysis import QLiveAnalysis
from includes.module_input import QConfigInput


class Window(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle('LiveViewer')

        main_layout = QtWidgets.QHBoxLayout(self)
        side_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(side_layout)
        self.config_input = QConfigInput(self, side_layout)
        self.live_analysis = QLiveAnalysis(self, side_layout)
        self.live_display = QLiveDisplay(self, main_layout)

        self.config_input.signal_start.connect(self.live_analysis.start_record)
        #self.config_input.signal_stop.connect(self.live_analysis.cancel_record)
        self.live_analysis.signal_recording_stopped.connect(self.config_input.recoding_stopped)

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.live_analysis.closeEvent(a0)


if __name__ == '__main__':
    if sys.platform[:3] == 'win':
        myappid = 'fabrybiophysics.flowcytometer'  # arbitrary string
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    # start the Qt application
    app = QtWidgets.QApplication(sys.argv)

    window = Window()
    window.show()
    sys.exit(app.exec_())
