from .test import Test, TestInterface

from SSIM_PIL import compare_ssim
from PIL import ImageGrab, Image
from unidecode import unidecode
from ctypes import windll
from time import sleep

import pytesseract
import numpy as np
import screeninfo
import webbrowser
import pynput
import cv2
import os

# Looks for the Tesseract-OCR folder on the same folder as Tester.py.
dirname = os.path.dirname(__file__)
filepath = os.path.join(dirname, r'Tesseract-OCR\tesseract.exe')
pytesseract.pytesseract.tesseract_cmd = filepath

class IncompatibleMonitor(Exception):
    pass

class InputFieldValidation(Exception):
    pass

class Validation():
    """
    Class responsible for holding the individual input field validation data.
    """
    def __init__(self, x: int, y: int):
        self.image = ImageGrab.grab(
            bbox = (
                x - 200, y - 75, 
                x + 200, y + 75
            )
        )
        self.img_cv = cv2.cvtColor(
            np.array(
                self.image
            ), 
            cv2.COLOR_RGB2BGR
        )
        self.img_cv = cv2.cvtColor(
            self.img_cv, 
            cv2.COLOR_BGR2GRAY
        )
        self.text = unidecode(
            pytesseract.image_to_string(
                self.img_cv, 
                lang='eng', 
                config='--psm 6'
            )
        ).lower()
        self.x = x
        self.y = y

class Tester():
    """
    Class responsible for running Test classes.
    """
    mouse = pynput.mouse.Controller()
    keyboard = pynput.keyboard.Controller()
    last_click = None

    @staticmethod
    def execute(test: Test) -> float:
        def invalid_screen_size(test_screen: list) -> bool:
            current_screen = screeninfo.get_monitors()[0]
            return test_screen[0] != current_screen.width and test_screen[1] != current_screen.height

        def validate_result(base_img: np.array) -> float:
            print(">> Validating...")
            sleep(4) # Assumes you clicked 'submit' or something, so longer sleep to account for loading.

            new_img = ImageGrab.grab()
            base_img = Image.fromarray(base_img)
            return compare_ssim(base_img, new_img)
        
        def execute_instructions(test: Test) -> None:
            def validate_input_field(mensagem: str) -> bool:
                return any(substr in mensagem for substr in ['err', 'invalid', 'incorr', 'obrigat'])

            def move_mouse(x: int, y: int) -> None:
                Tester.mouse.position = (x, y)
                sleep(1)

            def scroll_mouse(x: int, y: int) -> None:
                Tester.mouse.move(50, 50)
                Tester.mouse.scroll(x, y)
                sleep(1)

            def click_mouse(button: int, index: int) -> None:
                if button == 1:
                    Tester.mouse.click(pynput.mouse.Button.left, 1)
                elif button == 2:
                    Tester.mouse.click(pynput.mouse.Button.right, 1)
                elif button == 3:
                    Tester.mouse.click(pynput.mouse.Button.middle, 1)

                if button == 1: # Left button.
                    sleep(0.5)
                    if Tester.last_click is not None:
                        current_state = Validation(
                            Tester.last_click.x,
                            Tester.last_click.y)
                        
                        # This is here in case some drop-down menu fails/doesn't appears/something/etc. 
                        if validate_input_field(current_state.text):
                            current_state.image.show()
                            raise InputFieldValidation("Instruction result doesn't match; test has failed!")

                        # If the click was just validated, there's no need to validate it next time.
                        Tester.last_click = None
                        return

                    # Saves the click position to validate it next time a click occurs.
                    Tester.last_click = Validation(
                        test.steps[index - 1][1],
                        test.steps[index - 1][2])
                sleep(1)

            def type_keyboard(key: str, index: int) -> None:
                sleep(0.25)
                try:
                    Tester.keyboard.tap(key)

                    # Last instruction.
                    if index >= len(test.steps) - 1:
                        return

                    # Keyboarding something that isn't an Enter press.
                    if test.steps[index + 1][0] == 4:
                        if test.steps[index + 1][1] != 'enter':
                            return 

                    # If there's nothing to compare against.
                    if Tester.last_click is None:
                        return

                    # Gets here if the next instruction is a click or enter press. 
                    sleep(0.25)
                    current_state = Validation(
                        Tester.last_click.x, 
                        Tester.last_click.y)
                    Tester.last_click = None

                    if validate_input_field(current_state.text):
                        current_state.image.show()
                        raise InputFieldValidation("Instruction result doesn't match; test has failed!")  

                except (TypeError, ValueError):
                    # Letters and actual buttons on the kb have different formatting, 
                    # so it'll get here if it's not a letter.
                    Tester.keyboard.tap(getattr(pynput.keyboard.Key, key))
                sleep(0.25)

            def url_open(url: str) -> None:
                webbrowser.open(url)
                sleep(2)

            # Minimizes the console window.
            windll.user32.ShowWindow(windll.kernel32.GetConsoleWindow(), 6)

            print(">> Testing...")
            for index, instruction in enumerate(test.steps):
                {
                    1: lambda: move_mouse(instruction[1], instruction[2]),
                    2: lambda: click_mouse(instruction[1], index),
                    3: lambda: scroll_mouse(instruction[1], instruction[2], index),
                    4: lambda: type_keyboard(instruction[1], index),
                    5: lambda: url_open(instruction[1])
                }.get(
                    instruction[0]
                )()

            # Brings the console back front.
            windll.user32.ShowWindow(windll.kernel32.GetConsoleWindow(), 1)

        if not isinstance(test, TestInterface):
            raise NotImplementedError("Given test does not implement the TestInterface interface.")
    
        if invalid_screen_size(test.screen):
            raise IncompatibleMonitor("Your monitor resolution is incompatible with the test's resolution.")

        execute_instructions(test)
        return validate_result(test.validation)   