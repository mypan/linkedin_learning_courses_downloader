<img src="https://i.imgur.com/TkbiSQY.png" width="175" align="right">

# Linkedin Learning Downloader
[![built with Requests](https://img.shields.io/badge/built%20with-Requests-yellow.svg?style=flat-square)](http://docs.python-requests.org)
[![built with Python2.7](https://img.shields.io/badge/built%20with-Python2.7-red.svg?style=flat-square)](https://www.python.org/)

### A scraping tool that downloads video lessons from Linkedin Learning
Implemented in python using requests

### How to use
First install the requirements:
```
pip install -r requirements.txt
```
In the `config.py` file, write your login info and fill the `COURSES` array with the slug of the the courses you want to download, for example:

`https://www.linkedin.com/learning/it-security-foundations-core-concepts/ -> it-security-foundations-core-concepts`

```
USERNAME = 'user@email.com'
PASSWORD = 'password'

COURSES = [
    'it-security-foundations-core-concepts',
    'javascript-for-web-designers-2'
]
```
Then excecute the script:
```
python llcd.py
```
The courses will be saved in the `out` folder.

### Demo
[![asciicast](https://asciinema.org/a/143894.png)](https://asciinema.org/a/143894)

---
###### Have Fun & Feel Free to report any issues
---