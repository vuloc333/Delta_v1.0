import datetime
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

        self.config_manager = ConfigManager("pyqt\\Services\\config.json")

        self.load_config()

        self.btnSavePara.clicked.connect(self.save_config)
        self.btnLoadPara.clicked.connect(self.load_config)
        self.btnPlcConnect.clicked.connect(self.connect_plc)
        self.btnPlcDisconnect.clicked.connect(self.disconnect_plc)
        self.btnSaveTeaching.clicked.connect(self.teaching_save)
        self.btnAllMove.clicked.connect(self.Movetest)


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

            "Para": {
                "RadiusBase": self.lineBaseRadius,
                "RadiusEE": self.lineEeRadius,
                "BicepLength": self.lineBicepLength,
                "ForeArmLength": self.lineForeArmLength,
            },
            "arm1": {
                "run_speed": self.lineArm1RunSpeed,
                "ramp": self.lineArm1Ramp,
                "jog_speed": self.lineArm1JogSpeed,
                "gear_ratio": self.lineArm1Gear,
                "micro_step": self.lineArm1MicroStepMode,
            },
            "arm2": {
                
                "ramp": self.lineArm2Ramp,
                "jog_speed": self.lineArm2JogSpeed,
                "gear_ratio": self.lineArm2Gear,
                "micro_step": self.lineArm2MicroStepMode,
            },
            "arm3": {
                
                "ramp": self.lineArm3Ramp,
                "jog_speed": self.lineArm3JogSpeed,
                "gear_ratio": self.lineArm3Gear,
                "micro_step": self.lineArm3MicroStepMode,
            },
            "teaching": {
                "z_prepick": self.lineZPrepick,
                "z_offset_pd": self.lineZoffsetPd,
                "z_class": self.lineZClass,
                "z_pitch_class": self.lineZPitchClass,
                "x_class1": self.lineXClass1,
                "y_class1": self.lineYClass1,
                "y_pitch_class1": self.lineYPitchClass1,
            },
            "conveyor": {
                "speed": self.lineConvSpeed,
                
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
        if self.plc is None or not self.plc.client.connected:
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

        # Write bit logic 
        self.plc.o_Arm1JogFw = self.btnArm1JogFw.isDown()
        self.plc.o_Arm1JogBw = self.btnArm1JogBw.isDown()
        
        self.plc.o_Arm2JogFw = self.btnArm2JogFw.isDown()
        self.plc.o_Arm2JogBw = self.btnArm2JogBw.isDown()

        self.plc.o_Arm3JogFw = self.btnArm3JogFw.isDown()
        self.plc.o_Arm3JogBw = self.btnArm3JogBw.isDown()

        self.plc.o_AllHome = self.btnAllHome.isDown()
        self.plc.o_AllMove = self.btnAllMove.isDown()


        # Write data logic
        def s_int(edit): return int(edit.text() or 0)

        self.plc.o_arm1RunSpeed = s_int(self.lineArm1RunSpeed)
        self.plc.o_arm1Ramp = s_int(self.lineArm1Ramp)
        self.plc.o_arm1JogSpeed = s_int(self.lineArm1JogSpeed)
        self.plc.o_arm1gear = s_int(self.lineArm1Gear)
        self.plc.o_arm1MicroStep = s_int(self.lineArm1MicroStepMode)

        self.plc.o_arm2Ramp = s_int(self.lineArm2Ramp)
        self.plc.o_arm2JogSpeed = s_int(self.lineArm2JogSpeed)
        self.plc.o_arm2gear = s_int(self.lineArm2Gear)
        self.plc.o_arm2MicroStep = s_int(self.lineArm2MicroStepMode)

        self.plc.o_arm3Ramp = s_int(self.lineArm3Ramp)
        self.plc.o_arm3JogSpeed = s_int(self.lineArm3JogSpeed)
        self.plc.o_arm3gear = s_int(self.lineArm3Gear)
        self.plc.o_arm3MicroStep = s_int(self.lineArm3MicroStepMode)

        self.plc.o_ConvRunSpeed = s_int(self.lineConvSpeed)

        self.plc.Write_data()

    def teaching_save(self):
        
        if self.plc is None:
            print("PLC is not connected, Connect PLC first!")
            return
        
        def s_int(edit): return int(edit.text() or 0)

        #Teaching

        self.plc.o_zPrePick = s_int(self.lineZPrepick)
        self.plc.o_zClass = s_int(self.lineZClass)
        self.plc.o_zPitchClass = s_int(self.lineZPitchClass)
        self.plc.o_yPitchClass = s_int(self.lineYPitchClass1)

        self.plc.o_xClass1 = s_int(self.lineXClass1)
        self.plc.o_yClass1 = s_int(self.lineYClass1)

        #Parameters

        self.plc.o_RadiusBase = s_int(self.lineBaseRadius)
        self.plc.o_RadiusEE = s_int(self.lineEeRadius)  
        self.plc.o_BicepLength = s_int(self.lineBicepLength)
        self.plc.o_ForeArmLength = s_int(self.lineForeArmLength)


        # Implement teaching save logic here
    def Movetest(self):
        
        if self.plc is None:
            print("PLC is not connected, Connect PLC first!")
            return
        
        def s_int(edit): return int(edit.text() or 0)

        #Teaching
        self.plc.o_xTestPos = s_int(self.lineXtestTarget)
        self.plc.o_yTestPos = s_int(self.lineYtestTarget)
        self.plc.o_zTestPos = s_int(self.lineZtestTarget)