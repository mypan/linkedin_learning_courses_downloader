import sys
import codecs
import traceback
import os
import re

from requests import get

from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains

import config
"""
	ELEMENT SELECTORS
"""

LINKEDIN_LOGIN = "https://www.linkedin.com/uas/login"
EMAIL_INPUT = 'input#session_key-login'
PASSWORD_INPUT = 'input#session_password-login'
LOGIN_BUTTON = '#btn-primary'
MAIN_CONTAINER = '.core-rail'

SIDEBAR = '.sidebar-area'

CHAPTER_ITEMS = '.chapter-item'
CHAPTER_NAME = '.chapter-name'
VIDEOS = '.video-item-container'
VIDEO_SETTINGS = '.mejs-settings-button'
VIDEO_NAME = '.banner-course-title'
STREAM_QUALITIES = '.stream-qualities > li'

LOADER = '.route-loader-container'
class url_change(object):
    def __init__(self, prev_url):
        self.prev_url = prev_url

    def __call__(self, driver):
        return self.prev_url != driver.current_url


class LinkedinVideoDownloader(object):
    def __init__(self):

        self.driver = webdriver.Firefox()
        self.driver.set_window_size(1600, 900)

    def __del__(self):

        if self.driver:
            self.driver.close()

    def start(self):
        self.login()
        for course in config.COURSES:
            self.get_videos(course)
        return self

    def login(self):
        self.driver.get(LINKEDIN_LOGIN)
        email_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, EMAIL_INPUT)))
        email_input.send_keys(config.USERNAME)
        password_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, PASSWORD_INPUT)))
        password_input.send_keys(config.PASSWORD)
        self.driver.find_element(By.CSS_SELECTOR, LOGIN_BUTTON).click()
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, MAIN_CONTAINER)))

    def get_videos(self, url):
        self.driver.get(url)
        sidebar = WebDriverWait(self.driver, 20).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, SIDEBAR)))
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        WebDriverWait(self.driver, 20).until(
            EC.invisibility_of_element_located((By.CSS_SELECTOR, LOADER)))

        chapters = sidebar.find_elements(By.CSS_SELECTOR, CHAPTER_ITEMS)
        course_name = self.driver.find_element(By.CSS_SELECTOR, '.course-title').text
        course_name = re.sub(r'[\\/*?:"<>|]', "", course_name)

        is_HD = False

        for chapter in chapters:
            chapter_name = chapter.find_element(By.CSS_SELECTOR, CHAPTER_NAME).text
            v = 0
            videos = chapter.find_elements(By.CSS_SELECTOR, VIDEOS)
            for video in videos:

                url_before = self.driver.current_url
                self.driver.execute_script("return arguments[0].scrollIntoView();", video)
                video.click()
                WebDriverWait(self.driver, 10).until(url_change(url_before))

                if not is_HD and config.HD:
                    settings_button = self.driver.find_element(By.CSS_SELECTOR, VIDEO_SETTINGS)
                    ActionChains(self.driver).move_to_element(settings_button).perform()
                    stream_qual = self.driver.find_elements(By.CSS_SELECTOR, STREAM_QUALITIES)
                    stream_qual[-1].click()
                    is_HD = True

                video_name = self.driver.find_element(By.CSS_SELECTOR, VIDEO_NAME).text
                video_name = re.sub(r'[\\/*?:"<>|]', "", video_name)
                try:
                    video_element = self.driver.find_element(By.CSS_SELECTOR, 'video')
                except:
                    print '"' + video_name + '" is blocked'
                    break
                video_url = video_element.get_attribute('src')
                self.download_file(video_url, course_name + '/' + chapter_name, str(v) + '_' + video_name + '.mp4')
                v += 1

    def download_file(self, url, file_path, file_name):
        reply = get(url, stream=True)
        if not os.path.exists(file_path):
            os.makedirs(file_path)

        with open(file_path + '/' + file_name, 'wb') as f:
            for chunk in reply.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)


def main():
    sys.stdout = codecs.getwriter('utf8')(sys.stdout, 'strict')
    sys.stderr = codecs.getwriter('utf8')(sys.stderr, 'strict')

    downloader = LinkedinVideoDownloader()

    try:
        downloader.start()
    except:
        err_msg = traceback.format_exc()
        print err_msg


if __name__ == "__main__":
    main()