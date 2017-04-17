import os
import sys

from cx_Freeze import setup, Executable

sys.argv.append("build")

interpreter_path = os.path.dirname(sys.executable)

include_files = [r"{0}\DLLs\tcl86t.dll".format(interpreter_path),
                 r"{0}\DLLs\tk86t.dll".format(interpreter_path),
                 "mttkinter.py",
                 "ITwython.py",
                 "auth_gui.py",
                 "token_manager.py",
                 "../data/secrets"]

os.environ['TCL_LIBRARY'] = r'{0}\tcl\tcl8.6'.format(interpreter_path)
os.environ['TK_LIBRARY'] = r'{0}\tcl\tk8.6'.format(interpreter_path)

includes = []

base = None
if sys.platform == 'win32':
    base = 'Win32GUI'

executables = [
    Executable('main_app.py', base=base)
]

setup(name='TwISN',
      version='0.1',
      description='Simple Twitter client.',
      options={"build_exe": {"includes": includes, "include_files": include_files}},
      executables=executables
      )
