from typing import Any, Dict, Optional, Tuple

from com.plc_map import plc_map


class PlcController:
    def __init__(self, plc_factory=plc_map):
        self._plc_factory = plc_factory
        self.plc = None

    def connect(self, ip_address: str) -> Tuple[bool, str]:
        if self.is_connected():
            return False, "Already connected to PLC."

        try:
            self.plc = self._plc_factory(ip_address)
            return True, "Connected"
        except Exception as exc:
            self.plc = None
            return False, f"Connection failed: {exc}"

    def disconnect(self) -> None:
        if self.plc is not None:
            try:
                self.plc.client.disconnect()
            except Exception:
                pass
            finally:
                self.plc = None

    def is_connected(self) -> bool:
        if self.plc is None:
            return False

        try:
            return self.plc.client.get_connected() == 1
        except Exception:
            return False

    def read_positions(self) -> Dict[str, int]:
        if not self.is_connected():
            raise ConnectionError("PLC is not connected")

        self.plc.Read_data()
        return {
            "arm1": int(self.plc.i_deltaData1),
            "arm2": int(self.plc.i_deltaData2),
            "arm3": int(self.plc.i_deltaData3),
        }

    def write_outputs(self, outputs: Dict[str, Any]) -> None:
        if not self.is_connected():
            raise ConnectionError("PLC is not connected")

        for key, value in outputs.items():
            if hasattr(self.plc, key):
                setattr(self.plc, key, value)

        self.plc.Write_data()

    def write_teaching(self, values: Dict[str, Any]) -> None:
        self.write_outputs(values)

    def write_parameters(self, values: Dict[str, Any]) -> None:
        self.write_outputs(values)
