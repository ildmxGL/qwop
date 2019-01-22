#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from pytesseract import image_to_string
from PIL import Image
from io import BytesIO
import time
import cv2
import numpy as np
import sys
import win32api, win32con
import keyboard

VK_CODE = {'q':0x51,
           'w':0x57,
           'o':0x4F,
           'p':0x50}

# In[ ]:


class Game:
    def __init__(self):
        self._driver = webdriver.Chrome('./w4/chromedriver')
        self._driver.implicitly_wait(3)
        self._driver.get('http://www.foddy.net/Athletics.html')
        delay = 5
        time.sleep(delay)
        self._driver.execute_script("window.scrollTo(0, document.head.scrollHeight);")
        self._driver.find_element_by_tag_name("body").click()
        self._driver.execute_script("window.scrollTo(0, document.head.scrollHeight);")
        time.sleep(1)
        self.score_prior = 0

        
    def get(self):
        img = self.screenshot()
        final_score = 0
        
        state = self.get_state(img)
        score = self.get_score(img)
        final_score_str = self.get_final_score(img)
        done = self.is_done(final_score_str)
        if done:
            final_score = self.score2float(final_score_str)
        
        return state, score, done, final_score
    
    def click(self, x=439, y=600):
        self._driver.execute_script("window.scrollTo(0, document.head.scrollHeight);")
        win32api.SetCursorPos((x,y))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)
    
    def score2float(self, score_str):
        score_str = score_str.strip()
        score_str = score_str[:-7]
        try:
            score = float(score_str)
            self.score_prior = score
        except ValueError as e:
            print("error: ", e, "\nscore: ", score_str)
            #sys.exit(1)
            return self.score_prior
            
        return score
    
    def screenshot(self):
        element = self._driver.find_element_by_id('window1')
        location = element.location 
        size = element.size
        png = self._driver.get_screenshot_as_png()
        im = Image.open(BytesIO(png))
        left = location['x']
        top = location['y']
        right = location['x'] + size['width']
        bottom = location['y'] + size['height']
        im = im.crop((left, top, right, bottom))
        # im.save('screenshot.png')
        
        return im
    
    def convert_pil2cv(self, im):
        img = cv2.cvtColor(np.asarray(im), cv2.COLOR_RGB2GRAY)
        
        return img
    
    def is_done(self, x):
        return False if x == '' else True
    
    def get_final_score(self, img):
        img = img.crop((220, 190, 420, 215))
        try:
            final_score = image_to_string(img)
        except Exception as e:
            print("There is a error: ", e)
            sys.exit(1)
        
        return final_score
    
    def get_state(self, img):
        img = img.crop((140, 80, 440, 380))
        img = self.convert_pil2cv(img)
        img = cv2.Canny(img, 100, 200)
        img = cv2.resize(img, (80, 80))
        
        return img
    
    def get_score(self, img):
        img = img.crop((160, 25, 480, 50))
        img.save('get_score.png')
        score_str = image_to_string(img)
        
        return self.score2float(score_str)
      
    def press_key(self, key, delay=0.25):
        self.click()
        if key in VK_CODE:
            win32api.keybd_event(VK_CODE[key], 0, 0, 0)
            stop = time.time() + delay
            while time.time() < stop:
                time.sleep(0.01)
                win32api.keybd_event(VK_CODE[key], 0, 0, 0)
            win32api.keybd_event(VK_CODE[key], 0, win32con.KEYEVENTF_KEYUP, 0)
            time.sleep(0.1)
        else:
             print("Wrong key pressed")
        
    def restart(self):
        self._driver.find_element_by_tag_name("body").send_keys(Keys.SPACE)
    
    def end(self):
        self._driver.close()


