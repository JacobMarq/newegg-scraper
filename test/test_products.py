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

import newegg_scraper
from newegg_scraper.products import create_header_dict, update_header_dict, get_headers_from_csv
from newegg_scraper.products import create_file_path
from newegg_scraper.products import get_soup, check_for_captcha

class TestProductMethods(unittest.TestCase):
    def setUp(self):
        self.dir_name = 'file://' + dirname(__file__)
        self.are_you_human = "html_file_example/are-you-a-human.html"
        self.test_url = "https://www.google.com"
        self.test_url_NE = "html_file_example/RTX3090.html"
        warnings.simplefilter('ignore', ResourceWarning)

    # ===== header_dict methods =====
    def test_get_headers_from_csv(self):
        csvfile = StringIO()
        csvfile.seek(0)
        fieldnames = ['header_1', 'header_2']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow({'header_1':'test1', 'header_2':'test1'})
        writer.writerow({'header_1':'test2', 'header_2':'test2'})
        csvfile.seek(0)

        open_mock = mock_open(read_data=csvfile.read())
        with patch("newegg_scraper.products.open", open_mock, create=True) as m:
            get_headers_from_csv(m)

        self.assertTrue(m.return_value({'header_1': None, 'header_2': None}))
    
    def test_create_header_dict(self):
        file = '/does/not/exist'
        self.assertEqual(create_header_dict(file), {'price':None, 'image':None, 'newegg_url':None})
        with self.assertRaises(TypeError):
            create_header_dict(None)

    def test_update_header_dict(self):
        old_dict = {'key_1': None, 'key_2': None}
        new_keys = {'key_2': None, 'key_3': None}
        result_dict = {'key_1':None, 'key_2':None, 'key_3': None}
        self.assertEqual(update_header_dict(new_keys, old_dict), result_dict)
        with self.assertRaises(AttributeError):
            update_header_dict(None, old_dict)

    # ===== Selenium methods =====
    def test_check_for_captcha(self):
        soup = get_soup(self.dir_name + self.test_url_NE)
        self.assertEqual(check_for_captcha(soup, self.dir_name + self.test_url_NE), soup)
        with self.assertRaises(AttributeError):
            check_for_captcha(None, None)

    def test_get_soup(self):
        url = self.test_url
        self.assertIsInstance(get_soup(url), BeautifulSoup)

    # =====  File handling methods =====
    def test_create_file_path(self):
        save_dir = 'save/dir/'
        category = 'category'
        file_type = '.file_type'
        self.assertEqual(create_file_path(save_dir, category, file_type), 'save/dir/category.file_type')
        self.assertRegex(create_file_path(save_dir, category, file_type), r'\w+\/\w+\.\w+')
        with self.assertRaises(TypeError):
            create_file_path(2,category,2)

if __name__ == '__main__':
    unittest.main()