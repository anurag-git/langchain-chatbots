# Installation
## Setup your virtual environment
python -m venv .venv

## Activate your virtual environment
### Windows
.venv\scripts\activate

### Linux
source .venv/bin/activate

## Install all required python modules
pip install -r requirements.txt

# Execution
## Execute the python code
python <file_name.py> e.g. 1_chatbot-simple.py

## Execute streamlit app
streamlit run <main_file_name.py> e.g. streamlit run app.py

