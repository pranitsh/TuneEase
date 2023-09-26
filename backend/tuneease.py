import os
from click import FileError
import music21 
import random
from .logger import ServerLogger
from .pathutility import PathUtility
from .converter import Converter
from .track_generation import main as music_generator

class TuneEase:
    """
    A class for generating, converting, and processing music using TuneEase.

    Attributes:
        util (PathUtility): An instance of PathUtility for handling file paths.
        museScore_path (str): The path to the MuseScore executable.
        logger (ServerLogger): An instance of ServerLogger for logging messages.
        converter (Converter): An instance of Converter for file conversion.

    Methods:
        __init__(self, museScore_path=""):
        convert(self, filepath):
        split(self, filepath, start, end=""):
        number(self, filepath):
        random_score(self, time_signature='4/4', number_measures='8'):
        generate(self, form, file=None):

    Example:
        >>> tuneease = TuneEase()
        >>> output_path = tuneease.convert(input_path)
    """
    util = PathUtility()
    museScore_path = util.museScore_path()
    logger = ServerLogger("tuneease.log").get()
    def __init__(self, museScore_path = ""):
        if museScore_path:
            self.museScore_path = museScore_path
        self.converter = Converter(museScore_path=self.museScore_path)

    def convert(self, filepath):
        """
        Converts a music file to the MusicXML format.

        Args:
            filepath (str): The path to the input music file.

        Returns:
            str or Exception: The path to the converted MusicXML file if successful, or an exception if an error occurs.

        Example:
            >>> tuneease = TuneEase()
            >>> converted_file = tuneease.convert("input_music.mid")
        """
        self.logger.info("Running convert")
        try:
            output_filepath = self.converter.convert_to(filepath)
            return output_filepath
        except Exception as e:
            return e

    def split(self, filepath, start, end = ""):
        """
        Get specific measures from a music file and save the result as MusicXML.

        Args:
            filepath (str): The path to the input music file.
            start (int): The starting measure number.
            end (int, optional): The ending measure number. If not provided, only the start measure is extracted.

        Returns:
            str: The path to the split MusicXML file.

        Example:
            >>> tuneease = TuneEase()
            >>> split_filepath = tuneease.split('inputfile.xml', 2, 5)
        """
        self.logger.info("Running split" + filepath + " with " + str(start) + "-" + str(end))
        filepath = os.path.join(self.util.project_directory(), 'temp', filepath)
        measure_filepath = os.path.join(self.util.project_directory(), 'temp', os.path.splitext(filepath)[0] + '-measure-' + str(start) + "-" + str(end) + ".xml")
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        try:
            parsed_song = music21.converter.parse(filepath)
            measures = []
            for part in parsed_song.parts:
                measures.extend(part.getElementsByClass('Measure'))
            if end == "":
                stream = measures[start]
            else: 
                measures_to_combine = measures[start-1:end]
                stream = music21.stream.Stream()
                for measure in measures_to_combine:
                    stream.append(measure)
            stream.write('musicxml', measure_filepath)
        finally:
            return measure_filepath

    def number(self, filepath):
        """
        Add measure numbers to a music score file.

        Args:
            filepath (str): The path to the input music score file.

        Returns:
            str: The path to the output music score file with measure numbers.

        Example:
            >>> tuneease = TuneEase()
            >>> output_file = tuneease.number("input.xml")
        """
        self.logger.info("Running number on {}".format(filepath))
        filepath = os.path.join(self.util.project_directory(), 'temp', filepath)
        output_filepath = os.path.join(self.util.project_directory(), 'temp', os.path.splitext(filepath)[0] + '-number.xml')
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        score = music21.converter.parse(filepath)
        for part in score.parts:
            for i, measure in enumerate(part.getElementsByClass(music21.stream.Measure)):
                text_expression = music21.expressions.TextExpression("Measure {}".format(i + 1))
                text_expression.style.absoluteY = 20  
                text_expression.style.justify = 'left'
                measure.insert(0, text_expression)
        score.write('musicxml', output_filepath)
        return output_filepath

    def random_score(self, time_signature = '4/4', number_measures = '8'):
        """
        Generate a random music score.

        Args:
            time_signature (str): The time signature of the generated score.
            number_measures (str): The number of measures in the generated score.

        Returns:
            str: The path to the generated random music score file.

        Example:
            >>> tuneease = TuneEase()
            >>> random_score_file = tuneease.random_score(time_signature='4/4', number_measures='8')

        Notes:
            - This method generates a random music score with random notes along with random correct or incorrect signs above each image.
        """
        self.logger.info("Running random score")
        quarter_length = 1.0 / (int(time_signature.split('/')[1]) / 4)
        number_measures = int(number_measures) * int(time_signature.split('/')[0])
        s = music21.stream.Stream()
        ts = music21.meter.TimeSignature(time_signature)
        s.append(ts)
        md = music21.metadata.Metadata()
        md.title = 'Random'
        md.composer = 'MuseTune'
        s.insert(0, md)
        notes = ['A4', 'B4', 'C4', 'D4', 'E4', 'F4', 'G4']
        lyrics = ['✔', 'x']
        for i in range(number_measures):
            note_name = random.choice(notes)
            n = music21.note.Note(note_name, quarterLength=quarter_length)
            n.lyric = random.choice(lyrics)
            s.append(n)
        idx = 0
        while os.path.exists(os.path.join(self.util.project_directory(), 'temp', f"random{idx}.xml")):
            idx += 1
        filepath = os.path.join(self.util.project_directory(), 'temp', f"random{idx}.xml")
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        s.write('musicxml', filepath)
        return filepath

    def generate(self, input_dict = dict(), file = None, gpu= False):
        """
        Generate music based on user input or a template file.

        Args:
            form (dict): A dictionary containing user input parameters.
            file (str): Optional. A file to base the generated content on.

        Returns:
            str: The path to the generated music XML file.

        Example:
            >>> tuneease = TuneEase()
            >>> user_input = {
            ...     'condition-lead': 'True',
            ...     'condition-bass': 'False',
            ... }
            >>> generated_file = tuneease.generate()

        Notes:
            - Defaults follow below: condition is what is in the input, content is what is to be outputed
            conditional_tracks = "".join([
                str(int(form.get("condition-lead", False) == True)),
                str(int(form.get("condition-bass", False) == True)),
                str(int(form.get("condition-drums", False) == True)),
                str(int(form.get("condition-guitar", False) == True)),
                str(int(form.get("condition-piano", False) == True)),
                str(int(form.get("condition-strings", False) == True)),
                str(int(True))
            ])
            content_tracks = "".join([
                str(int(form.get("content-lead", False) == True)),
                str(int(form.get("content-bass", False) == True)),
                str(int(form.get("content-drums", False) == True)),
                str(int(form.get("content-guitar", False) == True)),
                str(int(form.get("content-piano", True) == True)),
                str(int(form.get("content-strings", False) == True)),
                str(int(False))
            ])
            seed = input_dict.get("seed", 0)
        """
        self.logger.info("Received a generate request with {}".format(str(input_dict)))
        conditional_tracks = "".join([
            str(int(input_dict.get("condition-lead", False))),
            str(int(input_dict.get("condition-bass", False))),
            str(int(input_dict.get("condition-drums", False))),
            str(int(input_dict.get("condition-guitar", False))),
            str(int(input_dict.get("condition-piano", False))),
            str(int(input_dict.get("condition-strings", False))),
            str(int(True))
        ])
        content_tracks = "".join([
            str(int(input_dict.get("content-lead", False))),
            str(int(input_dict.get("content-bass", False))),
            str(int(input_dict.get("content-drums", False))),
            str(int(input_dict.get("content-guitar", False))),
            str(int(input_dict.get("content-piano", True))),
            str(int(input_dict.get("content-strings", True))),
            str(int(False))
        ])
        seed = input_dict.get("seed", 0)
        if file:
            assert os.path.exists(file)
            filepath = file
        else:
            self.logger.info("Performing with template file")
            time_signature = input_dict.get('time_signature', '4/4')
            quarter_length = 1.0 / (int(time_signature.split('/')[1]) / 4)
            number_measures = int(input_dict.get('number_measures', '2')) * int(time_signature.split('/')[0])
            stream = music21.stream.Stream()
            time_signature = music21.meter.TimeSignature(time_signature)
            stream.append(time_signature)
            metadata = music21.metadata.Metadata()
            metadata.title = 'Random'
            metadata.composer = 'MuseTune'
            stream.insert(0, metadata)
            notes = ['A4', 'B4', 'C4', 'D4', 'E4', 'F4', 'G4']
            for _ in range(number_measures):
                note_name = random.choice(notes)
                n = music21.note.Note(note_name, quarterLength=quarter_length)
                stream.append(n)
            filepath = os.path.join(self.util.project_directory(), 'temp', "template.xml")
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            stream.write('musicxml', filepath)

        if os.path.splitext(filepath)[1] == ".xml":
            output_filepath = os.path.splitext(filepath)[0] + ".mid"
            musicxml_file = music21.converter.parse(filepath)
            try:
                musicxml_file.write('midi', fp=output_filepath)
            except Exception as e:
                self.logger.error("Had an error converting to midi with {} - {}".format(filepath, str(e)))
                raise e
        elif os.path.splitext(filepath)[1] == ".mid":
            output_filepath = filepath
        else:
            raise FileError("Only .mid or .xml accepted atm")
        cmd = [
            '--file_path', output_filepath,
            "--seed", str(seed),
            "--conditional_tracks", conditional_tracks,
            "--content_tracks", content_tracks,
        ]
        save_path = os.path.splitext(music_generator(cmd, gpu=gpu))[0]
        musicxml_file = music21.converter.parse(save_path + ".mid")
        try:
            musicxml_file.write('musicxml', fp=save_path + ".xml")
        except Exception as e:
            self.logger.error("Had an error converting the generated content to xml (probably some error with input file) - {}".format(str(e)))
            raise e
        return save_path + ".xml"

def tuneease():
    tuneease = TuneEase()
    print(tuneease.generate())    
    
if __name__=="__main__":
    tuneease()