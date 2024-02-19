import sys

import pandas as pd

from scraper import utils
from scraper.selenium_scraper import Scraper


def main(url):
    base_url = utils.parse_zonaprop_url(url)
    print(f'Running scraper for {base_url}')
    print(f'This may take a while...')
    scraper = Scraper(base_url)
    estates = scraper.scrap_website()
    print(f'Found {len(estates)} estates')
    df = pd.DataFrame(estates)
    df.to_csv('estates.csv', index=False)
    print('Data saved to estates.csv')
    
    
if __name__ == '__main__':
    # Check if at least one command-line argument is provided
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        # Default URL to use if no argument is provided
        url = 'https://www.zonaprop.com.ar/departamentos-alquiler-capital-federal-mas-de-1-bano-1-habitacion-2-ambientes-sin-garages-40-50-m2-cubiertos.html'
    
    main(url)