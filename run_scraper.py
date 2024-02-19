import sys

import pandas as pd

from scraper import utils
from scraper.browser import Browser
from scraper.scraper import Scraper


def main(url):
    base_url = utils.parse_zonaprop_url(url)
    print(f'Running scraper for {base_url}')
    print(f'This may take a while...')
    browser = Browser()
    scraper = Scraper(browser, base_url)
    estates = scraper.scrap_website()
    df = pd.DataFrame(estates)
    print('Scraping finished !!!')
    print('Saving data to csv file')
    filename = utils.get_filename_from_datetime(base_url, 'csv')
    utils.save_df_to_csv(df, filename)
    print(f'Data saved to {filename}')
    print('Scrap finished !!!')

if __name__ == '__main__':
    # Check if at least one command-line argument is provided
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        # Default URL to use if no argument is provided
        url = 'https://www.zonaprop.com.ar/departamentos-alquiler-capital-federal-mas-de-1-bano-1-habitacion-2-ambientes-sin-garages-40-50-m2-cubiertos.html'
    
    main(url)