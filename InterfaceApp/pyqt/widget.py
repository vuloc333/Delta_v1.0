from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QWidget
from pyqt.ui_widget import Ui_wgSetting
from com.plc_map import plc_map

class Widget(QWidget ,Ui_wgSetting):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Setting")
        self.plc = plc_map()

        self.timer = QTimer()
        self.timer.timeout.connect(self.polling_data)
        self.timer.start(100)

    def polling_data(self):
        self.plc.o_deltabit0_0 = self.btnArm1JogFw.isDown()
        self.plc.o_deltabit0_1 = self.btnArm1JogBw.isDown()
        self.plc.o_deltabit0_2 = self.btnArm1Home.isDown()
        print(self.plc.o_deltabit0_0, self.plc.o_deltabit0_1, self.plc.o_deltabit0_2)

        self.plc.Write_data()
        