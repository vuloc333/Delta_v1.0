import sys
from PyQt6 import QtWidgets
from pyqt.comUiPlc import Widget

app = QtWidgets.QApplication(sys.argv)

window = Widget()

window.show()


app.exec()