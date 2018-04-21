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
import math
import glob
import string
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
    invalid_file_chars = r'[^A-Za-z0-9\-\.]+'
    
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
    except Exception as e:
        print 'Error. Deleting last incomplete file. Also check last created file manually for integrity'
        os.remove(file_path + '/' + file_name)     
        print(e)

                
def to_hhmmssms(ms):
    sec,ms = divmod(ms,1000)
    min,sec = divmod(sec,60)
    hr,min = divmod(min,60)
    return "%d:%02d:%02d.%03d" % (hr,min,sec,ms)
    
    
def download_subtitles(file_path, file_name):
    if not os.path.exists(file_path):
        os.makedirs(file_path)
    #srt needs start and end time, while LinkedIn is only providing start time. So I use end-time of a subtitle = start time of the next subtitle.
    try:
        with open(file_path + '/' + file_name, 'a') as subtitle_file:
            index_next_subtitle = 1
            for subtitle in subtitles:                   
                #print('Next-Index: "%i"') % index_next_subtitle
                transcriptStartAt = milliseconds=subtitle['transcriptStartAt']                            
                #for last subtitle (which hasn't a successor) we use an end time that is probably longer than the video has now left (+5 seconds)
                if (index_next_subtitle == len(subtitles)): #detecting last subtitle / list index out of boundary
                    transcriptEndAt = transcriptStartAt + 5000
                else:
                    transcriptEndAt = milliseconds=subtitles[index_next_subtitle]['transcriptStartAt']            
                caption = subtitle['caption']
                #write to file (line for line)
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
        
    except Exception as e:
        print 'Error. Deleting last incomplete file. Also check last created file manually for integrity'
        os.remove(file_path + '/' + file_name)     
        print(e)

def download_description(file_path, file_name, description, course_url):
    if not os.path.exists(file_path):
        os.makedirs(file_path)
    try:
        with open(file_path + '/' + file_name, 'a') as description_file:
            description_file.write(description)
            description_file.write('\n')
            description_file.write('Link: %s' % course_url)
        description_file.close()
        
    except Exception as e:
        print 'IO error. Deleting last incomplete file. Also check last created file manually for integrity'
        os.remove(file_path + '/' + file_name)     
        print(e)

 
def parse_bookmarks():
    #LinkedIn is only providing 10 bookmarked courses at a time, api has to be triggered several times
    #First: get amount of bookmarked courses by using extraordinary number (don't know any other apicall to do so for now)
    bookmarks_api_url = 'https://www.linkedin.com/learning-api/listedBookmarks?q=listedBookmarks&start='        
    req = requests.get(bookmarks_api_url+str(3000), cookies=cookies, headers=headers)
    bookmarked_courses_number = req.json()['paging']['total']
    print("[*] Total number of online bookmarked courses: %s" % bookmarked_courses_number)
    bookmarked_courses_number_rounded = int(math.ceil(bookmarked_courses_number / 10.0)) * 10 #round number of bookmarks to next tenner
    needed_loops = bookmarked_courses_number_rounded / 10 #needed loops/api calls with each receiving 10 bookmarks
    start=0 #start with bookmarks 0-10
    while start < bookmarked_courses_number_rounded:
        r = requests.get(bookmarks_api_url + str(start), cookies=cookies, headers=headers)
        course_elements  = r.json()['elements']
        with open("config.py", "r") as config_file: #copy everything from old config to memory for easier inserting new lines in center of file
            prev_contents = config_file.readlines()        
        with open("config.py", "w") as config_file_new: #new config file replacing old        
            for course in course_elements:            
                course_slug = course['content']['com.linkedin.learning.api.ListedCourse']['slug']
                for line in prev_contents:                
                    if course_slug in line: #do nothing, go searching for next course-slug (outer loop)
                        break
                else:   #else-after-forloop: if course-slug not found in any line/iteration, add this course-slug (before the "]")
                    prev_contents.insert(len(prev_contents)-1, "    '" + course_slug + "',\n")
            config_file_new.writelines(prev_contents)
        start+=10 #get next round of 10 bookmarks
    #reload edited config file
    reload(config)
    
        
    
def comment_out_finished_course(course_slug):    
    with open("config.py", "r") as config_file:
        prev_contents = config_file.readlines()        
    with open("config.py", "w") as config_file_new: #new config file replacing old        
        for i, line in enumerate(prev_contents):
            if course_slug in line:
                prev_contents[i] = line[:4] + "#" + line[4:]
        config_file_new.writelines(prev_contents)
    #reload edited config file
    reload(config)

def extractName(namestring):
    # get name with just alphabets
    ind = 0
    iterator = 0
    for ch in namestring:
        if ch in string.ascii_letters:
            ind = iterator
            break
        iterator += 1
    namestring = namestring.replace('- ', ' ') # some new video names have '- ' in them but old ones don't
    namestring = namestring.replace('.', ' ') # some new folder names have '.' in them but old ones don't
    return namestring[ind:]

def renameOldFolder(course_folder_path, chapter_index, chapter_name, file_path):
    # check if old type chapter folder is present; if present rename it
    file_path_alternate = course_folder_path + '\\' + '%s - %s' % (str(chapter_index).zfill(2),chapter_name)
    # print '\t checking if old type chapter folder is present; if present rename it'
    # print '%s %s %s %s' %(course_folder_path, chapter_index, chapter_name, file_path)
    if len(glob.glob(course_folder_path + '/*' + chapter_name)) < 1:
        print '||\t Old Folder Not Found'
        return
    for file in glob.glob(course_folder_path + '/*' + chapter_name):
        # course present
        print file
        print file_path
        print file_path_alternate
        if file != file_path and file != file_path_alternate:
            # old chapter type - rename needed
            os.rename(file, file_path)
            print '\t Old type chapter folder FOUND - Rename successful'
            # break

def renameOldFile(file_path, extractedVideoName, file_type_video, file_path_full):
    # check if old type video is present; if present rename it    
    # print '\t check if old type video is present; if present rename it'    
    file_path_full_alternate = file_path + '\\' + file_name + file_type_video # to match return value from glob.glob
    if len(glob.glob(file_path + '/*' + extractedVideoName + file_type_video)) < 1:
        print '||\t Old File Not Found'
        return
    for file in glob.glob(file_path + '/*' + extractedVideoName + file_type_video):
        # video present
        # print file
        if file != file_path_full and file != file_path_full_alternate:
            # old type video name - rename needed
            os.rename(file, file_path_full)
            print '\t Old type video file FOUND - Rename successful'
            # break

# runs = 0
        
if __name__ == '__main__':
    cookies = authenticate()
    headers = {'Csrf-Token': 'ajax:4332914976342601831'}
    cookies['JSESSIONID'] = 'ajax:4332914976342601831'
    if config.BASE_DOWNLOAD_PATH != '':
        base_download_path = config.BASE_DOWNLOAD_PATH
    else:
        'out'
    file_type_video = '.mp4'
    file_type_srt = '.srt'
    #file_type_exercise = '.zip' #no need for that, extracted filename already contains the filetype
    file_type_description = '.txt'   
    
    #Read bookmarks and add them to config file (this way you can still use the manual way of adding courses). Then reload config file.
    bookmarked_courses = parse_bookmarks()   
    
    
    
    #Courses
    for course in config.COURSES:
        print('\n')
        #Request important course data fields
        course_api_url = 'https://www.linkedin.com/learning-api/detailedCourses' \
                     '??fields=fullCourseUnlocked,releasedOn,exerciseFileUrls,exerciseFiles&addParagraphsToTranscript=true&courseSlug={0}&q=slugs'.format(course)
        #print 'Course-URL: "%s"' % course_api_url
        r = requests.get(course_api_url, cookies=cookies, headers=headers)
        #print 'Response from Server: %s' % r        
        try:
            course_name = cleanup_string(r.json()['elements'][0]['title'])
        except:
            if r.json()['status'] == 404:
                print('[!] Server-Reponse: 404. Mostly caused by user failure when providing a wrong course slug in config file.\n[!] Check for errors like: course-title-xyz/setting-up-the-abc. Only course slug is allowed.')
            if r.json()['status'] == 429:
                print("[!] Server-Reponse: 429 (Too Many Requests). Thus your account has been temporarily blocked by LinkedIn.\n[!] Try again in 12 hours. Each new made request in that time will reset and/or double the waiting time.")
            exit(0);
        else:
            course_description = r.json()['elements'][0]['description']
            fullCourseUnlocked = r.json()['elements'][0]['fullCourseUnlocked']
            course_releasedate_unix = r.json()['elements'][0]['releasedOn']
            course_releasedate = time.strftime("%Y.%m", time.gmtime(course_releasedate_unix / 1000.0))
                #for future use: tag/name of updated-element unknown on LinkedIn Learning so far. If known, use the newer Update date for course-folder instead of old initial release date
                #course_updatedate_unix = 
                #course_updatedate_
            course_folder_path = '%s/%s (%s)' % (base_download_path, course_name, course_releasedate)

            extractedCourseName = extractName(course_name)
            course_folder_path_old = '%s/%s' % (base_download_path, extractedCourseName) # old version of path to course
            # course_dir_structure_old = False

            print '[*] __________ Starting download of course "%s" __________' % course_name        
            #Check if access to full course
            if fullCourseUnlocked == True:
                print('[*] Access to full course is GRANTED :). Start downloading.\n')
            else:
                print('[!] Access to full course is DENIED ):. Check login data and/or premium-status of account. Trying next course.\n')
                continue   
            
            # if old type name course folder is present rename it
            if os.path.exists(course_folder_path_old):
                # course_dir_structure_old = True
                print '** Course directory structure is old **\n\t Renaming Course Folder \n'
                os.rename(course_folder_path_old, course_folder_path) # will not work on windows if new type folder is already present.
                print '\t[!] Rename Successful\n'
                 
            #Download course description
            if os.path.exists(course_folder_path + '/' + 'Description' + file_type_description):
                    print '[!] Description file: already existing.\n'                    
            else:
                print ('[*] Course description: downloading...')
                download_description(course_folder_path, 'Description' + file_type_description, course_description, 'https://www.linkedin.com/learning/' + course)
                print('[*] --- finished.\n')
            #Download course exercise files        
            try:
                exercise_file_name = r.json()['elements'][0]['exerciseFiles'][0]['name']
                exercise_file_url = r.json()['elements'][0]['exerciseFiles'][0]['url']
                exercise_size = (r.json()['elements'][0]['exerciseFiles'][0]['sizeInBytes'])/1024/1024
            except:
                print('[!] Exercise files: not available for this course.\n')
            else:                
                if os.path.exists(course_folder_path + '/' + exercise_file_name):
                    print '[!] Exercise file: already existing.\n'
                else:
                    print ('[*] Exercise file (%s MB): downloading...' % exercise_size)
                    download_file(exercise_file_url, course_folder_path, exercise_file_name)                    
                    print('[*] --- finished.\n')
            #Chapters
            chapters = r.json()['elements'][0]['chapters']
            print ('[*] Parsing course\'s chapters')
            print ('[*] [%d chapters found]' % len(chapters))
            chapter_index = 0
            for chapter in chapters:
                print("")
                chapter_name = cleanup_string(chapter['title'])
                videos = chapter['videos']
                video_index = 0
                chapter_index +=1
                print ('[*] --- Parsing chapter #%s "%s" for videos') % (str(chapter_index).zfill(2), chapter_name)
                print ('[*] --- [%d videos found]' % len(videos))

                file_path = course_folder_path + '/' + '%s - %s' % (str(chapter_index).zfill(2),chapter_name) # Folder path of current chapter (new naming convention)

                extractedName = extractName(chapter_name)

                if not os.path.exists(file_path):
                    print '||\t New folder not found. Checking for old folder'                    
                    renameOldFolder(course_folder_path, chapter_index, extractedName, file_path)

                #Videos
                for video in videos:
                    video_name = cleanup_string (video['title'])
                    video_slug = video['slug']
                    video_url = 'https://www.linkedin.com/learning-api/detailedCourses' \
                                '?addParagraphsToTranscript=false&courseSlug={0}&q=slugs&resolution=_720&videoSlug={1}'.format(course, video_slug)
                    r = requests.get(video_url, cookies=cookies, headers=headers)                
                    video_index += 1
                    #Download videos
                    try:
                        download_url = re.search('"progressiveUrl":"(.+)","streamingUrl"', r.text).group(1)
                        #print 'Searching-URL: "%s"' % download_url
                    except Exception as e:        
                        print ('[!] ------ Can\'t download the video "%s", probably is only for premium users. Check full access in browser' % video_name)
                        print(e)
                    else:
                        #
                        #.zfill(2) wieder hinzufügen nach dem Verifying der bisherigen Downloads!!
                            #.zfill(2) Add again after verifying the previous Downloads!!

                        file_name = '%s - %s' % (str(video_index).zfill(2), video_name)          

                        file_path_full = file_path + '/' + file_name + file_type_video

                        extractedVideoName = extractName(video_name)

                        if not os.path.exists(file_path_full):
                            print '||\t New file not found. Checking for old file'
                            renameOldFile(file_path, extractedVideoName, file_type_video, file_path_full)
                                            
                        print ('[*] ------ Downloading video #%s "%s"' % (str(video_index).zfill(2), video_name))
                        if os.path.exists(file_path + '/' + file_name + file_type_video):
                            print '[!]          ->video file already existing, now checking subtitle existence'                    
                        else:
                            download_file(download_url, file_path, file_name + file_type_video)
                    #Download subtitles
                    try:
                        subtitles = r.json()['elements'][0]['selectedVideo']['transcript']['lines']
                    except Exception as e:
                        print('[*] ------ No subtitles available')
                        print(e)
                    else:                    
                        print ('[*] ------ Downloading subtitles')
                        if os.path.exists(file_path + '/' + file_name + file_type_srt):
                            print('[!]          ->subtitle file already existing, skipping to next')
                        else:
                            download_subtitles(file_path, file_name + file_type_srt)
                        # runs += 1
                        # if runs % 10 == 0:
                        #     print '================= %d videos done' % runs
                        #     # sys.exit(0)
                    print("")
        #automatically comment course out from download list in config file
        comment_out_finished_course(course)
        
        print '[*] __________ Finished course "%s" __________' % course_name
                    