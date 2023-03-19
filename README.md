
# QR Code Generator - "QResponse"

***

## Short description

This program generates QR Codes using different input data. Input of the parameters is done through the console, and there are a lot of different customization parameters than can be changed by the user manually.

***

## Table of contents

* [Features](#features)
  * [Data types for QR Code](#data-types-for-qr-code)
  * [Output of the generated QR Code in](#output-of-the-generated-qr-code)
* [Program execution / How to get started](#program-execution--how-to-get-started)
* [Program explanation](#program-explanation--problems-in-the-code)
  * [ECC Computation problem for format string](#ecc-computation-problem-for-format-string)
* [Images](#images)
* [Dependencies](#dependencies)
* [Sources](#sources)

***

## Features

### Data types for QR Code

1. URLs (website links)
2. Plain text
3. Email templates
4. SMS templates
5. ~~(WIFI - und location coordinates data)~~[^1]

Select through choosing the appropriate mode in the console.  

<!-- , vielleicht auch in die Grafische Benutzeroberfläche mit eingebaut (je nach Komplexität und Zeit) -->

### Output of the generated QR Code

* several image formats (PNG, JPEG, ~~GIF, SVG~~[^1])
* ~~to the clipboard of the machine~~[^1]
* different dimensions and scales
* different back - and foreground colors (solid ~~and gradient~~ [^1])
* different redundancies (Reed Solomon Error Correction)
* the console (compatible with IDLE and other terminals)
* a different window showing the image (using tkinter)
* ~~animated GIFS (animating gradients)~~ [^1]

[^1]: Not implemented yet.

## Program execution / How to get started

This program can be executed offline as long as python and all other dependencies are installed.  
You can also pass the parameter `-nodelay` to it when calling or executing, which skips delays in the code to improve user experience. This enables the program to run as fast as possible.
Example:

```shell
    $ python main.py -nodelay
    ...
```

The program can only be interacted with in the console (IDLE and terminal are supported).  
***Follow the instructions in the console to generate the QR Code.***

### Note

After Code generation:
Should the output into the console not work or look odd, choose "`Output into separate window`" (second option, index 1) to load a tkinter window containing the image.

The tkinter window sometimes does not show up on the screen. To see if the window has even launched, look at your task bar. If it is there, click on it to bring it to the front.

***

## Program explanation / Problems in the code

### ECC Computation problem for format string

```python
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
```

***Line 513 - 539 in [qr_gen.py](qr_gen.py)***  
This bit of code is responsible for generating the format information, which is a 15 bit string that contains information about the error correction level and the mask pattern used. This information is then inserted into the QR Code. The mathematics behind this generation method are very complex and involve Galois fields. I do not understand it fully myself, and as I had no way of accessing the *ISO standard ISO/IEC 18004:2015 Information technology - Automatic identification and data capture techniques - QR Code - Part 4: Data structures and encoding methods* document, I had to reverse engineer the algorithm from other tutorials, which I linked below. Those tutorials, however, leave some execution steps open. I had to fill in the blanks myself, which is why I am not 100% sure that this code is correct. I have tested it with a few QR Codes, and it seems to work, but I cannot guarantee anything. The problem lies in the `formatString` variable, which if the mask and error correction level are 0, will output 0 aswell. The tutorial says to add 10 zeros to the right, and remove all zeros on the left, but that would leave an empty string to `bitString`, which throws an error when I try to XOR it with the generator polynomial in the next iterative divison step. Currently the QR Code generates even in this case, as I added some additional steps, but the reader does not recognize it, which means the format string was not correctly calculated. This problem does not happen in the next step of the code, where I compute the version information, as the version is always at least 7 when the program tries to generate it.

### Frequent use of LUTs (Look-Up Tables)

Let me first say that I hate using LUTs or hardcoding for anything, if it does not improve readability. Unfortunately, the nature of QR Codes forced me to use them, as the values I will now show could not easily be calculated.  
*(Again, I think the ISO document would've helped me with that)*

***Adapted from Line 846 - 886 in [qr_gen.py](qr_gen.py)***

```python
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
    #... This continues until Version 40 is reached
]
```

or

***Adapted from Line 119 - 161 in [qr_ecc.py](qr_ecc.py)***

```python
# A table listing the amount of codewords a certain code version requires
# Calculated with the table "RS block size" https://en.m.wikiversity.org/wiki/Reed%E2%80%93Solomon_codes_for_coders/Additional_information#RS_block_size
EC_CODEWORDS_TABLE = (
    # L, M, Q, H (These are the error correction levels)
    (7, 10, 13, 17),  # Version 1
    (10, 16, 22, 28),  # Version 2
    (15, 26, 36, 44),  # Version 3
    (20, 36, 52, 64),  # Version 4
    (26, 48, 72, 88),  # Version 5
    (36, 64, 96, 112),  # Version 6
    (40, 72, 108, 130),  # Version 7
    (48, 88, 132, 156),  # Version 8
    (60, 110, 160, 192),  # Version 9
    # Again, this one goes to 40 as well
)
```

These kinds of things are a big potential for human error, as I had to manually enter and sometimes even calculate the values from a website I had to trust to actually have read the ISO specification. This is not how I usually want my code to look. I would've preferred to have a function that calculates the values, but I could not find a way to do that. It was just too many values I had to find a function for. One good thing about this is that it minimally impacted the program's processing time in a positive way, as it did not have to calculate all *STUFF* you see up there. It just had to look up the values in the LUTs. That's the only good thing the optimist in me can find.

***

## Images

![A generated QR Code example linking to this GitHub site](/img/Result1_link_to_website_270deg_H.png)  

A generated QR Code example linking to this GitHub site.  
Background color gray (50,50,50) with foreground color magenta(250,0,250).  
Rotated 270 degrees.  
PNG Format

![An instance of the program running in the terminal](/img/running_instance_terminal.png)  
VSCode built-in terminal running the program

***

## Dependencies

* [Python 3.7](https://www.python.org/downloads/) (or higher)
* [Pillow](https://pypi.org/project/Pillow/) (PIL fork)
* Python modules (standard library):  
  * sys (system module)
  * math (mathematical module)
  * time (time module)
  * tkinter (GUI module)
  * string (string module)
  * tkinter.filedialog (file dialog module)
  
***

## Sources

***I do not have access to the ISO standards for QR Codes (those are hidden behind a paywall), so I had to get the required information out of tutorials from others:***

*[Wikipedia site](https://en.wikipedia.org/wiki/QR_code)* Basic information about QR Codes and their history, as well as encoding  
*[Thonky’s QR Code Tutorial](https://www.thonky.com/qr-code-tutorial/)* as overall information about QR Codes and how to generate them  
*[Wikiversity article about Reed Solomon Codes](https://en.wikiversity.org/wiki/Reed%E2%80%93Solomon_codes_for_coders)* for further information about the Reed Solomon Error Correction and it's implementation  
