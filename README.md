# Linkedin Learning Courses Downloader ☄️☄️☄️

###### v0.2: now works without webdriver

A simple python scraper tool that downloads video lessons from Linkedin Learning

## How to use

In the `config.py` file, write your login info and fill the `COURSES` array with the slug of the courses you want to download, for example:

`https://www.linkedin.com/learning/it-security-foundations-core-concepts/` -> `it-security-foundations-core-concepts`

```python
USERNAME = 'user@email.com'
PASSWORD = 'password'

COURSES = [
    'it-security-foundations-core-concepts',
    'javascript-for-web-designers-2',
    ...
]
```

You can either run docker-compose or run the code locally.

### docker-compose

You need to have docker installed. Then run:

```bash
docker-compose up --build
```

### Locally

First install the requirements:

```bash
pip install -r requirements.txt
```

If `pip` is not installed, run:

```bash
python get-pip.py
```

An updated version of `get-pip.py` can also be obtained by executing:

```bash
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
```

For more info, check [`this resource`](https://pip.pypa.io/en/stable/installing/)

Then execute the script:

```bash
python llcd.py
```

### Outcome

The courses will be saved in the `out` folder.

### Demo

[![asciicast](https://asciinema.org/a/143894.png)](https://asciinema.org/a/143894)
