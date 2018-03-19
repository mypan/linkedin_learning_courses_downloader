# -*- coding: utf-8 -*-
import cookielib
import os
import urllib
import urllib2
import sys
import config
import requests
import re
import time
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
        print ('[*] Obtained new session: %s' % session)
        cookies = dict(li_at=session)
    except Exception as e:
        print(e)
        sys.exit('[!] Could not authenticate to linkedin. %s' % e)
    return cookies


def load_page(opener, url, data=None):
    try:
        response = opener.open(url)
    except:
        print ('[Fatal] Your IP may have been temporarily blocked')
    try:
        if data is not None:
            response = opener.open(url, data)
        else:
            response = opener.open(url)
        return ''.join(response.readlines())
    except:
        print ('[Notice] Exception hit')
        sys.exit(0)

def cleanup_string(string):
    replacementDictionary = {u'Ä': 'Ae',
                        u'Ö': 'Oe',
                        u'Ü': 'Ue',
                        u'ä': 'ae',
                        u'ö': 'oe',
                        u'ü': 'ue',
                        ':': ' -'                      
                        }
    invalid_file_chars = r'[^A-Za-z0-9-]+'
    
    #replace Umlaut first
    umap = {ord(key):unicode(val) for key, val in replacementDictionary.items()}
    string = string.translate(umap)
    #then replace other forbidden chars
    string = re.sub(invalid_file_chars, " ", string).strip().encode('utf-8')
    return string    
    

        
def download_file(url, file_path, file_name):
    reply = requests.get(url, stream=True)
    if not os.path.exists(file_path):
        os.makedirs(file_path)
    #print(file_path + '/' + file_name)    
    try:
        with open(file_path + '/' + file_name, 'wb') as f:
            for chunk in reply.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)    
    except EnvironmentError:
        print 'IO error. Deleting last incomplete file. Also check last created file manually for integrity'
        os.remove(file_path + '/' + file_name)     

                
def to_hhmmssms(ms):
    sec,ms = divmod(ms,1000)
    min,sec = divmod(sec,60)
    hr,min = divmod(min,60)
    return "%d:%02d:%02d.%03d" % (hr,min,sec,ms)
    
    
def download_subtitles(filepath_and_name):
    #srt needs start and end time, while LinkedIn is only providing start time. So I use end-time of a subtitle = start time of the next subtitle.
    try:
        with open(filepath_and_name, 'a') as subtitle_file:
            index_next_subtitle = 1
            for subtitle in subtitles:                   
                #print('Next-Index: "%i"') % index_next_subtitle
                transcriptStartAt = milliseconds=subtitle['transcriptStartAt']                            
                #for last subtitle (which hasn't a successor) use an end time that is probably longer than the video has now left (+5 seconds)
                if (index_next_subtitle == len(subtitles)): #detecting list index out of boundary
                    transcriptEndAt = transcriptStartAt + 5000
                else:
                    transcriptEndAt = milliseconds=subtitles[index_next_subtitle]['transcriptStartAt']            
                caption = subtitle['caption']            
                subtitle_file.write(str(index_next_subtitle))
                subtitle_file.write('\n')
                subtitle_file.write(str(to_hhmmssms(transcriptStartAt)))
                subtitle_file.write(' --> ')
                subtitle_file.write(str(to_hhmmssms(transcriptEndAt)))
                subtitle_file.write('\n')
                subtitle_file.write(caption)
                subtitle_file.write('\n \n')       
                index_next_subtitle+=1                        
        subtitle_file.close()
        
    except EnvironmentError:
        print 'IO error. Deleting last incomplete file. Also check last created file manually for integrity'
        os.remove(filepath_and_name)     


if __name__ == '__main__':
    cookies = authenticate()
    headers = {'Csrf-Token': 'ajax:4332914976342601831'}
    cookies['JSESSIONID'] = 'ajax:4332914976342601831'
    for course in config.COURSES:
        print('\n')
        #request release-time field of course
        course_url = 'https://www.linkedin.com/learning-api/detailedCourses' \
                     '??fields=releasedOn&addParagraphsToTranscript=true&courseSlug={0}&q=slugs'.format(course)
        #print 'Course-URL: "%s"' % course_url
        r = requests.get(course_url, cookies=cookies, headers=headers)
        #print 'Response from Server: %s' % r
        course_name = cleanup_string(r.json()['elements'][0]['title'])
        #invalid_file_chars = r'[^A-Za-z0-9 ]+'
        #course_name = re.sub(invalid_file_chars, " ", course_name)
        print '[*] __________ Starting download of course "%s" __________' % course_name
        course_releasedate_unix = r.json()['elements'][0]['releasedOn']
        course_releasedate = time.strftime("%Y-%m-%d", time.gmtime(course_releasedate_unix / 1000.0))
        #for future use: tag/name of updated-element unknown on LinkedIn Learning so far. If known, use the newer Update date for course-folder instead of old initial release date
        #course_updatedate_unix = 
        #course_releasedate
        chapters = r.json()['elements'][0]['chapters']
        print ('[*] Parsing course\'s chapters')
        print ('[*] [%d chapters found]' % len(chapters))
        chapter_index = 0
        for chapter in chapters:
            print("")
            chapter_name = cleanup_string(chapter['title'])  
            # chapter_name = re.sub(invalid_file_chars, " ", chapter['title'])
            #chapter_name = re.sub(r'[\\/*?:"<>|]', "", chapter['title'])
            videos = chapter['videos']
            video_index = 0
            chapter_index +=1
            print ('[*] --- Parsing chapter #%s "%s" for videos') % (str(chapter_index), chapter_name)
            print ('[*] --- [%d videos found]' % len(videos))
            for video in videos:
                video_name = cleanup_string (video['title'])
                #video_name = re.sub(invalid_file_chars, " ", video['title'])
                video_slug = video['slug']
                video_url = 'https://www.linkedin.com/learning-api/detailedCourses' \
                            '?addParagraphsToTranscript=false&courseSlug={0}&q=slugs&resolution=_720&videoSlug={1}'\
                    .format(course, video_slug)
                r = requests.get(video_url, cookies=cookies, headers=headers)                
                video_index += 1
                try:
                    download_url = re.search('"progressiveUrl":"(.+)","streamingUrl"', r.text).group(1)
                    #print 'Searching-URL: "%s"' % download_url
                except:
                    print ('[!] ------ Can\'t download the video "%s", probably is only for premium users' % video_name)
                else:
                    file_path = 'out/%s (%s)/%s - %s' % (course_name,course_releasedate,str(chapter_index),chapter_name)
                    file_name = '%s - %s' % (str(video_index), video_name)
                    file_type_video = '.mp4'
                    print ('[*] ------ Downloading video #%s "%s"' % (str(video_index), video_name))
                    if os.path.exists(file_path + '/' + file_name + file_type_video):
                        print '[!]          ->video file already present, now checking subtitle existence'                    
                    else:
                        #print 'Video-URL: "%s"' % download_url
                        download_file(download_url, file_path, file_name + file_type_video)
                try:
                    subtitles = r.json()['elements'][0]['selectedVideo']['transcript']['lines']
                except:
                    print('[*] ------ No subtitles available')
                else:
                    file_type_srt = '.srt'
                    print ('[*] ------ Downloading subtitles')
                    if os.path.exists(file_path + '/' + file_name + file_type_srt):
                        print('[!]          ->subtitle file already present, skipping to next')
                    else:                        
                        #print 'Video-URL: "%s"' % download_url
                        download_subtitles(file_path + '/' + file_name + file_type_srt)
                print("")
    print '[*] __________ Finished course "%s" __________' % course_name
                    