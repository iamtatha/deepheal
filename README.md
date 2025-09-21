# Deepheal Codebase
World's first AI-powered mental health assistant. Led by Tathagata Dey [Webpage](www.iamtatha.github.io).

## How to Set up
- Install python `3.10` and then pip install the virtuelenv library by the following
```
pip install virtualenv
```
- Start a new virtual environment with the name `env`
```
python -m venv env
```
- Initiate the virtual environment
  - On windows
```
source env/Scripts/activate
```
  - On Linux/Mac
```
source env/bin/activate
```
- Install the requirements folder
```
pip install -r requirements.txt
```
- You still need to install `ffmpeg`
### MAC Process
```
brew install ffmpeg
```
### Linux Process
```
sudo apt install ffmpeg -y
```
### Windows Process
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
