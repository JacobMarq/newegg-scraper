from datetime import time
from distutils.spawn import spawn
from random import Random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from newegg_scraper.dialogue import prompt_complete_captcha
from bs4 import BeautifulSoup
from collections import deque
from os.path import exists
import pandas as pd
import json
import csv

# newegg monitors traffic for bot activity 
# redirects request to 'are you human' page
# requires captcha
def check_for_captcha(soup: BeautifulSoup):
        for h1 in soup.find_all('h1'):
            if h1 is not None:
                if h1.text.lower() == 'human?': 
                    return True
        return False

def handle_captcha(url: str):
    options = Options()
    options.add_experimental_option('detach', True)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(url)
    prompt_complete_captcha()

# Handles http request
def get_soup(url: str):
    options = Options()
    options.headless = True
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(url)
    content = driver.page_source
    soup = BeautifulSoup(content, features="html.parser")
    driver.close()
    return soup

# def parse_data(url: str):
#     product = { 
#         'specs': None,
#         'price': None,
#         'image': None,
#         'newegg_url': url
#     }
#     soup = get_soup(url)
#     if check_for_captcha(soup):
#         handle_captcha(url)
#         soup = get_soup(url)

#     price = get_product_price(soup)
#     product.update({'price':price})

#     img = get_product_image(soup)
#     product.update({'image':img})

#     specs = get_product_specs(soup)
#     product.update({'specs':specs})
#     return product