from datetime import time
from distutils.spawn import spawn
from random import Random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from newegg_scraper.dialogue import prompt_complete_captcha
from newegg_scraper.interface import get_soup, check_for_captcha, handle_captcha
from bs4 import BeautifulSoup
from collections import deque
from os.path import exists
import pandas as pd
import json
import csv

def get_headers_from_csv(file: str):
    header_dict = {}
    with open(file, newline='') as csv_file:
        reader = csv.DictReader(csv_file)
        header_dict = (dict.fromkeys(list(reader)[0]))
    return header_dict

# header dictionary used when converting to csv file
def create_header_dict(file: str):
    header_dict = {'price':None, 'image':None, 'newegg_url':None}
    if exists(file):
        header_dict = get_headers_from_csv(file)
    return header_dict

def update_header_dict(specs: dict, header_dict: dict):
    for key in specs.keys():
        if not key:
            continue

        if key not in header_dict:
            header_dict[key] = None
        else:
            continue
    return header_dict
 
def get_product_price(soup: BeautifulSoup):
    price = soup.find('li', class_='price-current')
    if price is None:
        return None
    price = price.text
    if " –" in price:
        price = price[:-2]
    return price

def get_product_image(soup: BeautifulSoup):
    img = soup.find('div', attrs={'style':'order:-1'})
    if img is None:
        return None
    elif img.div.img['src'] == 'https://c1.neweggimages.com/ProductImageCompressAll300/AFRX_1_201808132111656731.jpg':
        return None
    img = img.div.img['src']
    return img

# specification names are stored as table header elements
def get_spec_table_header(tr: BeautifulSoup):
    th = tr.find('th')
    if th is None:
        return None
    # some table headers contain a question mark button that
    # displays a div giving more information about that
    # header
    
    # next 2 lines remove that button and its children
    # from the header
    if th.a is not None:
        th.a.decompose()

    if th.has_attr('class'):
        return None

    th = th.text.strip().lower()
    # Similar Products table begins with 'products' header
    # next 2 lines exits the loop before Similar Products Table
    if th == 'products':
        return th
    th = th.replace(" ", "_")
    return th

def get_product_specs(soup: BeautifulSoup):
    specs = {}
    # all items under specs tab are stored as table row
    # items under 'Compare With Similar Products' are also table rows
    for tr in soup.find_all('tr', limit=25):
        th = get_spec_table_header(tr)
        if th is None:
            continue
        elif th == 'products':
            break
        
        td = tr.find('td')
        if td is not None:
            td = tr.text.strip()
        
        specs[th] = td
    return specs

def parse_data(url: str):
    product = { 
        'specs': None,
        'price': None,
        'image': None,
        'newegg_url': url
    }
    soup = get_soup(url)
    if check_for_captcha(soup):
        handle_captcha(url)
        soup = get_soup(url)

    price = get_product_price(soup)
    product.update({'price':price})

    img = get_product_image(soup)
    product.update({'image':img})

    specs = get_product_specs(soup)
    product.update({'specs':specs})
    return product

# handles full file path creation from user input on main
def create_file_path(save_dir: str, category: str, file_type: str):
    file_path = save_dir + category + file_type
    return file_path

def write_data_to_json(data: dict, file: str):
    json_string = json.dumps(data)
    file_mode = None
    if exists(file):
        file_mode = 'w'
    else:
        file_mode = 'x'
    with open(file, file_mode) as save_file:
        save_file.write(json_string)

def update_json_file(data: dict, file: str):
    file_data = None
    with open(file, 'r') as json_file:
        file_data = json.load(json_file)
    file_data['products'].extend(data['products'])
    write_data_to_json(file_data, file)

# corrects for varying order and number of keys in dict to match csv columns
def create_row(product: dict, headers: list):
    if product['specs']:
        specs = product.pop('specs') 
        product.update(specs)
    else:
        product.pop('specs')
        
    new_dict = {}
    for header in headers:
        if header in product:
            new_dict[header] = product[header]
        else:
            new_dict[header] = None
    return new_dict

def write_data_to_csv(data: list, file: str, header_dict: dict):
    # header dictionary handles the issue of having an unknown number of various headers on each product within a category  
    headers = header_dict.keys()

    with open(file, 'x') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=headers)
        writer.writeheader()
        for product in data:
            new_dict = create_row(product, headers)
            writer.writerow(new_dict)

def append_data_to_csv(data: list, file: str, header_dict: dict):
    headers = header_dict.keys()

    with open(file, 'a') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=headers)
        for product in data:
            new_dict = create_row(product, headers)
            writer.writerow(new_dict)

# data stored as a list allows new products to be appended simply to the existing list
def overwrite_csv(data: list, file: str, header_dict: dict):
    headers = header_dict.keys()

    with open(file, 'r+') as csv_file:
        reader = csv.DictReader(csv_file)
        data = list(reader) + data
        writer = csv.DictWriter(csv_file, fieldnames=headers)
        writer.writeheader()
        for product in data:
            new_dict = create_row(product, headers)
            writer.writerow(new_dict)

def handle_csv_file_update(data: list, file: str, header_dict: dict, csv_headers: dict):
    if header_dict == csv_headers:
        append_data_to_csv(data, file, header_dict)
    else:
        overwrite_csv(data, file, header_dict)

# main product data collection method
def scrape_product_data(save_dir: str, category: str, file_type: str, queue=deque()):
    data = None
    products_list = []
    file_path = create_file_path(save_dir, category, file_type)
    if file_type == '.csv':
        header_dict = create_header_dict(file_path)
        csv_headers = header_dict

    while queue:
        product_url = queue.popleft()
        product = parse_data(product_url, file_type)
        if file_type == '.csv':
            header_dict = update_header_dict(product['specs'], header_dict)
        products_list.append(product)
        time.sleep(Random.randint(0, 5))

    if file_type == '.json':
        data = {'products':products_list} # stores products in nested dict format for easy json file conversion
        
        if exists(file_path):
            update_json_file(data, file_path)
        else:
            write_data_to_json(data, file_path)
    elif file_type == '.csv':
        data = products_list # keeps products as a list for easier csv file conversion

        if exists(file_path):
            handle_csv_file_update(data, file_path, header_dict, csv_headers)
        else:
            write_data_to_csv(data, file_path, header_dict)