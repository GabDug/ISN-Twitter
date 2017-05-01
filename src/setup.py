import os
import sys

from cx_Freeze import setup, Executable

# Add the argument build so we can run setup.py as usual
# Ajoute l'argument build pour lancer setup.py normalement au lieu de "python setup.py -build"
sys.argv.append("build")

# Get the python interpreter path directory
interpreter_path = os.path.dirname(sys.executable)

include_files = [r"{0}\DLLs\tcl86t.dll".format(interpreter_path),
                 r"{0}\DLLs\tk86t.dll".format(interpreter_path),
                 "mttkinter.py",
                 "ITwython.py",
                 "auth_gui.py",
                 "token_manager.py",
                 "../dev_assets/list_tweets.py",
                 "../data/secrets",
                 "../assets/twisn.png"]

os.environ['TCL_LIBRARY'] = r'{0}\tcl\tcl8.6'.format(interpreter_path)
os.environ['TK_LIBRARY'] = r'{0}\tcl\tk8.6'.format(interpreter_path)

includes = []

base = None
if sys.platform == 'win32':
    base = 'Win32GUI'

executables = [
    Executable('main_app.py', base=base, icon="../assets/twisn.ico")
]

setup(name='TwISN',
      version='0.1',
      description='Simple Twitter client.',
      options={"build_exe": {"includes": includes, "include_files": include_files}},
      executables=executables
      )
