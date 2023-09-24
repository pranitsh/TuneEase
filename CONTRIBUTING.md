To run the tests and see the benchmarks:

```sh
pip install pytest==7.4.2 pytest-benchmark==4.0.0
cd keyflare
pytests tests/
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
