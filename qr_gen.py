import qr_ecc as ecc
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk as toolkit


class QRCode:

    Color_types = (
        "SOLID", "GRADIENT"
    )

    Color_bands = (
        ("GRAYSCALE", "L"),
        ("BLACKWHITE", "1"),
        ("RGB", "RGB")
    )

    def computeSize(self, version):
        return (version - 1) * 4 + 21

    def __init__(self, config):
        self.img = Image.new("L", (21, 21))
        self.pixelArr = []
        self.pixelScale = 10
        self.color = {
            "type": (QRCode.Color_types[0], QRCode.Color_bands[0]),
            "foreground": "",
            "background": "",
        }
        self.config = config
        self.decorations = []

    def insertStaticMarkers(self):
        # Insert the locator patterns and markers into the pixelarray

        pass

    def insertMetaData(self):
        # Insert version, ECC mode and pattern data into the pixelarray
        pass

    def insertData(self):
        # Insert the message and corresponding ECC data into the pixelarray
        pass

    def chooseAndApplyMask(self):
        # Let the program choose the preferred mask by evaluating group size
        # and avoidung misleading patterns (that for example look like locators)
        pass

    def generateImage(self):
        # Translate the pixelarray into an image
        pass

    def scale(self):
        # Scale all pixels by the corresponding scale variable (not in SVG)
        pass

    def generate(self):
        self.insertStaticMarkers()
        self.insertMetaData()
        self.insertData()
        self.chooseAndApplyMask()
        self.generateImage()
        self.scale()
        self.loadImageWindow()

    def loadImageWindow(self):
        window = tk.Tk()
        frame = toolkit.Frame(padding=10)
        image = ImageTk.PhotoImage(self.img)
        toolkit.Label(frame, image=image).pack()
        frame.grid()
