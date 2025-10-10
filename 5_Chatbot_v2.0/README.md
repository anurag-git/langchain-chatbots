# Installation
## Setup your virtual environment
python -m venv .venv

## Activate your virtual environment
### Windows
.venv\scripts\activate

### Linux
source .venv/bin/activate

## Install all required python modules (if requirements.txt is used)
pip install -r requirements.txt

## Installs your project + all dependencies (if pyproject.toml is used)
pip install -e .  


# Execution
## Execute the python code
python <file_name.py> e.g. 1_chatbot-simple.py

## Execute streamlit app
streamlit run <main_file_name.py> e.g. streamlit run app.py


# Application Structure
chatbot-app/
│
├── app.py                    # Main Streamlit app entry point
├── requirements.txt          # Python dependencies
├── pyproject.toml            # Modern Python packaging and build system
├── README.md                 # Project documentation
├── .gitignore                # Ignore venv, __pycache__, etc.
├── .env.example              # Environment variable template
│
├── config/
│   ├── settings.yaml         # Main configuration file (API keys, model params)
│   ├── logging.conf          # Logging configuration
│   └── environments/
│       ├── development.yaml
│       ├── staging.yaml
│       └── production.yaml
│
├── monitoring/
│   ├── __init__.py
│   ├── metrics.py            # Performance metrics collection
│   ├── analytics.py          # User interaction analytics
│   └── health_checks.py      # System health monitoring
│
├── utils/
│   ├── __init__.py
│   ├── file_utils.py         # File operations
│   ├── validation.py         # Input validation
│   └── decorators.py         # Common decorators
│
├── exceptions/
│   ├── __init__.py
│   ├── chatbot_exceptions.py
│   └── api_exceptions.py
│
├── data/
│   ├── intents.json
│   └── sample_conversations/
│
├── src/
│   ├── __init__.py
│   ├── chatbot.py
│   ├── nlp_utils.py
│   ├── conversation_manager.py
│   └── api_utils.py
│
├── ui/
│   ├── __init__.py
│   ├── components.py
│   └── styles.css
│
├── tests/
│   ├── test_chatbot.py
│   ├── test_api_utils.py
│   └── test_ui.py
│
├── logs/
│   └── chat_logs.txt
│
└── docs/
    └── architecture.md

# To import requirement.txt to pyprojects.toml
uv add -r requirements.txt    # Imports requirements.txt into pyproject.toml
rm requirements.txt           # Remove old file
