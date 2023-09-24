To check for duplicated code:
```sh
pip install flake8 flake8-duplicated pylint autoflake
# from project directory
pylint --min-similarity-lines 2 .\backend\
flake8 .

```

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
