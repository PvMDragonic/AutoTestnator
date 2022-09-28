from .test import Test, TestInterface

from SSIM_PIL import compare_ssim
from PIL import ImageGrab, Image
from time import sleep

import numpy as np
import screeninfo
import webbrowser
import pynput
import os

class IncompatibleMonitor(Exception):
    pass

class Tester():
    """
    Class responsible for running the Test classes.
    """
    mouse = pynput.mouse.Controller()
    keyboard = pynput.keyboard.Controller()

    @staticmethod
    def execute(test: Test) -> float:
        def move_mouse(x: int, y: int) -> None:
            Tester.mouse.position = (x, y)
            sleep(1)

        def click_mouse(button: int) -> None:
            if button == 1:
                Tester.mouse.click(pynput.mouse.Button.left, 1)
            elif button == 2:
                Tester.mouse.click(pynput.mouse.Button.right, 1)
            elif button == 3:
                Tester.mouse.click(pynput.mouse.Button.middle, 1)
            sleep(1)

        def type_keyboard(key: str) -> None:
            try:
                Tester.keyboard.tap(key)
            except (TypeError, ValueError):
                # Letters and actual buttons on the kb have different formatting, 
                # so it'll get here if it's not a letter.
                Tester.keyboard.tap(getattr(pynput.keyboard.Key, key))
            sleep(0.25)

        def url_open(url: str) -> None:
            webbrowser.open(url)
            sleep(2)

        def validate_result(base_img: np.array) -> float:
            def clear_screen():
                if os.name == 'nt': # Windows
                    os.system('cls') 
                else:
                    os.system('clear') # Linux/Mac

            sleep(4)
            clear_screen()
            new_img = ImageGrab.grab()
            base_img = Image.fromarray(base_img)
            return compare_ssim(base_img, new_img)

        def invalid_screen_size(test_screen: list) -> bool:
            current_screen = screeninfo.get_monitors()[0]
            if test_screen[0] == current_screen.width and test_screen[1] == current_screen.height:
                return False
            return True

        if not isinstance(test, TestInterface):
            raise NotImplementedError("Given test does not implement the TestInterface interface.")
    
        if invalid_screen_size(test.screen):
            raise IncompatibleMonitor("Your monitor resolution is incompatible with the test's resolution.")

        print('>> Test started.')
        for instruction in test.steps:
            if instruction[0] == 1:
                move_mouse(instruction[1], instruction[2])
            elif instruction[0] == 2:
                click_mouse(instruction[1])
            elif instruction[0] == 3:
                type_keyboard(instruction[1])
            elif instruction[0] == 4:
                url_open(instruction[1])

        return validate_result(test.validation)