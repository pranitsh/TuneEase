import os
import pytest
from werkzeug.datastructures import FileStorage
from ..converter import Converter
from ..pathutility import PathUtility
from ..tuneease import TuneEase


@pytest.fixture
def get_converter():
    path_util = PathUtility()
    museScore_path = path_util.musescore_path()
    return Converter(log_file="tuneease.log", museScore_path=museScore_path)


@pytest.fixture
def get_music_file():
    tuneease = TuneEase()
    random_score_file = tuneease.random_score()
    assert os.path.exists(random_score_file)
    return random_score_file


def test_converter_init(get_converter):
    converter = get_converter
    assert isinstance(converter, Converter)


def test_converter_save_file(get_converter, get_music_file):
    converter = get_converter
    music_file = get_music_file
    destination_folder = "temp"
    filepath = converter.save_file(
        FileStorage(
            stream=open(music_file),
            filename=music_file,
            name=os.path.split(music_file)[-1],
        ),
        destination_folder,
    )
    assert os.path.exists(filepath)


@pytest.mark.benchmark(min_rounds=10)
def test_benchmark_convert(benchmark, get_converter, get_music_file):
    converter = get_converter
    music_file = get_music_file
    result = benchmark(converter.convert_to, music_file, output_extension=".xml")
    assert os.path.exists(result)
