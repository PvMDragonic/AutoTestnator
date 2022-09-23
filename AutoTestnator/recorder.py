from pynput import mouse, keyboard
from PIL import ImageGrab

import numpy as np
import screeninfo
import h5py

class Recorder():
    """
    Class responsible for recording the tests into a Test class compatible file.
    """
    recording = False
    steps = []

    @staticmethod
    def record():
        def mouse_handler(x, y, button, pressed):
            if not Recorder.recording:
                return

            # This method is called when the mouse is clicked and released,
            # so this validation filters it out.
            if pressed:
                Recorder.steps.append(['1', str(x), str(y)])
                if button == mouse.Button.left:
                    Recorder.steps.append(['2', '1', '-1'])
                elif button == mouse.Button.right:
                    Recorder.steps.append(['2', '2', '-1'])

        def keyboard_handler(key):
            if key == keyboard.Key.f12:
                Recorder.recording = not Recorder.recording

                if Recorder.recording == True:
                    print("-> Recording started!")
                    return
                else:
                    return False
            if key == keyboard.Key.enter:
                return False
            if key in dir(keyboard.Key):
                return
            if not Recorder.recording:
                return

            Recorder.steps.append(['3', str(key), '-1'])

        print("Press 'Enter' to cancel the recording;")
        print("Press 'F12' to begin or finish the test's recording.\n\nAll your actions will be recorded for future use.")

        mouse.Listener(
            on_click = mouse_handler
        ).start()

        with keyboard.Listener(
            on_press = keyboard_handler
        ) as listener:
            listener.join() # Holds code execution until recording is canceled or finished.

        if Recorder.steps:
            monitor = screeninfo.get_monitors()[0]
            size = [monitor.width, monitor.height, -1]

            validation = ImageGrab.grab()
            validation = np.array(validation)

            test_name = input("> Insert a name for the test file: ")

            with h5py.File(f'{test_name}.hdf5', 'w') as f:
                f.create_dataset("size", data = size)
                f.create_dataset("steps", data = Recorder.steps)
                f.create_dataset("validation", data = validation)