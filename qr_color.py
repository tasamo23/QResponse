
TYPES = ("SOLID", "LINEAR_GRADIENT", "RADIAL_GRADIENT")


BANDS = {"GRAYSCALE": "L", "BLACK_WHITE": "1", "RGB": "RGB"}


class Design:
    def __init__(self, type: str = "SOLID", bands: str = BANDS["BLACK_WHITE"], background: tuple[int, ...] = (0,), foreground: tuple[int, ...] = (1,), rotation: int = 0) -> None:
        self.type = type
        self.bands = bands

        # Not supported yet
        if type == "LINEAR_GRADIENT":
            pass
        elif type == "RADIAL_GRADIENT":
            pass

        self.background = background[0] if bands != BANDS["RGB"] else background
        self.foreground = foreground[0] if bands != BANDS["RGB"] else foreground
        self.rotation = rotation
        # self.backgroundImg = Image.new("RGB", (1, 1))
