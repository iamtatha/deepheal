# Deepheal Codebase
World's first AI-powered mental health assistant. Led by Tathagata Dey [Webpage](https://iamtatha.github.io).

## How to Set up
- Install python `3.10` and then pip install the virtuelenv library, create a library and initialize to install the requirements. For now start an environment with the name `env`.
```
pip install virtualenv
python -m venv env
```
- Initiate the virtual environment
  - On windows: `source env/Scripts/activate`
  - On Linux/Mac: `source env/bin/activate`
- Install the requirements folder
```
pip install -r requirements.txt
```
- You still need to install `ffmpeg`
### Install ffmpeg: MAC Process
```
brew install ffmpeg
```
### Install ffmpeg: Linux Process
```
sudo apt install ffmpeg -y
```
### Install ffmpeg: Windows Process
```
winget install ffmpeg
```
Check the installation by `ffmpeg -version`

## How to Run?
Verify `Django` has been installed.
Now open a terminal and start the virtual environment
Run the following
```
python manage.py runserver
```
Now you will be able to chat in `localhost:8000` address and see the logs in `localhost:8000/logs`


## License
This project is licensed under the [Custom License](./LICENSE).

