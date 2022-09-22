import numpy as np
import h5py

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
    def __init__(self, arqv: str) -> None:
        def load_data(arqv: str) -> list:
            def fix_list(hdf5: h5py._hl.dataset.Dataset) -> list:
                lst = []
                for arr in hdf5:
                    if arr[0] == b'1':
                        temp = []
                        for elem in arr:
                            temp.append(int(elem))
                        lst.append(temp)
                    elif arr[0] == b'2':
                        temp = [int(arr[0]), int(arr[1])]
                        lst.append(temp)
                    elif arr[0] == b'3':
                        temp = [int(arr[0]), str(arr[1], 'UTF-8')[1]]
                        lst.append(temp)
                return lst

            with h5py.File(arqv, 'r') as f:
                try:
                    return [
                        list(f['size']), 
                        fix_list(f['steps']), 
                        np.array(f['validation'])
                    ]
                except Exception:
                    return []

        if (type(arqv) != str):
            raise ValueError('Param must be a string that leads to a valid directory.')
        
        data = load_data(arqv)

        if len(data) != 3: 
            raise ValueError('hdf5 file must contain 3 elements.')
        
        self.screen = data[0]
        self.steps = data[1]
        self.validation = data[2]

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
        for index, step in enumerate(self.steps):
            if step[0] == 1:
                print(f'{index + 1} - Move to x:{step[1]} y:{step[2]};')
            elif step[0] == 2:
                print(f'{index + 1} - {"Left" if step[1] == 1 else "Right"} click;')
            elif step[0] == 3:
                print(f'{index + 1} - Type "{step[1]}";')
        print("\n")

    def show_validation(self) -> None:
        """
        Shows the image, saved on the test file, that will be used for validation of completion (or failure) of test runs.
        """
        from PIL import Image
        img = Image.fromarray(self.validation)
        img.show()