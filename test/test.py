from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QApplication

import sys

from PyQt5 import uic
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QFileDialog

from pypylon import pylon
from scipy.ndimage import gaussian_filter
from skimage.feature import peak_local_max

import numpy as np
import cv2 

import pyqtgraph as pg

import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.ticker as ticker



#----------general fonts for plots and figures----------
font = {'family' : 'sans-serif',
        'sans-serif':['Arial'],
        'weight' : 'normal',
        'size'   : 10}
plt.rc('font', **font)
plt.rc('legend', fontsize=7)
plt.rc('axes', titlesize=10)



class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = plt.figure(figsize=(width, height), dpi=dpi)
        self.canvas = FigureCanvas(self.fig)
        self.axes = self.fig.add_subplot(111)
        self.axes.yaxis.set_visible(False)
        super(MplCanvas, self).__init__(self.fig)
        self.fig.tight_layout()
        self.axes.set_facecolor('snow')
        self.fig.set_facecolor('whitesmoke')

class MainWindow(QtWidgets.QMainWindow):
    # QApplication.setStyle('Fusion')
    # QApplication.setApplicationName('cell counting')
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        # self.ui = uic.loadUi('src/main/python/main.ui', self)
        # self.setWindowIcon(QtGui.QIcon('src/main/icons/icon.png'))
        self.ui = uic.loadUi('test.ui', self)
        # self.setWindowIcon(QtGui.QIcon('icon.png'))




def main():
    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()
    app.setStyle('Fusion')
    main.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()