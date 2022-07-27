import csv
from collections import deque
from io import StringIO
from bs4 import BeautifulSoup
from os.path import exists, dirname

import unittest
from unittest.mock import Mock, patch, mock_open, call
from newegg_scraper import product_urls
from newegg_scraper.product_urls import append_queue_to_csv, create_product_queue_from_category, create_url_file_path, enqueue_new_items, enqueue_product_urls, get_last_rows_from_csv, get_queue_list_from_csv, last_rows_contain_last_item, update_product_urls, write_queue_to_csv
from newegg_scraper.constant import CSV_HEADER_1, CSV_HEADER_2, CSV_HEADER_3, ORDER_BY, PAGE_NUM, PAGE_SIZE, SOLD_BY_NE

from test.helper_methods import get_file_reader

CATEGORY_HTML = dirname(__file__) + "/html_file_example/category.html"

class TestProductUrlMethods(unittest.TestCase):

    # ===== Product queue creation =====
    def test_enqueue_product_urls(self):
        soup = BeautifulSoup(get_file_reader(CATEGORY_HTML), features='html.parser')
        queue = deque()

        self.assertEqual(enqueue_product_urls(soup, queue), deque(['url1', 'url2', 'url3']))
        with self.assertRaises(AttributeError):
            enqueue_product_urls(None, None)

    # ----- create_product_queue_from_category() - start
    @patch.object(product_urls, 'enqueue_product_urls', return_value = deque([1]))
    @patch.object(product_urls, 'get_soup', return_value = BeautifulSoup("<span class='list-tool-pagination-text'>Page <!-- --> <strong> 1 <!-- --> / <!-- --> 1 </strong></span>", features='html.parser'))
    def test_create_product_queue_from_category_with_one_page(self, mock_get_soup: Mock, mock_enqueue_product_urls: Mock):
        url = ''

        q = create_product_queue_from_category(url)
    
        self.assertEqual(q, deque([1]))
        mock_get_soup.assert_called_once()
        mock_enqueue_product_urls.assert_called_once()

    @patch.object(product_urls, 'enqueue_product_urls', return_value = deque([1]))
    @patch.object(product_urls, 'get_soup', return_value = BeautifulSoup("<span class='list-tool-pagination-text'>Page <!-- --> <strong> 1 <!-- --> / <!-- --> 3 </strong></span>", features='html.parser'))
    def test_create_product_queue_from_category_with_many_pages(self, mock_get_soup: Mock, mock_enqueue_product_urls: Mock):
        url = ''

        q = create_product_queue_from_category(url)

        self.assertEqual(q, deque([1]))
        self.assertEqual(mock_get_soup.call_count, 3)
        self.assertEqual(mock_enqueue_product_urls.call_count, 3)

    # should collect nothing because page 2 of 1 does not exist
    @patch.object(product_urls, 'enqueue_product_urls', return_value = deque([1]))
    @patch.object(product_urls, 'get_soup', return_value = BeautifulSoup("<span class='list-tool-pagination-text'>Page <!-- --> <strong> 1 <!-- --> / <!-- --> 1 </strong></span>", features='html.parser'))
    def test_create_product_queue_from_category_page_after_total_pages(self, mock_get_soup: Mock, mock_enqueue_product_urls: Mock):
        url = ''

        q = create_product_queue_from_category(url, 0, 2)

        self.assertEqual(q, deque())
        self.assertEqual(mock_get_soup.call_count, 1)
        self.assertEqual(mock_enqueue_product_urls.call_count, 0)

    @patch.object(product_urls, 'enqueue_product_urls', return_value = deque([1]))
    @patch.object(product_urls, 'get_soup', return_value = BeautifulSoup("<span class='list-tool-pagination-text'>Page <!-- --> <strong> 1 <!-- --> / <!-- --> 4 </strong></span>", features='html.parser'))
    def test_create_product_queue_from_category_first_two_pages(self, mock_get_soup: Mock, mock_enqueue_product_urls: Mock):
        url = ''

        q = create_product_queue_from_category(url, 2, 1)

        self.assertEqual(q, deque([1]))
        self.assertEqual(mock_get_soup.call_count, 2)
        self.assertEqual(mock_enqueue_product_urls.call_count, 2)

    @patch.object(product_urls, 'enqueue_product_urls', return_value = deque([1]))
    @patch.object(product_urls, 'get_soup', return_value = BeautifulSoup("<span class='list-tool-pagination-text'>Page <!-- --> <strong> 1 <!-- --> / <!-- --> 4 </strong></span>", features='html.parser'))
    def test_create_product_queue_from_category_third_page_only(self, mock_get_soup: Mock, mock_enqueue_product_urls: Mock):
        url = ''
        full_url = SOLD_BY_NE + ORDER_BY + PAGE_SIZE + PAGE_NUM
        q = create_product_queue_from_category(url, 1, 3)

        self.assertEqual(q, deque([1]))
        mock_get_soup.assert_called_once_with(full_url + '3')
        self.assertEqual(mock_get_soup.call_count, 1)
        self.assertEqual(mock_enqueue_product_urls.call_count, 1)

    @patch.object(product_urls, 'enqueue_product_urls', return_value = deque([1]))
    @patch.object(product_urls, 'get_soup', return_value = BeautifulSoup("<span class='list-tool-pagination-text'>Page <!-- --> <strong> 1 <!-- --> / <!-- --> 5 </strong></span>", features='html.parser'))
    def test_create_product_queue_from_category_third_and_fourth_page_only(self, mock_get_soup: Mock, mock_enqueue_product_urls: Mock):
        url = ''
        full_url = SOLD_BY_NE + ORDER_BY + PAGE_SIZE + PAGE_NUM
        calls = [call(full_url + '3'), call(full_url + '4')]
        q = create_product_queue_from_category(url, 2, 3)

        self.assertEqual(q, deque([1]))
        mock_get_soup.assert_has_calls(calls)
        self.assertEqual(mock_get_soup.call_count, 2)
        self.assertEqual(mock_enqueue_product_urls.call_count, 2)

    # should collect products from page 3 only because there are only 3 pages
    @patch.object(product_urls, 'enqueue_product_urls', return_value = deque([1]))
    @patch.object(product_urls, 'get_soup', return_value = BeautifulSoup("<span class='list-tool-pagination-text'>Page <!-- --> <strong> 1 <!-- --> / <!-- --> 3 </strong></span>", features='html.parser'))
    def test_create_product_queue_from_category_page_three_and_four_with_only_three_pages(self, mock_get_soup: Mock, mock_enqueue_product_urls: Mock):
        url = ''
        q = create_product_queue_from_category(url, 2, 3)

        self.assertEqual(q, deque([1]))
        self.assertEqual(mock_get_soup.call_count, 1)
        self.assertEqual(mock_enqueue_product_urls.call_count, 1)
    # ----- create_product_queue_from_category() - end

    # ===== File creation =====
    @patch.object(product_urls, 'dirname', return_value='/dir/name')
    def test_create_url_file_path(self, mock_dirname: Mock):
        category = 'category'
        file_path = '/dir/name/url_files/category_urls.csv'

        self.assertEqual(create_url_file_path(category), file_path)
        mock_dirname.assert_called_once()
        with self.assertRaises(TypeError):
            create_url_file_path(1)
    
    def test_write_queue_to_csv(self):
        queue = deque(['a', 'b', 'c'])
        calls = [
            call().write('Page Number,Product Page URL,Entry Number\r\n'), 
            call().write('1,a,1\r\n'), 
            call().write('1,b,2\r\n'), 
            call().write('1,c,3\r\n')
        ]

        open_mock = mock_open()
        with patch("newegg_scraper.product_urls.open", open_mock, create=True) as m:
            write_queue_to_csv(queue, m)

        self.assertTrue(calls in m.mock_calls)

    # ===== Update existing file =====

    def test_append_queue_to_csv(self):
        queue = deque(['a', 'b', 'c'])
        calls = [ 
            call().write('1,a,4\r\n'), 
            call().write('1,b,5\r\n'), 
            call().write('1,c,6\r\n')
        ]

        open_mock = mock_open()
        with patch("newegg_scraper.product_urls.open", open_mock, create=True) as m:
            append_queue_to_csv(queue, 3, m)

        self.assertTrue(calls in m.mock_calls)

    def test_get_last_rows_from_csv(self):
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
        with patch("newegg_scraper.product_urls.open", open_mock, create=True) as m:
            result = get_last_rows_from_csv(m)

        self.assertTrue(len(result) == 2)
        self.assertEqual(result[0], {'header_1':'test2', 'header_2':'test2'})
        self.assertEqual(result[1], {'header_1':'test1', 'header_2':'test1'})

    def test_last_rows_contain_last_item(self):
        rows = [{CSV_HEADER_2: 'item1'}, {CSV_HEADER_2: 'item2'}]
        false_rows = [{CSV_HEADER_2: None}, {CSV_HEADER_2: None}]
        item = 'item2'

        self.assertTrue(last_rows_contain_last_item(rows, item))
        self.assertFalse(last_rows_contain_last_item(false_rows, item))

    def test_enqueue_new_items(self):
        last_row = {CSV_HEADER_2: 'url1'}
        queue = deque(['url1', 'url2', 'url3'])
        result = deque(['url2', 'url3'])

        self.assertEqual(enqueue_new_items(queue, last_row), result)
        with self.assertRaises(AttributeError):
            enqueue_new_items(None, None)

    @patch.object(product_urls, 'create_product_queue_from_category', return_value=deque(['1','a','1']))
    @patch.object(product_urls, 'get_last_rows_from_csv', return_value=[{CSV_HEADER_1: '1', CSV_HEADER_2: 'a', CSV_HEADER_3: '1'}])
    @patch.object(product_urls, 'last_rows_contain_last_item', return_value=False)
    @patch.object(product_urls, 'enqueue_new_items', return_value=deque(['1','a','1']))
    @patch.object(product_urls, 'append_queue_to_csv', return_value=None)
    def test_update_product_urls(self,
                                 mock_append_queue_to_csv: Mock,
                                 mock_enqueue_new_items: Mock,
                                 mock_last_rows_contain_last_item: Mock,
                                 mock_get_last_rows_from_csv: Mock,
                                 mock_create_product_queue_from_category: Mock):
        file = ''
        category = ''
        category_url = ''

        self.assertEqual(update_product_urls(file, category, category_url, 0), 1)
        mock_create_product_queue_from_category.assert_called_once_with('', 0, 1)
        mock_get_last_rows_from_csv.assert_called_once_with('')
        mock_last_rows_contain_last_item.assert_called_once_with([{CSV_HEADER_1: '1', CSV_HEADER_2: 'a', CSV_HEADER_3: '1'}],'1')
        mock_enqueue_new_items.assert_called_once_with(deque(['1','a','1']), {CSV_HEADER_1: '1', CSV_HEADER_2: 'a', CSV_HEADER_3: '1'})
        mock_append_queue_to_csv.assert_called_once_with(deque(['1','a','1']), 1, '')

    # ===== Queue list creation =====

    def test_get_queue_list_from_csv(self):
        csvfile = StringIO()
        csvfile.seek(0)
        fieldnames = [CSV_HEADER_1, CSV_HEADER_2, CSV_HEADER_3]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow({CSV_HEADER_1:'1', CSV_HEADER_2:'test1', CSV_HEADER_3:'1'})
        writer.writerow({CSV_HEADER_1:'1', CSV_HEADER_2:'test2', CSV_HEADER_3:'2'})
        csvfile.seek(0)
        result = None

        open_mock = mock_open(read_data=csvfile.read())
        with patch("newegg_scraper.product_urls.open", open_mock, create=True) as m:
            result = get_queue_list_from_csv(m)

        self.assertTrue(len(result) == 1)
        self.assertEqual(result[0], deque(['test1', 'test2']))