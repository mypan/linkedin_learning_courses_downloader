# LLCD ☄️☄️☄️
##### Linkedin Learning Courses Downloader
###### v0.2: now works without webdriver

A simple python scraper tool that downloads video lessons from Linkedin Learning

## How to use
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