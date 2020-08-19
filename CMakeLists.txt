cmake_minimum_required(VERSION 3.14)

project(bossac C CXX ASM)

set(P_VERSION "1.9.1")

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -O2 -std=c++11 -DVERSION=\"${P_VERSION}\"")
set(CMAKE_EXE_LINKER_FLAGS, "${CMAKE_EXE_LINKER_FLAGS} -Wl,--as-needed")
set(TARGET_SYSTEM CACHE STRING "Define the target system to build BOSSA")
set(SOURCE_CODE_DIR "build/BOSSA-master/src")
set(CMAKE_BUILD_TYPE Debug)

include_directories("build/wxWidgets-3.1.4/include")

set(COMMON_SRCS
    ${SOURCE_CODE_DIR}/Samba.cpp
    ${SOURCE_CODE_DIR}/Flash.cpp
    ${SOURCE_CODE_DIR}/D5xNvmFlash.cpp
    ${SOURCE_CODE_DIR}/D2xNvmFlash.cpp
    ${SOURCE_CODE_DIR}/EfcFlash.cpp
    ${SOURCE_CODE_DIR}/EefcFlash.cpp
    ${SOURCE_CODE_DIR}/Applet.cpp
    ${SOURCE_CODE_DIR}/WordCopyApplet.cpp
    ${SOURCE_CODE_DIR}/Flasher.cpp
    ${SOURCE_CODE_DIR}/Device.cpp
    ${SOURCE_CODE_DIR}/WordCopyArm.cpp
)

set(APPLET_SRCS 
    ${SOURCE_CODE_DIR}/WordCopyArm.asm
)

set(BOSSAC_SRCS
    ${SOURCE_CODE_DIR}/bossac.cpp
    ${SOURCE_CODE_DIR}/CmdOpts.cpp
)

if(${TARGET_SYSTEM} MATCHES "macos")
    set(COMMON_SRCS
        ${COMMON_SRCS}
        ${SOURCE_CODE_DIR}/PosixSerialPort.cpp
        ${SOURCE_CODE_DIR}/OSXPortFactory.cpp
    )

    message("> System: MACOS")
elseif(${TARGET_SYSTEM} MATCHES "linux")
    set(COMMON_SRCS
        ${COMMON_SRCS}
        ${SOURCE_CODE_DIR}/PosixSerialPort.cpp
        ${SOURCE_CODE_DIR}/LinuxPortFactory.cpp
    )

    message("> System: LINUX")
elseif(${TARGET_SYSTEM} MATCHES "android")
    set(COMMON_SRCS
        ${COMMON_SRCS}
        ${SOURCE_CODE_DIR}/PosixSerialPort.cpp
        ${SOURCE_CODE_DIR}/LinuxPortFactory.cpp
    )

    message("> System: ANDROID")
elseif(${TARGET_SYSTEM} MATCHES "windows")
    set(COMMON_SRCS
        ${COMMON_SRCS}
        ${SOURCE_CODE_DIR}/WinSerialPort.cpp
        ${SOURCE_CODE_DIR}/WinPortFactory.cpp
    )

    message("> System: WINDOWS")
else()
   message(FATAL_ERROR "Unsupported system detected, check configuration!")
endif()

set(
    ALL_FILES 
    ${COMMON_SRCS}
    ${BOSSAC_SRCS}
    CACHE INTERNAL ""
)

#add_executable(bossac ${ALL_FILES})
add_library(bossac SHARED ${ALL_FILES})

if(${TARGET_SYSTEM} MATCHES "android")
    target_link_libraries(bossac log android)
endif()
