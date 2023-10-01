import os
import sys
import shutil
import urllib.request
from .logger import ServerLogger
from argparse import ArgumentParser


def get_args():
    parser = ArgumentParser()
    parser.add_argument("--musescore_path", default=None)
    parser.add_argument("--checkpoint_path", default=None)
    args = parser.parse_args()
    logger = ServerLogger("tuneease.log").get()
    logger.debug("checkpoint_path from args: " + str(args.checkpoint_path))
    logger.debug("musescore_path from args: " + str(args.musescore_path))
    return args


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

    logger = ServerLogger("tuneease.log").get()

    def __init__(self):
        self.current_file_path = os.path.abspath(__file__)
        args = get_args()
        self.logger = ServerLogger("tuneease.log").get()
        if args.checkpoint_path:
            self.checkpoint_path = lambda: os.path.abspath(args.checkpoint_path)
        else:
            self.checkpoint_path(printsuccess=True)
        if args.musescore_path:
            self.musescore_path = lambda: os.path.abspath(args.musescore_path)
        else:
            self.musescore_path(printsuccess=True)

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

    def tuneease_dir(self):
        """
        Get the path to the python code directory.

        Args:
            None

        Returns:
            str: The path to the python code directory.

        Example:
            >>> path_util = PathUtility()
            >>> tuneease_dir = path_util.tuneease_dir()
        """
        return os.path.dirname(self.current_file_path)

    def musescore_path(self, printsuccess=False):
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
        mscore_mac = "mscore" if sys.platform != "win32" else "MuseScore"
        musescore_windows = "MuseScore" if sys.platform != "win32" else "MuseScore4.exe"
        musescore_linux = (
            "MuseScore.AppImage" if sys.platform.startswith("linux") else None
        )
        path = shutil.which(mscore_mac)
        if path:
            return path
        path = shutil.which(musescore_windows)
        if path:
            return path
        directories = list()
        if sys.platform.startswith("linux"):
            directories += [os.path.join(self.project_directory(), "temp")]
        elif sys.platform == "darwin":
            directories += [
                "/Applications/MuseScore 4.app/Contents/Resources/bin",
                os.path.join(os.getenv("HOME"), "bin"),
            ]
        elif sys.platform == "win32":
            directories += [
                r"C:\Program Files\MuseScore 4\bin",
                r"C:\Program Files (x86)\MuseScore 4\bin",
            ]
        for directory in directories:
            if musescore_windows:
                path = os.path.join(directory, musescore_windows)
                if os.path.exists(path):
                    if printsuccess:
                        toprint = f"Found museScore {path}"
                        self.logger.info(toprint)
                    return path
            if mscore_mac:
                path = os.path.join(directory, mscore_mac)
                if os.path.exists(path):
                    if printsuccess:
                        toprint = f"Found museScore {path}"
                        self.logger.info(toprint)
                    return path
            if musescore_linux:
                path = os.path.join(directory, musescore_linux)
                if os.path.exists(path):
                    if printsuccess:
                        toprint = f"Found museScore {path}"
                        self.logger.info(toprint)
                    return path
                if sys.platform.startswith("linux"):
                    self.logger.info(
                        "Sometimes terminal downloads are too slow. Download with your browser:"
                    )
                    fileurl = "https://cdn.jsdelivr.net/musescore/v4.1.1/MuseScore-4.1.1.232071203-x86_64.AppImage"
                    self.logger.info(fileurl, "\nThen, move it this spot:")
                    filename = os.path.join(
                        self.project_directory(), "temp", "MuseScore.AppImage"
                    )
                    self.logger.info(filename)
                    os.makedirs(
                        os.path.join(self.project_directory(), "temp"), exist_ok=True
                    )
                    urllib.request.urlretrieve(
                        fileurl, filename, reporthook=self.download_progress_bar
                    )
                    toprint = f"Downloaded {filename}."
                    self.logger.info(toprint)
                    toprint = f"Please perform `chmod +x {filename}`"
                    self.logger.info(toprint)
                    return filename
        self.logger.info("On Windows and macOS, install MuseScore through the website:")
        self.logger.info("[https://musescore.org/en](https://musescore.org/en).")
        self.logger.info(
            "Attempts are made to find it automatically. If necessary, use --musescore_path <path>"
        )
        return None

    def checkpoint_path(self, printsuccess=False):
        path = os.path.join(self.project_directory(), "checkpoint.pth")
        if not os.path.exists(path):
            self.logger.info(
                "Install the below at the following path or use --checkpoint_path <path>"
            )
            fileurl = "https://1drv.ms/u/s!ArHNvccy1VzPkWGKXZDQY5k-kDi4?e=fFxcEq"
            self.logger.info(fileurl)
            self.logger.info(path)
            return None
        else:
            if printsuccess:
                toprint = f"Found museScore {path}"
                self.logger.info(toprint)
            return path

    def download_progress_bar(self, blocknum, blocksize, totalsize):
        downloaded = blocknum * blocksize
        percent_complete = (downloaded / totalsize) * 100
        self.logger.info(f"Downloaded {percent_complete:.2f}% from {totalsize}")
