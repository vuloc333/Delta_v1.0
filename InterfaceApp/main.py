import sys
from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt, QTimer
from pyqt.widget import Widget
from com.plc_map import plc_map

app = QtWidgets.QApplication(sys.argv)

window = Widget()

window.show()

app.exec()

