.ONESHELL:
SHELL=/bin/bash
CONDA_ACTIVATE=source $$(conda info --base)/etc/profile.d/conda.sh ; conda activate ; conda activate

# run the program
default: run
run: activate
	python3 main.py

# create the new environment from the environment.yaml
.SILENT:
setup:
	conda env create --file environment.yaml 2> /dev/null || echo "team3 environment already exists"

# activate the conda environment
activate: setup
	$(CONDA_ACTIVATE) team3 || exit 1

# run the linter on all the python files
lint: activate
	autoflake --in-place --recursive --remove-all-unused-imports --remove-unused-variables --expand-star-imports *.py
	pylint *.py

# remove the team3 environment
remove-env: activate
	conda env remove -n team3

# update the environment.yaml when a new package is installed
update:
	conda env export > environment.yaml
