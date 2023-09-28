import os
from ..pathutility import PathUtility

def test_path_utility_init():
    path_util = PathUtility()
    assert isinstance(path_util, PathUtility)
    assert os.path.exists(os.path.abspath(__file__))

def test_path_utility_project_directory():
    path_util = PathUtility()
    project_dir = path_util.project_directory()
    assert os.path.isdir(project_dir)

def test_path_utility_museScore_path():
    path_util = PathUtility()
    musescore_path = path_util.musescore_path()
    assert os.path.exists(musescore_path)
