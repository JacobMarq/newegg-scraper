# Web Scraper For Newegg.com
----------------------------

The goal of this application is to parse and collect 
pricing, main image, urls, and various specifications 
regarding computer hardware on newegg.

Data is collected by category en masse. This application
is not intended for single item lookup but could be
altered to do so.

## DOCS
----------------------------
### TO INSTALL

### DEPENDENCIES
    
>    main/requirements.txt
>    
>    beautifulsoup4==4.11.1
>    pandas==1.4.3
>    selenium==4.3.0
>    webdriver_manager==3.7.1

### UNIT TESTS

Run all unit tests:
```
python3 -m unittest -v
```
Run unit test for specific module:
```
python3 -m unittest -v test.file_name
```
<sub>-v: verbose output</sub>

### MODULES

### HOW TOs