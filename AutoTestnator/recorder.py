from multiprocessing import Process
from pynput import mouse, keyboard
from webbrowser import open
from PIL import ImageGrab
from time import sleep

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
    def _url_recording(url: str) -> None:
        open(url)
        sleep(3)
        keyboard.Controller().tap(keyboard.Key.f11)
        print("-> Recording started!")

    @staticmethod
    def record(url: str = None) -> None:
        def mouse_click_handler(x, y, button, pressed):
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

        def mouse_scroll_handler(x: int, y: int, dx: int, dy: int) -> None:
            if not Recorder.recording:
                return

            # 'x' and 'y' are the pos where the scroll happened; 'dx' and 'dy' are how much was scrolled.
            Recorder.steps.append(['3', str(dx), str(dy)])

        def keyboard_handler(key):
            if not Recorder.recording:
                return

            if isinstance(key, keyboard.Key):
                Recorder.steps.append(['4', key._name_, '-1'])
            elif isinstance(key, keyboard.KeyCode):
                Recorder.steps.append(['4', key.char, '-1'])

        def start_recording(url: str):
            if Recorder.recording:
                Recorder.recording = False
                Recorder.record_listener.stop()
                return

            if url is not None:
                if not any(substr in url for substr in ['www', 'https']):
                    url = f'www.{url}' 

                # Something on pynput's listeners' join() doesn't like the "webbrowser.open()" or
                # pynput's own "keyboard.Controller().tap()", making the Recorder.record_listener's
                # join() break when it shouldn't.

                # Doesn't happen on all machines and may have to do with some return value or another treadding/multiprocessing schenanigan.
                # Calling "webbrowser.open()" and "keyboard.Controller().tap()" in another Process fixes things.
                Process(
                    target = Recorder._url_recording, 
                    args = (url, )
                ).start()

                # The F11 will be appended when the Process presses it and the keyboard listener catches it. 
                Recorder.steps.append(['5', url, '-1'])

            Recorder.mouse_listener.start()
            Recorder.kb_listener.start()
            Recorder.recording = True

            if url:
                print("-> Wait for the browser to open and go fullscreen...")
            else:
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
            on_click = mouse_click_handler,
            on_scroll = mouse_scroll_handler
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
            
            # Needs to be reset, since this static class never unloads and reloads.
            Recorder.steps = []