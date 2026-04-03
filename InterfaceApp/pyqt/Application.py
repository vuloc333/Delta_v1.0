import datetime
from typing import Any

from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QIntValidator
from PyQt6.QtWidgets import QWidget
from pyqt.Services.ui_widget import Ui_wgDelta_Control
from pyqt.Services.config_load import ConfigManager
from com.plc_map import plc_map
from vision.vision_control import VisionControl
from pyqt.comVisionPlc import VisionPlcHandler

class Widget(QWidget, Ui_wgDelta_Control):
    def __init__(self) -> None:
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Delta Robot Control Panel")
        # region Setup Validators for integer-only LineEdits
        self._setup_int_validators()
        # endregion
        # region UI Setup
        self.config_manager = ConfigManager("pyqt\\Services\\config.json")
        
        self.plc = None
        self.vision = None
        self.plc_vision = None
        
        # Khởi tạo vision sau khi UI setup
        self.init_vision()
        
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
        
        self.Sync.timeout.connect(self.polling_data)
        self.Sync.timeout.connect(self.start_auto_cycle)
        self.Sync.timeout.connect(self.update_vision_status)
        self.CheckConnection.timeout.connect(self.check_plc_connection)
         
        self.CheckConnection.start(2000)
        self.Sync.start(50)
        # endregion
    
    def init_vision(self):
        """Khởi tạo vision system"""
        try:
            # 1. Khởi tạo vision control
            self.vision = VisionControl(self.lblWebcam, camera_id=1)
            self.vision.start()
            
            # 2. Timer đợi camera sẵn sàng rồi cấu hình ROI
            self.init_timer = QTimer()
            self.init_timer.timeout.connect(self._setup_roi)
            self.init_timer.start(200)
            
            print("Vision initialized")
        except Exception as e:
            print(f"Vision init error: {e}")
            
    def _setup_roi(self):
        """Setup ROI khi camera đã sẵn sàng"""
        try:
            if self.vision and self.vision.is_ready():
                self.init_timer.stop()
                pass
            else: 
                return
        except:
            return
        # Lấy kích thước frame từ camera
        w, h = self.vision.get_frame_size()
        self.log(f"Camera size: {w}x{h}")
        
        # Cấu hình ROI sliders
        self.slideRoiX.setRange(0, w - 1)
        self.slideRoiY.setRange(0, h - 1)
        self.slideRoiW.setRange(1, w)
        self.slideRoiH.setRange(1, h)
        
        # Set giá trị mặc định (full frame)
        self.slideRoiX.setValue(0)
        self.slideRoiY.setValue(0)
        self.slideRoiW.setValue(w)
        self.slideRoiH.setValue(h)
        
        # Connect ROI sliders
        self.slideRoiX.valueChanged.connect(self.update_roi)
        self.slideRoiY.valueChanged.connect(self.update_roi)
        self.slideRoiW.valueChanged.connect(self.update_roi)
        self.slideRoiH.valueChanged.connect(self.update_roi)
        
        # Load config ROI
        self._load_vision_config()
        
        print("ROI setup complete")
            
    def update_roi(self):
        """Update ROI từ sliders"""
        if self.vision:
            x = self.slideRoiX.value()
            y = self.slideRoiY.value()
            w = self.slideRoiW.value()
            h = self.slideRoiH.value()
            self.vision.set_roi(x, y, w, h)
            
    def update_vision_status(self):
        """Cập nhật trạng thái vision lên UI"""
        if self.vision:
            detections = self.vision.get_detections()
            if detections:
                info = " | ".join([f"{d.get('class', '?' )}({d.get('x', 0)},{d.get('y', 0)})" for d in detections])
                self.lblVisionStatus.setText(info)
            else:
                self.lblVisionStatus.setText("No objects")
                
    def _load_vision_config(self):
        """Load vision ROI từ config"""
        try:
            data = self.config_manager.load()
            if data and "vision_roi" in data:
                roi = data["vision_roi"]
                self.slideRoiX.setValue(roi.get("x", 0))
                self.slideRoiY.setValue(roi.get("y", 0))
                self.slideRoiW.setValue(roi.get("w", 640))
                self.slideRoiH.setValue(roi.get("h", 480))
                self.update_roi()
                print("Vision ROI loaded from config")
        except Exception as e:
            print(f"Load vision config error: {e}")
    
    def _setup_int_validators(self) -> None:
        """Thiết lập validator chỉ cho phép nhập số nguyên cho các LineEdit"""
        int_validator = QIntValidator()

        # Robot kinematic parameters
        self.lineBaseRadius.setValidator(int_validator)
        self.lineEeRadius.setValidator(int_validator)
        self.lineBicepLength.setValidator(int_validator)
        self.lineForeArmLength.setValidator(int_validator)

        # Arm speeds and ramps
        self.lineArm1RunSpeed.setValidator(int_validator)
        self.lineArm1Ramp.setValidator(int_validator)
        self.lineArm1JogSpeed.setValidator(int_validator)
        self.lineArm2Ramp.setValidator(int_validator)
        self.lineArm2JogSpeed.setValidator(int_validator)
        self.lineArm3Ramp.setValidator(int_validator)
        self.lineArm3JogSpeed.setValidator(int_validator)

        # Conveyor
        self.lineConvSpeed.setValidator(int_validator)

        # Teaching positions
        self.lineZPrepick.setValidator(int_validator)
        self.lineZoffsetPd.setValidator(int_validator)
        self.lineZClass.setValidator(int_validator)
        self.lineXClass1.setValidator(int_validator)
        self.lineYClass1.setValidator(int_validator)
        self.lineYPitchClass1.setValidator(int_validator)

        # Test targets (inverse kinematic)
        self.lineXtestTarget.setValidator(int_validator)
        self.lineYtestTarget.setValidator(int_validator)
        self.lineZtestTarget.setValidator(int_validator)

        # Vision parameters
        self.lineOffsetCamX.setValidator(int_validator)
        self.lineOffsetCamY.setValidator(int_validator)
        self.lineRatePixel.setValidator(int_validator)

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
                "vision_roi": {
                    "x": self.slideRoiX.value(),
                    "y": self.slideRoiY.value(),
                    "w": self.slideRoiW.value(),
                    "h": self.slideRoiH.value()
                },
                "vision_params": {
                    "offset_x": int(self.lineOffsetCamX.text() or 0),
                    "offset_y": int(self.lineOffsetCamY.text() or 0),
                    "pixel_rate": int(self.lineRatePixel.text() or 1)
                },
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
            },
            "arm2": {
                
                "ramp": self.lineArm2Ramp,
                "jog_speed": self.lineArm2JogSpeed,
            },
            "arm3": {
                
                "ramp": self.lineArm3Ramp,
                "jog_speed": self.lineArm3JogSpeed,
            },
            "teaching": {
                "z_prepick": self.lineZPrepick,
                "z_offset_pd": self.lineZoffsetPd,
                "z_class": self.lineZClass,
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
            self.log("No config file found or file is empty.")
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
        
        # Load vision_params
        vp_data = data.get("vision_params", {})
        self.lineOffsetCamX.setText(str(vp_data.get("offset_x", 0)))
        self.lineOffsetCamY.setText(str(vp_data.get("offset_y", 0)))
        self.lineRatePixel.setText(str(vp_data.get("pixel_rate", 1)))
    # endregion
    
    # region PLC Connection
    def connect_plc(self) -> None:
        try:            
            ip = self.lineIpPlc.text()
            self.plc = plc_map(ip)
            # Initialize PLC controller after connection
            self.lblConnectStatus.setText("Connected")
            self.teaching_save()
            
            # Cập nhật PLC reference cho vision_plc nếu đang chạy
            if hasattr(self, 'vision_plc') and self.vision_plc is not None:
                self.vision_plc.update_plc(self.plc)

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
        self.plc.o_yPitchClass = self._to_int(self.lineYPitchClass1)
        self.plc.o_xClass1 = self._to_int(self.lineXClass1)
        self.plc.o_yClass1 = self._to_int(self.lineYClass1)
        self.plc.o_RadiusBase = self._to_int(self.lineBaseRadius)
        self.plc.o_RadiusEE = self._to_int(self.lineEeRadius)
        self.plc.o_BicepLength = self._to_int(self.lineBicepLength)
        self.plc.o_ForeArmLength = self._to_int(self.lineForeArmLength)

        #Robot Teaching
        self.plc.o_OffsetX = self._to_int(self.lineOffsetCamX)
        self.plc.o_OffsetY = self._to_int(self.lineOffsetCamY)
        self.plc.o_pixelRate = self._to_int(self.lineRatePixel)

        self.plc.o_xClass1 = self._to_int(self.lineXClass1)
        self.plc.o_yClass1 = self._to_int(self.lineYClass1)
        self.plc.o_zClass = self._to_int(self.lineZClass)
        self.plc.o_yPitchClass = self._to_int(self.lineYPitchClass1)
        self.plc.o_zPrePick = self._to_int(self.lineZPrepick)
        self.plc.o_zObject = self._to_int(self.lineZoffsetPd)

    def _to_int(self, edit: Any) -> int:
        return int(edit.text() or 0)

    def _collect_ui_values(self) -> None:
        # update bit
        self.plc.o_Arm1JogFw = self.btnArm1JogFw.isDown()
        self.plc.o_Arm1JogBw = self.btnArm1JogBw.isDown()
        self.plc.o_Arm2JogFw = self.btnArm2JogFw.isDown()
        self.plc.o_Arm2JogBw = self.btnArm2JogBw.isDown()
        self.plc.o_Arm3JogFw = self.btnArm3JogFw.isDown()
        self.plc.o_Arm3JogBw = self.btnArm3JogBw.isDown()
        self.plc.o_AllHome = self.btnAllHome.isDown()
        self.plc.o_AllMove = self.btnAllMove.isDown()

        self.plc.o_Startbtn = self.btnStart.isDown()
        self.plc.o_Stopbtn = self.btnStop.isDown()
        self.plc.o_ResetBtn = self.btnReset.isDown()

        # update data
        self.plc.o_arm1RunSpeed = self._to_int(self.lineArm1RunSpeed)
        self.plc.o_arm1Ramp = self._to_int(self.lineArm1Ramp)
        self.plc.o_arm1JogSpeed = self._to_int(self.lineArm1JogSpeed)
        self.plc.o_arm2Ramp = self._to_int(self.lineArm2Ramp)
        self.plc.o_arm2JogSpeed = self._to_int(self.lineArm2JogSpeed)
        self.plc.o_arm3Ramp = self._to_int(self.lineArm3Ramp)
        self.plc.o_arm3JogSpeed = self._to_int(self.lineArm3JogSpeed)
        self.plc.o_ConvRunSpeed = self._to_int(self.lineConvSpeed)

    def polling_data(self) -> None:
        try:
            if not self.plc.is_connected():
                return
        except:
            return

        self.updateUi()
        self.updatePlc()

    def updateUi(self) -> None:

        self.plc.Read_data()
        #Positioning
        self.lineArm1CurPos.setText(str(self.plc.i_Arm1CurPos))
        self.lineArm2CurPos.setText(str(self.plc.i_Arm2CurPos))
        self.lineArm3CurPos.setText(str(self.plc.i_Arm3CurPos))

        #Product Count
        self.linePdYel.setText(str(self.plc.i_YelCirCount))
        self.linePdRed.setText(str(self.plc.i_RedRecCount))
        #self.linePdBlu.setText(str(self.plc.i_BlueTriCount))


    def updatePlc(self) -> None:

        self._collect_ui_values()
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
    
    def closeEvent(self, event):
        """Cleanup khi đóng app"""
        if self.vision:
            self.vision.stop()
        event.accept()
        
    # region Auto Cycle
    def start_auto_cycle(self):
        """Bắt đầu chu trình tự động PLC+Vision"""
        try:
            if not self.plc or not self.vision:
                self.lblRobotStatus.setText("Chưa kết nối Robot")
                return
        except:
            self.lblRobotStatus.setText("Chưa kết nối Robot")
            return 

        if not hasattr(self, 'vision_plc') or self.vision_plc is None:
            self.vision_plc = VisionPlcHandler(self.plc, self.vision)
            self.vision_plc.log.connect(self.log)

        self.vision_plc.run_cycle()
        self.auto_cycle_status()
        
    def auto_cycle_status(self):

        object_type = ""

        match self.plc.o_visionObjectType:
            
            case 0: 
                object_type = "Xanh tam giác"
            case 1: 
                object_type = "Đỏ vuông"
            case 2: 
                object_type = "Vàng tròn"

        match self.plc.i_autoCycleStatus:
            case 0:
                self.lblRobotStatus.setText("Chế độ tự động đang chờ...")
            case 1:
                self.lblRobotStatus.setText("Đang lấy gốc...")
            case 2:
                self.lblRobotStatus.setText("Đang di chuyển tới vị trí chờ")
            case 4:
                self.lblRobotStatus.setText(f"Đang phân loại... {object_type}")
            case 5:
                self.lblRobotStatus.setText(f"Đang phân loại... {object_type}")
            case 6:
                self.lblRobotStatus.setText(f"Đang phân loại... {object_type}")
            case 7:
                self.lblRobotStatus.setText(f"Đã nhận sản phẩm {object_type}")
            case 8:
                self.lblRobotStatus.setText(f"Đang phân loại")
            case 10:
                self.lblRobotStatus.setText(f"Hoàn thành phân loại!")

    #endregion
    
    def log(self, message: Any) -> None:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        print(log_message)
        try:
            self.pteLog.appendPlainText(str(log_message))
        except Exception:
            pass

