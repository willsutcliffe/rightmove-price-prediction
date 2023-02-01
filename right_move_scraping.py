import requests
from urllib.parse import urlencode
from bs4 import BeautifulSoup
from csv import writer
import os
import re
from matplotlib import pyplot as plt
import cv2
import numpy as np
import pandas as pd
from PIL import Image
from pytesseract import pytesseract
from pytesseract import image_to_string


# Classes for scraping right move
class RMScraper():
        """
            Class for scraping property pages from
            RightMove
            
            Atributes
            ---------

            _url : str
                a string representing the rightmove page url

            _headers : str
                string containing header for making requests

            _info : dict
                for storing the details of a property

            _data : list
                list to store all data collected
                
        """
    def __init__(self,url):
        """
        Constructor initialises _url

        Parameters
        ----------

            _url : str
                a string representing the rightmove page url
        """
        self._url = url
        self._headers = {
      "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36"
       }
        self._info = {}
        self._data = []
        
    def get_href(self, block):
        """
        stores property link in dict _info
        """
        self._info['href'] = block.find('a', class_="propertyCard-link").get("href")
        
    def get_property_description(self, block):
        """
        stores property description in dict _info
        """
        self._info['description'] = block.text
        
    def get_title(self, block):
        """
        stores property title in dict _info
        """
        self._info['title_and_address'] = block.text
    
    def get_price(self, block):
        """
        stores price in dict _info
        """
        self._info['price'] = block.text
        
    def property_loop(self):
        """
        main loop over properties. Loops over all
        properties on each page and stores the information
        in _data. This includes also looping over all property
        pages.
        """
        sections = self._soup.find_all('div', class_="propertyCard-section")
        descriptions = self._soup.find_all('div', class_="propertyCard-description")
        #self._images.append(self._soup.find_all('div', class_="propertyCard-img"))
        prices = self._soup.find_all('div', class_="propertyCard-price")
        for i in range(0,len(sections)-1):
            self.get_href(sections[i])
            self.get_price(prices[i])
            self.get_property_description(descriptions[i])
            self.get_title(sections[i])
            self._data.append(dict(self._info))
    def loop_page(self,url):
        for j in range(1,43):
            new_index = f'index={str(j*24)}'
            url = self._url.replace('index=1', new_index)
            self._r = requests.get(url, headers=self._headers)
            self._soup = BeautifulSoup(self._r.content,'html.parser')
            self.property_loop()


class RMPageScraper():
    def __init__(self,url):
        self._url = url
        self._headers = {
      "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36"
       }
        self._r = requests.get(url, headers=self._headers)
        self._soup = BeautifulSoup(self._r.content,'html.parser')
        self._info = {}
        self._data = []
        
    def get_address(self):
        lists = self._soup.find_all('h1', class_="_2uQQ3SV0eMHL1P6t5ZDo2q")
        if len(lists) > 0:
            self._info['address'] =  lists[0].text
        else:
            self._info['address'] =  None
        
    def get_price(self):
        lists = self._soup.find_all('div', class_="_1gfnqJ3Vtd1z40MlC0MzXu")
        if len(lists) > 0:
            s = lists[0].text
            self._info['price'] = s   
        
    def get_description(self):
        lists = self._soup.find_all('div', class_="OD0O7FWw1TjbTD4sdRi1_")
        if len(lists) > 0:
            self._info['description'] =  lists[0].text
        else:
            self._info['description'] =  None
    
    
    def get_stations(self):
        lists = self._soup.find_all('ul', class_="_2f-e_tRT-PqO8w8MBRckcn")
        if len(lists) > 0:
            self._info['stations'] = lists[0].text
        else:
            self._info['stations'] = None            

    def get_plan(self):
        lists = self._soup.find_all('a', class_="_1EKvilxkEc0XS32Gwbn-iU")
        self._info[f'plan'] = None
        if len(lists) > 0:
            url = self._url + '#/floorplan?activePlan=1&channel=RES_BUY'
            url = url.replace("/?channel=RES_BUY#/", "/")
            r = requests.get(url, headers=self._headers)
            soup = BeautifulSoup(r.content,'html.parser')
            self._info[f'plan1'] = None
            self._info[f'plan2'] = None
            self._info[f'plan3'] = None
            for image in soup.find_all('img'):
                if "floor" in str(image).lower():
                    s = str(image)
                    start = 'src='
                    end = '>'
                    result = re.search('%s(.*)%s' % (start, end), s).group(1)
                    if self._info['plan'] == None:
                        self._info['plan'] = result
                        if ".gif" in result:
                            self._info['plan_text'] = None
                        else:
                            self._info['plan_text'] = self.get_text_from_image(result)
                        break

                        
    def get_text_from_image(self,text):
        if '.gif' in text:
            text = text[text.find('"h')+1:text.find('f"')+1]
        else:
            text = text[text.find('"h')+1:text.find('g"')+1]
        text = text.replace("/dir/", "/")
        text = text.replace("_max_296x197","")
        os.system(f'wget {text}')
        filename = text.split('/')[-1]
        print(filename)
        img = cv2.imread(filename)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (3,3), 0)
        thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
        return image_to_string(thresh)
        
    def get_info(self):
        items = self._soup.find_all('dd', class_="_1hV1kqpVceE9m-QrX_hWDN")

        if(len(items) > 0):
            self._info['type'] = items[0].text
        else:
            self._info['type'] = None
        if(len(items) > 1):
            self._info['n_bedrooms'] = items[1].text
        else:
            self._info['n_bedrooms'] = None
        if(len(items) > 2):
            self._info['n_bathrooms'] = items[2].text
        else:
            self._info['n_bathrooms'] = None
        if(len(items) > 3):
            self._info['tenure'] = items[3].text
        else:
            self._info['tenure'] = None
        if(len(items) > 4):
            self._info['size'] = items[4].text
        else:
            self._info['size'] = None
    def get_agent(self):
        try:
            self._info['agent'] = self._soup.find_all('div', class_="fk2DXJdjfI5FItgj0w4Fd")[0].text.split(',')[0]
        except:
            print("An agent exception occurred") 
            self._info['agent'] = None
            
    
    def get_images(self):
        img_tags = self._soup.find_all('img')
        for i in range(0,3):
            s = str(img_tags[i])
            start = 'src='
            end = '>'
            result = re.search('%s(.*)%s' % (start, end), s).group(1)
            self._info[f'image{i}'] =  result
            
        

    def get_all(self):
        self.get_address()
        self.get_price()
        self.get_description()
        self.get_stations()
        self.get_info()
        self.get_plan()
        self.get_agent()
        
    def property_loop(self):
        sections = self._soup.find_all('div', class_="propertyCard-section")
        descriptions = self._soup.find_all('div', class_="propertyCard-description")
        prices = self._soup.find_all('div', class_="propertyCard-price")
        for i in range(0,len(sections)-1):
            #print(i)
            self.get_href(sections[i])
            self.get_price(prices[i])
            self.get_property_description(descriptions[i])
            self.get_title(sections[i])
            self._data.append(list(self._info.values()))
    def loop_page(self,url):
        for j in range(1,43):
            new_index = f'index={str(j*24)}'
            print(url, j)
            url = self._url.replace('index=1', new_index)
            self._r = requests.get(url, headers=self._headers)
            self._soup = BeautifulSoup(self._r.content,'html.parser')
            self.property_loop()
