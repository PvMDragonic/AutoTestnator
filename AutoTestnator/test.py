import numpy as np
import errno
import h5py
import os

class TestMeta(type):
    """
    Custom meta class to make sure the test has all it's attributes in place.
    """
    def __call__(cls, *args, **kwargs):
        obj = type.__call__(cls, *args, **kwargs)
        obj.check_variables()
        return obj
     
class TestInterface(metaclass = TestMeta):
    """
    Test class interface.
    """
    screen = None
    steps = None
    validation = None
 
    def check_variables(self):
        if self.screen is None:
            raise NotImplementedError('Attribute "screen" undefined.')
        elif type(self.screen) is not list:
            raise ValueError('Attribute "screen" must be a list.')

        if self.steps is None:
            raise NotImplementedError('Attribute "steps" undefined.')
        elif type(self.steps) is not list:
            raise ValueError('Attribute "steps" must be a list.')

        if self.validation is None:
            raise NotImplementedError('Attribute "validation" undefined.')
        elif type(self.validation) is not np.ndarray:
            raise ValueError('Attribute "validation" must be a numpy array.')

class Test(TestInterface):  
    """
    Class which holds all the steps and validation for a given test.
    """  
    def __init__(self, file_name: str) -> None:
        def fix_list(dataset: h5py._hl.dataset.Dataset) -> list:
            """
            Transforms the saved binary steps into the correct format for the Tester class.
            """
            return [
                {
                    b'1': lambda: [int(arr[0]), int(arr[1]), int(arr[2])],
                    b'2': lambda: [int(arr[0]), int(arr[1])],
                    b'3': lambda: [int(arr[0]), int(arr[1]), int(arr[2])],
                    b'4': lambda: [int(arr[0]), str(arr[1], 'UTF-8')],
                    b'5': lambda: [int(arr[0]), str(arr[1], 'UTF-8')]
                }.get(arr[0])() for arr in dataset
            ]

        if not os.path.exists(file_name):
            raise TypeError('Invalid file name or path.')
        
        with h5py.File(file_name, 'r') as file:
            try:
                self.screen = list(file['size'])
            except Exception:
                self.screen = None

            try:
                self.steps = fix_list(file['steps'])
            except Exception:
                self.steps = None

            try:
                self.validation = np.array(file['validation'])
            except Exception:
                self.validation = None

    def __str__(self) -> str:
        return f"{self.screen}\n{self.steps}\n{self.validation}"

    def show_screen_size(self) -> None:
        """
        Shows the monitor size used for the test. 
        If the monitor sizes differ, the test wont work as intended.
        """
        print(f"Monitor: {self.screen[0]}x{self.screen[1]}")

    def show_steps(self) -> None:
        """
        Shows the steps recorded into the test file.
        """
        print("\n")
        for index, instruction in enumerate(self.steps):
            {
                1: lambda: print(f'{index + 1} - Move to x:{instruction[1]} y:{instruction[2]};'),
                2: lambda: print(f'{index + 1} - {"Left" if instruction[1] == 1 else "Right"} click;'),
                3: lambda: print(f'{index + 1} - Scroll {instruction[2]} {"up" if instruction[2] > 0 else "down"};'),
                4: lambda: print(f'{index + 1} - Type "{instruction[1]}";'),
                5: lambda: print(f'{index + 1} - Open URL "{instruction[1]}";')
            }.get(
                instruction[0]
            )()

    def show_validation(self) -> None:
        """
        Shows the image, saved on the test file, that will be used for validation of completion (or failure) of test runs.
        """
        from PIL import Image
        img = Image.fromarray(self.validation)
        img.show()