import os
import music21 
import random
from logger import ServerLogger
from pathutility import PathUtility
from converter import Converter
from getmusic.track_generation import main as music_generator

class TuneEase:
    util = PathUtility()
    museScore_path = util.museScore_path()
    logger = ServerLogger("tuneease.log").get()
    def __init__(self, museScore_path = ""):
        if museScore_path:
            self.museScore_path = museScore_path
        self.converter = Converter(museScore_path=self.museScore_path)

    def convert(self, filepath):
        self.logger.info("Running convert")
        try:
            output_filepath = self.converter.convert(filepath)
            return output_filepath
        except Exception as e:
            return e

    def split(self, filepath, start, end = ""):
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
        filepath = os.path.join(self.util.project_directory(), 'temp', "random.xml")
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        s.write('musicxml', filepath)
        return filepath

    def generate(self, form, file = None):
        self.logger.info("Received a generate request with {}".format(str(form)))
        conditional_tracks = ", ".join([
            str(form.get("condition-lead", "False") == "True"),
            str(form.get("condition-bass", "False") == "True"),
            str(form.get("condition-drums", "False") == "True"),
            str(form.get("condition-guitar", "False") == "True"),
            str(form.get("condition-piano", "False") == "True"),
            str(form.get("condition-strings", "False") == "True"),
            str(True)
        ])
        content_tracks = ", ".join([
            str(form.get("content-lead", "False") == "True"),
            str(form.get("content-bass", "False") == "True"),
            str(form.get("content-drums", "False") == "True"),
            str(form.get("content-guitar", "False") == "True"),
            str(form.get("content-piano", "True") == "True"),
            str(form.get("content-strings", "False") == "True"),
            str(False)
        ])
        seed = form.get("seed", "0")

        if file:
            self.logger.info("Performing with input file")
            assert file.filename != '', "File is empty"
            assert os.path.splitext(file.filename)[1] == ".xml", "File is not .xml"
            filepath = os.path.join(self.util.project_directory(), 'temp', file.filename)
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            file.save(filepath)
        else:
            self.logger.info("Performing with template file")
            time_signature = form.get('time_signature', '4/4')
            quarter_length = 1.0 / (int(time_signature.split('/')[1]) / 4)
            number_measures = int(form.get('number_measures', '2')) * int(time_signature.split('/')[0])
            s = music21.stream.Stream()
            ts = music21.meter.TimeSignature(time_signature)
            s.append(ts)
            md = music21.metadata.Metadata()
            md.title = 'Random'
            md.composer = 'MuseTune'
            s.insert(0, md)
            notes = ['A4', 'B4', 'C4', 'D4', 'E4', 'F4', 'G4']
            for _ in range(number_measures):
                note_name = random.choice(notes)
                n = music21.note.Note(note_name, quarterLength=quarter_length)
                s.append(n)
            filepath = os.path.join(self.util.project_directory(), 'temp', "template.xml")
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            s.write('musicxml', filepath)

        output_filepath = os.path.splitext(filepath)[0] + ".mid"
        musicxml_file = music21.converter.parse(filepath)
        try:
            musicxml_file.write('midi', fp=output_filepath)
        except Exception as e:
            self.logger.error("Had an error converting to midi with {} - {}".format(filepath, str(e)))
            raise e

        cmd = [
            '--file_path', output_filepath,
            "--seed", str(seed),
            "--conditional_tracks", conditional_tracks,
            "--content_tracks", content_tracks,
        ]

        save_path = os.path.splitext(music_generator.main(cmd))[0]
        musicxml_file = music21.converter.parse(save_path + ".mid")
        try:
            musicxml_file.write('musicxml', fp=save_path + ".xml")
        except Exception as e:
            self.logger.error("Had an error converting the generated content to xml (probably model error) - {}".format(str(e)))
            raise e
        return save_path + ".xml"