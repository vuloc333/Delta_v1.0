import datetime
from typing import Any, Dict
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import QWidget
from pyqt.Services.ui_widget import Ui_wgDelta_Control
from pyqt.Services.config_load import ConfigManager
from .plc_controller import PlcController
from .vision_controller import VisionController

class Widget(QWidget, Ui_wgDelta_Control):
    def __init__(self) -> None:
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


        self.plc_controller = PlcController()
        self.vision_controller = VisionController()
        self.video_timer = QTimer()
        self.video_timer.timeout.connect(self.update_webcam_frame)

        self.btnStart.clicked.connect(self.start_webcam)
        self.btnStop.clicked.connect(self.stop_webcam)
        self.btnReset.clicked.connect(self.reset_webcam)

        self.Sync = QTimer()
        self.CheckConnection = QTimer()
        self.Sync.timeout.connect(self.polling_data)
        self.CheckConnection.timeout.connect(self.check_plc_connection)
        self.CheckConnection.start(1000)
        self.Sync.start(50)

    def save_config(self) -> None:
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

    def connect_plc(self) -> None:
        ip = self.lineIpPlc.text()
        self.lblConnectStatus.setText(f"Attempting to connect to {ip}")
        success, message = self.plc_controller.connect(ip)
        self.lblConnectStatus.setText(message)
        if success:
            print(f"Connected to {ip}")
        else:
            print(f"Connection Error: {message}")

    def disconnect_plc(self) -> None:
        if not self.plc_controller.is_connected():
            self.lblConnectStatus.setText("PLC is not connected")
            print("No PLC connection to disconnect.")
            return

        self.plc_controller.disconnect()
        self.lblConnectStatus.setText("Disconnected")
        print("Disconnected from PLC.")

    def polling_data(self) -> None:
        if not self.plc_controller.is_connected():
            self.lblConnectStatus.setText("No Connection")
            return

        self.lblConnectStatus.setText("Connected")
        self.updateUi()
        self.updatePlc()

    def check_plc_connection(self) -> None:
        if self.plc_controller.is_connected():
            self.lblConnectStatus.setText("Connected")
        else:
            self.lblConnectStatus.setText("No Connection")

    def _to_int(self, edit: Any) -> int:
        return int(edit.text() or 0)

    def _collect_output_values(self) -> dict[str, Any]:
        return {
            "o_Arm1JogFw": self.btnArm1JogFw.isDown(),
            "o_Arm1JogBw": self.btnArm1JogBw.isDown(),
            "o_Arm2JogFw": self.btnArm2JogFw.isDown(),
            "o_Arm2JogBw": self.btnArm2JogBw.isDown(),
            "o_Arm3JogFw": self.btnArm3JogFw.isDown(),
            "o_Arm3JogBw": self.btnArm3JogBw.isDown(),
            "o_AllHome": self.btnAllHome.isDown(),
            "o_AllMove": self.btnAllMove.isDown(),
            "o_arm1RunSpeed": self._to_int(self.lineArm1RunSpeed),
            "o_arm1Ramp": self._to_int(self.lineArm1Ramp),
            "o_arm1JogSpeed": self._to_int(self.lineArm1JogSpeed),
            "o_arm1gear": self._to_int(self.lineArm1Gear),
            "o_arm1MicroStep": self._to_int(self.lineArm1MicroStepMode),
            "o_arm2Ramp": self._to_int(self.lineArm2Ramp),
            "o_arm2JogSpeed": self._to_int(self.lineArm2JogSpeed),
            "o_arm2gear": self._to_int(self.lineArm2Gear),
            "o_arm2MicroStep": self._to_int(self.lineArm2MicroStepMode),
            "o_arm3Ramp": self._to_int(self.lineArm3Ramp),
            "o_arm3JogSpeed": self._to_int(self.lineArm3JogSpeed),
            "o_arm3gear": self._to_int(self.lineArm3Gear),
            "o_arm3MicroStep": self._to_int(self.lineArm3MicroStepMode),
            "o_ConvRunSpeed": self._to_int(self.lineConvSpeed),
        }

    def _collect_teaching_values(self) -> dict[str, int]:
        return {
            "o_zPrePick": self._to_int(self.lineZPrepick),
            "o_zClass": self._to_int(self.lineZClass),
            "o_zPitchClass": self._to_int(self.lineZPitchClass),
            "o_yPitchClass": self._to_int(self.lineYPitchClass1),
            "o_xClass1": self._to_int(self.lineXClass1),
            "o_yClass1": self._to_int(self.lineYClass1),
        }

    def _collect_parameters(self) -> dict[str, int]:
        return {
            "o_RadiusBase": self._to_int(self.lineBaseRadius),
            "o_RadiusEE": self._to_int(self.lineEeRadius),
            "o_BicepLength": self._to_int(self.lineBicepLength),
            "o_ForeArmLength": self._to_int(self.lineForeArmLength),
        }

    def _collect_movetest_values(self) -> dict[str, int]:
        return {
            "o_xTestPos": self._to_int(self.lineXtestTarget),
            "o_yTestPos": self._to_int(self.lineYtestTarget),
            "o_zTestPos": self._to_int(self.lineZtestTarget),
        }

    def log(self, message: Any) -> None:
        print(message)
        try:
            self.pteLog.appendPlainText(str(message))
        except Exception:
            pass

    def start_webcam(self) -> None:
        if self.video_timer.isActive():
            return

        success, message = self.vision_controller.start()
        self.lblVisionStatus.setText(message)
        self.log(message)

        if success:
            self.video_timer.start(30)

    def stop_webcam(self) -> None:
        if self.video_timer.isActive():
            self.video_timer.stop()

        self.vision_controller.stop()
        self.lblVisionStatus.setText("Webcam stopped")
        self.log("Webcam stopped")

    def reset_webcam(self) -> None:
        self.stop_webcam()
        self.lblWebcam.clear()
        self.lblVisionStatus.setText("Webcam reset")

    def update_webcam_frame(self) -> None:
        frame = self.vision_controller.read_frame()
        if frame is None:
            self.lblVisionStatus.setText("No webcam frame")
            self.stop_webcam()
            return

        annotated = self.vision_controller.annotate_frame(frame)
        height, width, channel = annotated.shape
        bytes_per_line = channel * width
        image = QImage(
            annotated.data,
            width,
            height,
            bytes_per_line,
            QImage.Format.Format_BGR888,
        )
        pixmap = QPixmap.fromImage(image)
        self.lblWebcam.setPixmap(
            pixmap.scaled(
                self.lblWebcam.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )

    def updateUi(self) -> None:
        try:
            positions = self.plc_controller.read_positions()
            self.lineArm1CurPos.setText(str(positions.get("arm1", 0)))
            self.lineArm2CurPos.setText(str(positions.get("arm2", 0)))
            self.lineArm3CurPos.setText(str(positions.get("arm3", 0)))
        except Exception:
            pass

    def updatePlc(self) -> None:
        if not self.plc_controller.is_connected():
            return

        try:
            self.plc_controller.write_outputs(self._collect_output_values())
        except Exception:
            pass

    def teaching_save(self) -> None:
        if not self.plc_controller.is_connected():
            print("PLC is not connected, Connect PLC first!")
            return

        try:
            self.plc_controller.write_teaching(self._collect_teaching_values())
            self.plc_controller.write_parameters(self._collect_parameters())
        except Exception as e:
            print(f"Teaching save error: {e}")
    def Movetest(self) -> None:
        if not self.plc_controller.is_connected():
            print("PLC is not connected, Connect PLC first!")
            return

        try:
            self.plc_controller.write_outputs(self._collect_movetest_values())
        except Exception as e:
            print(f"Movetest error: {e}")