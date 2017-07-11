#!/bin/bash
rm -rf build dist
python setup.py sdist
python setup.py bdist_wheel
#twine upload dist/*
