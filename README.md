# AutoTestnator
A tool for test automation for (any) desktop app or website.

## Intended use
While this can be used to automate program installation, or checks to see if n number of programs are present on a machine, for example, its intended use is for webpage (forms) validation, where you need to input information on every field again and again to test it after every update. 

## How it works
AutoTestnator is capable of recording actions (like a keylogger) and saving them for future reprodution. Alongside repeating the same set of instructions, at the end it validates to see if the same endscreen (result) was achieved or not.

Mouse and keyboard recording and manipulation are handled by [pynput](https://pypi.org/project/pynput/), while the endscreen validation is done by a [structural similarity algorithm](https://pypi.org/project/SSIM-PIL/) implementation.

## Features
- Record test instructions into a hdf5 file;
    - Mouse right clicks;
    - Mouse left clicks;
    - Mouse middle clicks;
    - Mouse position when clicking;
    - Mouse scroll distance;
    - Keyboard letters;
    - Keyboard keys;
    - Keyboard numpad.
- Read test instructions from hdf5 files;
- Show information saved on a test file;
- Execute tests from hdf5 files;
- Show endscreen similarity to what it should be, based on result during recording.

## Usage
The recording can be started by calling, which takes the optional argument `url`:
```
    Recorder().record()
    Recorder().record('www.google.com')
```

The execution of a recorded test can be started by first instantiating a Test object, which recieves the path to a test.hdf5 file as argument. Then, you pass the test object to the Tester's `execute()` method:
```
    test = Test(file)
    result = Tester.execute(test)
    print(result)
```

The `example.py` file contains an implementation of the module for a testing application.