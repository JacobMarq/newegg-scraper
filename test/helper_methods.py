def get_file_reader(url):
    with open(url, 'r') as file:
        reader = file.read()
    return reader