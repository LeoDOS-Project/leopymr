#! /bin/bash
find . -type f -name '*.py' -exec autopep8 --in-place --aggressive --aggressive '{}' \;
pylint *.py
pylint docker
