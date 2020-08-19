# BOSSA - MOBILE

![Bossa Mobile - Android](https://github.com/prsolucoes/bossa-mobile/workflows/Bossa%20Mobile%20-%20Android/badge.svg)

![Bossa Mobile - macOS](https://github.com/prsolucoes/bossa-mobile/workflows/Bossa%20Mobile%20-%20macOS/badge.svg)

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
python3 make.py run patch-bossa
```

## Android steps

```
python3 make.py run get-ndk
python3 make.py run patch-android
python3 make.py run build-android
python3 make.py run test-android
python3 make.py run install-android
```

## macOS steps

Requirements:
- dart
  - brew tap dart-lang/dart
  - brew install dart


```
python3 make.py run patch-macos
python3 make.py run build-macos
python3 make.py run test-macos
python3 make.py run install-macos
python3 make.py run run-macos
```

## Custom functions to fluttter

Patch automatically add this lines to the end of file "bossac.cpp":

```
extern "C" {
    #include <android/log.h>
    #include <string>
    
    __attribute__((visibility("default"))) __attribute__((used))
    int tokeniseToArgcArgv(char *buffer, int *argc, char *argv[], const int argv_length)
    {
        int i = 0;

        for (i = 0; i < argv_length; i++) 
        {
            if (NULL == (argv[i] = strtok_r(NULL, " ", &buffer))) 
            {
                break;
            }
        }

        *argc = i;

        return i;
    }

    __attribute__((visibility("default"))) __attribute__((used))
    void test_flutter_void() 
    {
        fprintf(stdout, "Function [test_flutter_void] was called\n");
        __android_log_print(ANDROID_LOG_DEBUG, "BOSSA", "Function [test_flutter_void] was called");
    }

    __attribute__((visibility("default"))) __attribute__((used))
    char * test_flutter_pointer(int argc, char* args) 
    {
        fprintf(stdout, "Function [test_flutter_pointer] was called\n");
        __android_log_print(ANDROID_LOG_DEBUG, "BOSSA", "Function [test_flutter_pointer] was called");
        __android_log_print(ANDROID_LOG_DEBUG, "BOSSA", "Function [test_flutter_pointer] Value send: %d | %s", argc, args);

        return args;
    }

    __attribute__((visibility("default"))) __attribute__((used))
    int bossa_main(int argc, char* args)
    {
        fprintf(stdout, "Function [bossa_main] was called\n");
        __android_log_print(ANDROID_LOG_DEBUG, "BOSSA", "Function [bossa_main] was called");
        __android_log_print(ANDROID_LOG_DEBUG, "BOSSA", "Function [bossa_main] Value send: %d | %s", argc, args);

        // convert string to array of params
        int nargc = 0;
        char *nargv[255] = {0};

        tokeniseToArgcArgv(args, &nargc, nargv, sizeof(nargv));

        // check converted array
        int i = 0;

        for (i = 0; i < nargc; i++) 
        {
            __android_log_print(ANDROID_LOG_DEBUG, "BOSSA", "Function [bossa_main] Value %d parsed: %s", (i + 1), nargv[i]);
        }
        
        // call main with new params
        return main(nargc, nargv);
    }
}
```