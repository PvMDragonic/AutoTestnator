# AutoTestnator
A tool for test automation for (any) desktop app or website.

## Intended use
While this can be used to automate program installation, or checks to see if n number of programs are present on a machine, for example, its intended use is for webpage (forms) validation, where you need to input information on every field again and again to test it after every update. 

## How it works
AutoTestnator is capable of recording actions (like a keylogger) and saving them for future reprodution. Alongside repeating the same set of instructions, at the end it validates to see if the same endscreen (result) was achieved or not. It also validates individual input fields by searching for error words around where the mouse clicked (assuming it clicked on a form input field).

Mouse and keyboard recording and manipulation are handled by [pynput](https://pypi.org/project/pynput/); the endscreen validation is done by a [structural similarity algorithm](https://pypi.org/project/SSIM-PIL/) implementation; and the individual fields are validated by [PyTesseract](https://pypi.org/project/pytesseract/).

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

*Hotkey recording (like Ctrl + C, for example) is currently unsupported.* 

## Usage
### Recorder
The recording can be started by calling the `record()` method from the `Recorder` class, which takes the optional `url` argument:
```
    Recorder().record()
    Recorder().record('www.google.com')
```
After calling the `record()` method, it'll start listening for the hotkeys to either start the keylogging or to cancel the process altogether.

### Tester
The execution of a recorded test can be started by first instantiating a Test object, which recieves the path to a test.hdf5 file as argument. Then, the test object must be given to the `execute()` method from the `Tester` class:
```
    test = Test(file)
    result = Tester.execute(test)
    print(result)
```
The return value from `Tester.execute()` is a float value between 0 and 1, which represents the similarity between the endscreen saved during recording and the one taken during a given replay of the recorded instructions.

The `config.json` file contains some configurations related to the Tester class, like Tesseract location; input field language; and input field error strings.

### Test
The `Test` class must recieve a valid hdf5 file path, containing 3 sets of data: 
- The monitor screen size; 
- The recorded actions; and
- A numpy array of the endscreen print.

If fed an irregular filepath (wrong format; wrong data set; etc), the `Test` class will throw any of the following exceptions:
- `TypeError` if the filepath is wrong or invalid;
- `NotImplementedError` if the class isn't initiated with the correct attributes;
- `ValueError` if any of the attributes is of the wrong type.

The `Tester` class will also throw a `NotImplementedError` if given a `Test` which doesn't implement the `TestInterface` interface.

### Implementation
The `example.py` file contains an implementation of the module for a testing application.

## F.A.Q
### Why?
This was done mostly as a learning exercise, but it can still have pratical use.

### What about Selenium?
Selenium is all fine and dandy, but I find it too restrictive. You need to write the script with the exact naming for classes and elements, and if one of those ends up changing, the script breaks. You also need to know how to use Selenium. With AutoTestnator, you can just rock and roll (assuming you cope with the barebones example implementation).

### Isn't PyTesseract overkill?
Yes! Unfortunately, I couldn't find another solution. Using SSIM for input field validation wouldn't work as the image would always change due to recieving text; then I tried looking for color changes on the input field (as most input fields change colors or give a warning with a different color when it doesn't accept the given input), but that also didn't work, as the gradient from color A to color B means a ton of different color values (even though for a human is only one color to the other). It's too random to be properly compared, so I landed on PyTesseract as a last ditch effort to look for error messages around the input field.

### Why hdf5 files?
To save on space. At first I used json to hold the Test information, but numpy images are really big, so straight binary was the way to go.