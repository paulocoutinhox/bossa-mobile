import 'dart:ffi';
import 'package:ffi/ffi.dart';
import 'dart:io';

import 'package:flutter/material.dart';

void main() {
  runApp(MyApp());
}

typedef MainFunction = int Function(int argc, Pointer<Utf8> argv);
typedef MainFunctionFFI = Int32 Function(Int32 argc, Pointer<Utf8> argv);

typedef TestFlutterFunction = void Function();
typedef TestFlutterFunctionFFI = Void Function();

typedef TestFlutterPointerFunction = Pointer<Utf8> Function(
    int argc, Pointer<Utf8> argv);
typedef TestFlutterPointerFunctionFFI = Pointer<Utf8> Function(
    Int32 argc, Pointer<Utf8> argv);

final DynamicLibrary nativeLib = Platform.isAndroid
    ? DynamicLibrary.open("libbossac.so")
    : DynamicLibrary.process();

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Bossa Demo',
      theme: ThemeData(
        primarySwatch: Colors.blue,
        visualDensity: VisualDensity.adaptivePlatformDensity,
      ),
      debugShowCheckedModeBanner: false,
      home: HomePageView(),
    );
  }
}

class HomePageView extends StatefulWidget {
  @override
  _HomePageViewState createState() => _HomePageViewState();
}

class _HomePageViewState extends State<HomePageView> {
  final controller = TextEditingController(text: "bossac -p /dev/ttyS0");

  var consoleMessages = "> Output message will go here";

  void doExecuteTest() {
    TestFlutterFunction function = nativeLib
        .lookup<NativeFunction<TestFlutterFunctionFFI>>("test_flutter_void")
        .asFunction();

    doDebug("[doExecuteTest]");

    function();
  }

  void doExecuteTestPointer() {
    TestFlutterPointerFunction function = nativeLib
        .lookup<NativeFunction<TestFlutterPointerFunctionFFI>>(
            "test_flutter_pointer")
        .asFunction();

    doDebug("[doExecuteTestPointer]");

    var result = function(3, Utf8.toUtf8(controller.text));

    doDebug("Result: ${Utf8.fromUtf8(result)}");
  }

  void doExecuteMain() {
    MainFunction function = nativeLib
        .lookup<NativeFunction<MainFunctionFFI>>("bossa_main")
        .asFunction();

    doDebug("[doExecuteMain]");

    var result = function(0, Utf8.toUtf8(controller.text));

    doDebug("Return: $result");
  }

  void doDebug(String message) {
    setState(() {
      consoleMessages = "> " + message + "\n\n" + consoleMessages;
    });
  }

  void doClear() {
    setState(() {
      consoleMessages = "> Cleared!";
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text("Bossa Mobile"),
      ),
      body: Container(
        child: Padding(
          padding: const EdgeInsets.all(8.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Text(
                "Type command to run:",
                textAlign: TextAlign.center,
                style: TextStyle(
                  fontSize: 15,
                ),
              ),
              TextField(
                controller: controller,
                decoration: new InputDecoration(
                  hintText: 'Type here',
                ),
              ),
              SizedBox(
                height: 20,
              ),
              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Column(
                    children: [
                      MaterialButton(
                        child: Text(
                          "Execute",
                          style: TextStyle(color: Colors.white),
                        ),
                        color: Colors.deepOrange,
                        onPressed: () {
                          doExecuteMain();
                        },
                      ),
                      SizedBox(
                        width: 20,
                      ),
                      MaterialButton(
                        child: Text(
                          "Test",
                          style: TextStyle(color: Colors.white),
                        ),
                        color: Colors.deepOrange,
                        onPressed: () {
                          doExecuteTest();
                        },
                      ),
                    ],
                  ),
                  SizedBox(
                    width: 20,
                  ),
                  Column(
                    children: [
                      MaterialButton(
                        child: Text(
                          "Test pointer",
                          style: TextStyle(color: Colors.white),
                        ),
                        color: Colors.deepOrange,
                        onPressed: () {
                          doExecuteTestPointer();
                        },
                      ),
                      SizedBox(
                        width: 20,
                      ),
                      MaterialButton(
                        child: Text(
                          "Clear",
                          style: TextStyle(color: Colors.white),
                        ),
                        color: Colors.deepOrange,
                        onPressed: () {
                          doClear();
                        },
                      ),
                    ],
                  ),
                ],
              ),
              SizedBox(
                height: 30,
              ),
              Text(
                "$consoleMessages",
                textAlign: TextAlign.start,
                overflow: TextOverflow.fade,
                style: TextStyle(
                  fontSize: 12.0,
                  color: Colors.black87,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
