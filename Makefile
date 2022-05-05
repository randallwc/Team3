.ONESHELL:

SHELL=/bin/bash
CONDA_ACTIVATE=source $$(conda info --base)/etc/profile.d/conda.sh ; conda activate ; conda activate

##############
# CLIENT STUFF
##############

default: run
run:
	$(CONDA_ACTIVATE) team3
	python client/main.py

setup:
	conda env create --file client/environment.yaml

lint:
	$(CONDA_ACTIVATE) team3
	autoflake --in-place --recursive --remove-all-unused-imports --remove-unused-variables --expand-star-imports client/*.py
	pylint --recursive=y client/*.py

remove-env:
	conda env remove -n team3

update:
	$(CONDA_ACTIVATE) team3
	conda env export > client/environment.yaml

##############
# SERVER STUFF
##############

server: npm-install
	echo '[OPEN WHEN CREATING DB] http://localhost:8000/api/v1/createhighscoresobject'
	cd server && nodemon server.js

npm-install:
	npm --prefix ./server install ./server

database:
	mkdir server/localDB; mongod --dbpath server/localDB

clean:
	rm -rf server/localDB
