
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
* [Program explanation](#program-explanation)
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

## Program explanation

```python
def init_lookup_tables(prim=0x11d):
    # Precompute the logarithm and anti-log tables for faster computation later, using the provided primitive polynomial (prim)
    global gf_exp, gf_log
    gf_exp = [0] * 512  # anti-log (exponential) table
    gf_log = [0] * 256  # log table

    # For each possible value in the galois field 2^8, we will pre-compute the logarithm and anti-logarithm (exponential) of this value
    x = 1
    for i in range(0, 255):
        gf_exp[i] = x  # compute anti-log for this value and store it in a table
        gf_log[x] = i  # compute log at the same time
        x = gf_mult_noLUT(x, 2, prim)

    for i in range(255, 512):
        gf_exp[i] = gf_exp[i - 255]
    return [gf_log, gf_exp]
```

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
