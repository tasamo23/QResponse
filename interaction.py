import json
from enum import Enum

Mode = Enum("Mode", ["NEW", "MODIFY", "EXPORT"])


def initPrompt():
    print("\nWhat do you want to do?\n")

    while True:
        print("\t[0] Create new QR code (default)")
        print("\t[1] Modify existing configuration")
        print("\t[2] Export existing configuration\n")
        # print("")

        option = input("Press enter to choose default\t[0-2]: ")

        if option == "" or option == "0":
            return Mode.NEW

        elif option == "1":
            return Mode.MODIFY

        elif option == "2":
            return Mode.EXPORT

        else:
            print("Error. Input does not match expected values")


def loadAllConfigurations():
    # Search the folder for existing code configurations in json format and load them all in
    return []
