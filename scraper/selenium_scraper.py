import re
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

# Constants and dictionaries
PAGE_URL_SUFFIX = '-pagina-'
HTML_EXTENSION = '.html'
FEATURE_UNIT_DICT = {
    'm²': 'square_meters_area',
    'amb': 'rooms',
    'dorm': 'bedrooms',
    'baño': 'bathrooms',
    'baños': 'bathrooms',
    'coch': 'parking',
}
LABEL_DICT = {
    'POSTING_CARD_PRICE': 'price',
    'expensas': 'expenses',
    'POSTING_CARD_LOCATION': 'location',
    'POSTING_CARD_DESCRIPTION': 'description',
}

class Scraper:
    def __init__(self, base_url):
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--no-sandbox')
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        self.base_url = base_url

    def scrap_page(self, page_number):
        if page_number == 1:
            page_url = f'{self.base_url}{HTML_EXTENSION}'
        else:
            page_url = f'{self.base_url}{PAGE_URL_SUFFIX}{page_number}{HTML_EXTENSION}'

        print(f'URL: {page_url}')
        self.driver.get(page_url)
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@data-posting-type]"))
        )
        page = self.driver.page_source
        soup = BeautifulSoup(page, 'lxml')
        estate_posts = soup.find_all('div', attrs={'data-posting-type': True})
        estates = [self.parse_estate(post) for post in estate_posts]
        return estates

    def scrap_website(self):
        page_number = 1
        estates = []
        while True:
            print(f'Scraping page: {page_number}')
            new_estates = self.scrap_page(page_number)
            if not new_estates:
                break  # Stop if no more estates are found
            estates += new_estates
            page_number += 1
            time.sleep(2)  # Be polite and don't hammer the server
        return estates

    def get_estates_quantity(self):
        self.driver.get(f'{self.base_url}{HTML_EXTENSION}')
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "h1"))
        )
        page = self.driver.page_source
        soup = BeautifulSoup(page, 'lxml')
        h1_tag = soup.find('h1')
        if h1_tag:
            estates_quantity_text = h1_tag.text
            estates_quantity = re.findall(r'\d+\.?\d*', estates_quantity_text.replace('.', ''))[0]
            estates_quantity = int(estates_quantity)
            return estates_quantity
        else:
            print('No h1 tags found')
            return 0
    
    def parse_estate(self, estate_post):
        # find div with anything data-qa atributte
        data_qa = estate_post.find_all('div', attrs={'data-qa': True})
        # find h2 with anything data-qa atribnutte
        data_qa.append(estate_post.find('h2', attrs={'data-qa': True}))
        # find h2 with anything data-qa atributte
        data_qa.append(estate_post.find('h3', attrs={'data-qa': True}))

        url = estate_post.get_attribute_list('data-to-posting')[0]
        estate = {}
        estate['url'] = url
        print(url)
        for data in data_qa:
            label = data['data-qa']
            text = None
            if label in ['POSTING_CARD_PRICE', 'expensas']:
                currency_value, currency_type = self.parse_currency_value(data.get_text())
                estate[LABEL_DICT[label] + '_' + 'value'] = currency_value
                estate[LABEL_DICT[label] + '_' + 'type'] = currency_type
            elif label in ['POSTING_CARD_LOCATION']:
                text = self.parse_text(data.get_text())
                #Divide on the "," and get two columns category and subcategory
                estate['category'], estate['subcategory'] = text.split(',')
            elif label in ['POSTING_CARD_FEATURES']:
                features = self.parse_features(data.get_text())
                estate.update(features)
            else:
                text = data.get_text()
                estate[label] = text
        return estate

    def parse_currency_value(self, text):
        try:
            currency_value = re.findall(r'\d+\.?\d+', text)[0]
            currency_value = currency_value.replace('.', '')
            currency_value = int(currency_value)
            currency_type = re.findall(r'(USD)|(ARS)|(\$)', text)[0]
            currency_type = [x for x in currency_type if x != ''][0]
            return currency_value, currency_type
        except:
            return text, None

    def parse_text(self, text):
        text = text.replace('\n', '')
        text = text.replace('\t', '')
        text = text.strip()
        return text

    def parse_features(self, text):

        features_matches = re.compile(r'(\d+\.?\d*)\s(\w+)').findall(text)

        features = {}

        for feature in features_matches:
            feature_value = feature[0]
            feature_unit = feature[1]
            feature_unit = FEATURE_UNIT_DICT[feature_unit]
            features[feature_unit] = feature_value

        return features
    