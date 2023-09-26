To perform some quality checks on the code:
```sh
pip install flake8 flake8-duplicated pylint autoflake
pylint --min-similarity-lines 2 .\tuneease\
flake8 .
```
Current score is a 2.45 out of 10. This is not going into precommit checks yet.

To run the tests and see the benchmarks:
```sh
pip install pytest==7.4.2 pytest-benchmark==4.0.0
pytest -v
```

To test before you upload:
```sh
pip install -e .
```

To build the package and upload:

```sh
# Make sure to delete dist/ if necessary
pip install setuptools wheel twine
python setup.py sdist bdist_wheel
twine upload dist/*
```
