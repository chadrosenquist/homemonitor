# Add the module's directory to the path.
# This allows the user to run the program without setting PYTHONPATH.
# Ex: python homemonitor
import os
import sys
lib_path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(lib_path)

# noinspection PyPep8
import homemonitor.cli


if __name__ == '__main__':
    sys.exit(homemonitor.cli.main(sys.argv[1:]))
