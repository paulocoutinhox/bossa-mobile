# BOSSA - MOBILE

![Bossa Mobile - Android](https://github.com/prsolucoes/bossa-mobile/workflows/Bossa%20Mobile%20-%20Android/badge.svg)

Compiling project BOSSA for mobile.

Only tool **bossac** will be generated because other tool depends from GUI and wxWidgets.

## Requirements

- Python 3
    - https://www.python.org/downloads/
- PIP
    - https://pip.pypa.io/en/stable/installing/
- CMake 3.14
    - https://cmake.org/download/

## General steps

```
pip3 install -r requirements.txt
python3 make.py run get-wx
python3 make.py run get-bossa
```

## Android steps

```
python3 make.py run get-ndk
python3 make.py run build-android
python3 make.py run test-android
```