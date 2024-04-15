##### HAY QUE EJECUTAR ESTE CODIGO ANTES PARA QUE ANDE TODO playwright install

import asyncio
import datetime
import json
import re
import unicodedata

import pandas as pd

from load.gcs_load import load_data_to_db
from playwright.async_api import async_playwright
from playwright_scripts.selectors_supermarket import (POPUP_SELECTORS, STORE_MULT_SELECTORS,
                                  STORE_SINGLE_SELECTORS)


def normalize_text(text):
    # Normalizar el texto para reemplazar caracteres con tilde y ñ
    text = unicodedata.normalize('NFD', text)  # Descomponer en caracteres y diacríticos
    text = text.encode('ascii', 'ignore')  # Convertir a ASCII y omitir errores
    text = text.decode('utf-8')  # Decodificar de vuelta a UTF-8
    return text

def transform_data(data, url):
    all_data = {}
    today = datetime.datetime.now().strftime("%d/%m/%Y")
    store_name = get_store_name_from_url(url)

    # Asegúrate de que existen las claves necesarias en el diccionario all_data
    if today not in all_data:
        all_data[today] = {}
    if store_name not in all_data[today]:
        all_data[today][store_name] = {}

    for product in data:
        product_name = normalize_text(product['name'])
        cleaned_price = re.sub(r'[^\d.,]', '', product['price']).replace('.', '').replace(',', '.')
        price_number = float(re.search(r'\d+(\.\d+)?', cleaned_price).group(0)) if re.search(r'\d+(\.\d+)?', cleaned_price) else None
        all_data[today][store_name][product_name] = price_number

    return all_data

def get_store_name_from_url(url):
    store_domains = {
        'disco.com.ar': 'disco',
        'mercadolibre.com.ar': 'MELI',
        'carrefour.com.ar': 'carrefour',
        'masonline.com.ar': 'chango_mas',
        'dexter.com.ar': 'dexter',
        'levi.com.ar': 'levis',
        'zonaprop.com.ar': 'zonaprop',
        'fravega.com': 'fravega',
        'musimundo.com': 'musimundo'
    }
    domain = url.split('/')[2].replace('www.', '')  # Strip 'www.' if present
    return store_domains.get(domain, 'unknown')

def get_type_store(url):
    if any(word in url.lower() for word in ['order', 'sort', 'depar']):
        return 'all'
    else:
        return 'single'
class StorePage:
    def __init__(self, page, max_pages=None):
        self.page = page
        self.max_pages = max_pages

    async def extract_price(self, url):
        store_name = get_store_name_from_url(url)
        max_retries = 2
        retry_wait = 1
        for attempt in range(max_retries):
            try:
                await self.page.goto(url, wait_until="domcontentloaded")
                await self.close_popups()  # Intenta cerrar pop-ups después de cargar la página
                if store_name in STORE_SINGLE_SELECTORS:
                    price_div = await self.page.wait_for_selector(f'.{STORE_SINGLE_SELECTORS[store_name]}', timeout=retry_wait*1000)
                    if price_div:
                        return await price_div.text_content()
            except Exception as e:
                print(f"Error on attempt {attempt+1}: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_wait)
                    retry_wait *= 2
        return None

    async def close_popups(self):
        for selector in POPUP_SELECTORS:
            try:
                # Cierra todos los pop-ups detectados
                popups = await self.page.query_selector_all(selector)
                for popup in popups:
                    if await popup.is_visible():
                        await popup.click()
                        print(f"Pop-up cerrado usando {selector}.")
            except Exception as e:
                print(f"No se pudo cerrar pop-up con {selector}: {str(e)}")

    async def navigate_and_extract(self, url):
        try:
            # Limpiar cookies y permisos antes de iniciar la navegación
            await self.page.context.clear_cookies()
            await self.page.context.clear_permissions()

            await self.page.goto(url, wait_until="networkidle", timeout=50000)
            store_name = get_store_name_from_url(url)

            data = []
            pages_visited = 0

            while True:
                await self.close_popups()

                # Extraer datos de la página actual
                current_data = await self.extract_multiple_prices_and_names(url)
                for product in current_data:
                    if product not in data:
                        data.append(product)

                pages_visited += 1
                if self.max_pages is not None and pages_visited >= self.max_pages:
                    break
                if store_name == 'disco':
                    # Lógica especial para Disco
                    next_page_buttons = await self.page.query_selector_all(STORE_MULT_SELECTORS['disco']['next_button'])
                    if pages_visited < len(next_page_buttons):
                        await next_page_buttons[pages_visited - 1].click()  # Clickea el botón de la siguiente página
                        try:
                            await self.page.wait_for_load_state('networkidle', timeout=80000)
                        except TimeoutError:
                            print("Timeout alcanzado, continuando con la siguiente página")
                            continue

                        await asyncio.sleep(3)
                    else:
                        print("No más páginas disponibles o límite alcanzado para Disco.")
                        break
                else:

                    # Intentar navegar a la siguiente página
                    next_button_selector = STORE_MULT_SELECTORS.get(store_name, {}).get('next_button', '')
                    next_button = await self.page.query_selector(next_button_selector)
                    if next_button and await next_button.is_visible() and await next_button.is_enabled():
                        # Guardar la URL actual antes de hacer clic
                        current_url = self.page.url
                        await next_button.click()
                        try:
                            await self.page.wait_for_load_state('networkidle', timeout=50000)
                        except TimeoutError:
                            print("Timeout alcanzado, continuando con la siguiente página")
                            return data

                        # Comprobar si la URL ha cambiado después de navegar
                        new_url = self.page.url
                        if new_url == current_url:
                            print("La página no ha cambiado después de hacer clic en 'Siguiente'.")
                        else:
                            await asyncio.sleep(3)  # Esperar para asegurar que la nueva página se ha cargado completamente
                    else:
                        print(f"No se encontró el botón 'Siguiente' o no está disponible de la store {store_name}. usando el selector {next_button_selector} en la url {url}")
                        break
            print(f"Total de productos únicos extraídos: {len(data)}")
            transformed_data = transform_data(data, url)
            return transformed_data
        except Exception as e:
            print(f"Error en la navegación y extracción: {e}")
            return {}

    async def extract_multiple_prices_and_names(self, url):
        store_name = get_store_name_from_url(url)
        if store_name not in STORE_MULT_SELECTORS:
            print(f"Store '{store_name}' not supported.")
            return []

        # Asegúrate de que la página ha cargado completamente
        try:
            await self.page.wait_for_load_state('networkidle', timeout=50000)
        except TimeoutError:
            print("Timeout alcanzado, continuando con la siguiente página")
            return []
        # Realiza scrolling para asegurar que todos los elementos se carguen
        last_height = await self.page.evaluate("document.body.scrollHeight")
        while True:
            await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(3)  # Aumenta este tiempo si es necesario
            new_height = await self.page.evaluate("document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        # Espera explícita por los selectores de precios y nombres
        try:
            await self.page.wait_for_load_state('networkidle')
            await self.page.wait_for_selector(STORE_MULT_SELECTORS[store_name]['price'], state="visible", timeout=5000)
            await self.page.wait_for_selector(STORE_MULT_SELECTORS[store_name]['name'], state="visible", timeout=5000)
        except Exception as e:
            print(f"Error esperando los selectores: {e} de la pagina {url}")
            return []

        price_elements = await self.page.query_selector_all(STORE_MULT_SELECTORS[store_name]['price'])
        name_elements = await self.page.query_selector_all(STORE_MULT_SELECTORS[store_name]['name'])

        products = []
        for price_el, name_el in zip(price_elements, name_elements):
            raw_price = await price_el.text_content()
            name = await name_el.text_content()

            cleaned_price = re.sub(r'[^\d,]', '', raw_price)
            price = None if cleaned_price == '' else cleaned_price

            if price is not None:  # Only add products with a valid price
                products.append({'name': name.strip(), 'price': price})
            else:
                print(f"Invalid or missing price for product: {name.strip()}")
        
        return products

def merge_data(all_data, new_data):
    for date, stores in new_data.items():
        if date not in all_data:
            all_data[date] = stores
        else:
            for store, products in stores.items():
                if store not in all_data[date]:
                    all_data[date][store] = products
                else:
                    all_data[date][store].update(products)

async def main():
    datos = pd.read_csv('url_productos_pruebas.csv', encoding='ISO-8859-1')

    all_data = {}
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox','--user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"'])
        for index,row in datos.iterrows():
            page = await browser.new_page()
            max_pages = row['cantidad_paginas']
            store_page = StorePage(page, max_pages=max_pages)
            formatted_data = await store_page.navigate_and_extract(row['URL'])
            merge_data(all_data, formatted_data)
            await page.close()
        await browser.close()

    # FORMAT JSON TO PRINT IT
    load_data_to_db(all_data)

if __name__ == '__main__':
    asyncio.run(main())
