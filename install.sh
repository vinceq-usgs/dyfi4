#!/bin/bash

echo "Path:"
echo $PATH

VENV=dyfi

# Turn off whatever other virtual environment user might be in
source deactivate


conda=$(which conda)
if [ ! "$conda" ] ; then
    echo "Install miniconda before proceeding."
    exit
fi

# Create a conda virtual environment
echo "Creating the $VENV virtual environment:"
conda env create --name $VENV -f environment.yml

# Activate the new environment
echo "Activating the $VENV virtual environment"
source activate $VENV

# This package
# echo "Installing..."
# pip install -r requirements.txt

# Tell the user they have to activate this environment
echo "Type 'source activate $VENV' to use this new virtual environment."
echo "To run tests, use 'pytest tests/'"

