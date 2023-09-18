import os
import subprocess
from logger import ServerLogger
from pathutility import PathUtility
import platform

class Converter:
    def __init__(self, log_file="server.log", museScore_path = None):
        self.logger = ServerLogger(log_file).get()
        self.util = PathUtility()
        self.project_directory = self.util.project_directory()
        self.ubuntu = 'Ubuntu' in platform.platform()
        if museScore_path == None:
            raise ValueError("The value of the museScorePath cannot be null in this case. " 
                             "Provide input arguments to the path of museScore when running server.py")
        self.museScore_path = museScore_path

    def save_file(self, file, destination_folder="temp"):
        try:
            assert file.filename != '', "File is empty"
            filepath = self.util.combine_paths(self.project_directory, destination_folder, file.filename)
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            file.save(filepath)
            return filepath
        except Exception as e:
            self.logger.error(f"Failed to save the file. Error message: {str(e)}", "error")
            raise

    def convert_to(self, filepath, output_extension: str = ".xml"):
        output_filepath = os.path.splitext(filepath)[0] + output_extension
        try:
            if not self.ubuntu:
                if not os.path.exists(output_filepath):
                    subprocess.run([self.museScore_path, filepath, '-o', output_filepath], check=True, cwd=self.project_directory)
            return output_filepath
        except subprocess.CalledProcessError as e:
            self.error(f"Failed to run MuseScore command. Error message: {str(e)}")
        except Exception as e:
            self.error(f"Failed to convert score to MusicXML. Error message: {str(e)}")
    
    def convert(self, file, output_extension: str = ".xml"):
        filepath = self.save_file(file)
        output_filepath = self.convert_to(filepath, output_extension=output_extension)
        return output_filepath