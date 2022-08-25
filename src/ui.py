import obj
import sys
from os import name, system
from os.path import join


def clear():
    if name == "nt":
        system("cls")
    else:
        system("clear")

def space():
    print()

def restart():
    system(f"py {join(obj.directory, 'main.py')}")
    sys.exit()