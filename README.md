# FlowStudio - Windows Desktop Application

A Python-based desktop application for Windows that provides workflow automation and management capabilities.

## System Requirements

- **Operating System**: Windows 7 or later
- **Python Version**: 3.7.9 (no longer maintained)
- **RAM**: Minimum 2GB (recommended 4GB or more)

## Project Setup

### Important: Python 3.7 Setup

Since Python 3.7 is no longer maintained, standard virtual environment management tools may not work properly. Follow these steps:

#### 1. Download Python 3.7

1. Go to [Python Releases for Windows](https://www.python.org/downloads/windows/) 
2. Download Python 3.7.x installer
3. Run the installer

#### 2. Verify Installation

```bash
py --list
```

This will show all installed Python versions. Ensure Python 3.7 is listed.

#### 3. Create Virtual Environment

Use the `py` command with explicit version:

```bash
py -3.7 -m venv .venv
```

#### 4. Install Project Dependencies

```bash
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Local Development Testing

### Configuration for Local AI Agent Service

If you need to test with a local AI agent service, make the following changes:

#### 1. **thread_worker.py**

Update the WebSocket URL:
```python
ws_url = "ws://localhost:14080/flowai/ws/getAgentResponse_v4"
```

#### 2. **constant.json**

Set environment to production:
```json
"env": "prod"
```

#### 3. **flow_ai_manager.py**

Update email and token settings:
```python
email = 'local@test'
token = self.parent.license_mechanism.token if self.parent.license_mechanism.user is not None else "test_token"
```

#### 4. **flow_build_manager.py**

Set version for local testing:
```python
VERSION = "2.3.5-pro"
```

#### 5. **flow_license_mechanism.py**

Ensure testing mode is enabled in `__init__`:
```python
def __init__(self, parent: 'QWidget' = None, is_testing=True, splash = None):
```

#### 6. **flow_window.py**

Verify the hidapi.dll path is correctly set:
```python
# Load hidapi.dll using absolute path based on module location
_dll_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'bin', 'hidapi.dll'))
ctypes.CDLL(_dll_path)
```

## Running the Application

### Startup Command

Once the environment is set up and all configurations are in place, run:

```powershell
.venv\Scripts\Activate.ps1; $env:PYTHONPATH = ".."; python main.py
```

**Note**: You may need to adjust the PYTHONPATH based on your project structure.

## Development

### Automation Testing

Run all tests:
```bash
cd flowstudio
pytest
```

### Automation Testing with Coverage Report

Coverage report will be generated in `flowstudio/htmlcov` folder:
```bash
cd flowstudio
pytest --cov=./ --cov-report=html
```

## Building and Packaging

### Generate Windows Installer and Distribution Package

To generate the NSIS installer and tar distribution:

```bash
cd flowstudio
python main_build.py prod free    # For free version
# or
python main_build.py prod pro     # For pro version
```

This will generate:
- `build_NSIS.nsi` - Windows NSIS installer script
- `FLOW_Studio_Ver_x.xx.x.tar` - Distribution tar archive

## License

See [License.txt](License.txt) for details.