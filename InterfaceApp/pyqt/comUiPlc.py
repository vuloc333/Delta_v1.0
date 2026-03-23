import datetime  # Dùng thư viện chuẩn của Python
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QWidget
from pyqt.Services.ui_widget import Ui_wgDelta_Control
from com.plc_map import plc_map
from pyqt.Services.config_load import ConfigManager

class Widget(QWidget, Ui_wgDelta_Control):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Delta Robot Control Panel")

        self.config_manager = ConfigManager("pyqt\\config.json")

        self.load_config()

        self.btnSavePara.clicked.connect(self.save_config)
        self.btnLoadPara.clicked.connect(self.load_config)
        self.btnPlcConnect.clicked.connect(self.connect_plc)
        self.btnPlcDisconnect.clicked.connect(self.disconnect_plc)


        self.plc = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.polling_data)
        self.timer.start(100)

    def save_config(self):
        mapping = self.get_ui_mapping()
        robot_params = {}

        for group_name, widgets in mapping.items():

            group_dict = {}
            
            for key, value in widgets.items():
                group_dict[key] = int(value.text() or 0)
            
            robot_params[group_name] = group_dict

        config_data = {
            "connection": {"ip_plc": self.lineIpPlc.text()},
            "robot_params": robot_params,
            "last_update": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        self.config_manager.save(config_data)

    def get_ui_mapping(self):
        return {
            "arm1": {
                "run_speed": self.lineArm1RunSpeed,
                "ramp": self.lineArm1Ramp,
                "jog_speed": self.lineArm1JogSpeed,
                "gear_ratio": self.lineArm1Gear,
                "micro_step": self.lineArm1MicroStepMode,
            },
            "arm2": {
                "run_speed": self.lineArm2RunSpeed,
                "ramp": self.lineArm2Ramp,
                "jog_speed": self.lineArm2JogSpeed,
                "gear_ratio": self.lineArm2Gear,
                "micro_step": self.lineArm2MicroStepMode,
            },
            "conveyor": {
                "speed": self.lineConvSpeed,
                "ramp": self.lineConvRamp,
            }
        }

    def load_config(self):
        data = self.config_manager.load()

        if not data:
            print("No config file found or file is empty.")
            return

        rp_data = data.get("robot_params", {})
        mapping = self.get_ui_mapping()
        
        for arm_key, params in mapping.items():
            arm_data = rp_data.get(arm_key, {})
            for param_key, widget in params.items():
                widget.setText(str(arm_data.get(param_key, 0)))

        self.lineIpPlc.setText(str(data.get("connection", {}).get("ip_plc", 0)))

    def connect_plc(self):
        ip = self.lineIpPlc.text()
        if self.plc is None:
            try:
                self.plc = plc_map(ip) 
                print(f"Attempting to connect to {ip}")
            except Exception as e:
                print(f"Connection Error: {e}")
                self.plc = None
        else:
            print("Already connected to PLC.")

    def disconnect_plc(self):
        if self.plc is not None:
            self.plc.client.disconnect()
            self.plc = None
            print("Disconnected from PLC.")
        else:
            print("No PLC connection to disconnect.")

    def polling_data(self):
        if self.plc is None:
            self.lblConnectStatus.setText("No Connection")
            return
        
        self.lblConnectStatus.setText("Connected")
        self.updateUi()
        self.updatePlc()
        
    def updateUi(self):
        self.plc.Read_data()
        self.lineArm1CurPos.setText(str(self.plc.i_deltaData1))
        self.lineArm2CurPos.setText(str(self.plc.i_deltaData2))
        self.lineArm3CurPos.setText(str(self.plc.i_deltaData3))

    def updatePlc(self):
        # Write bit logic (giữ nguyên)
        self.plc.o_deltabit0_0 = self.btnArm1JogFw.isDown()
        self.plc.o_deltabit0_1 = self.btnArm1JogBw.isDown()
        self.plc.o_deltabit0_2 = self.btnArm1Home.isDown()
        
        self.plc.o_deltabit1_0 = self.btnArm2JogFw.isDown()
        self.plc.o_deltabit1_1 = self.btnArm2JogBw.isDown()
        self.plc.o_deltabit1_2 = self.btnArm2Home.isDown()

        self.plc.o_deltabit2_0 = self.btnArm3JogFw.isDown()
        self.plc.o_deltabit2_1 = self.btnArm3JogBw.isDown()
        self.plc.o_deltabit2_2 = self.btnArm3Home.isDown()

        # Write data logic
        def s_int(edit): return int(edit.text() or 0)

        self.plc.o_deltaData1 = s_int(self.lineArm1RunSpeed)
        self.plc.o_deltaData2 = s_int(self.lineArm1Ramp)
        self.plc.o_deltaData3 = s_int(self.lineArm1JogSpeed)
        self.plc.o_deltaData4 = s_int(self.lineArm1Gear)
        self.plc.o_deltaData5 = s_int(self.lineArm1MicroStepMode)

        self.plc.o_deltaData6 = s_int(self.lineArm2RunSpeed)
        self.plc.o_deltaData7 = s_int(self.lineArm2Ramp)
        self.plc.o_deltaData8 = s_int(self.lineArm2JogSpeed)
        self.plc.o_deltaData9 = s_int(self.lineArm2Gear)
        self.plc.o_deltaData10 = s_int(self.lineArm2MicroStepMode)

        self.plc.o_deltaData11 = s_int(self.lineArm3RunSpeed)
        self.plc.o_deltaData12 = s_int(self.lineArm3Ramp)
        self.plc.o_deltaData13 = s_int(self.lineArm3JogSpeed)
        self.plc.o_deltaData14 = s_int(self.lineArm3Gear)
        self.plc.o_deltaData15 = s_int(self.lineArm3MicroStepMode)

        self.plc.o_deltaData16 = s_int(self.lineConvSpeed)
        self.plc.o_deltaData17 = s_int(self.lineConvRamp)

        self.plc.Write_data()