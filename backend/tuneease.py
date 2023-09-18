import os
import music21 
import random

from torch import NoneType
from logger import ServerLogger
from pathutility import PathUtility
from converter import Converter
from getmusic.track_generation import main as music_generator
from argparse import ArgumentParser

class TuneEase:
    
    def __init__(self, arguments = None):
        if arguments == None:
            self.args = self.parse()
        else: 
            self.args = self.parse(arguments=arguments)
            
    def parse(self, arguments=None):
        parser = ArgumentParser(description="Process music files with TuneEase")
        
        # General arguments
        parser.add_argument('--file', type=str, help="Path to the music file.")
        parser.add_argument('--museScore', type=str, help="Path to museScore.")
        parser.add_argument('--measure_number', type=int, help="Measure number for splitting.")
        
        # Random Score arguments
        parser.add_argument('--time_signature', default='4/4', help="Time signature for random score generation.")
        parser.add_argument('--number_measures', default=8, type=int, help="Number of measures for random score generation.")
        
        # Generate method arguments
        parser.add_argument('--conditional_tracks', type=str, help="Conditional tracks for music generation.")
        parser.add_argument('--content_tracks', type=str, help="Content tracks for music generation.")
        parser.add_argument('--seed', default=0, type=int, help="Seed for music generation.")
        
        if arguments is None:
            args = parser.parse_args()
        else:
            args = parser.parse_args(arguments)
        
        return args

    def convert(self):
        logger = ServerLogger("server.log").get()
        logger.info("Received a /convert request")
        converter = Converter(self.args.museScore)
        try:
            output_filepath = converter.convert_to(self.args.file)
            return output_filepath
        except Exception as e:
            print(e)
            exit


    def split(self, ):
        logger = ServerLogger("server.log").get()
        logger.info("Received a request")
        try:
            file = request.files['file']
            assert file.filename != '', "File is empty"
            assert os.path.splitext(file.filename)[1] == ".xml", "File is not .xml"
            measure_number = request.form['measure_number']
            assert measure_number != "" and measure_number != None, "Measure Number is empty"
            measure_number = int(measure_number)
        except Exception as e:
            logger.error(f"Failed to start /split. Error message: {str(e)}")
            return 'Possible Clientside error', 500

        util = PathUtility()
        filepath = util.combine_paths(util.project_directory(), 'temp'.filename)
        measure_filepath = util.combine_paths(util.project_directory(), 'temp', os.path.splitext(file.filename)[0] + '-measure-' + str(measure_number))
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        file.save(filepath)
        
        try:
            # Split the MusicXML into measures and save as separate files
            measures = music21.converter.parse(filepath).makeVoices().makeMeasures()
            measures[measure_number].write('musicxml', measure_filepath + ".xml")
            return measure_filepath + ".xml"
        except Exception as e:
            logger.error(f'Error: {str(e)}')
            return f'Error', 500
        

    def number(self, ):
        logger = ServerLogger("server.log").get()
        logger.info("Received a /number request " + str(request.files))
        try:
            file = request.files['file']
            assert file.filename != '', "File is empty"
            assert os.path.splitext(file.filename)[1] == ".xml", "File is not .musixml"
        except Exception as e:
            logger.error(f"Failed to start /number. Error message: {str(e)}")
            return 'Possible Clientside error', 500

        util = PathUtility()
        filepath = util.combine_paths(util.project_directory(), 'temp'.filename)
        output_filepath = util.combine_paths(util.project_directory(), 'temp', os.path.splitext(file.filename)[0] + '-number.xml')
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        file.save(filepath)
        
        try:
            score = music21.converter.parse(filepath)
            for part in score.parts:
                for i, measure in enumerate(part.getElementsByClass(music21.stream.Measure)):
                    text_expression = music21.expressions.TextExpression(f"Measure {i + 1}")
                    text_expression.style.absoluteY = 20  # Adjust for positioning
                    text_expression.style.justify = 'left'
                    measure.insert(0, text_expression)
            return output_filepath
        except Exception as e:
            logger.error(f'Error: {str(e)}')
            return f'Error', 500


    def random_score(self, ):
        logger = ServerLogger("server.log").get()
        logger.info("Received a /random request")
        try:
            time_signature = request.form.get('time_signature', '4/4')
            quarter_length = 1.0 / (int(time_signature.split('/')[1]) / 4)
            number_measures = int(request.form.get('number_measures', '8')) * int(time_signature.split('/')[0])
            s =  music21.stream.Stream()
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

            util = PathUtility()
            filepath = util.combine_paths(util.project_directory(), 'temp', "random.xml")
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            s.write('musicxml'path)
            return filepath
        except Exception as e:
            logger.error(f'Error: {str(e)}')
            return f'Error', 500


    def gnerate(self, ):
        logger = ServerLogger("server.log").get()
        logger.info("Received a /generate request with " + str(request.form))
        conditional_tracks = ", ".join([
            str(request.form.get("condition-lead", "False") == "True"),
            str(request.form.get("condition-bass", "False") == "True"),
            str(request.form.get("condition-drums", "False") == "True"),
            str(request.form.get("condition-guitar", "False") == "True"),
            str(request.form.get("condition-piano", "False") == "True"),
            str(request.form.get("condition-strings", "False") == "True"), 
            str(True)
        ])
        content_tracks = ", ".join([
            str(request.form.get("content-lead", "False") == "True"),
            str(request.form.get("content-bass", "False") == "True"),
            str(request.form.get("content-drums", "False") == "True"),
            str(request.form.get("content-guitar", "False") == "True"),
            str(request.form.get("content-piano", "True") == "True"),
            str(request.form.get("content-strings", "False") == "True"), 
            str(False)
        ])
        seed = request.form.get("seed", "0")

        if 'file' in request.files:
            logger.info("Performing with input file")
            file = request.files['file']
            assert file.filename != '', "File is empty"
            assert os.path.splitext(file.filename)[1] == ".xml", "File is not .xml"

            util = PathUtility()
            filepath = util.combine_paths(util.project_directory(), 'temp'.filename)
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            file.save(filepath)
        else:
            logger.info("Performing with template file")
            time_signature = request.form.get('time_signature', '4/4')
            quarter_length = 1.0 / (int(time_signature.split('/')[1]) / 4)
            number_measures = int(request.form.get('number_measures', '2')) * int(time_signature.split('/')[0])
            s =  music21.stream.Stream()
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
            util = PathUtility()
            filepath = util.combine_paths(util.project_directory(), 'temp', "template.xml")
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            s.write('musicxml'path)

        converter = Converter(museScore_path=app.config["museScore_path"])
        try:
            output_filepath = converter.convert_to(filepath, output_extension=".mid")
        except Exception as e:
            print(e)
            return str(e), 500

        cmd = [
            '--file_path', output_filepath,
            "--seed", str(seed),
            "--conditional_tracks", conditional_tracks,
            "--content_tracks", content_tracks,       
        ]

        save_path = music_generator(cmd)

        try:
            output_filepath = converter.convert_to(file, output_extension=".xml")
        except:
            return 500

        return send_file(save_path + ".xml", as_attachment=True, download_name=save_path + ".xml")