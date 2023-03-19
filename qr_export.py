import json
from PIL import Image


class Exporter:

    def __init__(self, code) -> None:
        pass

    # JSON
    def asJSON(self):
        pass  # Return the file

    # JPEG
    def asJPEG(self) -> None:
        pass  # Return the file

    # PNG
    def asPNG(self) -> None:
        pass  # Return the file

    # SVG
    def asSVG(self) -> None:
        pass  # Return the file

    # Console
    def toConsole(self) -> tuple[str]:
        # Print as colorcoded string
        return ("",)

    # Text
    def asString(self) -> str:
        # Return as series of ASCII box characters
        return ""

    # File
    def saveFile(self, file) -> None:
        pass

    # Clipboard
    def copyToClipboard(self, exportObj):
        pass
