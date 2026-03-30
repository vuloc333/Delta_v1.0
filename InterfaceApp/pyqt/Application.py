import datetime
from typing import Any, Dict, Optional

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QWidget
from pyqt.Services.ui_widget import Ui_wgDelta_Control
from pyqt.Services.config_load import ConfigManager
from com.plc_map import plc_map
from vision.vision_controller import VisionController

class Widget(QWidget, Ui_wgDelta_Control):
    def __init__(self) -> None:
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Delta Robot Control Panel")
        # region UI Setup
        self.config_manager = ConfigManager("pyqt\\Services\\config.json")
        
        self.plc = None
        
        # Initialize Vision Controller for RX 470
        self.vision = VisionController(self.lblWebcam, camera_id=1)
        self.vision.start()

        self.load_config()
        # endregion

        # region Button Connections
        self.btnSavePara.clicked.connect(self.save_config)
        self.btnLoadPara.clicked.connect(self.load_config)
        self.btnPlcConnect.clicked.connect(self.connect_plc)
        self.btnPlcDisconnect.clicked.connect(self.disconnect_plc)
        self.btnSaveTeaching.clicked.connect(self.teaching_save)
        self.btnAllMove.clicked.connect(self.IK_Move) 
        # endregion 

        # region Timers Setup
        self.Sync = QTimer()
        self.CheckConnection = QTimer()
        self.VisionTimer = QTimer()  # Update vision status
        self.Sync.timeout.connect(self.polling_data)
        self.CheckConnection.timeout.connect(self.check_plc_connection)
        self.VisionTimer.timeout.connect(self.update_vision_status)
         
        self.CheckConnection.start(2000)
        self.Sync.start(30)
        self.VisionTimer.start(100)  # 10Hz update
        # endregion
    
    def update_vision_status(self):
        """Update vision status label"""
        try:
            if hasattr(self, 'vision'):
                detections = self.vision.get_detections()
                if detections:
                    info = " | ".join([f"{d['class']}:{d['confidence']:.2f}" for d in detections])
                    self.lblVisionStatus.setText(f"Detected: {info}")
                else:
                    self.lblVisionStatus.setText("No objects detected")
        except:
            pass
    
    def closeEvent(self, event):
        """Cleanup when closing"""
        if hasattr(self, 'vision'):
            self.vision.stop()
        event.accept()
    

    # region Save/Load Config

    def save_config(self) -> None:
        try:
            mapping = self.get_ui_mapping()
            robot_params = {}

            # Chia robot_params
            for group_name, widgets in mapping.items():
                group_dict = {}
                for key, value in widgets.items():
                    if hasattr(value, 'value'):  # QSlider
                        group_dict[key] = value.value()
                    else:  # QLineEdit
                        group_dict[key] = int(value.text() or 0)
                
                robot_params[group_name] = group_dict

            config_data = {
                "connection": {"ip_plc": self.lineIpPlc.text()},
                "robot_params": robot_params,
                "last_update": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            self.config_manager.save(config_data)
        except ValueError as exc:
            self.log(f"Invalid numeric input while saving config: {exc}")
        except Exception as exc:
            self.log(f"Failed to save config: {exc}")

    def get_ui_mapping(self) -> dict[str, dict[str, Any]]:
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

    def load_config(self) -> None:
        try:
            data = self.config_manager.load()
        except:
            return
        
        if not data:
            print("No config file found or file is empty.")
            return

        rp_data = data.get("robot_params", {})
        mapping = self.get_ui_mapping()
        
        # Load robot_params
        for arm_key, params in mapping.items():
            arm_data = rp_data.get(arm_key, {})
            for param_key, widget in params.items():
                if hasattr(widget, 'setValue'):  # QSlider
                    widget.setValue(arm_data.get(param_key, 0))
                else:  # QLineEdit
                    widget.setText(str(arm_data.get(param_key, 0)))
    
        self.lineIpPlc.setText(str(data.get("connection", {}).get("ip_plc", "")))

    # endregion
    
    # region PLC Connection
    def connect_plc(self) -> None:
        try:            
            ip = self.lineIpPlc.text()
            self.plc = plc_map(ip)
            # Initialize PLC controller after connection
            self.lblConnectStatus.setText("Connected")
        except Exception as exc:
            self.lblConnectStatus.setText("Connect failed")
            self.log(f"connect_plc error: {exc}")

    def disconnect_plc(self) -> None:
        try:
            if not self.plc.is_connected():
                self.lblConnectStatus.setText("PLC is not connected")
                print("No PLC connection to disconnect.")
                return

            self.plc.disconnect()
            self.lblConnectStatus.setText("Disconnected")
            print("Disconnected from PLC.")
        except Exception as exc:
            self.lblConnectStatus.setText("Disconnect failed")
            self.log(f"disconnect_plc error: {exc}")
    
    def _collect_teaching_values(self) -> None:
        self.plc.o_zPrePick = self._to_int(self.lineZPrepick)
        self.plc.o_zClass = self._to_int(self.lineZClass)
        self.plc.o_zPitchClass = self._to_int(self.lineZPitchClass)
        self.plc.o_yPitchClass = self._to_int(self.lineYPitchClass1)
        self.plc.o_xClass1 = self._to_int(self.lineXClass1)
        self.plc.o_yClass1 = self._to_int(self.lineYClass1)
        self.plc.o_RadiusBase = self._to_int(self.lineBaseRadius)
        self.plc.o_RadiusEE = self._to_int(self.lineEeRadius)
        self.plc.o_BicepLength = self._to_int(self.lineBicepLength)
        self.plc.o_ForeArmLength = self._to_int(self.lineForeArmLength)

    def _to_int(self, edit: Any) -> int:
        return int(edit.text() or 0)

    def _collect_output_values(self) -> None:
        # update bit
        self.plc.o_Arm1JogFw = self.btnArm1JogFw.isDown()
        self.plc.o_Arm1JogBw = self.btnArm1JogBw.isDown()
        self.plc.o_Arm2JogFw = self.btnArm2JogFw.isDown()
        self.plc.o_Arm2JogBw = self.btnArm2JogBw.isDown()
        self.plc.o_Arm3JogFw = self.btnArm3JogFw.isDown()
        self.plc.o_Arm3JogBw = self.btnArm3JogBw.isDown()
        self.plc.o_AllHome = self.btnAllHome.isDown()
        self.plc.o_AllMove = self.btnAllMove.isDown()

        # update data
        self.plc.o_arm1RunSpeed = self._to_int(self.lineArm1RunSpeed)
        self.plc.o_arm1Ramp = self._to_int(self.lineArm1Ramp)
        self.plc.o_arm1JogSpeed = self._to_int(self.lineArm1JogSpeed)
        self.plc.o_arm1gear = self._to_int(self.lineArm1Gear)
        self.plc.o_arm1MicroStep = self._to_int(self.lineArm1MicroStepMode)
        self.plc.o_arm2Ramp = self._to_int(self.lineArm2Ramp)
        self.plc.o_arm2JogSpeed = self._to_int(self.lineArm2JogSpeed)
        self.plc.o_arm2gear = self._to_int(self.lineArm2Gear)
        self.plc.o_arm2MicroStep = self._to_int(self.lineArm2MicroStepMode)
        self.plc.o_arm3Ramp = self._to_int(self.lineArm3Ramp)
        self.plc.o_arm3JogSpeed = self._to_int(self.lineArm3JogSpeed)
        self.plc.o_arm3gear = self._to_int(self.lineArm3Gear)
        self.plc.o_arm3MicroStep = self._to_int(self.lineArm3MicroStepMode)
        self.plc.o_ConvRunSpeed = self._to_int(self.lineConvSpeed)

    def polling_data(self) -> None:
        try:
            if self.plc.is_connected():
                pass
        except:
            return
        
        self.lblConnectStatus.setText("Connected")
        self.updateUi()
        self.updatePlc()

    def updateUi(self) -> None:

        self.plc.Read_data()
        self.lineArm1CurPos.setText(str(self.plc.i_deltaData1))
        self.lineArm2CurPos.setText(str(self.plc.i_deltaData2))
        self.lineArm3CurPos.setText(str(self.plc.i_deltaData3))

    def updatePlc(self) -> None:

        self._collect_output_values()
        self.plc.Write_data()

    def IK_Move(self) -> None:

        try:
            self.plc.o_xTestPos = self._to_int(self.lineXtestTarget)
            self.plc.o_yTestPos = self._to_int(self.lineYtestTarget)
            self.plc.o_zTestPos = self._to_int(self.lineZtestTarget)
            self.plc.Write_data()

        except:
            return  

    def teaching_save(self) -> None:
        try:
            if self.plc.is_connected():
                self._collect_teaching_values()
                self.plc.Write_data()
                self.log(f"Teaching save success")
        except Exception as exc:
            self.log(f"Teaching save error: {exc}")
 
    def check_plc_connection(self) -> None:
        try:
            if self.plc.is_connected():
                self.lblConnectStatus.setText("Connected")
            else:
                self.lblConnectStatus.setText("No Connection")
        except:
            self.lblConnectStatus.setText("No Connection")
            return
    # endregion
    
    def log(self, message: Any) -> None:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        print(log_message)
        try:
            self.pteLog.appendPlainText(str(log_message))
        except Exception:
            pass

