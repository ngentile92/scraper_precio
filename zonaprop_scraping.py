import pandas as pd

from zonaprop_src import utils
from zonaprop_src.browser import Browser
from zonaprop_src.scraper import Scraper

import re
import pandas as pd

def procesar_zonaprop(url):
    base_url = utils.parse_zonaprop_url(url)
    print(f'Running scraper for {base_url}')
    print(f'This may take a while...')
    browser = Browser()
    scraper = Scraper(browser, base_url)
    estates = scraper.scrap_website()
    df = pd.DataFrame(estates)
    # La línea para guardar en CSV se elimina
    # print('Saving data to csv file')
    # filename = utils.get_filename_from_datetime(base_url, 'csv')
    # utils.save_df_to_csv(df, filename)
    # print(f'Data saved to {filename}')
    # Extraer la localidad de la URL
    localidad_match = re.search(r'https://www.zonaprop.com.ar/(?:inmuebles|departamentos)-alquiler-([^/]+?)-', url)
    if localidad_match:
        localidad = localidad_match.group(1)
    else:
        localidad = "Desconocida"  # En caso de que no se encuentre el patrón

    if localidad == 'ciudad':
        localidad = 'mendoza'
    elif localidad == 'rosario':
        localidad = 'rosario'
    elif localidad == 'capital':
        localidad = 'CABA'
    elif localidad == 'cordoba':
        localidad = 'cordoba'
    else:
        localidad = 'desconocida'
    
    # Agregar la columna "localidad" al DataFrame
    df['localidad'] = localidad
    
    print('Scraping finished !!!')
    print('Scrap finished !!!')
    return df



if __name__ == '__main__':
    urls = ['https://www.zonaprop.com.ar/departamentos-alquiler-mendoza-mas-de-1-bano-1-habitacion-2-ambientes-sin-garages-40-50-m2-cubiertos.html',
            'https://www.zonaprop.com.ar/departamentos-alquiler-rosario-mas-de-1-bano-1-habitacion-2-ambientes-sin-garages-40-50-m2-cubiertos.html',
            'https://www.zonaprop.com.ar/departamentos-alquiler-cordoba-cb-mas-de-1-bano-1-habitacion-2-ambientes-sin-garages-40-50-m2-cubiertos.html',
            'https://www.zonaprop.com.ar/departamentos-alquiler-capital-federal-mas-de-1-bano-1-habitacion-2-ambientes-sin-garages-40-50-m2-cubiertos.html']
    

    urls = ['https://www.zonaprop.com.ar/inmuebles-alquiler-ciudad-de-mendoza-mz-1-habitacion.html',
            'https://www.zonaprop.com.ar/inmuebles-alquiler-rosario-1-habitacion.html',
            'https://www.zonaprop.com.ar/inmuebles-alquiler-capital-federal-1-habitacion.html',
            'https://www.zonaprop.com.ar/inmuebles-alquiler-cordoba-1-habitacion.html'
            ]
    dfs = []
    for url in urls:
        df = procesar_zonaprop(url)
        dfs.append(df)
    
    # Concatenamos todos los DataFrames en uno solo
    final_df = pd.concat(dfs, ignore_index=True)
    print(final_df)
    #save un a csv
    final_df.to_csv('final_df.csv', index=False)


#https://www.zonaprop.com.ar/departamentos-alquiler-mendoza-mas-de-1-bano-1-habitacion-2-ambientes-sin-garages-40-50-m2-cubiertos.html
#https://www.zonaprop.com.ar/departamentos-alquiler-rosario-mas-de-1-bano-1-habitacion-2-ambientes-sin-garages-40-50-m2-cubiertos.html
#https://www.zonaprop.com.ar/departamentos-alquiler-cordoba-cb-mas-de-1-bano-1-habitacion-2-ambientes-sin-garages-40-50-m2-cubiertos.html
#https://www.zonaprop.com.ar/departamentos-alquiler-capital-federal-mas-de-1-bano-1-habitacion-2-ambientes-sin-garages-40-50-m2-cubiertos.html