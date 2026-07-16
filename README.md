# Project Preparations

The Python version used in this project is 3.7.9

#### create virtual environment

```
python -m venv venv
```

#### activate virtual environment in Windows

```sh
.\venv\Scripts\activate
```

#### upgrade pip

```
python -m pip install --upgrade pip
```

#### install project dependencies

```
pip install -r requirements.txt
```

# Automation Testing

```
cd flowstudio
pytest
```

# Automation Testing with coverage report output
coverage report will be in flowstudio/htmlcov folder
```
cd flowstudio
pytest --cov=./ --cov-report=html
```

# Generate build_NSIS.nsi and FLOW_Studio_Ver_x.xx.x.tar
```
cd flowstudio
python main_build.py prod free (or prod pro)
```