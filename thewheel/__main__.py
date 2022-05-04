"""Runs the main program.

Add the module's directory to the path.
This allows the user to run the program without setting PYTHONPATH.
Ex: python homemonitor
"""
import os
import sys
LIB_PATH = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(LIB_PATH)

# noinspection PyPep8
import thewheel.cli


if __name__ == '__main__':
    sys.exit(thewheel.cli.main(sys.argv[1:]))
