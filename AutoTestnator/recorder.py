from pynput import mouse, keyboard
from PIL import ImageGrab

import webbrowser, time
import numpy as np
import screeninfo
import h5py

class Recorder():
    """
    Class responsible for recording the tests into a Test class compatible file.
    """
    recording = False
    record_listener = None
    mouse_listener = None
    kb_listener = None
    steps = []

    @staticmethod
    def record(url = None):
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
                elif button == mouse.Button.middle:
                    Recorder.steps.append(['2', '3', '-1'])

        def keyboard_handler(key):
            if not Recorder.recording:
                return

            if isinstance(key, keyboard.Key):
                Recorder.steps.append(['3', key._name_, '-1'])
            elif isinstance(key, keyboard.KeyCode):
                Recorder.steps.append(['3', key.char, '-1'])

        def start_recording(url):
            if Recorder.recording:
                Recorder.recording = False
                Recorder.record_listener.stop()
                return

            if url:
                webbrowser.open(url)
                time.sleep(1)
                keyboard.Controller().tap(keyboard.Key.f11)

                Recorder.steps.append(['4', url, '-1'])
                Recorder.steps.append(['3', 'f11', '-1'])

            Recorder.mouse_listener.start()
            Recorder.kb_listener.start()
            Recorder.recording = True
            print("-> Recording started!")
        
        def cancel_recording():    
            Recorder.recording = False 
            Recorder.steps = []
            Recorder.record_listener.stop()

        print("\nAll your actions will be recorded for future replication.\n")
        print("Commands:")
        print(">> 'Ctrl Alt C' to cancel the recording;")
        print(">> 'Ctrl Alt R' to begin and finish the recording.\n")

        Recorder.mouse_listener = mouse.Listener(
            on_click = mouse_handler
        )

        Recorder.kb_listener = keyboard.Listener(
            on_press = keyboard_handler
        ) 

        hotkey1 = keyboard.HotKey(
            keyboard.HotKey.parse('<ctrl>+<alt>+c'),
            cancel_recording
        )

        hotkey2 = keyboard.HotKey(
            keyboard.HotKey.parse('<ctrl>+<alt>+r'),
            lambda: start_recording(url)
        )

        keyboard.Listener(
            on_press=lambda k: hotkey1.press(Recorder.record_listener.canonical(k)),
            on_release=lambda k: hotkey1.release(Recorder.record_listener.canonical(k))
        ).start() 

        with keyboard.Listener(
            on_press=lambda k: hotkey2.press(Recorder.record_listener.canonical(k)),
            on_release=lambda k: hotkey2.release(Recorder.record_listener.canonical(k))
        ) as Recorder.record_listener:
            Recorder.record_listener.join() # Holds code execution until recording is canceled or finished.

        Recorder.mouse_listener.stop()
        Recorder.kb_listener.stop() 

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
            
            Recorder.steps = []