from qr_gen import QRCode
import json


class QRConfig:

    Err_corr_lvls = {
        "LOW": {"percentage": 7, "bits": (0, 1)},
        "MEDIUM": {"percentage": 15, "bits": (0, 0)},
        "QUARTERLY": {"percentage": 25, "bits": (1, 1)},
        "HIGH": {"percentage": 30, "bits": (1, 0)}
    }

    Data_types = ("URL", "PLAINTEXT", "WIFI", "BINARY", "COORDINATES")

    Mask_patterns = [
        lambda x, y:(y + x) % 2 == 0,
        lambda x, y:y % 2 == 0,
        lambda x, y:x % 3 == 0,
        lambda x, y:(y + x) % 3 == 0,
        lambda x, y:(y // 2 + x // 3) % 2 == 0,
        lambda x, y:(y * x) % 2 + (y * x) % 3 == 0,
        lambda x, y:((y * x) % 3 + y * x) % 2 == 0,
        lambda x, y:((y * x) % 3 + y + x) % 2 == 0,
    ]

    def __init__(self, version):
        self.version = version
        self.data = {
            "type": QRConfig.Data_types[1],
            "value": ""
        }
        self.err_corr_mode = QRConfig.Err_corr_lvls["LOW"]
        self.mask_pattern = 0  # Index of mask pattern
        self.code = QRCode(self)

    def exportToJSON(self):
        pass
