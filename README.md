# prof_backend

## Dependencies

Python 3.8.10
python modules from requirements.txt

## Install dependencies

`python3 -m virtualenv venv`\
`source venv/bin/activate`\
`pip install -r requirements.txt`

## Start services

`python3 -m providers.SERVICENAME`

## Start app

`uvicorn main:app --reload`\
or \
`python3 main.py`