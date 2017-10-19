# Linkedin Learning Courses Downloader 🔓
###### Tested with Firefox 46.0.1 and Selenium 2.53.0

A simple python tool to download video lessons from Linkedin Learning

## How to use
First install the requirements:
```
pip install requirements.txt
```
In the `config.py` file, write your login info and fill the `COURSES` array with the url of the courses you want to download. Set `HD` to `False` if you want to download the videos in standard resolution.
```
USERNAME = 'user@email.com'
PASSWORD = 'password'

COURSES = [
    'https://www.linkedin.com/learning/it-security-foundations-core-concepts/',
    'https://www.linkedin.com/learning/javascript-for-web-designers-2'
]

HD = True
```
Then excecute the script:
```
python video_downloader.py
```