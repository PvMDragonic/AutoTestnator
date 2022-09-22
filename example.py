from AutoTestnator import Recorder
from AutoTestnator import Tester
from AutoTestnator import Test

import screeninfo
import glob
import os

def clear_console():
    if os.name == 'nt': # Windows
        os.system('cls') 
    else:
        os.system('clear') # Linux/Mac

def welcome_message():
    clear_console()
    if len(screeninfo.get_monitors()) > 1:
        print("Warning: This program may not work as intended with more than one monitor.\n")

    print("======= Testnator5000 =======")
    print("'1' - Record a new test;")
    print("'2' - Play a recorded test.")

def recording():
    clear_console()
    Recorder.record()

def execution():
    def list_files():
        print("'Enter' to return.\n")
        print(">> Select your file:")
        files = glob.glob('*.hdf5')
        for index, elem in enumerate(files):
            print(f"'{index + 1}' - {elem}")
        
        while True:         
            try: 
                opt = input() # Split in two lines so if it fails when casting, it still retains the value.
                opt = int(opt)

                if opt > len(files) or opt < 0:
                    print(">> Select a valid option!")
                    continue

                return files[opt - 1]
            except ValueError:
                if opt == "": # If pressed 'Enter'.
                    return None

                print(">> Select a valid option!")
 
    clear_console()
    file = list_files()
    if not file: # If pressed 'Enter'.
        return  

    clear_console()
    try:
        test = Test(file)
        #test.show_steps()
        #test.show_validation()
        result = Tester.execute(test)
        print(f">> Test similarity: {round(result, 2) * 100}%\n")
        if result >= 0.90:
            print(">> Test succeeded!")
        else:
            print(">> Test failed!")
    except Exception as e:
        print(e)

    input("\n\nPress 'Enter' to continue...")

if __name__ == "__main__":
    welcome_message()

    while True:
        try:
            opt = int(input())
        except ValueError:
            print("\n>> Invalid number!")
            continue

        if opt == 1:
            recording()
            welcome_message()
        elif opt == 2:
            execution()
            welcome_message()
        else:
            print("\n>> Invalid option; insert a valid number!\n")