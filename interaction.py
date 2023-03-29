from time import sleep
from typing import Tuple,List
import qr_color as Color


# All the input prompts put into a separate file for better organisation

# Note! I did not document this file with comments as thoroughly as the other files,
# because it is mostly just a bunch of input prompts which have to be validated. Nothing too complicated or special

def data_askFormat(delay: float) -> int:
    print("===============================================================================")

    format = None

    while format not in ("0", "1", "2", "3", ""):

        if format != None:
            print("Invalid input. Try again.")

        DATA_TYPES = (
            "Text (Plain text, kanji and numbers supported)",
            "URL (Internet link)",
            "Email (Email address)",
            "SMS (short message)"
            # "WLAN (Wireless network) login data"
            # "Location (GPS coordinates)": "",
        )

        print("\nChoose the data type:\n")
        # Alternative way to print the options:
        # for modeIndex in range(len(DATA_TYPES)):
        #     print("\t[{}]\t{}".format(modeIndex, DATA_TYPES[modeIndex]))
        print("\t[0]\tText (Plain text, kanji and numbers supported)")
        print("\t[1]\tURL (Internet link)")
        print("\t[2]\tEmail (Email address)")
        print("\t[3]\tSMS (short message)")

        print("\nPress enter to choose default (0)")
        format = input("[0-3]: ")

    print("\n===============================================================================\n")
    sleep(delay)
    return 0 if format == "" else int(format)


def data_askPlainText(delay: float, format) -> str:
    print("===============================================================================")
    string = None
    while string == "" or string == None:
        if string != None:
            print("\nInvalid input. Empty character strings are not supported.")
        print("\nType the {}:".format("text message"if format == 0 else "website link"))
        string = input("{}: ".format("Message"if format == 0 else "Link"))
        if string != "":
            if input("Your input was:\n"+string+'\nPress enter to continue \nand confirm your input or type "c" and enter to cancel and return to input: ') == "c":
                print("Discarding former input...")
                string = None
    print("\n===============================================================================\n")
    sleep(delay)
    return str(string)


def data_askMail(delay: float) -> str:
    print("===============================================================================")
    address = None
    while address == "" or address == None:
        if address != None:
            print("\nInvalid input. Empty character strings are not supported.")
        print("\nType email address:")
        address = input("Address: ")
        if address != "":
            if input("Your address is set to:\n"+address+'\nPress enter to continue \nand confirm your input or type "c" and enter to cancel and return to input: ') == "c":
                print("Discarding former input...")
                address = None

    print("\n=======================================")
    sleep(delay)
    subject = None
    while subject == "" or subject == None:
        if subject != None:
            print("\nInvalid input. Empty character strings are not supported.")
        print("\nType in your email's subject:")
        subject = input("Subject: ")
        if subject != "":
            if input("Your subject is set to:\n"+subject+'\nPress enter to continue \nand confirm your input or type "c" and enter to cancel and return to input: ') == "c":
                print("Discarding former input...")
                subject = None

    print("\n=======================================\n")
    sleep(delay)
    message = None
    while message == "" or message == None:
        if message != None:
            print("\nInvalid input. Empty character strings are not supported.")
        print("\nType in your email's message:")
        message = input("Message: ")
        if message != "":
            if input("Your email's message is set to:\n"+message+'\nPress enter to continue \nand confirm your input or type "c" and enter to cancel and return to input: ') == "c":
                print("Discarding former input...")
                message = None

    print("\n===============================================================================\n")
    sleep(delay)

    return "MATMSG:TO:{};SUB:{};BODY:{};;".format(address, subject, message)


def data_askSMS(delay: float) -> str:
    print("===============================================================================")
    phoneNum = None
    while phoneNum == "" or phoneNum == None:
        if phoneNum != None:
            print("\nInvalid input. Empty strings are not supported.")
        print("\nType in the receiver's phone number:")
        phoneNum = input("Phone number: ")
        if phoneNum != "":
            if input("The phone number you entered is:\n"+phoneNum+'\nPress enter to continue \nand confirm your input or type "c" and enter to cancel and return to input: ') == "c":
                print("Discarding former input...")
                phoneNum = None

    print("\n=======================================")
    sleep(delay)

    message = None
    while message == "" or message == None:
        if message != None:
            print("\nInvalid input. Empty character strings are not supported.")
        print("\nType in your email's message:")
        message = input("Message: ")
        if message != "":
            if input("Your email's message is set to:\n"+message+'\nPress enter to continue \nand confirm your input or type "c" and enter to cancel and return to input: ') == "c":
                print("Discarding former input...")
                message = None

    print("\n===============================================================================\n")
    sleep(delay)
    return "SMSTO:{}:{}".format(phoneNum, message)


def v_ec_askSize(delay: float, options: List[Tuple[int, int]]) -> Tuple[int, int]:
    print("===============================================================================")
    size = None
    # While the user input is not valid
    while size not in ([str(s) for s in range(len(options))] + [""]):
        # Check if the user input was valid
        if size != None:
            print("\nInvalid input. Try again.")

        # Print the options
        print("\nChoose a size - the higher the error correction, the higher the data redundancy \n(more data can be restored from a broken image):\n")
        for mode in range(len(options)):
            print("\t[{}]\tSize: {} \tError Correction: {}".format(mode, options[mode][0], ("LOW (7%)", "MEDIUM (15%)", "QUARTILE (25%)", "HIGH (30%)")[options[mode][1]]))

        # Offer default option
        print("\nPress enter to default to option 0: the smallest version and lowest error \ncorrection level")

        # Read user input
        size = input("[0-{}]: ".format(len(options)-1))

    print("\n===============================================================================\n")
    sleep(delay)

    # Return the user's choice as a tuple
    return options[int("0" if size == "" else size)]


def pixel_size_askSize(delay: float, size: int) -> int:
    val = "\nInvalid input"

    print("===============================================================================")

    tooBig, tooSmall = False, False

    # While the user input is not valid
    while ((not val.isdigit()) and val != "") or tooBig or tooSmall:
        # Check if the user input was valid
        if (not val.isdigit()) and val != "" and val != "\nInvalid input":
            print("\nInvalid input. Try again.")
        else:
            # Ask the user if scale isn't too big
            if tooBig:
                if input("\nThe scale you chose ({}) is larger then the recommended resolution of 2000 pixels ({}).\nThis could lead to a longer generating time and a larger image file.\nDo you really want to continue?".format(int(val), int(val)*size)
                         + "\nType \"yes\" to continue with all afromentioned consequences or press enter to try again:") == "yes":
                    print("\n===============================================================================\n")
                    sleep(delay)
                    return int(val)
            # Ask the user if scale isn't too small
            if tooSmall:
                if input("\nThe scale you chose ({}) is smaller then the recommended resolution of 100 pixels ({}).\nThis could lead to a difficulties for the scanning device.\nDo you really want to continue?".format(int(val), int(val)*size)
                         + "\nType \"yes\" to continue with all afromentioned consequences or press enter to try again:") == "yes":
                    print("\n===============================================================================\n")
                    sleep(delay)
                    return int(val)

        # Present choice
        print("\nChoose a pixel scale - every QR code rectangle will get scaled accordingly:")

        print("\tYour current output image resolution is {}x{} code rectangles,".format(size+8, size+8)
              + "\n\tso we would recommend a scale value between {} and {}".format(10, 2000//(size+8)))

        # Offer default option
        print("\tPress enter to default to a scale of 10 pixels")

        # Read user input
        val = input("Size: ")
        tooBig = (False if (not val.isdigit() or val == "") else int(val)*(size+8) > 2000)
        tooSmall = (False if (not val.isdigit() or val == "") else int(val)*(size+8) < 100)

    print("\n===============================================================================\n")
    sleep(delay)

    # Default value
    if (val == ""):
        return 10

    return int(val)


def design_askDesign(delay: float) -> Color.Design:
    # Variable initialization
    type, bands, bg, fg, rotation = None, None, [-1, -1, -1], [-1, -1, -1], None

    # Type not supported yet:
    # print("===============================================================================")

    # while type not in ("0", "1", "2", "") or type == None:
    #     if type != None:
    #         print("Invalid input. Try again.")
    #     print("\nChoose color type:\n")
    #     print("\t[0]\tSolid color")
    #     print("\t[1]\tLinear gradient")
    #     print("\t[2]\tRadial gradient")
    #     # Alternative approach (less code, no hardcoding, but less readable)
    #     # for typeIndex in range(len(Color.TYPES)):
    #     #     print("\t[{}]\t{}".format(typeIndex, Color.TYPES[typeIndex].capitalize().replace("_", " ")+" color"))
    #     print("\nPress enter to choose default (0)")
    #     type = input("[0-2]: ")
    # type = 0 if type == "" else int(type)

    # print("\n===============================================================================\n")
    # sleep(delay)
    type = 0

    print("===============================================================================")

    while bands not in ("0", "1", "2", "") or bands == None:
        if bands != None:
            print("Invalid input. Try again.")
        print("\nChoose color bands:\n")
        print("\t[0]\tBlack - White (no transition)")
        print("\t[1]\tGrayscale (several shades of gray)")
        print("\t[2]\tColor (RGB format)")
        # Alternative approach (less code, no hardcoding, but less readable)
        # for typeIndex in range(len(Color.TYPES)):
        #     print("\t[{}]\t{}".format(typeIndex, Color.TYPES[typeIndex].capitalize().replace("_", " ")+" color"))
        print("\nPress enter to choose default (0)")
        bands = input("[0-2]: ")
    bands = "BLACK_WHITE" if bands == "" else ("BLACK_WHITE", "GRAYSCALE", "RGB")[int(bands)]

    print("\n===============================================================================\n")
    sleep(delay)
    print("===============================================================================")

    for i in range(3 if bands == "RGB" else 1):
        while bg[i] not in range(2 if bands == "BLACK_WHITE" else 256) or bg[i] == -1:
            if bg[i] != -1:
                print("Invalid input. Try again.")
            print("\nEnter code background color {} value:".format(("Red", "Green", "Blue")[i] if bands == "RGB" else "Gray" if bands == "GRAYSCALE" else "Black - White"))
            print("\nPress enter to choose default ({})".format(1 if bands == "BLACK_WHITE" else 255))
            val = input("[0-{}]: ".format(1 if bands == "BLACK_WHITE" else 255))
            try:
                bg[i] = int((1 if bands == "BLACK_WHITE" else 255) if val == "" else val)
            except ValueError:
                continue
        if i in range((3 if bands == "RGB" else 1)-1):
            print("=======================================")

    print("\n===============================================================================\n")
    sleep(delay)
    print("===============================================================================")

    for i in range(3 if bands == "RGB" else 1):
        while fg[i] not in range(2 if bands == "BLACK_WHITE" else 256) or fg[i] == -1:
            if fg[i] != -1:
                print("Invalid input. Try again.")
            print("\nEnter code foreground color {} value:".format(("Red", "Green", "Blue")[i] if bands == "RGB" else "Gray" if bands == "GRAYSCALE" else "Black - White"))
            print("\nPress enter to choose default ({})".format(0))
            val = input("[0-{}]: ".format(1 if bands == "BLACK_WHITE" else 255))
            try:
                fg[i] = int(0 if val == "" else val)
            except ValueError:
                continue
        if i in range((3 if bands == "RGB" else 1)-1):
            print("=======================================")

    print("\n===============================================================================\n")
    sleep(delay)
    print("===============================================================================")

    while rotation not in ("0", "1", "2", "3", ""):
        if rotation != None:
            print("Invalid input. Try again.")
        print("\nChoose a rotation mode:\n")
        for mode in range(4):
            print("\t[{}]\t[{}] degrees".format(mode, (0, 90, 180, 270)[mode]))
        print("\nPress enter to skip rotation")
        rotation = input("[0-3]: ")
    rotation = (0, 90, 180, 270)[int("0" if rotation == "" else rotation)]

    print("\n===============================================================================\n")
    sleep(delay)

    return Color.Design(Color.TYPES[type], bands, tuple(bg), tuple(fg), rotation)


def export_askChoice(delay: float) -> int:
    # Variable initialization
    choice = None
    print("===============================================================================")

    choice = None
    while choice not in ("0", "1", "2", "3", "4", "") or choice == None:
        if choice != None:
            print("Invalid input. Try again.")
        print("\nWhat should be done with your QR Code?:\n")
        print("\t[0]\tConsole output")
        print("\t[1]\tOutput into separate window")
        print("\t[2]\tSave as JPEG image (window prompt)")
        print("\t[3]\tSave as PNG image (window prompt)")
        print("\t[4]\tQuit program (no output)")
        print("\nPress enter to choose default (0)")
        choice = input("[0-4]: ")
    print("\n===============================================================================\n")
    sleep(delay)
    return 0 if choice == "" else int(choice)
