# Train Timetables
I wrote this small program in order to improve my programming skills in Python.\
I used:
* [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/) to scrape information from webpage,
* [requests](https://requests.readthedocs.io/en/latest/) to get webpage content and download files,
* [PyPDF](https://github.com/py-pdf/pypdf) to parse PDF files,
* [PyYAML](https://pyyaml.org/) to read configuration from YAML file,
* [tqdm](https://tqdm.github.io/) for download progress bar,
* [logging](https://docs.python.org/3/library/logging.html) for additional debug information,
* [Pytest](https://docs.pytest.org/) for testing.

## Description
This program extracts links to PDF files containing current train timetables for defined lines from a railway operator's
website.\
It proceeds to download these files, parse them and saves the arrival and departure times for defined train stations
to a text file.\
The train lines, stations, output file and download directory are configurable in `config.yaml` file.

### History
I wrote this program for me and my family to provide them with convenient and quick access to current train timetables.

## Installation
First of all, You must have the [Python](https://www.python.org/downloads/) installed.\
Next, 3 options to choose from:
#### I. PyCharm or IntelliJ IDEA with the "Python Community Edition" plugin
1. Create a New Project and choose the virtual environment, for example **Virtualenv**.
2. Open the IDE terminal.
3. Type:
   ```
   git clone git@github.com:arkadiusz-l/train-timetables.git
   ```
   or
   ```
   git clone https://github.com/arkadiusz-l/train-timetables.git
   ```
4. Navigate to the program's directory by typing:
   ```
   cd train-timetables
   ```
5. Make sure that you are inside the virtual environment - you should see `(venv)` before the path.
6. Type:
   ```
   pip install -r requirements.txt
   ```
   to install the required dependencies necessary for the program to run.

#### II. Downloading release
1. Download the [latest release](https://github.com/arkadiusz-l/train-timetables/releases/latest)
   in a .zip archive.
2. Unpack the downloaded archive in a directory of your choice.
3. Open the terminal.
4. Navigate to the directory with the unpacked program by typing:
   ```
   cd directoryname
   ```
5. Type:
   ```
   python -m venv venv
   ```
   to create virtual environment and wait for confirmation.
6. If you are on Windows, type:
   ```
   venv\Scripts\activate
   ```
   If you are on Linux or macOS, type:
   ```
   source venv/bin/activate
   ```
7. Make sure that you are inside the virtual environment - you should see `(venv)` before the path.
8. Type:
   ```
   pip install -r requirements.txt
   ```
   to install the required dependencies necessary for the program to run.

#### III. Cloning repository
1. Open the terminal.
2. Create a new directory by typing:
   ```
   mkdir directoryname
   ```
3. Navigate to that directory by typing:
   ```
   cd directoryname
   ```
4. Type:
   ```
   git clone git@github.com:arkadiusz-l/train-timetables.git
   ```
   or
   ```
   git clone https://github.com/arkadiusz-l/train-timetables.git
   ```
5. Navigate to the program's directory by typing:
   ```
   cd train-timetables
   ```
6. Type:
   ```
   python -m venv venv
   ```
   to create virtual environment and wait for confirmation.
7. If you are on Windows, type:
   ```
   venv\Scripts\activate
   ```
   If you are on Linux or macOS, type:
   ```
   source venv/bin/activate
   ```
8. Make sure that you are inside the virtual environment - you should see `(venv)` before the path.
9. Type:
   ```
   pip install -r requirements.txt
   ```
   to install the required dependencies necessary for the program to run.

## Usage
1. See configuration examples in the `config.yaml.example` file and enter the required data in the `config.yaml` file.
2. Run the program by typing in Terminal:
   ```
   python main.py
   ```
3. The program will find train timetables for the entered data and save them in the defined output text file.
4. After using the program, exit the virtual environment by typing:
   ```
   deactivate
   ```
   The `(venv)` should disappear.