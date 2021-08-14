from http import cookiejar
import os
from urllib import request
from urllib  import parse
import sys
import config
import requests
import re
from bs4 import BeautifulSoup
from importlib import reload 

reload(sys)

def login():
    cookie_filename = 'cookies.txt'

    cookie_jar = cookiejar.MozillaCookieJar(cookie_filename)

    opener = request.build_opener(
                request.HTTPRedirectHandler(),
                request.HTTPHandler(debuglevel=0),
                request.HTTPSHandler(debuglevel=0),
                request.HTTPCookieProcessor(cookie_jar)
            )
    print("login1")
    html = load_page(opener, 'https://www.linkedin.com/checkpoint/lg/login')
    soup = BeautifulSoup(html, 'html.parser')

    print("login2")

    csrf = soup.find('input',{'name':'csrfToken'}).get('value')
    loginCsrfParam = soup.find('input',{'name':'loginCsrfParam'}).get('value')

    login_data = parse.urlencode({
                    'session_key': config.USERNAME,
                    'session_password': config.PASSWORD,
                    'csrfToken': csrf,
                    'loginCsrfParam': loginCsrfParam
                })

    load_page(opener, 'https://www.linkedin.com/checkpoint/lg/login-submit', login_data)

    try:
        cookie = cookie_jar._cookies['.www.linkedin.com']['/']['li_at'].value
        jsessionid = ''
        for ck in cookie_jar:
            # print cookie.name, cookie.value, cookie.domain
            if ck.name == 'JSESSIONID':
                jsessionid = ck.value
    except Exception as e:
        print (e)
        sys.exit(0)

    cookie_jar.save()
    os.remove(cookie_filename)

    return cookie, csrf


def authenticate():
    try:
        session, jsessionid = login()
        if len(session) == 0:
            sys.exit('[!] Unable to login to LinkedIn.com')
        print ('[*] Obtained new session: %s' % session)
        cookies = dict(li_at=session, JSESSIONID=jsessionid)
    except Exception as e:
        sys.exit('[!] Could not authenticate to linkedin. %s' % e)
    return cookies


def load_page(opener, url, data=None):

    try:
        if data is not None:
            response = opener.open(url, data)
        else:
            response = opener.open(url)
        return ''.join(response.readlines())
    except Exception as e:
        print ('[Notice] Exception hit')
        print (e)
        sys.exit(0)


def download_file(url, file_path, file_name):
    reply = requests.get(url, stream=True)
    if not os.path.exists(file_path):
        os.makedirs(file_path)
    with open(file_path + '/' + file_name, 'wb') as f:
        for chunk in reply.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)

if __name__ == '__main__':
    print('here0')
    cookies = authenticate()
    headers = {'Csrf-Token':cookies['JSESSIONID']}
    # cookies['JSESSIONID'] = cookies['JSESSIONID']

    print('here1')
    for course in config.COURSES:
        print ('')
        course_url = 'https://www.linkedin.com/learning-api/detailedCourses' \
                     '??fields=videos&addParagraphsToTranscript=true&courseSlug={0}&q=slugs'.format(course)
        r = requests.get(course_url, cookies=cookies, headers=headers)
        print (r)
        # break
        course_name = r.json()['elements'][0]['title']
        course_name = re.sub(r'[\\/*?:"<>|]', "", course_name)
        chapters = r.json()['elements'][0]['chapters']
        print ('[*] Parsing "%s" course\'s chapters' % course_name)
        print ('[*] [%d chapters found]' % len(chapters))
        for chapter in chapters:
            chapter_name = re.sub(r'[\\/*?:"<>|]', "", chapter['title'])
            videos = chapter['videos']
            vc = 0
            print ('[*] --- Parsing "%s" chapters\'s videos' % chapter_name)
            print ('[*] --- [%d videos found]' % len(videos))
            for video in videos:
                video_name = re.sub(r'[\\/*?:"<>|]', "", video['title']).encode("utf-8", errors='ignore')
                video_slug = video['slug']
                video_url = 'https://www.linkedin.com/learning-api/detailedCourses' \
                            '?addParagraphsToTranscript=false&courseSlug={0}&q=slugs&resolution=_720&videoSlug={1}'\
                    .format(course, video_slug)
                r = requests.get(video_url, cookies=cookies, headers=headers)
                vc += 1
                try:
                    download_url = re.search('"progressiveUrl":"(.+)","expiresAt"', r.text).group(1)
                except Exception as e:
                    print ('[!] ------ Can\'t download the video "%s", probably is only for premium users' % video_name)
                    print (e)
                else:
                    print ('[*] ------ Downloading video "%s"' % video_name)
                    download_file(download_url, 'out/%s/%s' % (course_name, chapter_name), '%s. %s.mp4' % (str(vc), video_name))
