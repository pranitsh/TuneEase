import os
import subprocess
from .logger import ServerLogger
from .pathutility import PathUtility

class Converter:
    """
    A class for converting music files to MusicXML format using MuseScore.

    Attributes:
        logger (ServerLogger): An instance of ServerLogger for logging messages.
        util (PathUtility): An instance of PathUtility for handling file paths.
        project_directory (str): The path to the project directory.
        museScore_path (str): The path to the MuseScore executable.

    Methods:
        __init__(self, log_file="server.log", museScore_path=None):
        save_file(self, file, destination_folder="temp"):
        convert_to(self, filepath, output_extension=".xml"):
        convert(self, file, output_extension=".xml"):

    Raises:
        ValueError: If museScore_path is not provided during initialization.
    """

    def __init__(self, log_file="server.log", museScore_path = None):
        self.logger = ServerLogger(log_file).get()
        self.util = PathUtility()
        self.project_directory = self.util.project_directory()
        if museScore_path == None:
            raise ValueError("The value of the museScorePath cannot be null in this case. " 
                             "Provide input arguments to the path of museScore when running server.py")
        self.museScore_path = museScore_path

    def save_file(self, file, destination_folder="temp"):
        """
        Save an uploaded file from the server to a temporary file storage folder.

        Args:
            file (FileStorage): The uploaded file object.
            destination_folder (str, optional): The name of the temporary folder. Defaults to "temp".

        Returns:
            str: The path to the saved file.

        Raises:
            AssertionError: If the uploaded file is empty or has no filename.
            Exception: If any other error occurs during file saving.

        Example:
            filepath = converter.save_file(uploaded_file, destination_folder="uploads")
        """
        try:
            assert file.filename != '', "File is empty"
            filepath = os.path.join(self.project_directory, destination_folder, file.filename)
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            file.save(filepath)
            return filepath
        except Exception as e:
            self.logger.error(f"Failed to save the file. Error message: {str(e)}", "error")
            raise

    def convert_to(self, filepath, output_extension: str = ".xml"):
        """
        Convert some music file to the MusicXML format using MuseScore.

        Args:
            filepath (str): The path to the input music file.
            output_extension (str, optional): The file extension for the converted output. Defaults to ".xml".

        Returns:
            str: The path to the converted MusicXML file.

        Raises:
            subprocess.CalledProcessError: If the MuseScore command fails.
            Exception: If any other error occurs during conversion.

        Example:
            output_filepath = converter.convert_to(input_filepath, output_extension=".mxl")
        """
        output_filepath = os.path.splitext(filepath)[0] + output_extension
        try:
            subprocess.run([self.museScore_path, filepath, '-o', output_filepath], check=True, cwd=self.project_directory)
            return output_filepath
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to run MuseScore command. Error message: {str(e)}")
        except Exception as e:
            self.logger.error(f"Failed to convert score to MusicXML. Error message: {str(e)}")
    
    def convert(self, file, output_extension: str = ".xml"):
        """
        Save and convert an uploaded music file from the server to the MusicXML format.

        Args:
            file (FileStorage): The uploaded music file object.
            output_extension (str, optional): The file extension for the converted output. Defaults to ".xml".

        Returns:
            str: The path to the converted MusicXML file.

        Example:
            converted_filepath = converter.convert(uploaded_music_file, output_extension=".mxl")
        """
        filepath = self.save_file(file)
        output_filepath = self.convert_to(filepath, output_extension=output_extension)
        return output_filepath