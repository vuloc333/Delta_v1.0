import json
import os
from typing import Any, Optional

class ConfigManager:
    def __init__(self, file_path: str = "config.json") -> None:
        self.file_path: str = file_path

    def save(self, data: Any) -> bool:
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
            return True
        except Exception as e:
            print(f"Lỗi khi lưu file: {e}")
            return False

    def load(self) -> Optional[Any]:
        if not os.path.exists(self.file_path):
            return None
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Lỗi khi đọc file: {e}")
            return None