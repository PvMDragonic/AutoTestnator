from .test import Test, TestInterface

from SSIM_PIL import compare_ssim
from PIL import ImageGrab, Image
from time import sleep

import numpy as np
import screeninfo
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
    def _move_mouse(x: int, y: int) -> None:
        Tester.mouse.position = (x, y)
        sleep(1)

    @staticmethod
    def _click_mouse(button: int) -> None:
        if button == 1:
            Tester.mouse.click(pynput.mouse.Button.left, 1)
        elif button == 2:
            Tester.mouse.click(pynput.mouse.Button.right, 1)
        sleep(1)

    @staticmethod
    def _keyboard_type(key: str) -> None:
        Tester.keyboard.tap(key)
        sleep(0.25)

    @staticmethod
    def _validate_result(base_img: np.array, new_img: np.array) -> float:
        def clear_screen():
            if os.name == 'nt': # Windows
                os.system('cls') 
            else:
                os.system('clear') # Linux/Mac

        sleep(4)
        clear_screen()
        base_img = Image.fromarray(base_img)
        new_img = Image.fromarray(new_img)
        return compare_ssim(base_img, new_img)

    @staticmethod
    def execute(test: Test) -> float:
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
                Tester._move_mouse(instruction[1], instruction[2])
            elif instruction[0] == 2:
                Tester._click_mouse(instruction[1])
            elif instruction[0] == 3:
                Tester._keyboard_type(instruction[1])

        return Tester._validate_result(test.validation, np.array(ImageGrab.grab()))