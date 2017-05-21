import os
import sys
# noinspection PyUnresolvedReferences
from multiprocessing import Queue

from cx_Freeze import setup, Executable

# Cx_freeze n'importe pas Queue si on ne lui dit pas manuellement. "noinspection" inidque que l'import ne doit pas
# être supprimé par l'IDE (l'IDE va le supprimer automatiquement puisqu'il ne parait pas utilisé dans ce fichier)

# Ajoute l'argument build pour lancer setup.py normalement au lieu de "python setup.py -build"
sys.argv.append("build")

# On récupère le chemin du dossier python
interpreter_path = os.path.dirname(sys.executable)

# Ajoute les fichiers suivants
# r"" permet de conserver les slashs/antislashs sans les échapper.
include_files = [r"{0}\DLLs\tcl86t.dll".format(interpreter_path),
                 r"{0}\DLLs\tk86t.dll".format(interpreter_path),
                 "lib/mttkinter.py",
                 "auth_gui.py",
                 "user_gui.py",
                 "options_gui.py",
                 "token_manager.py",
                 "path_finder.py",
                 "ITwython.py",
                 "logger_conf.py",
                 "../dev_assets/list_tweets.py",
                 "../assets/app_tokens",
                 "../assets/twisn.png"]

# Ajoute les variables d'environnement nécessaires
os.environ['TCL_LIBRARY'] = r'{0}\tcl\tcl8.6'.format(interpreter_path)
os.environ['TK_LIBRARY'] = r'{0}\tcl\tk8.6'.format(interpreter_path)

includes = []

base = None
if sys.platform == 'win32':
    base = 'Win32GUI'

executables = [
    Executable('main_app.py', base=base, icon="../assets/twisn.ico")
]

setup(name='Twysn',
      version='0.9',
      description='Simple client Twitter.',
      options={"build_exe": {"includes": includes, "include_files": include_files}},
      executables=executables
      )
