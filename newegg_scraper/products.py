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
import json
import csv

# create global header dictionary to be used for a headers list when converting to csv file
def set_global_header_dict(file):
    global header_dict 
    header_dict = {'price':None, 'image':None, 'newegg_url':None}
    # TODO: if csv file exists import csv headers as global header dict
    if exists(file):
        pass

def update_global_header_dict(header):
    global header_dict
    if header not in header_dict:
        header_dict[header] = None

# newegg monitors traffic for bot activity 
# redirects request to 'are you human' page
# requires captcha
def check_for_captcha(soup, url):
    for h1 in soup.find_all('h1'):
        print(h1)
        if h1 is not None:
            if h1.text.lower() == 'human?':
                prompt_complete_captcha()
                soup = get_soup(url)
    return soup

# Get beautiful soup of content from product page
def get_soup(url):
    options = Options()
    options.headless = True
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(url)
    content = driver.page_source
    soup = BeautifulSoup(content, features="html.parser")
    soup = check_for_captcha(soup, url)
    return soup

# handle price collection 
def get_product_price(soup):
    price = soup.find('li', class_='price-current')
    if price is None:
        return None
    price = price.text
    if " –" in price:
        price = price[:-2]
    return price

# handle img collection
def get_product_image(soup):
    img = soup.find('div', attrs={'style':'order:-1'})
    if img is None:
        return None
    elif img.div.img['src'] == 'https://c1.neweggimages.com/ProductImageCompressAll300/AFRX_1_201808132111656731.jpg':
        return None
    img = img.div.img['src']
    return img

# handle specification header collection
def get_spec_header(tr):
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

# Get product specifications
def get_product_specs(soup, file_type):
    specs = {}
    # all items under specs tab are stored as table row
    # items under 'Compare With Similar Products' are also table rows
    for tr in soup.find_all('tr', limit=25):
        th = get_spec_header(tr)
        if th is None:
            continue
        elif th == 'products':
            break
        
        td = tr.find('td')
        if td is not None:
            td = tr.text.strip()
        
        specs[th] = td
        if file_type == '.csv':
            update_global_header_dict(th)
    return specs

# parse data from product page
def parse_data(url, file_type):
    product = { 
        'specs': None,
        'price': None,
        'image': None,
        'newegg_url': url
    }
    soup = get_soup(url)

    price = get_product_price(soup)
    product.update({'price':price})

    img = get_product_image(soup)
    product.update({'image':img})

    specs = get_product_specs(soup, file_type)
    product.update({'specs':specs})
    return product

# handles save file path creation from user input on main
def create_save_file_path(save_dir, category, file_type):
    file_path = save_dir + category + file_type
    return file_path

# convert data dictionary to json string
# write json string to file at save file path
def write_data_to_json(data, file):
    json_string = json.dumps(data)
    with open(file, 'w') as save_file:
        save_file.write(json_string)
        save_file.close()

# handle updating json file
def update_json_file(data, file):
    file_data = None
    with open(file) as json_file:
        file_data = json.load(json_file)
        json_file.close
    file_data['products'].extend(data['products'])
    write_data_to_json(file_data, file)

# use global header dictionary and a flattened data dictionary to write csv file
def write_data_to_csv(data, file):
    # global header dictionary handles the issue of having an unknown number of various headers on each product within a category  
    headers = header_dict.keys()

    with open(file, "x") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=headers)
        writer.writeheader()
        for product in data:
            specs = product.pop('specs') 
            product.update(specs)
            new_dict = {}
            for header in headers:
                if header in product:
                    new_dict[header] = product[header]
                else:
                    new_dict[header] = None
            writer.writerow(new_dict)
        csv_file.close()

# TODO create method to handle updating product data
# read headers from csv file
# if headers match csv headers then append to file
# else import data as dictionary from csv file and rewrite headers
# merge new data to csv data, then write to new file
def update_csv_file(data, file):
    pass

# main product data collection method
def scrape_product_data(save_dir, category, file_type, queue=deque()):
    data = None
    products_list = []
    file_path = create_save_file_path(save_dir, category, file_type)
    if file_type == '.csv':
        set_global_header_dict(file_path)

    while queue:
        product_url = queue.popleft()
        product = parse_data(product_url, file_type)
        products_list.append(product)
        time.sleep(Random.randint(0, 5))

    if file_type == '.json':
        data = {'products':products_list} # stores products in proper dict format for easy json file conversion
        
        if exists(file_path):
            update_json_file(data, file_path)
        else:
            write_data_to_json(data, file_path)
    elif file_type == '.csv':
        data = products_list # keeps products as a list to iterate for easier csv file conversion

        if exists(file_path):
            update_csv_file(data, file_path)
        else:
            write_data_to_csv(data, file_path)