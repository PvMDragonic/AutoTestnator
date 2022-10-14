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

            # Numpad keys return numbers instead of actual keys.
            if hasattr(key, 'vk') and 96 <= key.vk <= 111:
                {
                    96: lambda: Recorder.steps.append(['4', '0', '-1']),
                    97: lambda: Recorder.steps.append(['4', '1', '-1']),
                    98: lambda: Recorder.steps.append(['4', '2', '-1']),
                    99: lambda: Recorder.steps.append(['4', '3', '-1']),
                    100: lambda: Recorder.steps.append(['4', '4', '-1']),
                    101: lambda: Recorder.steps.append(['4', '5', '-1']),
                    102: lambda: Recorder.steps.append(['4', '6', '-1']),
                    103: lambda: Recorder.steps.append(['4', '7', '-1']),
                    104: lambda: Recorder.steps.append(['4', '8', '-1']),
                    105: lambda: Recorder.steps.append(['4', '9', '-1']),
                    106: lambda: Recorder.steps.append(['4', '*', '-1']),
                    107: lambda: Recorder.steps.append(['4', '+', '-1']),
                    109: lambda: Recorder.steps.append(['4', '-', '-1']),
                    110: lambda: Recorder.steps.append(['4', ',', '-1']),
                    111: lambda: Recorder.steps.append(['4', '/', '-1'])
                }.get(key.vk)()
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

            if url:
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

            if url is not None:
                print("-> Wait for the browser to open and go fullscreen...")
            else:
                print("-> Recording started!")
        
        def cancel_recording():     
            Recorder.recording = False    
            Recorder.steps = []
            Recorder.record_listener.stop()

        def clear_junk_instructions():
            """
            Clears the junk from the end of the steps list.
            Some useless things get caught when you press the hotkey to end recording.
            """
            while Recorder.steps[-1][1] in ('f11', '7', 'alt_l', 'ctrl_l'):
                del Recorder.steps[-1]
        
        def join_scrolls():
            """
            Puts all the individual scroll instructions into a single, big scroll.
            Saves on run time, since the code waits a bit after each instruction.
            """
            while True:
                continue_for = True
                for i in range(len(Recorder.steps)):
                    if not continue_for: 
                        break
                    if Recorder.steps[i][0] == '3': # '3' means Scroll.
                        if Recorder.steps[i + 1][0] == '3':
                            Recorder.steps[i][2] += Recorder.steps[i + 1][2]
                            del Recorder.steps[i]
                            continue_for = False
                            continue
                    if i == len(Recorder.steps) - 1:
                        return

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

        try:
            keyboard.Listener(
                on_press=lambda k: hotkey1.press(Recorder.record_listener.canonical(k)),
                on_release=lambda k: hotkey1.release(Recorder.record_listener.canonical(k))
            ).start() 
        except AttributeError:
            # Sometimes give "'NoneType' object has no attribute 'canonical'" for no clear reason.
            # Giving the error a pass doesnt seem to affect any functionality.
            pass 

        with keyboard.Listener(
            on_press=lambda k: hotkey2.press(Recorder.record_listener.canonical(k)),
            on_release=lambda k: hotkey2.release(Recorder.record_listener.canonical(k))
        ) as Recorder.record_listener:
            Recorder.record_listener.join() # Holds code execution until recording is canceled or finished.

        Recorder.mouse_listener.stop()
        Recorder.kb_listener.stop() 

        if url:
            keyboard.Controller().tap(keyboard.Key.f11)

        if Recorder.steps:
            clear_junk_instructions()
            join_scrolls()

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