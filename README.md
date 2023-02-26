# MTP

Keys in One-time pad encryption (OTP) should only be used once, when they get reused we can do a Many-time pad attack.

MTP Interactive uses automated cryptanalysis to present a partial decryption which can be solved interactively.

## Install

Python 3.7+ required

```
pip3 install mtp
```

## Usage

```
mtp examples/sample.ciphertexts
```

[![asciicast](https://asciinema.org/a/204705.png)](https://asciinema.org/a/204705)

### Intstructions

Cursor movement is similar to Sublime Text:
 - Left, Right, Up and Down for simple movement
 - Home, End, Page Up and Page Down for larger movement
 - Left Click for jumping to mouse cursor

Letters can be entered using the keyboard any time.

The menu can be opened with the escape key. The "Export" button in the menu
will write the JSON state of the decryption to a file named 'result.json' by default. Use the -o flag to specify the desired filename for export.

You can exit the program cleanly using the "Quit" menu button.

Window resizing and text size changes are supported.

## Development

Use a Python 3.11 virtual environment to develop on this project

```
virtualenv venv -p python3.11
source ./venv/bin/activate
pip install -r requirements.txt
```

Pull Requests and Issues welcome!
