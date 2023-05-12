import bpy
import os
import sys
import re
from pprint import pprint


enc = sys.getfilesystemencoding()


def abspath(path):
    return os.path.abspath(bpy.path.abspath(path))


def quotepath(path):
    if " " in path:
        path = f'"{path}"'
    return path


def add_path_to_recent_files(path):
    '''
    add the path to the recent files list, for some reason it's not done automatically when saving or loading
    '''

    try:
        recent_path = bpy.utils.user_resource('CONFIG', path="recent-files.txt")
        with open(recent_path, "r+", encoding=enc) as f:
            content = f.read()
            f.seek(0, 0)
            f.write(path.rstrip('\r\n') + '\n' + content)

    except (IOError, OSError):
        pass


def open_folder(path):
    import platform
    import subprocess

    if platform.system() == "Windows":
        os.startfile(path)
    elif platform.system() == "Darwin":
        subprocess.Popen(["open", path])
    else:
        # subprocess.Popen(["xdg-open", path])
        os.system(f'xdg-open "{path}" > /dev/null 2> /dev/null &')


def makedir(pathstring):
    if not os.path.exists(pathstring):
        os.makedirs(pathstring)
    return pathstring


def printd(d, name=''):
    print(f"\n{name}")
    pprint(d, sort_dicts=False)


def get_incremented_paths(currentblend):
    path = os.path.dirname(currentblend)
    filename = os.path.basename(currentblend)

    filenameRegex = re.compile(r"(.+)\.blend\d*$")

    if mo := filenameRegex.match(filename):
        name = mo[1]
        numberendRegex = re.compile(r"(.*?)(\d+)$")

        if mo := numberendRegex.match(name):
            basename = mo[1]
            numberstr = mo[2]
        else:
            basename = f"{name}_"
            numberstr = "000"

        number = int(numberstr)

        incr = number + 1
        incrstr = str(incr).zfill(len(numberstr))

        incrname = basename + incrstr + ".blend"

        return os.path.join(path, incrname), os.path.join(path, f'{name}_01.blend')
