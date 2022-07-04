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
from url_constant import DESKTOP_CORE_COMPONENTS

def get_soup(pg):
    # &Order= determines order of product on page
    # options are: [0,1,2,3,4,5]
    # 0 = featured items
    # 1 = lowest price
    # 2 = highest price
    # 3 = best selling
    # 4 = best rating
    # 5 = most reviews
    # &PageSize= determines number of products per page
    # options are: [36, 60, 96]
    # &page= current page number
    # %208000 determines that the items displayed are sold by newegg
    url = "https://www.newegg.com/p/pl?N=100007611%208000&Order=2&PageSize=96&page="
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get(url + pg)
    content = driver.page_source
    soup = BeautifulSoup(content, features="html.parser")
    return soup

# recursively pull product page urls from memory product list page
def parse_category_pages(queue=deque(), total_pages=None, pg=1):
    # on first loop pull total page number from pagination text
    if total_pages is None:
        soup = get_soup('% s' % pg)
        span = soup.find('span', attrs={'class':'list-tool-pagination-text'})
        strong = span.strong.text
        total_pages = int(strong.split('/')[1])

        queue = queue_product_pages(soup, queue)
        return parse_category_pages(queue, total_pages, pg + 1)
    elif pg > 2:
        return queue

    soup = get_soup('% s' % pg)
    
    queue = queue_product_pages(soup, queue)
    return parse_category_pages(queue, total_pages, pg + 1)

# add product page urls to queue
def queue_product_pages(soup, queue):
    for div in soup.find_all('div', attrs={'class':'item-container'}):
        a = div.a
        # Motherboard RAM combos are listed with memory
        # next 2 lines will prevent adding these combo
        # item pages to the queue
        if 'combo-img-0' in a['class']:
            continue
        href = a['href']
        queue.append(href)
    return queue

# measure the length of a file by number of lines
def file_len(filename):
    with open(filename) as f:
        for i, _ in enumerate(f):
            pass
    return i + 1

# save queue data to csv file for ease of access
def write_pgs_queue_to_csv(queue, file):
    if exists(file) and file_len(file) is len(queue) + 1:
        return
   
    queue_copy = queue.copy()
    f = open(file, 'w')
    writer = csv.writer(f)
    writer.writerow(['product_num','Product Page URL'])
    i = 0
    while queue_copy:
        i += 1
        writer.writerow([i ,queue_copy.popleft()])

# main product page collection method 
def get_product_pages():
    product_pages_file = 'csv_files/product_pages.csv' # product pages file path
    dont_update = True # boolean for updating. set false to update existing data
    if exists(product_pages_file) and dont_update:
        print('product pages list exists')
        return

    product_page_queue = parse_category_pages()
    write_pgs_queue_to_csv(product_page_queue, product_pages_file)
    return product_page_queue

get_product_pages()
    