import unittest
from unittest import mock
from unittest.mock import Mock, patch, mock_open
from io import StringIO
import csv
import warnings
from os.path import dirname

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

from collections import deque
from test.helper_methods import get_file_reader

import newegg_scraper
from newegg_scraper.interface import get_soup, check_for_captcha, handle_captcha

class TestProductMethods(unittest.TestCase):
    def setUp(self):
        # self.dir_name = 'file://' + dirname(__file__)
        self.url_example_captcha = "/html_file_example/are-you-a-human.html"
        self.url_example_product = "/html_file_example/RTX3090.html"
        self.url_google_homepage = "https://www.google.com"

        url_captcha = dirname(__file__) + self.url_example_captcha
        url_product = dirname(__file__) + self.url_example_product
        self.soup_captcha = BeautifulSoup(get_file_reader(url_captcha), features='html.parser')
        self.soup_product_ex = BeautifulSoup(get_file_reader(url_product), features='html.parser')
        warnings.simplefilter('ignore', ResourceWarning)
    
    # ===== Page Content Gathering =====
    def test_check_for_captcha(self):
        soup = self.soup_product_ex
        self.assertFalse(check_for_captcha(soup))

        soup = self.soup_captcha
        self.assertTrue(check_for_captcha(soup))
        with self.assertRaises(AttributeError):
            check_for_captcha(None)

    def test_get_soup(self):
        url = self.url_google_homepage
        self.assertIsInstance(get_soup(url), BeautifulSoup)