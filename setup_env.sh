#!/bin/bash

MINICONDA_DIR=my_miniconda2_directory
VENV=dyfi
PYVER=3.5

DEPS="psutil scipy numpy geopy matplotlib basemap pyyaml geojson requests pillow sphinx pytest pytest-mpl flake8"

echo "If you have permissions issues, make sure your conda installation is not root-only"

if [ "$#" -le 1 ]; then
    #turn off whatever other virtual environment user might be in
    source deactivate
    
    #remove any previous virtual environments called $VENV
    conda remove --name $VENV --all -y
    
    #create a new virtual environment called $VENV with the below list of dependencies installed into it
    conda create --name $VENV --yes -c anaconda -c conda-forge -c ioos python=3.5 $DEPS -y

else
    conda install --yes -c anaconda -c conda-forge -c ioos python=3.5 $DEPS -y
fi

#do pip installs of those things that are not available via conda.
#pip install -r requirements.txt

# Add PYTHONPATH to mypy environment
echo "Editing $MINICONDA_DIR to add Python environment."
ENV_DIR=${MINICONDA_DIR}/envs/${VENV}/etc/conda/activate.d
mkdir -p $ENV_DIR
cp env_vars.sh $ENV_DIR

echo "Make sure ${ENV_DIR}/env_vars.sh points to this installation."
echo "Type 'source activate $VENV' to use this new virtual environment."

