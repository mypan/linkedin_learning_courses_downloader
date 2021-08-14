# Linkedin Learning Courses Downloader ☄️☄️☄️

A simple python scraper tool that downloads video lessons from Linkedin Learning

## How to use

In the `config.py` file, write your login info and fill the `COURSES` array with the slug of the courses you want to download, for example:

`https://www.linkedin.com/learning/it-security-foundations-core-concepts/` -> `it-security-foundations-core-concepts`

```python
USERNAME = 'user@email.com'
PASSWORD = 'password'
BASE_DOWNLOAD_PATH = '' #use "/" as separators (defaults to 'out')
SUBS = False # downloads subtitles
COURSES = [
    'it-security-foundations-core-concepts',
    'javascript-for-web-designers-2',
    ...
]
```

You can either run docker-compose or run the code locally.

### Containerized
#### pre-reqs
- install docker
- install docker-compose
#### run
```bash
docker-compose up --build
```

### Locally
#### pre-reqs
- install pipenv
#### run
```bash
pipenv run download
```

### Outcome

The courses will be saved in the `out` folder.

### Demo

[![asciicast](https://asciinema.org/a/143894.png)](https://asciinema.org/a/143894)
