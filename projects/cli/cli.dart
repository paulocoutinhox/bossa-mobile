import 'dart:ffi';
import 'dart:io' show Platform, Directory;
import 'package:ffi/ffi.dart';
import 'package:path/path.dart' as p;

typedef MainFunction = int Function(int argc, Pointer<Utf8> argv);
typedef MainFunctionFFI = Int32 Function(Int32 argc, Pointer<Utf8> argv);

typedef TestFlutterFunction = void Function();
typedef TestFlutterFunctionFFI = Void Function();

typedef TestFlutterPointerFunction = Pointer<Utf8> Function(
    int argc, Pointer<Utf8> argv);
typedef TestFlutterPointerFunctionFFI = Pointer<Utf8> Function(
    Int32 argc, Pointer<Utf8> argv);

main() {
  Directory currentDir = Directory.current;
  String mainPath = p.join(currentDir.path, 'lib', 'x86_64');
  String libPath = '';

  // open the dynamic library
  if (Platform.isLinux) {
    libPath = p.join(mainPath, 'libbossac.so');
  } else if (Platform.isMacOS) {
    libPath = p.join(mainPath, 'libbossac.dylib');
  } else if (Platform.isWindows) {
    libPath = p.join(mainPath, 'bossac.dll');
  } else {
    throw Exception("Your system is not supported!");
  }

  // close function (linux and android) for `dlclose` symbol lookup
  final DynamicLibrary dlLib = DynamicLibrary.process();

  final int Function(Pointer<Void>) dlCloseFun = dlLib
      .lookup<NativeFunction<Int32 Function(Pointer<Void>)>>("dlclose")
      .asFunction();

  {
    // open native lib
    final nativeLib = DynamicLibrary.open(libPath);

    // lookup function
    MainFunction function = nativeLib
        .lookup<NativeFunction<MainFunctionFFI>>("bossa_main")
        .asFunction();

    // first call
    function(
        0,
        Utf8.toUtf8(
          "bossac -i -d --port=/dev/ttyS0 -U -i -e -w -v FevoFirmware.bin -R",
        ));

    // close lib for reload
    int retClose = dlCloseFun(nativeLib.handle);

    if (retClose == 0) {
      print("Native library closed");
    }
  }

  {
    // open native lib
    final nativeLib = DynamicLibrary.open(libPath);

    // lookup function
    MainFunction function = nativeLib
        .lookup<NativeFunction<MainFunctionFFI>>("bossa_main")
        .asFunction();

    // second call
    function(
        0,
        Utf8.toUtf8(
          "bossac --help",
        ));

    // close lib for reload
    int retClose = dlCloseFun(nativeLib.handle);

    if (retClose == 0) {
      print("Native library closed");
    }
  }
}
