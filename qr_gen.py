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
        self.size=self.computeSize(config.version)
        self.img = Image.new("L", (self.size,self.size))
        self.pixelArr = []
        self.pixelScale = 10
        self.color = {
            "type": (QRCode.Color_types[0], QRCode.Color_bands[0]),
            "foreground": 0,
            "background": 1,
        }
        self.config = config
        self.decorations = []

        self.pixelArr=[[] for x in range(0,self.size)]


    #White is 0

    Static_marker=Image.new("1",(7,7)).putdata([
        1,1,1,1,1,1,1,
        1,0,0,0,0,0,1,
        1,0,1,1,1,0,1,
        1,0,1,1,1,0,1,
        1,0,1,1,1,0,1,
        1,0,0,0,0,0,1,
        1,1,1,1,1,1,1
    ])

    Locator=Image.new("1",(5,5)).putdata([
        1,1,1,1,1,
        1,0,0,0,1,
        1,0,1,0,1,
        1,0,0,0,1,
        1,1,1,1,1,
    ])

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
        self.img.putdata(tuple(self.pixelArr))
        pass

    def insertStaticMarkers(self):
        # Insert the locator patterns and markers into the pixelarray

        # Static Markers
        Image.Image.paste(self.img,QRCode.Static_marker,(0,0))
        Image.Image.paste(self.img,QRCode.Static_marker,(self.img.size[0]-7,0))
        Image.Image.paste(self.img,QRCode.Static_marker,(0,self.img.size[1]-7))

        # Locators


        # Timing Patterns

        for i in range(8,self.img.size[0])

        # pass

    def scale(self):
        # Scale all pixels by the corresponding scale variable (except in SVG)
        self.img=PIL.ImageOps.scale(self.img,self.scale,PIL.Image.NEAREST)
        # pass

    def generate(self):
        self.insertMetaData()
        self.insertData()
        self.chooseAndApplyMask()
        self.generateImage()
        self.insertStaticMarkers()
        self.scale()
        self.loadImageWindow()

    def loadImageWindow(self):
        # Create a TKinter window and embed the QR Code as an image 
        self.img.show()
        # window = tk.Tk()
        # frame = toolkit.Frame(padding=10)
        # image = ImageTk.PhotoImage(self.img)
        # toolkit.Label(frame, image=image).pack()
        # frame.grid()
