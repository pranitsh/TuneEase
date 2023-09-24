import os
import pytest
from ..tuneease import TuneEase
from ..pathutility import PathUtility
from ..converter import Converter

@pytest.fixture
def get_tuneease():
    path_util = PathUtility()
    museScore_path = path_util.museScore_path()
    return TuneEase(museScore_path=museScore_path)

@pytest.fixture
def get_music_file():
    tuneease = TuneEase()
    random_score_file = tuneease.random_score()
    assert os.path.exists(random_score_file)
    return random_score_file

@pytest.fixture
def get_converter():
    path_util = PathUtility()
    museScore_path = path_util.museScore_path()
    return Converter(log_file="server.log", museScore_path=museScore_path)

def test_tuneease_init(get_tuneease):
    tuneease = get_tuneease
    assert isinstance(tuneease, TuneEase)
    
def test_convert(get_tuneease, get_music_file, get_converter):
    converter = get_converter
    music_file = get_music_file
    midi_path = converter.convert_to(music_file, output_extension=".midi")
    assert os.path.exists(midi_path)
    tuner = get_tuneease
    output_filepath = tuner.convert(midi_path)
    assert os.path.exists(output_filepath)

def test_split(get_tuneease, get_music_file):
    music_file = get_music_file
    tuner = get_tuneease
    output_filepath = tuner.split(music_file, 1, 2)
    assert os.path.exists(output_filepath)

def test_number(get_tuneease, get_music_file):
    music_file = get_music_file
    tuner = get_tuneease
    output_filepath = tuner.number(music_file)
    assert os.path.exists(output_filepath)
    
def test_random_score(get_tuneease):
    tuner = get_tuneease
    random_score_file = tuner.random_score()
    assert os.path.exists(random_score_file)

def test_generate(get_tuneease):
    tuner = get_tuneease
    test_param = {
        "condition-lead": "True",
        "content-bass": "True",
    }
    output_filepath = tuner.generate(test_param)
    assert os.path.exists(output_filepath)    
