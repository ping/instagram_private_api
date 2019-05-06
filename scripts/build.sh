#!/bin/zsh
# Build instapy-cli

rm -Rf build
rm -Rf dist
python setup.py sdist
python setup.py bdist_wheel