import json
import os

class ConfigManager:
    def __init__(self, file_path="config.json"):
        self.file_path = file_path

    def save(self, data):
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
            return True
        except Exception as e:
            print(f"Lỗi khi lưu file: {e}")
            return False

    def load(self):

        if not os.path.exists(self.file_path):
            return None
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Lỗi khi đọc file: {e}")
            return None