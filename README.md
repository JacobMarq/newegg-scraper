# Web Scraper For Newegg.com
### OVERVIEW
----------------------------

The goal of this application is to parse and collect 
pricing, main image, urls, and various specifications 
regarding computer hardware on newegg.

Data is collected by category en masse. This application
is not intended for single item lookup but could be
altered to do so.

### DEPENDENCIES
----------------------------
    
    main/requirements.txt
    
    beautifulsoup4==4.11.1
    pandas==1.4.3
    selenium==4.3.0
    webdriver_manager==3.7.1

### UNIT TESTS
----------------------------

Found in 'newegg-scraper/test/'

Run all unit tests:
```
python3 -m unittest -v
```
Run unit test for specific module:
```
python3 -m unittest -v test.test_module_name
```
<sub>-v: verbose output</sub>

### MODULES
----------------------------

#### products
- collects product data
- writes data to csv/json file

#### product_urls
- collects product page urls from categories on Newegg.com
- writes ordered list of urls to csv file with corresponding page number
- returns a list of queues where each queue represents one page worth of products

#### interface
- handles http requests
- captcha checking

#### dialogue
- stores dialogue for running script from command line

#### constant
- stores list of url constants for categories available on Newegg.com

### HOW TOs
----------------------------

#### Installation
TODO

#### Run from command line
1. From inside of project repo run:
```
python3 -m newegg_scraper
```
2. Follow along with instructions on command line
