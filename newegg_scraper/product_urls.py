from distutils.spawn import spawn
from os import link
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager 
from bs4 import BeautifulSoup
import pandas as pd
from collections import deque
import csv
from os.path import exists
from os.path import dirname
import constant
import dialogue

# info for URL
# ORDER_BY = '&Order=': determines order of product on page
# set to 2 by default can be changed in constant.py
# options are: [0,1,2,3,4,5]
# 0 = featured items
# 1 = lowest price
# 2 = highest price
# 3 = best selling
# 4 = best rating
# 5 = most reviews

# PAGE_SIZE = '&PageSize=': determines number of products per page
# set to 96 by default can be changed in constant.py
# options are: [36, 60, 96]

# PAGE_NUM = '&page=': current page number
# SOLD_BY_NE = %208000: determines that the items displayed are sold by newegg
def append_category_url_params(url):
    new_url = url + constant.SOLD_BY_NE + constant.ORDER_BY + constant.PAGE_SIZE + constant.PAGE_NUM
    return new_url

# gather beautiful soup of url
def get_soup(url):
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get(url)
    content = driver.page_source
    soup = BeautifulSoup(content, features="html.parser")
    return soup

# add product urls to queue
def enqueue_product_urls(soup, queue):
    for div in soup.find_all('div', attrs={'class':'item-container'}):
        a = div.a
        # Motherboard RAM combos are listed in memory category
        # next 2 lines will prevent adding these combo
        # item pages to the queue
        if 'combo-img-0' in a['class']:
            continue
        href = a['href']
        queue.append(href)
    print('enqueue', len(queue))
    return queue

# recursively pull product urls from category pages
def parse_category_pages(url, queue=None, total_pages=None, pg=1):
    # on first loop append params to category url and pull total page number from pagination text
    if total_pages is None:
        queue = deque()
        url = append_category_url_params(url)
        soup = get_soup(url + ('% s' % pg))
        span = soup.find('span', attrs={'class':'list-tool-pagination-text'}) # contains '"Page" <!-- --> <strong> "x" <!-- --> "/" <!-- --> "y" </strong>'
        strong = span.strong.text # contains 'x/y'
        total_pages = int(strong.split('/')[1])

        print(1,len(queue))
        queue = enqueue_product_urls(soup, queue)
        print(2,len(queue))
        return parse_category_pages(url, queue, total_pages, pg + 1)
    elif pg > 2: # when testing recommend hard coding a small number / for production pg > total_pages
        return queue

    soup = get_soup(url + ('% s' % pg))
    print(3, len(queue))
    queue = enqueue_product_urls(soup, queue)
    print(4, len(queue))
    return parse_category_pages(url, queue, total_pages, pg + 1)

# measure the length of a file by number of lines
def file_len(filename):
    with open(filename) as f:
        for i, _ in enumerate(f):
            pass
    return i + 1

# create url.csv file path
def create_url_file_path(category):
    file_name = category + '_urls.csv'
    file_dir = '/url_files/'
    file_path = dirname(__file__) + file_dir + file_name
    return file_path

# save a copy of queue to csv file
def write_queue_to_csv(queue, file):
    if exists(file) and file_len(file) is len(queue) + 1:
        return
   
    queue_copy = queue.copy()
    with open(file, 'x') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow([constant.CSV_HEADER_1, constant.CSV_HEADER_2, constant.CSV_HEADER_3])
        entry_num = 0
        while queue_copy:
            entry_num += 1
            pg = int(entry_num / constant.E_PER_PAGE) + 1 # determine pg number by dividing entry number by the number of entries per page
            writer.writerow([pg ,queue_copy.popleft(), entry_num])
        csv_file.close()

# append queue of new items to url file
def append_queue_to_csv(queue, entry_num, file):
    queue_copy = queue.copy()
    with open(file, 'a') as csv_file:
        writer = csv.writer(csv_file)
        while queue_copy:
            entry_num += 1
            pg = int(entry_num / constant.E_PER_PAGE) + 1 # determine pg number by dividing entry number by the number of entries per page
            writer.writerow([pg, queue_copy.popleft(), entry_num])
        csv_file.close()

# create queue from url file
def get_queue_from_csv(file):
    queue = deque()
    with open(file, newline='') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            if row:
                queue.append(row[constant.CSV_HEADER_2])
        csv_file.close()
    return queue

# get last 20 rows including page number, url, and entry number from csv
def get_last_rows_from_csv(file):
    last_rows = []
    data = []
    with open(file, newline='') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            if row:
                data.append(row)
        csv_file.close()
    # last rows set to 20 due to variance in how the page is read and exclusion of combo items
    for i in range(1, 20):
        i = i * -1
        last_rows.append(data[i])  
    return last_rows

# check if the last item, from the category page, already exists in csv file
def last_rows_contain_last_item(rows, item):
    for row in rows:
        if row[constant.CSV_HEADER_2] == item: 
            return True
        else: 
            continue

# find all new items, appending them to new queue in proper order
def enqueue_new_items(queue, last_row):
    new_queue = deque()
    cur_item = queue.pop()
    while cur_item != last_row[constant.CSV_HEADER_2]:
        new_queue.appendleft(cur_item)
        cur_item = queue.pop()
    return new_queue

# yes/no prompt for user
def prompt_yes_no():
    inp = input().lower()
    while inp != 'yes' and inp != 'no':
        dialogue.input_error_yn()
        inp = input()
    if inp == 'yes': return True
    elif inp == 'no': return False

# handle url file update to check if new urls are needed, update file if so
def update_product_urls(file, category, category_url):
    queue = deque()
    last_rows = get_last_rows_from_csv(file) # array to store last rows scraped and added to file
    # reparse category pages starting from the last recorded page on file
    queue = parse_category_pages(category_url, queue, None, int(last_rows[0][constant.CSV_HEADER_1]))
    last_item = queue.pop() # last item found on category page

    # check if last item already exists on file
    if last_rows_contain_last_item(last_rows, last_item):
        # allow user to continue and scrape existing url file or skip it
        dialogue.continue_scraping(file)
        if prompt_yes_no(): 
            return get_product_urls(category, category_url, True)
        else: return None
    else:
        # append new items to end of csv file
        queue.append(last_item)
        queue = enqueue_new_items(queue, last_rows[0])
        append_queue_to_csv(queue, int(last_rows[0][constant.CSV_HEADER_3]), file)
        # return queue of new items for product scraping
        return queue

# main product url collection method 
def get_product_urls(category, category_url, dont_update = False):
    queue = deque()
    # file path to store product_urls.csv file
    url_file = create_url_file_path(category)
    # if url file does exist and no new urls are needed, pull queue from file
    if exists(url_file) and dont_update:
        queue = get_queue_from_csv(url_file) 
        return queue
    # if url file exists but new urls may be needed, update file
    elif exists(url_file) and not dont_update:
        return update_product_urls(url_file, category, category_url)

    # if url file does not exist, create one
    queue = parse_category_pages(category_url)
    print(category, len(queue))
    write_queue_to_csv(queue, url_file)
    return queue

# url = 'https://www.newegg.com/p/pl?N=100007611%208000&Order=2&PageSize=96&page=' # category url
# url_file = dirname(__file__) + '/csv_files/product_urls.csv' # product urls.csv file path
# queue = get_product_urls()
# print(queue) 