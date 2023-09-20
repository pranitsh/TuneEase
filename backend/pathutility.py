from pathlib import Path
import os
import sys
import shutil

class PathUtility:
    def __init__(self):
        self.current_file_path = Path(__file__).resolve()

    def project_directory(self):
        return self.current_file_path.parent.parent.as_posix()

    def combine_paths(self, *args):
        return Path(*args).as_posix()

    def museScore_path(self):
        mscore_mac_executable = 'mscore' if sys.platform != 'win32' else 'mscore.exe'
        museScore_window_executable = 'MuseScore' if sys.platform != 'win32' else 'MuseScore.exe'
        museScore_linux_executable = 'MuseScore.AppImage' if sys.platform.startswith('linux') else None
        path = shutil.which(mscore_mac_executable)
        if path:
            return path
        path = shutil.which(museScore_window_executable)
        if path:
            return path
        directories = list()
        if sys.platform.startswith('linux'):
            # linux
            directories += [
                os.path.join(self.project_directory(), 'temp')
            ]
        if sys.platform == 'darwin':
            directories += [
                '/Applications/MuseScore 4.app/Contents/Resources/bin',
                os.path.join(os.getenv('HOME'), 'bin')
            ]
        if sys.platform == 'win32':
            directories += [
                r'C:\Program Files\MuseScore 4\bin',
                r'C:\Program Files (x86)\MuseScore 4\bin'
            ]
        for directory in directories:
            if museScore_window_executable:
                path = os.path.join(directory, museScore_window_executable)
                if os.path.exists(path):
                    return path
            if mscore_mac_executable:
                path = os.path.join(directory, mscore_mac_executable)
                if os.path.exists(path):
                    return path
            if museScore_linux_executable:
                path = os.path.join(directory, museScore_linux_executable)
                if os.path.exists(path):
                    return path
        raise FileNotFoundError('MuseScore installation not found. Use the flag --museScore_path')
