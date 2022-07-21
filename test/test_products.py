import csv
import json
import warnings
from io import StringIO
from os.path import dirname
from bs4 import BeautifulSoup

import unittest
from unittest.mock import Mock, patch, mock_open, call

from newegg_scraper import products
from test.helper_methods import get_file_reader

# Header Dictionary
from newegg_scraper.products import create_header_dict, update_header_dict, get_headers_from_csv
# Data Parsing
from newegg_scraper.products import get_product_image, get_product_specs, get_product_price, get_spec_table_header, parse_data
# File Handling
from newegg_scraper.products import create_file_path
# - JSON
from newegg_scraper.products import write_data_to_json, update_json_file
# - CSV
from newegg_scraper.products import create_row, write_data_to_csv, handle_csv_file_update, append_data_to_csv, overwrite_csv

CAPTCHA_HTML = dirname(__file__) + "/html_file_example/are-you-a-human.html"
PRODUCT_HTML = dirname(__file__) + "/html_file_example/RTX3090.html"

class TestProductMethods(unittest.TestCase):
    def setUp(self):
        # self.dir_name = 'file://' + dirname(__file__)
        warnings.simplefilter('ignore', ResourceWarning)

    # ===== Header Dictionary =====
    def test_get_headers_from_csv(self):
        csvfile = StringIO()
        csvfile.seek(0)
        fieldnames = ['header_1', 'header_2']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow({'header_1':'test1', 'header_2':'test1'})
        writer.writerow({'header_1':'test2', 'header_2':'test2'})
        csvfile.seek(0)

        result = None

        open_mock = mock_open(read_data=csvfile.read())
        with patch("newegg_scraper.products.open", open_mock, create=True) as m:
            result = get_headers_from_csv(m)

        self.assertEqual(result, ({'header_1': None, 'header_2': None}))
    
    # ----- create_header_dict() - start
    def test_create_header_dict_with_default_values(self):
        file = '/does/not/exist'

        self.assertEqual(create_header_dict(file), {'price':None, 'image':None, 'newegg_url':None})
        with self.assertRaises(TypeError):
            create_header_dict(None)

    @patch.object(products, "exists", return_value = True)
    @patch.object(products, "get_headers_from_csv", return_value = {'header_1': None, 'header_2': None})
    def test_create_header_dict_with_mocked_file_values(self, mock_exists: Mock, mock_get_headers_from_csv: Mock):
        file = '/does/exist'
        header_dict = {'header_1': None, 'header_2': None}

        self.assertEqual(create_header_dict(file), header_dict)
        
        mock_exists.assert_called_once_with(file)
        mock_get_headers_from_csv.assert_called_once_with(file)
    # ----- create_header_dict() - end

    def test_update_header_dict(self):
        old_keys = {'key_1': None, 'key_2': None}
        new_keys = {'key_2': None, 'key_3': None}
        empty_keys = {'': None, None: None, 'key_2': None, 'key_3': None}
        correct_result = {'key_1':None, 'key_2':None, 'key_3': None}
        
        self.assertEqual(update_header_dict(new_keys, old_keys), correct_result)
        self.assertEqual(update_header_dict(empty_keys, old_keys), correct_result)
        with self.assertRaises(AttributeError):
            update_header_dict(None, old_keys)
        with self.assertRaises(TypeError):
            update_header_dict(new_keys, None)
    
    # ===== Data Parsing =====
    def test_get_product_price(self):
        soup_product_ex = BeautifulSoup(get_file_reader(PRODUCT_HTML), features='html.parser')
        soup_captcha = BeautifulSoup(get_file_reader(CAPTCHA_HTML), features='html.parser')

        self.assertRegex(get_product_price(soup_product_ex), r'\$+\d+')
        self.assertEqual(get_product_price(soup_captcha), None)
        with self.assertRaises(AttributeError):
            get_product_price(None)

    def test_get_product_image(self):
        soup_product_ex = BeautifulSoup(get_file_reader(PRODUCT_HTML), features='html.parser')
        soup_captcha = BeautifulSoup(get_file_reader(CAPTCHA_HTML), features='html.parser')

        self.assertRegex(get_product_image(soup_product_ex), r'https\:\/\/')
        self.assertEqual(get_product_image(soup_captcha), None)
        with self.assertRaises(AttributeError):
            get_product_image(None)

    def test_get_spec_table_header(self):
        soup_product_ex = BeautifulSoup(get_file_reader(PRODUCT_HTML), features='html.parser')
        soup_captcha = BeautifulSoup(get_file_reader(CAPTCHA_HTML), features='html.parser')

        self.assertIsInstance(get_spec_table_header(soup_product_ex.find('tr')), str)
        self.assertEqual(get_spec_table_header(soup_captcha), None)
        with self.assertRaises(AttributeError):
            get_spec_table_header(None)

    # ----- get_product_specs() - start
    def test_get_product_specs_from_example(self):
        soup_product_ex = BeautifulSoup(get_file_reader(PRODUCT_HTML), features='html.parser')
        
        new_dict = get_product_specs(soup_product_ex)

        for key in new_dict.keys():
            self.assertIsNotNone(new_dict[key])
        with self.assertRaises(AttributeError):
            get_product_specs(None)

    def test_get_product_specs_from_empty_soup(self):
        empty_soup = BeautifulSoup()
        self.assertIsInstance(get_product_specs(empty_soup), dict)
    # ----- get_product_specs() - end

    @patch.object(products, 'get_soup', return_value = BeautifulSoup())
    def test_parse_data(self,
                        mock_get_soup: Mock ):
        url = Mock()
        product_mock = {
            'specs': None,
            'price': None,
            'image': None,
            'newegg_url': None
        }
        product = parse_data(url)

        mock_get_soup.assert_called_once_with(url)
        self.assertIsInstance(product, dict)
        self.assertEqual(product.keys(), product_mock.keys())
        self.assertIsInstance(product['specs'], dict)
        self.assertEqual(product['newegg_url'], url)
        self.assertEqual(product['price'], None)
        self.assertEqual(product['image'], None)

    # ===== File handling =====
    def test_create_file_path(self):
        save_dir = 'save/dir/'
        category = 'category'
        file_type = '.file_type'

        self.assertEqual(create_file_path(save_dir, category, file_type), 'save/dir/category.file_type')
        self.assertRegex(create_file_path(save_dir, category, file_type), r'\w+\/\w+\.\w+')
        with self.assertRaises(TypeError):
            create_file_path(2,category,2)

    # ----- JSON - start
    # ----- write_data_to_json() - start
    @patch.object(products, "exists", return_value = True)
    def test_write_data_to_json_that_exists(self, mock_exists: Mock):
        data = {'products':[{'name': 'a'},{'name': 'b'},{'name': 'c'}]}
        calls = [call().write(json.dumps(data))]

        open_mock = mock_open()
        with patch("newegg_scraper.products.open", open_mock, create=True) as m:
            write_data_to_json(data, m)
        
        m.assert_has_calls(calls)
        mock_exists.assert_called_once_with(m)

    @patch.object(products, "exists", return_value = False)
    def test_write_data_to_json_that_does_not_exist(self, mock_exists: Mock):
        data = {'products':[{'name': 'a'},{'name': 'b'},{'name': 'c'}]}
        calls = [call().write(json.dumps(data))]

        open_mock = mock_open()
        with patch("newegg_scraper.products.open", open_mock, create=True) as m:
            write_data_to_json(data, m)
        
        m.assert_has_calls(calls)
        mock_exists.assert_called_once_with(m)
    # ----- write_data_to_json() - end

    @patch.object(products, "write_data_to_json", return_value = None)
    def test_update_json_file(self, mock_write_data_to_json: Mock):
        data = {'products':[{'name': 'c'}]}
        json_string = json.dumps({'products':[{'name': 'a'},{'name': 'b'}]})
        result_data = {'products':[{'name': 'a'},{'name': 'b'},{'name': 'c'}]}
        file = StringIO()
        file.seek(0)
        file.write(json_string)
        file.seek(0)
        file = file.read()

        open_mock = mock_open(read_data = file)
        with patch("newegg_scraper.products.open", open_mock, create=True) as m:
            update_json_file(data, m)

        mock_write_data_to_json.assert_called_once_with(result_data, m)
    # ----- JSON - end

    # ----- CSV - start
    def test_create_row(self):
        header_list = ['key1','key2','key3','key4']
        product = {
            'specs': {'key4': 4},
            'key1': 1,
            'key2': 2,
            'key3': 3
        }
        new_product = {
            'key1': 1,
            'key2': 2,
            'key3': 3,
            'key4': 4
        }

        self.assertEqual(create_row(product, header_list), new_product)
        with self.assertRaises(KeyError):
            create_row({}, header_list)

    @patch.object(products, "create_row", return_value = {'header_1': 1, 'header_2': 2})
    def test_write_data_to_csv(self, mock_create_row: Mock):
        header_dict = {'header_1': None, 'header_2': None}
        headers = header_dict.keys()
        data = [{'header_1': 1, 'header_2': 2}]
        calls = [call().write('header_1,header_2\r\n'), call().write('1,2\r\n')]

        open_mock = mock_open()
        with patch("newegg_scraper.products.open", open_mock, create=True) as m:
            write_data_to_csv(data, m, header_dict)

        m.assert_has_calls(calls)
        mock_create_row.assert_called_once_with(data[0], headers)

    @patch.object(products, "create_row", return_value = {'header_1': 1, 'header_2': 2})
    def test_append_data_to_csv(self, mock_create_row: Mock):
        header_dict = {'header_1': None, 'header_2': None}
        headers = header_dict.keys()
        data = [{'header_1': 1, 'header_2': 2}]
        calls = [call().write('1,2\r\n')]

        open_mock = mock_open()
        with patch("newegg_scraper.products.open", open_mock, create=True) as m:
            append_data_to_csv(data, m, header_dict)

        m.assert_has_calls(calls)
        mock_create_row.assert_called_once_with(data[0], headers)

    @patch.object(products, "create_row", return_value = {'header_1': 1, 'header_2': 2})
    def test_overwrite_csv(self, mock_create_row: Mock):
        header_dict = {'header_1': None, 'header_2': None}
        headers = header_dict.keys()
        data = [{'header_1': 1, 'header_2': 2}]
        calls = [call().write('header_1,header_2\r\n'), call().write('1,2\r\n')]

        open_mock = mock_open()
        with patch("newegg_scraper.products.open", open_mock, create=True) as m:
            overwrite_csv(data, m, header_dict)

        m.assert_has_calls(calls)
        mock_create_row.assert_called_once_with(data[0], headers)
    
    # ----- handle_csv_file_update() - start
    @patch.object(products, "append_data_to_csv", return_value = None)
    def test_handle_csv_file_update_when_headers_are_the_same(self, mock_append_data_to_csv: Mock):
        file = Mock()
        header_dict = {'header_1': None, 'header_2': None}
        data = [{'header_1': 1, 'header_2': 2}]

        handle_csv_file_update(data, file, header_dict, header_dict)
        mock_append_data_to_csv.assert_called_once_with(data, file, header_dict)

    @patch.object(products, "overwrite_csv", return_vale = None)
    def test_handle_csv_file_update_when_headers_are_different(self, mock_overwrite_csv: Mock):
        file = Mock()
        header_dict = {'header_1': None, 'header_2': None}
        diff_dict = {}
        data = [{'header_1': 1, 'header_2': 2}]

        handle_csv_file_update(data, file, header_dict, diff_dict)
        mock_overwrite_csv.assert_called_once_with(data, file, header_dict)
    # ----- handle_csv_file_update() - end
    # ----- CSV - end

if __name__ == '__main__':
    unittest.main()