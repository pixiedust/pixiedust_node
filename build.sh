#!/bin/bash
rm -rf build dist
python setup.py sdist upload -r pypi
