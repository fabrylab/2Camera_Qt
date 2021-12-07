from sys  import exit as sysExit

from PyQt5.QtCore    import *
from PyQt5.QtGui     import *
from PyQt5.QtWidgets import *

class Win1Disply(QFrame):
    def __init__(self, parent):
        QFrame.__init__(self)

        self.setFrameShape(QFrame.StyledPanel)
        self.setLineWidth(0.2)
        # -------
        self.Cntnr = QVBoxLayout()
        self.Cntnr.addWidget(QTextEdit('This is Window 1 with whatever contents you want'))
        self.Win1Btn = QPushButton('>>')
        self.Win1Btn.clicked.connect(parent.RightArrow)
        self.Cntnr.addWidget(self.Win1Btn)
        self.Cntnr.addStretch(1)
        # -------
        self.setLayout(self.Cntnr)

class Win2Disply(QFrame):
    def __init__(self, parent):
        QFrame.__init__(self)

        self.setFrameShape(QFrame.StyledPanel)
        self.setLineWidth(0.2)
        # -------
        self.Cntnr = QVBoxLayout()
        self.Cntnr.addWidget(QTextEdit('This is Window 2 with whatever contents you want'))
        self.Win1Btn = QPushButton('>>')
        self.Win1Btn.clicked.connect(parent.RightArrow)
        self.Cntnr.addWidget(self.Win1Btn)
        self.Cntnr.addStretch(1)
        # -------
        self.setLayout(self.Cntnr)

class OptionButtons(QToolButton):
# Class OptionButtons ("Text", Connector) inherits from QToolButton
    def __init__(self, Text, Connector):
        QToolButton.__init__(self)

        self.setText(Text)
        self.setStyleSheet("font: bold;color: blue;height: 55px;width: 55px;")
        self.setIconSize(QSize(32,32))
        self.clicked.connect(Connector)

############################## Settings Class ##############################
class OptionSettings(QDialog):
    def __init__(self, parent):
        QDialog.__init__(self, parent)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)

        self.btnWin1 = OptionButtons('Win One', self.ShowWindow1)
        self.btnWin2 = OptionButtons('Win Two', self.ShowWindow2)
      # Vertical Box for Buttons *************************************
        self.UpLeft  = QVBoxLayout()
        self.UpLeft.addWidget(self.btnWin1)
        self.UpLeft.addWidget(self.btnWin2)
        self.UpLeft.addStretch(1)
  # Display Area on Right
      # Widget Flip Display ******************************************
        self.UpRite   = QHBoxLayout()
        self.Contents = QStackedWidget()
        self.Contents.addWidget(QTextEdit('Nothing Selected'))
        self.Contents.addWidget(Win1Disply(self))
        self.Contents.addWidget(Win2Disply(self))
        self.Contents.addWidget(QTextEdit('Settings Saved'))
        self.Contents.setCurrentIndex(0)
        self.UpRite.addWidget(self.Contents)

  # Button and Display Area on Top
        self.Upper = QHBoxLayout()
        self.Upper.addLayout(self.UpLeft)
        self.Upper.addLayout(self.UpRite)
  # Save and Cancel Area on Bottom
        self.btnSave = QPushButton("Save")
        self.btnSave.clicked.connect(self.SaveSettings)
        self.btnCncl = QPushButton("Cancel")
        self.btnCncl.clicked.connect(self.close)
        self.Lower   = QHBoxLayout()
        self.Lower.addStretch(1)
        self.Lower.addWidget(self.btnSave)
        self.Lower.addWidget(self.btnCncl)
  # Entire Options Window Layout
        self.OuterBox = QVBoxLayout()
        self.OuterBox.addLayout(self.Upper)
        self.OuterBox.addLayout(self.Lower)
        self.setLayout(self.OuterBox)
        self.setWindowTitle('Settings')
        #Geometry(Left, Top, Width, Hight)
        self.setGeometry(250, 250, 550, 450)
        self.setModal(True)
        self.exec()

    def ShowWindow1(self):
        self.Contents.setCurrentIndex(1)

    def ShowWindow2(self):
        self.Contents.setCurrentIndex(2)

    def SaveSettings(self):
        self.Contents.setCurrentIndex(3)

    def RightArrow(self):
        if self.Contents.currentIndex() == 1:
           self.Contents.setCurrentIndex(2)
        else:
           self.Contents.setCurrentIndex(1)

class CenterPanel(QWidget):
    def __init__(self, MainWin):
        QWidget.__init__(self)

        CntrPane = QTextEdit('Center Panel is Placed Here')

        hbox = QHBoxLayout(self)
        hbox.addWidget(CntrPane)

        self.setLayout(hbox)

class MenuToolBar(QDockWidget):
    def __init__(self, MainWin):
        QDockWidget.__init__(self)
        self.MainWin = MainWin
        self.MainMenu = MainWin.menuBar()

        self.WndowMenu  = self.MainMenu.addMenu('Windows')

        self.OptnAct = QAction('Options', self)
        self.OptnAct.setStatusTip('Open the Options Window')
        self.OptnAct.triggered.connect(MainWin.ShowOptions)

        self.WndowMenu.addAction(self.OptnAct)

        self.InitToolBar(MainWin)

    def InitToolBar(self, MainWin):
        self.mainToolBar = MainWin.addToolBar("Quick Access")

        self.mainToolBar.addAction(self.OptnAct)

class UI_MainWindow(QMainWindow):
    def __init__(self):
        super(UI_MainWindow, self).__init__()
        self.setWindowTitle('Main Window')

      # Left, Top, Width, Height
        self.setGeometry(200, 200, 550, 550)

        self.CenterPane = CenterPanel(self)
        self.setCentralWidget(self.CenterPane)

        self.MenuToolBar = MenuToolBar(self)

    def ShowOptions(self):
        self.Options = OptionSettings(self)

if __name__ == '__main__':
    MainApp = QApplication([])

    MainGui = UI_MainWindow()
    MainGui.show()

    sysExit(MainApp.exec_())