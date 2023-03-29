import math
from time import sleep
import qr_ecc as ecc
import tkinter as tk
import sys
import string
import qr_color as Color
import tkinter.filedialog as tkFd
import interaction as Input
from typing import Tuple,List
from tkinter import ttk as toolkit
from PIL import Image, ImageOps, ImageChops, ImageTk

# If -noDelay is passed as an argument, the program will run without any delays
delay = 0 if "-noDelay" in sys.argv else 0.5


class QRCode:

    def __init__(self):

        # Data the code will be carrying
        self.dataString = self.promptDataString()

        # The data that will be encoded in the code as a byte string
        self.dataBytes = toByteString(self.dataString)

        # The version of the QR code, which determines the size of the code, and the redundancy of the code
        self.version, self.eccMode = self.determineVAndEC()

        # QR Code size in modules (= squares that represent the encoded data in bits or display other information)
        self.size = (self.version - 1) * 4 + 21

        # A scale for the amount of pixels a module has
        self.pixelScale = Input.pixel_size_askSize(delay, self.size)

        # The pattern to use for masking out the data
        self.maskNum = 1

        # The image that will be displayed
        self.img = Image.new("RGB", (2, 2), (255, 0, 255))

        # A black and white representation of the image, does not get scaled
        self.imgBW = Image.new("1", (self.size, self.size), 1)

        # A mask image of all exclusion zones, which are areas that will not be used for data
        self.reservedSpots = self.setReserved()

        # Codeword byte blocks holding data and ecc
        self.finalMessage = [0]

        # Design of the code, including background color, foreground color, rotation, etc.
        self.design = Input.design_askDesign(delay)

        print("\n\nGreat, all customization done!\nWe are ready to generate the code!\n\n")

        input("Press enter to continue...")

        # Start generating the QR code
        self.generate()

        # Export the code
        self.export()

    def promptDataString(self) -> str:

        format = Input.data_askFormat(delay)

        # Text or URL
        if format in (0, 1):
            return Input.data_askPlainText(delay, format)

        # Mail
        elif format == 2:
            return Input.data_askMail(delay)

        # SMS
        elif format == 3:
            return Input.data_askSMS(delay)

        return "DEFAULT"

    def determineVAndEC(self) -> Tuple[int, int]:
        # Determine the version and error correction level of the code based on user selection
        options = []

        # Iterative search for the smallest version that can hold the data with the corresponding error correction level
        for mode in range(4):
            for v in range(1, 41):
                # The capacity of the code, including data and ecc, is the number of bytes it can (and should) handle. Very complex formula
                # Formula adapted from https://en.m.wikiversity.org/wiki/Reed%E2%80%93Solomon_codes_for_coders/Additional_information#Symbol_size
                totalCodewordCapacity = int(1/8 * (16 * ((v ** 2) + (8 * v) + 4) - 25 * (((1 if v >= 2 else 0)+(v//7)) ** 2) - (1 if v >= 7 else 0) * (36 + 40 * (v//7))))

                # The number of error correction codewords (bytes)
                ecCodewords = ecc.EC_CODEWORDS_TABLE[v-1][mode]

                # The encoding type of the data
                dataType = testEncoding(self.dataString)

                # The accumulator is the amount the length indicator grows in length depending on code version and encoding
                accumulator = (2 if dataType != "BYTE" else 8) if (v <= 26 and v >= 10) else (4 if dataType != "BYTE" else 8) if v > 26 else 0

                # A length indicator for the reader to now the length of encoded data
                indicatorLength = (10, 9, 8, 8)[ENC_LIST.index(dataType)]+accumulator

                # The capacity for data codewords
                codewordsLeft = totalCodewordCapacity - ecCodewords

                # If we find a version that can hold the data and error correction, add it to the options list
                if codewordsLeft*8 >= len(self.dataBytes)+4+indicatorLength:
                    options.append((v, mode))
                    break

        # Return user selection
        return Input.v_ec_askSize(delay, options)

    def setReserved(self) -> Image.Image:
        # Initialize the image to be returned
        rImg = Image.new("1", (self.size, self.size), 255)

        # Create blank images to paste over the finder and alignment patterns
        finder_blank_nw = Image.new("1", (9, 9), 0)
        finder_blank_no = Image.new("1", (8, 9), 0)
        finder_blank_sw = Image.new("1", (9, 8), 0)
        alignment_blank = Image.new("1", (5, 5), 0)
        timer_horiz_blank = Image.new("1", (self.size-14, 1), 0)
        timer_vert_blank = Image.new("1", (1, self.size-14), 0)

        # version information reserving v>=7
        if self.version >= 7:
            version_blank = Image.new("1", (3, 6), 0)
            rImg.paste(version_blank, (self.size-11, 0))
            version_blank = Image.new("1", (6, 3), 0)
            rImg.paste(version_blank, (0, self.size-11))

        # Blank out reserved spots for finders so they don't get masked
        rImg.paste(finder_blank_nw, None)
        rImg.paste(finder_blank_no, (self.size-8, 0))
        rImg.paste(finder_blank_sw, (0, self.size-8))

        # Blank out reserved spots for aligment patterns so they don't get masked
        for pos in self.getAlignmentMarkers():
            rImg.paste(alignment_blank, (pos[0]-2, pos[1]-2))

        # Blank out timing pattern location
        rImg.paste(timer_horiz_blank, (7, 6))
        rImg.paste(timer_vert_blank, (6, 7))

        return rImg.convert("1")

    def getAlignmentMarkers(self) -> List[Tuple[int, int]]:

        # Version 1 has no alignment markers
        if self.version == 1:
            return []

        # Alternative: Steps to compute the alignment markers (opposed to using the LUT at the bottom)
        # first_item = 6
        # last_item = (self.size - 1) - 6
        # dist = last_item - first_item
        # number = math.ceil(dist/28)

        # if self.version == 32:
        #     intervals = 26
        # else:
        #     intervals = math.ceil(dist/number)
        #     intervals += (intervals % 2)

        # potLocs = [last_item]
        # for m in (number-1) * [intervals]:
        #     potLocs.append(potLocs[-1] - m)
        # potLocs.append(first_item)

        # Potential locations of alignment markers

        potLocs = ALIGNMENT_MARKERS[self.version-2]

        # List initialization
        locations = []

        for x in potLocs:
            for y in potLocs:
                # Test for collision with Finder patterns and image borders
                collidesWithUpperLeft = x-2 <= 7 and y-2 <= 7
                collidesWithBottomLeft = x+2 >= self.size-8 and y-2 <= 7
                collidesWithUpperRight = x-2 <= 7 and y+2 >= self.size-8
                isInBounds = x+2 <= self.size-1 and y+2 <= self.size-1
                # Only return non-colliding locations
                if not (collidesWithUpperLeft or collidesWithBottomLeft or collidesWithUpperRight) and isInBounds:
                    locations.append((x, y))
        return locations

    def generateData(self):

        # Variable redeclaration for shorter code and less self calls
        dataType = testEncoding(self.dataString)
        version = self.version

        # This is the data represented and encoded into a binary bit string
        encodedData = self.dataBytes

        # The capacity of the code, including data and ecc, is the number of bytes it can (and should) handle. Very complex formula
        # Formula adapted from https://en.m.wikiversity.org/wiki/Reed%E2%80%93Solomon_codes_for_coders/Additional_information#Symbol_size
        v = version
        totalCodewordCapacity = int(1/8 * (16 * ((v ** 2) + (8 * v) + 4) - 25 * (((1 if v >= 2 else 0)+(v//7)) ** 2) - (1 if v >= 7 else 0) * (36 + 40 * (v//7))))

        # The number of error correction codewords is the number of bytes that are used to correct errors
        ecCodewords = ecc.EC_CODEWORDS_TABLE[version-1][self.eccMode]

        # The number of data codewords that are used to store data
        dataCapacity = totalCodewordCapacity-ecCodewords

        # A mode indicator is a 4 bit string that tells the reader which encoding following data uses
        modeIndicator = ("0001", "0010", "0100", "1000")[ENC_LIST.index(dataType)]

        # The accumulator is the amount the indicator grows in length depending on code version and encoding
        accumulator = (2 if dataType != "BYTE" else 8) if (version <= 26 and version >= 10) else (4 if dataType != "BYTE" else 8) if version > 26 else 0
        indicatorLength = (10, 9, 8, 8)[ENC_LIST.index(dataType)]+accumulator

        # A count indicator is a binary bit string that tells the scanner how many characters there are
        countIndicator = intToByteString(len(self.dataString)).zfill(indicatorLength)

        # The terminator is the padding that at most is 4 0s long and tries to fill up remaining space
        terminator = "0" * (4 if dataCapacity*8-len(encodedData)-indicatorLength-4 >= 4 else dataCapacity*8-len(encodedData)-indicatorLength-4)

        # The filler is used to make the length of the data a multiple of 8
        filler = "0" * ((8-(len(modeIndicator+countIndicator+encodedData+terminator) % 8)) % 8)

        remainingSpace = dataCapacity*8-len(modeIndicator+countIndicator+encodedData+terminator+filler)

        # The padding fills in the remaining space of the code and has to be constructed from a specific sequence
        pad = ("1110110000010001" * ((remainingSpace//16)+1))[:remainingSpace]
        # TODO unfinished

        # This is the byte string that will later be broken up and put into the code
        seperatedByteString = modeIndicator+"\n"+countIndicator+"\n"+encodedData+"\n"+terminator+"\n"+filler+"\n"+pad
        byteString = seperatedByteString.replace("\n", "").replace("_", "")

        # Split the data into codeword blocks (initialize blockCount)
        blockCount = 1

        # Get the number of blocks to seperate the data into (set blockCount)
        for num in range(1, ecCodewords//2):
            isWholeDisivible = (ecCodewords % num == 0)
            isSmallerThan30 = ecCodewords//num <= 30
            evenOddMatch = (dataCapacity+math.ceil(ecCodewords/num)) % 2 == 0

            # print(num, isWholeDisivible, isSmallerThan30, evenOddMatch)
            if isWholeDisivible and isSmallerThan30 and evenOddMatch and num != 3:
                blockCount = num
                break

        # These are essentially the QR Code groups.
        # The only difference is that one holds one more codeword than the other
        minorBlockCount = blockCount-(dataCapacity % blockCount)
        majorBlockCount = dataCapacity % blockCount

        # Amount of codewords for each block in group
        minorBlockCodewords = dataCapacity//blockCount
        majorBlockCodewords = minorBlockCodewords+1

        # Calculate error correction codewords (bytes) per block
        ecCWPerBlock = ecCodewords//blockCount

        # Throw error if above calculation is wrong
        assert majorBlockCount*majorBlockCodewords+minorBlockCount*minorBlockCodewords == dataCapacity

        # Initialize block list
        byteBlocks = []

        # For every block, which has one less codeword than the major blocks
        for i in range(minorBlockCount):
            # Initialize block
            block = []
            # For every codeword in the block
            for j in range(minorBlockCodewords):
                pos = j*8+i*minorBlockCodewords*8
                block.append(byteString[pos:pos+8])

            # Convert the block to a list of integers
            intBlock = [int(x, 2) for x in block]

            # Append the block to the list of blocks, the error correction codewords already appended
            byteBlocks.append(ecc.rs_encode_msg(intBlock, ecCWPerBlock))

        # For every block, which has one more codeword than the minor blocks
        for i in range(majorBlockCount):
            # Initialize block
            block = []

            # For every codeword in the block
            for j in range(majorBlockCodewords):
                pos = j*8+i*majorBlockCodewords*8+minorBlockCodewords*minorBlockCount*8
                block.append(byteString[pos:pos+8])

            # Convert the block to a list of integers
            intBlock = [int(x, 2) for x in block]

            # Append the block to the list of blocks, the error correction codewords already appended
            byteBlocks.append(ecc.rs_encode_msg(intBlock, ecCWPerBlock))

        # Split the blocks into data and error correction codewords
        dataBlocks = [block[:(-ecCWPerBlock)] for block in byteBlocks]
        eccBlocks = [block[(-ecCWPerBlock):] for block in byteBlocks]

        # Interleave block data (initialize list)
        messageList = []

        # Insert every first codeword of every block, then the second and continue until all codewords are inserted
        for i in range(majorBlockCodewords):
            for block in dataBlocks:
                # Prevent out of bounds errors
                if i < len(block):
                    messageList.append(block[i])

        # Same thing with the error correction codewords
        for i in range(ecCWPerBlock):
            for block in eccBlocks:
                # Prevent out of bounds errors
                if i < len(block):
                    messageList.append(block[i])

        # Save into instance variable
        self.finalMessage = messageList

    def insertData(self):
        # Get pixel sequence of current mask
        flatSeq = [0]*(self.size*self.size)

        # Get pixel sequence of spots to avoid (as they are reserved for later inserts)
        seqToAvoid = list(self.reservedSpots.getdata())

        # Change the current pixel position to the next one,
        # accommodating for the mask and vertical timing pattern
        def moveBit(pos) -> Tuple[int, int]:
            rPos = pos
            lim = 1000

            while (seqToAvoid[rPos[0]+rPos[1]*self.size] == 0 or rPos == pos) and lim > 0:
                lim -= 1
                # if rPos[0] == 0 and rPos[1] == 0:
                #     print("0 0")

                upMode = (rPos[0]-(1 if rPos[0] > 6 else 0)) % 4 > 1
                diagMode = (rPos[0]-(1 if rPos[0] > 6 else 0)) % 2 == 0
                wrap = rPos[1]-(1 if upMode else -1)*(1 if diagMode else 0) < 0 or rPos[1]-(1 if upMode else -1)*(1 if diagMode else 0) >= self.size
                # print(rPos, wrap, upMode, diagMode)
                if wrap:
                    rPos = (rPos[0] - 1, rPos[1])
                else:
                    rPos = (rPos[0]+(1 if diagMode else -1), rPos[1]-(1 if upMode else -1)*(1 if diagMode else 0))
            return rPos

        # Start at the bottom right corner
        curPos = (self.size-1, self.size-1)

        # Insert the data codewords into the image, going around the already reserved spots
        for codeword in self.finalMessage:
            byteString = intToByteString(codeword).zfill(8)
            for bit in byteString:
                flatSeq[curPos[0]+curPos[1]*self.size] = (255 if bit == "0" else 0)
                curPos = moveBit(curPos)

        # Create a new image from the pixel sequence
        img = Image.new("L", (self.size, self.size))
        img.putdata(flatSeq)

        # Reflect on instance variable
        self.imgBW = ImageChops.logical_xor(self.imgBW, img.convert("1"))

    def insertMarkers(self):
        # Insert the finders and alignment patterns into the image.
        # These help the QR code reader to orient themselves and properly read the code.

        # An image of an finder marker later to be inserted into the image (B/W)
        Finder_marker = Image.new("1", (7, 7))
        Finder_marker.putdata([
            0, 0, 0, 0, 0, 0, 0,
            0, 1, 1, 1, 1, 1, 0,
            0, 1, 0, 0, 0, 1, 0,
            0, 1, 0, 0, 0, 1, 0,
            0, 1, 0, 0, 0, 1, 0,
            0, 1, 1, 1, 1, 1, 0,
            0, 0, 0, 0, 0, 0, 0,
        ])

        # An image of an alignment marker later to be inserted into the image (B/W)
        Aligment_marker = Image.new("1", (5, 5))
        Aligment_marker.putdata([
            0, 0, 0, 0, 0,
            0, 1, 1, 1, 0,
            0, 1, 0, 1, 0,
            0, 1, 1, 1, 0,
            0, 0, 0, 0, 0,
        ])

        # Insert all Finders
        self.imgBW.paste(Finder_marker, None)
        self.imgBW.paste(Finder_marker, (self.size-7, 0))
        self.imgBW.paste(Finder_marker, (0, self.size-7))

        # Insert all alignment patterns, first generating all locations where they should be
        for pos in self.getAlignmentMarkers():
            self.imgBW.paste(Aligment_marker, (pos[0]-2, pos[1]-2))

        # Timing Patterns (vertical and horizontal)
        for i in range(8, self.size-7, 2):
            self.imgBW.putpixel((6, i), 0)
        for i in range(8, self.size-7, 2):
            self.imgBW.putpixel((i, 6), 0)

    def chooseAndApplyMask(self):
        # Let the program choose the optimal mask by evaluating group size
        # and avoidung misleading patterns (that for example look like alignment patterns)

        # Set the current penalty to infinity, so any consecutive penalty will be lower
        curPenalty = math.inf

        # The image with the lowest penalty will be saved here
        imageToBe = Image.new("L", (self.size, self.size))

        # Iterate over all masks
        for mask in MASK_PATTERNS:

            # Reset the penalty and the image
            penalty = 0
            imgBW = self.imgBW

            # Construct the image by inserting the metadata (still not masked)
            self.insertMetaData(imgBW, MASK_PATTERNS.index(mask))

            # Initialize mask sequence
            maskSeq = [255]*(imgBW.width*imgBW.height)

            # Construct the mask
            for x in range(imgBW.width):
                for y in range(imgBW.height):
                    if mask(x, y):
                        maskSeq[x+y*imgBW.height] = 0

            # Create a mask image with the mask sequence
            imgMask = Image.new("L", (imgBW.width, imgBW.height))
            imgMask.putdata(maskSeq)

            # Exclude the reserved spots with AND operation
            imgMask = ImageChops.logical_and(imgMask.convert("1"), self.reservedSpots)

            # Apply mask with XOR operation
            imgBW = ImageChops.logical_xor(self.imgBW, imgMask)
            seq = list(imgBW.getdata())

            # Row by row and column by column (applying penalty system)
            for x in range(imgBW.width):
                # Streak column black/white
                streakCB, streakCW = 0, 0

                # Streak row black/white
                streakRB, streakRW = 0, 0

                # Column/row binary string
                rowString = ""
                columnString = ""
                for y in range(imgBW.height):

                    columnString += str(seq[x+y*self.size])
                    # Column streak
                    if seq[x+y*self.size] == 0:
                        streakCB += 1
                        penalty += (3+streakCW-5) if streakCW >= 5 else 0
                        streakCW = 0
                    else:
                        streakCW += 1
                        penalty += (3+streakCB-5) if streakCB >= 5 else 0
                        streakCB = 0

                    rowString += str(seq[y+x*self.size])
                    # Row streak
                    if seq[y+x*self.size] == 0:
                        streakRB += 1
                        penalty += (3+streakRW-5) if streakRW >= 5 else 0
                        streakRW = 0
                    else:
                        streakRW += 1
                        penalty += (3+streakRB-5) if streakRB >= 5 else 0
                        streakRB = 0

                    # Penalties for grouped modules (2x2)
                    if x < self.size-1 and y < self.size-1:
                        if seq[x+y*self.size]+seq[(x+1)+y*self.size]+seq[x+(y+1)*self.size]+seq[(x+1)+(y+1)*self.size] in (0, 4):
                            penalty += 3

                # Penalties for sections looking like finders
                penalty += (rowString.count("01000101111")+rowString.count("11110100010"))*40
                penalty += (columnString.count("01000101111")+columnString.count("11110100010"))*40

            # Penalty for potentially uneven dark/light ratio
            darkPercentage = seq.count(0)/len(seq)*100
            prevMultipleFive = darkPercentage-darkPercentage % 5
            nextMultipleFive = prevMultipleFive+5
            penalty += min(abs((prevMultipleFive-50)//5), abs((nextMultipleFive-50)//5))*10

            # Override the proposed image if the penalty is lower and set instance variable accordingly
            if curPenalty > penalty:
                imageToBe = imgBW
                curPenalty = penalty
                self.maskNum = MASK_PATTERNS.index(mask)

        # Reflect the chosen mask (and the image resulting from it) in the instance variable
        self.imgBW = imageToBe

    def insertMetaData(self, mask: Image.Image, maskNum: int):
        # Insert ECC mode and pattern data into the image for the scanner to identify

        # Construct the format string (not redundant yet)
        ecBits = ["01", "00", "11", "10"][self.eccMode]
        maskBit = intToByteString(maskNum).zfill(3)
        formatString = (ecBits+maskBit)

        # Generate ECC for format string
        bitString = formatString[::-1].zfill(15)[::-1].lstrip("0").zfill(10)
        eccFBit = int(bitString, 2)
        gen = int(intToByteString(0b10100110111)[::-1].zfill(len(bitString))[::-1], 2)
        eccFBit = eccFBit ^ gen
        while (len(intToByteString(eccFBit)) > 10):
            eccFBit = eccFBit ^ gen
            gen = int(intToByteString(0b10100110111)[::-1].zfill(len(intToByteString(eccFBit).zfill(10)))[::-1], 2)

        # Construct the final format string by adding original string and ECC string
        finalFormatString = formatString+intToByteString(eccFBit).zfill(10)

        # XOR the result one last time
        finalFormatString = intToByteString(int(finalFormatString, 2) ^ 0b101010000010010).zfill(15)

        # Insert format information
        for i1 in range(7):
            i2 = i1+7
            mask.putpixel((i1 + (1 if i1 > 5 else 0), 8), 0 if finalFormatString[i1] == "1" else 1)
            mask.putpixel((8, self.size-1-i1), 0 if finalFormatString[i1] == "1" else 1)
            mask.putpixel((self.size+i1-8, 8), 0 if finalFormatString[i2] == "1" else 1)
            mask.putpixel((8, 8-i1-(1 if i1 > 1 else 0)), 0 if finalFormatString[i2] == "1" else 1)

        # Insert last two pixels of format information (was not processed as the length is odd)
        mask.putpixel((self.size-1, 8), 0 if finalFormatString[14] == "1" else 1)
        mask.putpixel((8, 0), 0 if finalFormatString[14] == "1" else 1)

        # Insert Dark module (always in the same place)
        mask.putpixel((8, self.size-8,), 0,)

        # Generate and insert version information >=7
        if self.version >= 7:
            # Bose–Chaudhuri–Hocquenghem error correction code generation
            # The steps are similar to above, but the generator polynomial and targeted length is different
            bitString = intToByteString(self.version).zfill(6)[::-1].zfill(18)[::-1].lstrip("0").zfill(1)
            eccVBit = int(bitString, 2)
            gen = int(intToByteString(0b1111100100101)[::-1].zfill(len(bitString))[::-1], 2)
            eccVBit = eccVBit ^ gen

            # Magic (math), see above
            while (len(intToByteString(eccVBit)) > 12):
                gen = int(intToByteString(0b1111100100101)[::-1].zfill(len(intToByteString(eccVBit)))[::-1], 2)
                eccVBit = eccVBit ^ gen
            versionBitString = intToByteString(self.version).zfill(6)+intToByteString(eccVBit).zfill(12)

            # Insert version information
            for i in range(18):
                mask.putpixel((i // 3, self.size-11+i % 3), 0 if versionBitString[17-i] == "1" else 1)
                mask.putpixel((self.size-11+i % 3, i // 3), 0 if versionBitString[17-i] == "1" else 1)

    def scaleAndPad(self):
        # Scale all pixels by the corresponding scale variable (except in SVG)
        paddedMask = Image.new("1", ((self.size+8), (self.size+8)), 255)

        # Add a four-module wide padding
        paddedMask.paste(self.imgBW, (4, 4))

        # Reflect the scaled image in the instance variable
        self.imgBW = ImageOps.scale(paddedMask, self.pixelScale, Image.Resampling.NEAREST)

    def color(self):
        # Apply the foreground and background color to the image

        fgColorImg = Image.new(Color.BANDS[self.design.bands], ((self.size+8)*self.pixelScale, (self.size+8)*self.pixelScale), self.design.foreground)
        bgColorImg = Image.new(Color.BANDS[self.design.bands], ((self.size+8)*self.pixelScale, (self.size+8)*self.pixelScale), self.design.background)

        # Added the foreground and background color together, using the B/W data as a mask
        self.img = Image.composite(bgColorImg, fgColorImg, self.imgBW)

    def rotate(self):
        # Rotate the image by the specified amount
        self.img = self.img.rotate(self.design.rotation)

    def loadImageWindow(self):
        # Create a TKinter window
        window = tk.Tk()
        window.title("QResponse generated code")

        # Embed the QR Code as an image
        image = ImageTk.PhotoImage(self.img.convert("RGB"))
        label = toolkit.Label(master=window, image=image).pack()

        # Place it in the center and focus
        window.eval('tk::PlaceWindow . center')
        window.focus()

        window.mainloop()

    def loadToConsole(self):
        # An algorithm that creates a black-white one-pixel-scale flat image sequence
        smallImg = ImageOps.scale(self.imgBW, 1/self.pixelScale, Image.Resampling.NEAREST)
        flatSeq = list(smallImg.getdata())

        # Approach when using the IDLE launcher to render QR codes into the console
        try:
            # Only works in the IDLE launcher
            shell = sys.stdout.shell  # type: ignore

            # Iterative module rendering using double spaces and IDLE-specific formatting
            for mod in range(len(flatSeq)):
                isEnd = (mod+1) % smallImg.width == 0
                shell.write("  ", "hit" if flatSeq[mod] == 0 else "")
                if isEnd:
                    print("", end="\n ")

        # Approach when using any other modern terminal to render the code
        except AttributeError:
            # Colored strings (double spaces) which are either black or white (empty or occupied) using unicode
            modString = "\033[30;40m  "
            emptyModString = "\033[47m  "

            # Line break
            print("", end="\n ")

            # Iterative module rendering using unicode color formats
            for mod in range(len(flatSeq)):
                isEnd = (mod+1) % smallImg.width == 0
                print(modString if flatSeq[mod] == 0 else emptyModString, end="\033[m\n " if isEnd else "")

            sleep(delay)

            # Reset color formatting (normally continuous in the terminal and is quite annoying)
            print("\033[m")

    # Main function to start the generation process calling all subprocesses in order
    def generate(self):
        sleep(delay)

        print("Generating data...")
        self.generateData()
        sleep(delay)

        print("Inserting data...")
        self.insertData()
        sleep(delay)

        print("Inserting markers...")
        self.insertMarkers()
        sleep(delay)

        print("Applying mask...")
        self.chooseAndApplyMask()
        sleep(delay)

        print("Scaling...")
        self.scaleAndPad()
        sleep(delay)

        print("Coloring...")
        self.color()
        sleep(delay)

        print("Rotating...")
        self.rotate()
        sleep(delay)

        print("...Done!")
        sleep(delay)

    def export(self):
        # Infinite loop to allow multiple exports (intentional, as it can be broken by the user)
        while True:
            # User selection
            choice = Input.export_askChoice(delay)

            # Export to console
            if (choice == 0):
                self.loadToConsole()

            # Open image window
            elif (choice == 1):
                self.loadImageWindow()

            # Export as JPG
            elif (choice == 2):

                root = tk.Tk()
                root.withdraw()
                root.geometry('0x0+0+0')
                root.focus()

                fileName = tkFd.asksaveasfilename(filetypes=[("JPEG Image", "*.jpg,*.jpeg")], parent=root)
                root.destroy()
                if (fileName != ""):
                    if fileName[:-4] != ".jpg" or fileName[:-5] != ".jpeg":
                        fileName += ".jpg"

                    self.img.convert("RGB").save(fileName, "JPEG", quality=95)

            # Export as PNG
            elif (choice == 3):

                root = tk.Tk()
                root.withdraw()
                root.geometry('0x0+0+0')
                root.focus()

                fileName = tkFd.asksaveasfilename(filetypes=[("PNG Image", "*.png")], parent=root)
                root.destroy()
                if (fileName != ""):
                    if fileName[:-4] != ".png":
                        fileName += ".png"
                    self.img.convert("RGB").save(fileName, "PNG", compress_lvl=9)

            # Break the loop and quit program
            elif (choice == 4):
                break

# Standard constants and functions, which do not belong to the QR Code class


# All masks with which code data can be masked
# Parameters are the x and y coordinates of a module, to return a boolean of if the module will be flipped
MASK_PATTERNS = [
    lambda x, y:(y + x) % 2 == 0,
    lambda x, y:y % 2 == 0,
    lambda x, y:x % 3 == 0,
    lambda x, y:(y + x) % 3 == 0,
    lambda x, y:(y // 2 + x // 3) % 2 == 0,
    lambda x, y:(y * x) % 2 + (y * x) % 3 == 0,
    lambda x, y:((y * x) % 3 + y * x) % 2 == 0,
    lambda x, y:((y * x) % 3 + y + x) % 2 == 0,
]


# A method to convert a string to a byte string
def toByteString(string: str) -> str:
    encoding = testEncoding(string)
    returnList = []
    if encoding == "NUMERIC":
        # Pair every three characters together and output as binary
        for subStrI in range(0, len(string)+(((len(string) % 3)*2) % 3), 3):

            # Substring to process (normally 3 characters long)
            num = int(string[subStrI: subStrI+3])

            # Add binary representation to the list, saturating any bitstrings to length 10/7/4 by adding zeros
            returnList.append(intToByteString(num).zfill(len(str(num))*3+1))

    elif encoding == "ALPHANUMERIC":
        # Shortened encoding list for alphanumerics
        encs = ENCODINGS["ALPHANUMERIC"]

        # Get character pairs, process them, handle single characters differently
        for subStrI in range(0, len(string) + (len(string) % 2), 2):

            # Tests if last character is standing alone
            odd = len(string) == subStrI+1

            # Integer to convert to bytes later
            num = encs.index(string[subStrI])*(1 if odd else 45)+(0 if odd else encs.index(string[subStrI+1]))

            # Add binary representation to the list, saturating any bitstrings to length 11/6 by adding zeros
            returnList.append(intToByteString(num).zfill(6 if odd else 11))

    elif encoding == "BYTE":
        # Every character gets examined seperately
        for char in string:

            # Adds the byte (8-bit) binary representation of the character to the list
            returnList.append(intToByteString(int.from_bytes(char.encode("iso_8859_1"))).zfill(8))

    elif encoding == "KANJI":
        # Every character gets examined seperately
        for char in string:

            # Get the character value or index in the kanji (ShiftJIS) encoding
            index = int.from_bytes(char.encode("shiftjis"))

            # Tests on which of the two JIS ranges the character is, then converts it to a double byte string
            doubleByte = intToByteString(index-(0x8140 if index <= 0x9FFC else 0xC140)).zfill(16)

            # Normalizes values and adds the two bytes together
            num = int(doubleByte[0: 8], 2)*0xC0+int(doubleByte[8: 16], 2)

            # Add the 13-bit binary string representing the character to the list
            returnList.append(intToByteString(num).zfill(13))

    # Return the list as a continuous string
    return "".join(returnList)


# All encodings, which are bound to a string containing all characters that encoding style can handle
ENCODINGS = {
    "NUMERIC": "".join(str(item) for item in range(10)),
    "ALPHANUMERIC": str("".join(str(item) for item in range(10)))+string.ascii_uppercase+"".join([" ", "$", "%", "*", "+", "-", ".", "/", ":"]),
    "BYTE": bytes(range(256)).decode("iso_8859_1"),
    "KANJI": ""
}

# Adding all the characters for the kanji encoding
for j1 in range(32, 127):
    ENCODINGS["KANJI"] += bytes.fromhex(hex(j1)[2:]).decode("shiftjis")
    for j2 in range(33, 127):
        s1 = (j1+1)//2+112 if j1 <= 94 else (j1+1)//2+176
        s2 = j2+31 + j2//96 if j1 % 2 == 1 else j2+126
        try:
            ENCODINGS["KANJI"] += (bytes.fromhex(hex(s1)[2:])+bytes.fromhex(hex(s2)[2:])).decode("shift_jis")
        except UnicodeDecodeError:
            continue

# List of all encoding names
ENC_LIST = [key for key in ENCODINGS]


# A method to determine the encoding of a string (tries to be as efficient as possible)
def testEncoding(string: str) -> str:
    returnIndex = 0
    for char in string:
        if char in ENCODINGS["NUMERIC"]:
            returnIndex = max(0, returnIndex)
        elif char in ENCODINGS["ALPHANUMERIC"]:
            returnIndex = max(1, returnIndex)
        elif char in ENCODINGS["BYTE"]:
            returnIndex = max(2, returnIndex)
        elif char in ENCODINGS["KANJI"]:
            returnIndex = max(3, returnIndex)
        else:
            raise ValueError("Character "+char+" not supported. Processing failed. \n(Character was not found in any encoding this program supports.)")
    return ENC_LIST[returnIndex]


# A method to convert an integer to a binary string
def intToByteString(input: int) -> str:
    return '{:b}'.format(input)


# A LUT (lookup table) with the potential coordinates of all alignment markers (rows and columns alike)
ALIGNMENT_MARKERS = [
    (18,),  # Version 2
    (22,),  # Version 3
    (26,),  # Version 4
    (30,),  # Version 5
    (34,),  # Version 6
    (6, 22, 38),  # Version 7
    (6, 24, 42),  # Version 8
    (6, 26, 46),  # Version 9
    (6, 28, 50),  # Version 10
    (6, 30, 54),  # Version 11
    (6, 32, 58),  # Version 12
    (6, 34, 62),  # Version 13
    (6, 26, 46, 66),  # Version 14
    (6, 26, 48, 70),  # Version 15
    (6, 26, 50, 74),  # Version 16
    (6, 30, 54, 78),  # Version 17
    (6, 30, 56, 82),  # Version 18
    (6, 30, 58, 86),  # Version 19
    (6, 34, 62, 90),  # Version 20
    (6, 28, 50, 72, 94),  # Version 21
    (6, 26, 50, 74, 98),  # Version 22
    (6, 30, 54, 78, 102),  # Version 23
    (6, 28, 54, 80, 106),  # Version 24
    (6, 32, 58, 84, 110),  # Version 25
    (6, 30, 58, 86, 114),  # Version 26
    (6, 34, 62, 90, 118),  # Version 27
    (6, 26, 50, 74, 98, 122),  # Version 28
    (6, 30, 54, 78, 102, 126),  # Version 29
    (6, 26, 52, 78, 104, 130),  # Version 30
    (6, 30, 56, 82, 108, 134),  # Version 31
    (6, 34, 60, 86, 112, 138),  # Version 32
    (6, 30, 58, 86, 114, 142),  # Version 33
    (6, 34, 62, 90, 118, 146),  # Version 34
    (6, 30, 54, 78, 102, 126, 150),  # Version 35
    (6, 24, 50, 76, 102, 128, 154),  # Version 36
    (6, 28, 54, 80, 106, 132, 158),  # Version 37
    (6, 32, 58, 84, 110, 136, 162),  # Version 38
    (6, 26, 54, 82, 110, 138, 166),  # Version 39
    (6, 30, 58, 86, 114, 142, 170),  # Version 40
]
