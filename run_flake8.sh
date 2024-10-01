#!/bin/bash

# linters start
echo "Running flake8 checks..."
python -m flake8 .

if [ $? -ne 0 ]; then
    echo "flake8 returned an error. Aborting further checks."
    exit 1
fi

echo "Flake8 checks successfully passed."
