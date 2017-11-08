import cookielib
import os
import urllib
import urllib2
import sys
import config
import requests
import re
from bs4 import BeautifulSoup

reload(sys)
sys.setdefaultencoding('utf-8')


def login():
    cookie_filename = 'cookies.txt'

    cookie_jar = cookielib.MozillaCookieJar(cookie_filename)

    opener = urllib2.build_opener(
                urllib2.HTTPRedirectHandler(),
                urllib2.HTTPHandler(debuglevel=0),
                urllib2.HTTPSHandler(debuglevel=0),
                urllib2.HTTPCookieProcessor(cookie_jar)
            )

    html = load_page(opener, 'https://www.linkedin.com/')
    soup = BeautifulSoup(html, 'html.parser')
    csrf = soup.find(id='loginCsrfParam-login')['value']

    login_data = urllib.urlencode({
                    'session_key': config.USERNAME,
                    'session_password': config.PASSWORD,
                    'loginCsrfParam': csrf,
                })

    load_page(opener, 'https://www.linkedin.com/uas/login-submit', login_data)

    try:
        cookie = cookie_jar._cookies['.www.linkedin.com']['/']['li_at'].value
    except:
        sys.exit(0)

    cookie_jar.save()
    os.remove(cookie_filename)

    return cookie


def authenticate():
    try:
        session = login()
        if len(session) == 0:
            sys.exit('[!] Unable to login to LinkedIn.com')
        print '[*] Obtained new session: %s' % session
        cookies = dict(li_at=session)
    except Exception, e:
        sys.exit('[!] Could not authenticate to linkedin. %s' % e)
    return cookies


def load_page(opener, url, data=None):
    try:
        response = opener.open(url)
    except:
        print '[Fatal] Your IP may have been temporarily blocked'

    try:
        if data is not None:
            response = opener.open(url, data)
        else:
            response = opener.open(url)
        return ''.join(response.readlines())
    except:
        print '[Notice] Exception hit'
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
    cookies = authenticate()
    headers = {'Csrf-Token':'ajax:4332914976342601831'}
    cookies['JSESSIONID'] = 'ajax:4332914976342601831'

    for course in config.COURSES:
        print ''
        course_url = 'https://www.linkedin.com/learning-api/detailedCourses' \
                     '??fields=videos&addParagraphsToTranscript=true&courseSlug={0}&q=slugs'.format(course)
        r = requests.get(course_url, cookies=cookies, headers=headers)
        course_name = r.json()['elements'][0]['title']
        course_name = re.sub(r'[\\/*?:"<>|]', "", course_name)
        chapters = r.json()['elements'][0]['chapters']
        print '[*] Parsing "%s" course\'s chapters' % course_name
        print '[*] [%d chapters found]' % len(chapters)
        for chapter in chapters:
            chapter_name = re.sub(r'[\\/*?:"<>|]', "", chapter['title'])
            videos = chapter['videos']
            vc = 0
            print '[*] --- Parsing "%s" chapters\'s videos' % chapter_name
            print '[*] --- [%d videos found]' % len(videos)
            for video in videos:
                video_name = re.sub(r'[\\/*?:"<>|]', "", video['title'])
                video_slug = video['slug']
                video_url = 'https://www.linkedin.com/learning-api/detailedCourses' \
                            '?addParagraphsToTranscript=false&courseSlug={0}&q=slugs&resolution=_720&videoSlug={1}'\
                    .format(course, video_slug)
                r = requests.get(video_url, cookies=cookies, headers=headers)
                vc += 1
                try:
                    download_url = re.search('"progressiveUrl":"(.+)","streamingUrl"', r.text).group(1)
                except:
                    print '[!] ------ Can\'t download the video "%s", probably is only for premium users' % video_name
                else:
                    print '[*] ------ Downloading video "%s"' % video_name
                    download_file(download_url, 'out/%s/%s' % (course_name, chapter_name), '%s. %s.mp4' % (str(vc), video_name))

