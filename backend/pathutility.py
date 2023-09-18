from pathlib import Path

class PathUtility:
    def __init__(self):
        self.current_file_path = Path(__file__).resolve()

    def project_directory(self):
        return self.current_file_path.parent.parent.parent.as_posix()

    def combine_paths(self, *args):
        return Path(*args).as_posix()
