<img src="https://i.imgur.com/TkbiSQY.png" width="175" align="right">

# Linkedin Learning Downloader
[![built with Requests](https://img.shields.io/badge/built%20with-Requests-yellow.svg?style=flat-square)](http://docs.python-requests.org)
[![built with Python2.7](https://img.shields.io/badge/built%20with-Python2.7-red.svg?style=flat-square)](https://www.python.org/)

### A scraping tool that downloads video lessons from Linkedin Learning
Features:
* Implemented in python using requests.
* Downloading complete courses: course description, videos, exercise files and subtitles.
* Numbering of chapters, videos and subtitles.
* Subtitles will have the same name as the video file, so players like MPC-HC will automatically load the subtitles when playing a video file.

### How to use
First install the requirements:
```
pip install -r requirements.txt
```
The `config.py` looks like this:
```
USERNAME = 'user@email.com'
PASSWORD = 'password'
BASE_DOWNLOAD_PATH = 'E:/Downloads/LinkedInLearning' #use "/" as separators
SUBS = True
COURSES = [
    'it-security-foundations-core-concepts',
    'javascript-for-web-designers-2'
]
```

1. Enter your login info and download path.

2. Fill the `COURSES` array with the slug of the the courses you want to download and save the config file, for example:
`https://www.linkedin.com/learning/it-security-foundations-core-concepts/ -> it-security-foundations-core-concepts`

Then execute the script:
```
python lld.py
```
The courses will be saved in your defined download folder.

### Demo (outdated by now)
[![asciicast](https://asciinema.org/a/143894.png)](https://asciinema.org/a/143894)

---
###### Have Fun & Feel Free to report any issues
---
