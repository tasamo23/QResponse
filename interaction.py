import json
from enum import Enum

Mode = ("Mode",["NEW","MODIFY","EXPORT"]);

def initPrompt():
    print("What do you want to do?")

    while True:
        print("[0] Create new QR code (default)")
        print("[1] Modify existing configuration")
        print("[2] Export existing configuration")
        print("Press enter to choose default")

        option = input("[0-2]: ");

        if option == "" or option == "0":
            return Mode.NEW;
        
        elif option == "1":
            return Mode.MODIFY;

        elif option == "2":
            return Mode.EXPORT;

        else:
            print("Error. Input does not match expected values")

def loadAllConfigurations():
    #Search the folder for existing code configurations in json format and load them all in
    return [];
        