import os
from flask import Flask, request, send_file, send_from_directory
from flask_cors import CORS
import music21 
import random
from .logger import ServerLogger
from .pathutility import PathUtility
from .converter import Converter
from .track_generation import main as music_generator

util = PathUtility()
logger = ServerLogger().get()
static_path = os.path.join(util.project_directory(), 'frontend', 'build', 'static')
logger.debug(static_path)
app = Flask(__name__, static_url_path='/static', static_folder=static_path)
app.config["museScore_path"] = util.musescore_path()
CORS(app)

@app.route('/')
def index():
    util = PathUtility()
    build_dir = os.path.join(util.project_directory(), 'frontend', 'build')
    return send_from_directory(build_dir, 'index.html')

@app.route('/<path:filename>')
def serve_file(filename):
    util = PathUtility()
    build_dir = os.path.join(util.project_directory(), 'frontend', 'build')
    logger = ServerLogger("tuneease.log").get()
    logger.info("Received a request " + build_dir)
    return send_from_directory(build_dir, filename)


@app.route('/convert', methods=['POST'])
def convert():
    logger = ServerLogger("tuneease.log").get()
    logger.info("Received a /convert request")
    if app.config["museScore_path"]:
        converter = Converter(museScore_path=app.config["museScore_path"])
        try:
            file = request.files['file']
            output_filepath = converter.convert(file)
            return send_file(output_filepath, as_attachment=True, download_name=output_filepath)
        except Exception as e:
            return str(e), 500
    else:
        file = request.files['file']
        assert file.filename != '', "File is empty"
        filetail = os.path.split(file.filename)[-1]
        filepath = os.path.join(util.project_directory(), 'temp', filetail)
        file.save(filepath)
        fileext = os.path.splitext(filepath)[0]
        musicxml_file = music21.converter.parse(filepath)
        try:
            musicxml_file.write('musicxml', fp=fileext + ".xml")
        except Exception as E:
            logger.error("Had an error converting the generated content to xml (likely some error with the input file)" + str(E))
            return 500
        return send_file(fileext + ".xml", as_attachment=True, download_name=fileext + ".xml")



@app.route('/split', methods=['POST'])
def split():
    logger = ServerLogger("tuneease.log").get()
    logger.info("Received a /split request " + str(request.files) + " with " + str(request.form))
    try:
        file = request.files['file']
        assert file.filename != '', "File is empty"
        assert os.path.splitext(file.filename)[1] == ".xml", "File is not .xml"
        start_number = int(request.form['start'])
        if (end_number := request.form.get("end")) is not None:
            end_number = int(end_number)
        else:
            end_number = ""
    except Exception as e:
        logger.error(f"Failed to start /split. Error message: {str(e)}")
        return 'Possible Clientside error', 500
    util = PathUtility()
    filepath = os.path.join(util.project_directory(), 'temp', file.filename)
    measure_filepath = os.path.join(util.project_directory(), 'temp', os.path.splitext(file.filename)[0] + '-measure-' + str(start_number) + "-" + str(end_number))
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    file.save(filepath)
    try:
        parsed_song = music21.converter.parse(filepath)
        measures = []
        for part in parsed_song.parts:
            measures.extend(part.getElementsByClass('Measure'))
        try:
            if end_number == "":
                stream = measures[start_number].write('musicxml', measure_filepath + ".xml")
            else: 
                measures_to_combine = measures[start_number-1:end_number]
                stream = music21.stream.Stream()
                for measure in measures_to_combine:
                    stream.append(measure)
        except Exception as E:
            logger.error(f'Your input numbers were outside of the measures of the part (probably): {str(e)}')
            return f'Your input numbers were outside of the measures of the part (probably)', 500
        stream.write('musicxml', measure_filepath + ".xml")
        return send_file(measure_filepath + ".xml", as_attachment=True, download_name=measure_filepath + ".xml")
    except Exception as e:
        logger.error(f'Error: {str(e)}')
        return f'Error', 500

@app.route('/number', methods=['POST'])
def number():
    logger = ServerLogger("tuneease.log").get()
    logger.info("Received a /number request " + str(request.files))
    try:
        file = request.files['file']
        assert file.filename != '', "File is empty"
        assert os.path.splitext(file.filename)[1] == ".xml", "File is not .musixml"
    except Exception as e:
        logger.error(f"Failed to start /number. Error message: {str(e)}")
        return 'Possible Clientside error', 500

    util = PathUtility()
    filepath = os.path.join(util.project_directory(), 'temp', file.filename)
    output_filepath = os.path.join(util.project_directory(), 'temp', os.path.splitext(file.filename)[0] + '-number.xml')
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
        score.write('musicxml', output_filepath)
        return send_file(output_filepath, as_attachment=True, download_name=output_filepath)
    except Exception as e:
        logger.error(f'Error: {str(e)}')
        return f'Error', 500

@app.route('/random', methods=['GET'])
def random_score():
    logger = ServerLogger("tuneease.log").get()
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
        filepath = os.path.join(util.project_directory(), 'temp', "random.xml")
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        s.write('musicxml', filepath)
        return send_file(filepath, as_attachment=True, download_name=filepath)
    except Exception as e:
        logger.error(f'Error: {str(e)}')
        return f'Error', 500


@app.route('/generate', methods=['POST', 'GET'])
def generate():
    """Do note the lowercase in the boolean values!"""
    logger = ServerLogger("tuneease.log").get()
    logger.info("Received a /generate request with " + str(request.form))
    conditional_tracks = "".join([
        str(int(request.form.get("condition-lead", "false") == "true")),
        str(int(request.form.get("condition-bass", "false") == "true")),
        str(int(request.form.get("condition-drums", "false") == "true")),
        str(int(request.form.get("condition-guitar", "false") == "true")),
        str(int(request.form.get("condition-piano", "false") == "true")),
        str(int(request.form.get("condition-strings", "false") == "true")), 
        str(int(True))
    ])
    content_tracks = "".join([
        str(int(request.form.get("content-lead", "false") == "true")),
        str(int(request.form.get("content-bass", "false") == "true")),
        str(int(request.form.get("content-drums", "false") == "true")),
        str(int(request.form.get("content-guitar", "false") == "true")),
        str(int(request.form.get("content-piano", "true") == "true")),
        str(int(request.form.get("content-strings", "false") == "true")), 
        str(int(False))
    ])
    seed = request.form.get("seed", "0")

    if 'file' in request.files:
        logger.info("Performing with input file")
        file = request.files['file']
        assert file.filename != '', "File is empty"
        assert os.path.splitext(file.filename)[1] == ".xml" or os.path.splitext(file.filename)[1] == ".mid", "File is not .xml or .mid"
        util = PathUtility()
        filepath = os.path.join(util.project_directory(), 'temp', file.filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        file.save(filepath)
    else:
        logger.info("Performing with template file")
        time_signature = request.form.get('time_signature', '4/4')
        quarter_length = 1.0 / (int(time_signature.split('/')[1]) / 4)
        number_measures = int(request.form.get('number_measures', '10')) * int(time_signature.split('/')[0])
        score =  music21.stream.Stream()
        time_signature = music21.meter.TimeSignature(time_signature)
        score.append(time_signature)
        metadata = music21.metadata.Metadata()
        metadata.title = 'Random'
        metadata.composer = 'MuseTune'
        score.insert(0, metadata)
        note_names = ['A4', 'B4', 'C4', 'D4', 'E4', 'F4', 'G4']
        for _ in range(number_measures):
            note_name = random.choice(note_names)
            note = music21.note.Note(note_name, quarterLength=quarter_length)
            score.append(note)
        util = PathUtility()
        filepath = os.path.join(util.project_directory(), 'temp', "template.mid")
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        score.write('midi', filepath)
    if os.path.splitext(filepath)[1] == ".xml":
        output_filepath = os.path.splitext(filepath)[0] + ".mid"
        musicxml_file = music21.converter.parse(filepath)
        try:
            musicxml_file.write('midi', fp=output_filepath)
        except Exception as exception:
            logger.error("Had an error converting to midi with {} - {}".format(filepath, str(exception)))
            raise exception
    elif os.path.splitext(filepath)[1] == ".mid":
        output_filepath = filepath
    cmd = [
        '--file_path', output_filepath,
        "--seed", str(seed),
        "--conditional_tracks", conditional_tracks,
        "--content_tracks", content_tracks,       
    ]
    save_path = os.path.splitext(music_generator(cmd))[0]
    musicxml_file = music21.converter.parse(save_path + ".mid")
    try:
        musicxml_file.write('musicxml', fp=save_path + ".xml")
    except Exception as E:
        logger.error("Had an error converting the generated content to xml (likely some error with the input file)" + str(E))
        return 500
    return send_file(save_path + ".xml", as_attachment=True, download_name=save_path + ".xml")

def run_app():
    app.run(host='0.0.0.0', port=8080, debug=True)

if __name__ == '__main__':
    run_app()