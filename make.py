#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Make tool

Usage:
  make.py run <task-name>
  make.py [options]
  make.py -h | --help  

Options:
  -h --help                         Show this screen.
  -d --debug                        Enable debug mode.
  --version                         Show version.
  
Examples:
  python make.py -h

Tasks:
  - clear
  - get-wx
  - get-bossa
  - get-ndk
  - build-android
"""

import os
import shutil
import stat
import sys
import tarfile
import zipfile
import glob
import pwd
import platform
import pathlib

from simple_zip import ZipFileWithPermissions

from docopt import docopt
from slugify import slugify
from tqdm import tqdm

from subprocess import call, check_call
from shutil import copyfile, copytree, copy2

import urllib.request as urllib2
import urllib.parse as urlparse


def main(options):
    make_debug = False
    make_task = ""

    # show all params for debug
    if ("--debug" in options and options["--debug"]) or (
        "-d" in options and options["-d"]
    ):
        make_debug = True

    if make_debug:
        debug("You have executed with options:")
        message(str(options))
        message("")

    # bind options
    if "<task-name>" in options:
        make_task = options["<task-name>"]

    # validate data
    debug("Validating data...")

    # validate task
    if not make_task:
        error("Task is invalid")

    # clear
    if make_task == "clear":
        run_task_clear()

    # build android library
    elif make_task == "build-android":
        run_task_build_android()

    # get wxWidgets
    elif make_task == "get-wx":
        run_task_get_wx()

    # get BOSSA
    elif make_task == "get-bossa":
        run_task_get_bossa()

    # test android
    elif make_task == "test-android":
        run_task_test_android()

    # get ndk
    elif make_task == "get-ndk":
        run_task_get_ndk()

    else:
        error("Invalid task name: {0}".format(make_task))

    message("")
    debug("FINISHED!")


def debug(msg):
    print("> {0}".format(msg))


def message(msg):
    print("{0}".format(msg))


def error(msg):
    print("ERROR: {0}".format(msg))
    sys.exit(1)


def download_file(url, dest=None, filename=None):
    """
    Download and save a file specified by url to dest directory,
    """
    u = urllib2.urlopen(url)

    scheme, netloc, path, query, fragment = urlparse.urlsplit(url)

    if filename:
        dest_filename = filename
    else:
        dest_filename = os.path.basename(path)

        if not dest_filename:
            dest_filename = "downloaded.file"

    if dest:
        dest_filename = os.path.join(dest, dest_filename)

    with open(dest_filename, "wb") as f:
        debug("Downloading...")
        message("")

        meta = u.info()
        meta_func = meta.getheaders if hasattr(meta, "getheaders") else meta.get_all
        meta_length = meta_func("Content-Length")
        file_size = None
        pbar = None

        if meta_length:
            file_size = int(meta_length[0])

        if file_size:
            pbar = tqdm(total=file_size)

        file_size_dl = 0
        block_sz = 8192

        while True:
            dbuffer = u.read(block_sz)

            if not dbuffer:
                break

            dbuffer_len = len(dbuffer)
            file_size_dl += dbuffer_len
            f.write(dbuffer)

            if pbar:
                pbar.update(dbuffer_len)

        if pbar:
            pbar.close()
            message("")

        return dest_filename


def get_download_filename(url):
    scheme, netloc, path, query, fragment = urlparse.urlsplit(url)
    filename = os.path.basename(path)

    if not filename:
        filename = "downloaded.file"

    return filename


def list_subdirs(from_path):
    dirs = filter(
        lambda x: os.path.isdir(os.path.join(from_path, x)), os.listdir(from_path)
    )
    return dirs


def remove_all_files(base_path, files_to_remove):
    for file_to_remove in files_to_remove:
        try:
            file_to_remove = os.path.join(base_path, file_to_remove)

            if os.path.isdir(file_to_remove):
                shutil.rmtree(file_to_remove)
            else:
                os.remove(file_to_remove)
        except IOError as e:
            # we will ignore this message, is not important now
            # debug('Error removing file: {0} - {1}'.format(file_to_remove, e.strerror))
            pass
        except OSError as e:
            # we will ignore this message, is not important now
            # debug('Error removing file: {0} - {1}'.format(file_to_remove, e.strerror))
            pass


def get_cur_dir():
    return pathlib.Path().absolute()


def create_dir(dir_path):
    if not os.path.isdir(dir_path):
        os.makedirs(dir_path)


def remove_dir(dir_path):
    if os.path.isdir(dir_path):
        shutil.rmtree(dir_path)


def remove_file(filename):
    if os.path.isfile(filename):
        os.remove(filename)


def make_tarfile(output_filename, source_dir):
    with tarfile.open(output_filename, "w:gz") as tar:
        tar.add(source_dir, arcname=os.path.basename(source_dir))


def write_to_file(dirname, filename, content):
    full_file_path = os.path.join(dirname, filename)
    remove_file(full_file_path)
    create_dir(dirname)

    with open(full_file_path, "w") as f:
        f.write(content)
        f.close()


def find_files(directory, pattern):
    files = [
        f
        for (dir, subdirs, fs) in os.walk(directory)
        for f in fs
        if f.endswith(pattern)
    ]

    return files


def is_test_user():
    user = pwd.getpwuid(os.getuid())[0]
    return user == "paulo"


def replace_in_file(filename, old_string, new_string):
    with open(filename) as f:
        s = f.read()
        if old_string not in s:
            # print('"{old_string}" not found in {filename}.'.format(**locals()))
            return

    # Safely write the changed content, if found in the file
    with open(filename, "w") as f:
        # print('Changing "{old_string}" to "{new_string}" in {filename}'.format(**locals()))
        s = s.replace(old_string, new_string)
        f.write(s)


def run_task_clear():
    debug("Clearing...")
    remove_dir("build")
    remove_file(".DS_Store")
    remove_file("Thumbs.db")


def run_task_build_android():
    debug("Build for Android...")

    cur_dir = get_cur_dir()
    ndk_dir = os.path.join(cur_dir, "build", "android-ndk-r21d")

    build_dir = os.path.join("build", "android")
    dist_dir = os.path.join("dist", "android")

    remove_dir(build_dir)
    create_dir(build_dir)

    remove_dir(dist_dir)
    create_dir(dist_dir)

    archs = ["arm64-v8a", "armeabi-v7a", "x86", "x86_64"]

    for arch in archs:
        # compile
        arch_dir = os.path.join(build_dir, arch)
        create_dir(arch_dir)

        command = " ".join(
            [
                "cmake ../../../",
                "-DCMAKE_SYSTEM_NAME=Android",
                "-DCMAKE_ANDROID_ARCH_ABI={0}".format(arch),
                "-DCMAKE_ANDROID_NDK={0}".format(ndk_dir),
                "-DCMAKE_ANDROID_STL_TYPE=c++_static",
                "-DTARGET_SYSTEM=android",
            ]
        )
        check_call(command, cwd=arch_dir, shell=True)

        command = " ".join(["make"])
        check_call(command, cwd=arch_dir, shell=True)

        # install
        install_dir = os.path.join(dist_dir, arch)
        remove_dir(install_dir)
        create_dir(install_dir)

        from_file = os.path.join(arch_dir, "libbossac.so")
        to_file = os.path.join(install_dir, "libbossac.so")

        copy2(from_file, to_file)


def run_task_test_android():
    debug("Test for Android...")

    archs = ["arm64-v8a", "armeabi-v7a", "x86", "x86_64"]

    dist_dir = os.path.join("dist", "android")

    for arch in archs:
        install_dir = os.path.join(dist_dir, arch)
        lib_file = "libbossac.so"

        command = " ".join(["file", lib_file])
        check_call(command, cwd=install_dir, shell=True)


def run_task_get_wx():
    wx_url = "https://github.com/wxWidgets/wxWidgets/releases/download/v3.1.4/wxWidgets-3.1.4.tar.bz2"
    target_dir = os.path.join("build")

    create_dir(target_dir)

    # download
    if os.path.isfile(os.path.join(target_dir, "wxWidgets-3.1.4.tar.bz2")):
        debug("Downloaded: WXWIDGETS")
    else:
        debug("Download: WXWIDGETS")
        download_file(wx_url, target_dir, "wxWidgets-3.1.4.tar.bz2")
        debug("Downloaded: WXWIDGETS")

    # extract
    if os.path.isdir(os.path.join(target_dir, "wxWidgets-3.1.4")):
        debug("Extracted: WXWIDGETS")
    else:
        debug("Extract: WXWIDGETS")
        tar = tarfile.open(os.path.join(target_dir, "wxWidgets-3.1.4.tar.bz2"), "r:bz2")
        tar.extractall(target_dir)
        tar.close()
        debug("Extracted: WXWIDGETS")


def run_task_get_bossa():
    bossa_url = "https://github.com/shumatech/BOSSA/archive/master.tar.gz"
    target_dir = os.path.join("build")

    create_dir(target_dir)

    # download
    if os.path.isfile(os.path.join(target_dir, "BOSSA-master.tar.gz")):
        debug("Downloaded: BOSSA")
    else:
        debug("Download: BOSSA")
        download_file(bossa_url, target_dir, "BOSSA-master.tar.gz")
        debug("Downloaded: BOSSA")

    # extract
    if os.path.isdir(os.path.join(target_dir, "BOSSA-master")):
        debug("Extracted: BOSSA")
    else:
        debug("Extract: BOSSA")
        tar = tarfile.open(os.path.join(target_dir, "BOSSA-master.tar.gz"), "r:gz")
        tar.extractall(target_dir)
        tar.close()
        debug("Extracted: BOSSA")

    # patch
    debug("Patch: BOSSA")
    replace_in_file(
        os.path.join(target_dir, "BOSSA-master", "src", "bossac.cpp"),
        'Version " VERSION "',
        "1.9.1",
    )
    debug("Patched: BOSSA")


def run_task_get_ndk():
    system_name = platform.system().lower()
    ndk_url = ""
    ndk_filename = ""
    ndk_folder = "android-ndk-r21d"

    if system_name == "darwin":
        ndk_url = "https://dl.google.com/android/repository/android-ndk-r21d-darwin-x86_64.zip"
        ndk_filename = "android-ndk-r21d-darwin-x86_64.zip"
    elif system_name == "linux":
        ndk_url = (
            "https://dl.google.com/android/repository/android-ndk-r21d-linux-x86_64.zip"
        )
        ndk_filename = "android-ndk-r21d-linux-x86_64.zip"
    else:
        error("Platform not supported (only macos and linux)")

    target_dir = os.path.join("build")

    create_dir(target_dir)

    # download
    if os.path.isfile(os.path.join(target_dir, ndk_filename)):
        debug("Downloaded: NDK")
    else:
        debug("Download: NDK")
        download_file(ndk_url, target_dir, ndk_filename)
        debug("Downloaded: NDK")

    # extract
    if os.path.isdir(os.path.join(target_dir, ndk_folder)):
        debug("Extracted: NDK")
    else:
        debug("Extract: NDK")
        zip = ZipFileWithPermissions(os.path.join(target_dir, ndk_filename))
        zip.extractall(target_dir)
        zip.close()
        debug("Extracted: NDK")


if __name__ == "__main__":
    # main CLI entrypoint
    args = docopt(__doc__, version="1.0.0")
    main(args)