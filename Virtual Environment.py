Your computer
│
├── Project A
│   └── venv
│       └── its packages
│
└── Project B
    └── venv
        └── different packages

python -m venv venv
venv\Scripts\activate
source venv/bin/activate
pip install langchain

#uv is a newer, very fast Python package/project manager.
uv
├── Python versions
├── virtual environments
├── package installation
└── dependency management

uv init my-ai-project
uv venv
uv add langchain
uv run python main.py

#The easiest way to remember it
Tool	 : Main idea
pip    : 	Install Python packages
venv	 : Create isolated Python environment
uv	   : Modern tool that can manage the environment + packages + project
