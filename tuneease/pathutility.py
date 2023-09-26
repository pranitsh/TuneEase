import os
import sys
import shutil
import urllib.request
from .logger import ServerLogger

class PathUtility:
    """
    A utility class for handling file paths and locating the MuseScore executable's path.

    Attributes:
        current_file_path (str): The absolute path of the current file.

    Methods:
        __init__(self):
        project_directory(self):
        museScore_path(self):
        
    Example:
        >>> path_util = PathUtility()
        >>> path_util.current_file_path
        /path/to/the/file
    """
    def __init__(self):
        self.current_file_path = os.path.abspath(__file__)
        self.checkpoint_path()
        self.musescore_path()
        self.logger = ServerLogger('server.log').get()

    def project_directory(self):
        """
        Get the path to the project directory.

        Args:
            None

        Returns:
            str: The path to the project directory.

        Example:
            >>> path_util = PathUtility()
            >>> project_dir = path_util.project_directory()
        """
        return os.path.dirname(os.path.dirname(self.current_file_path))

    def musescore_path(self):
        """
        Locate and return the path to the MuseScore executable.

        Args:
            None

        Returns:
            str: The path to the MuseScore executable.

        Raises:
            FileNotFoundError: If MuseScore installation is not found.

        Example:
            >>> path_util = PathUtility()
            >>> muse_score_path = path_util.museScore_path()
        
        Notes:
            - On Linux, `<project directory>/temp/MuseScore.AppImage`
            - On macOS, the standard installation path and the user's 'bin' directory.
            - On Windows, it searches in common installation paths for 32 and 64-bit versions.
        """
        mscore_mac = 'mscore' if sys.platform != 'win32' else "MuseScore"
        musescore_windows = 'MuseScore' if sys.platform != 'win32' else 'MuseScore4.exe'
        musescore_linux = 'MuseScore.AppImage' if sys.platform.startswith('linux') else None
        path = shutil.which(mscore_mac)
        if path:
            return path
        path = shutil.which(musescore_windows)
        if path:
            return path
        directories = list()
        if sys.platform.startswith('linux'):
            directories += [
                os.path.join(self.project_directory(), 'temp')
            ]
        elif sys.platform == 'darwin':
            directories += [
                '/Applications/MuseScore 4.app/Contents/Resources/bin',
                os.path.join(os.getenv('HOME'), 'bin')
            ]
        elif sys.platform == 'win32':
            directories += [
                r'C:\Program Files\MuseScore 4\bin',
                r'C:\Program Files (x86)\MuseScore 4\bin'
            ]
        for directory in directories:
            if musescore_windows:
                path = os.path.join(directory, musescore_windows)
                if os.path.exists(path):
                    print(f'Found museScore {path}')
                    return path
            if mscore_mac:
                path = os.path.join(directory, mscore_mac)
                if os.path.exists(path):
                    print(f'Found museScore {path}')
                    return path
            if musescore_linux:
                path = os.path.join(directory, musescore_linux)
                if os.path.exists(path):
                    print(f'Found museScore {path}')
                    return path
                if sys.platform.startswith('linux'):
                    self.logger.info("Sometimes terminal downloads are too slow. Download with your browser:")
                    fileurl = 'https://cdn.jsdelivr.net/musescore/v4.1.1/MuseScore-4.1.1.232071203-x86_64.AppImage'
                    self.logger.info(fileurl, "\nThen, move it this spot:")
                    filename = os.path.join(self.project_directory(), "temp", "MuseScore.AppImage")
                    self.logger.info(filename)
                    os.makedirs(os.path.join(self.project_directory(), "temp"), exist_ok=True)
                    urllib.request.urlretrieve(fileurl, filename, reporthook=self.download_progress_bar)
                    toprint = f'Downloaded {filename}.'
                    self.logger.info(toprint)
                    toprint = f'Please perform `chmod +x {filename}`'
                    self.logger.info(toprint)
                    return filename
        self.logger.info("On Windows and macOS, install MuseScore through the website:")
        self.logger.info("[https://musescore.org/en](https://musescore.org/en).")
        self.logger.info("Attempts are made to find it automatically. Tested for windows.")
        self.logger.info("Test for Windows. Untested for macOS")
        raise FileNotFoundError('MuseScore installation not found.' \
            'If necessary, use the flag --museScore_path <museScore_path>')

    def checkpoint_path(self):
        if not os.path.exists(os.path.join(self.project_directory(), "checkpoint.pth")):
            self.logger.info("You have to install the below:")
            fileurl = 'https://1drv.ms/u/s!ArHNvccy1VzPkWGKXZDQY5k-kDi4?e=fFxcEq'
            self.logger.info(fileurl)
            toprint = fileurl + "\nThen, move it this spot:"
            self.logger.info(toprint)
            filename = os.path.join(self.project_directory(), "checkpoint.pth")
            self.logger.info(filename)
            raise FileNotFoundError("Check the logs. Could not install the model checkpoint.")
        else:
            print(f'Found {os.path.join(self.project_directory(), "checkpoint.pth")}.')
            return os.path.join(self.project_directory(), "checkpoint.pth")

    def download_progress_bar(self, blocknum, blocksize, totalsize):
        downloaded = blocknum * blocksize
        percent_complete = (downloaded / totalsize) * 100
        print(f'Downloaded {percent_complete:.2f}% from {totalsize}', end='\r')
