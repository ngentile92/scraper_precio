##### HAY QUE EJECUTAR ESTE CODIGO ANTES PARA QUE ANDE TODO playwright install

import asyncio
from playwright.async_api import async_playwright
import re
import datetime
import json
import pandas as pd

STORE_SINGLE_SELECTORS = {
    'disco': 'discoargentina-store-theme-1dCOMij_MzTzZOCohX1K7w',
    'carrefour': 'valtech-carrefourar-product-price-0-x-sellingPriceValue',
    'chango_mas': 'valtech-gdn-dynamic-product-0-x-dynamicProductPrice',
    'MELI': 'andes-money-amount__fraction',
    'dexter': 'value'
}
STORE_MULT_SELECTORS = {
    # Actualiza los selectores según sea necesario
    'levis': {
        'price': 'vtex-product-price-1-x-sellingPriceValue',
        'name': '.vtex-product-summary-2-x-productBrand.vtex-product-summary-2-x-brandName.t-body'
    },
    'carrefour': {
        'price': '.valtech-carrefourar-search-result-0-x-gallery .valtech-carrefourar-product-price-0-x-sellingPriceValue',
        'name': '.valtech-carrefourar-search-result-0-x-gallery .vtex-product-summary-2-x-productBrand.vtex-product-summary-2-x-brandName.t-body'
    },
    'disco': {
        'price': 'discoargentina-store-theme-1dCOMij_MzTzZOCohX1K7w',
        'name': '.vtex-product-summary-2-x-productBrand.vtex-product-summary-2-x-brandName.t-body'
    },
    'fravega': {
        'price': '[data-test-id="product-price"] .sc-66d25270-0.eiLwiO',
        'name': '.sc-ca346929-0',
    },
    'musimundo': {
        'price': 'span.mus-pro-price-number span',
        'name': 'h3.mus-pro-name a[data-test-plp="item_name"]',
    },
    'zonaprop': {
        'price': '[data-qa="POSTING_CARD_PRICE"]',  # Actualizado para uso de atributos
        'name': '[data-qa="POSTING_CARD_LOCATION"]',  # Actualizado para uso de atributos
    }
}

# Configuraciones de pop-ups
POPUP_SELECTORS = [
    '.valtech-carrefourar-minicart-repeat-order-0-x-closeDrawer',  # Ejemplo Carrefour
    '.close-popup',  # Ejemplo genérico para otro tipo de pop-up
    '.modal-close',  # Otro posible botón de cierre
    '[data-action="close-popup"]',  # Atributo específico para cierre
    '.onetrust-close-btn-handler',  # Ejemplo de cierre de pop-up de cookies
    '.dy-lb-close',
    # Añade más selectores según los necesites
]
next_button_selector = 'div.valtech-carrefourar-search-result-0-x-paginationButtonChangePage:last-child button'


def transform_data(data, url):
    today = datetime.datetime.now().strftime("%d/%m/%Y")
    store_name = get_store_name_from_url(url)
    formatted_data = {today: {store_name: {}}}

    for product in data:
        product_name = product['name']
        cleaned_price = re.sub(r'[^\d.,]', '', product['price']).replace('.', '').replace(',', '.')
        price_number = float(re.search(r'\d+(\.\d+)?', cleaned_price).group(0)) if re.search(r'\d+(\.\d+)?', cleaned_price) else None
        formatted_data[today][store_name][product_name] = price_number

    return formatted_data
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
        max_retries = 5
        retry_wait = 3
        for attempt in range(max_retries):
            try:
                await self.page.goto(url)
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
        # Limpiar cookies y permisos antes de iniciar la navegación
        await self.page.context.clear_cookies()
        await self.page.context.clear_permissions()

        await self.page.goto(url, wait_until="networkidle")
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

            # Intentar navegar a la siguiente página
            next_button = await self.page.query_selector(next_button_selector)
            if next_button and await next_button.is_visible() and await next_button.is_enabled():
                # Guardar la URL actual antes de hacer clic
                current_url = self.page.url
                await next_button.click()
                await self.page.wait_for_load_state('networkidle')

                # Comprobar si la URL ha cambiado después de navegar
                new_url = self.page.url
                if new_url == current_url:
                    print("La página no ha cambiado después de hacer clic en 'Siguiente'.")
                else:
                    await asyncio.sleep(3)  # Esperar para asegurar que la nueva página se ha cargado completamente
            else:
                print("No se encontró el botón 'Siguiente' o no está disponible.")
                break

        print(f"Total de productos únicos extraídos: {len(data)}")
        transformed_data = transform_data(data, url)
        return transformed_data

    async def extract_multiple_prices_and_names(self, url):
        store_name = get_store_name_from_url(url)
        if store_name not in STORE_MULT_SELECTORS:
            print(f"Store '{store_name}' not supported.")
            return []

        # Asegúrate de que la página ha cargado completamente
        await self.page.wait_for_load_state('networkidle')

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
            await self.page.wait_for_selector(STORE_MULT_SELECTORS[store_name]['price'], state="visible", timeout=10000)
            await self.page.wait_for_selector(STORE_MULT_SELECTORS[store_name]['name'], state="visible", timeout=10000)
        except Exception as e:
            print(f"Error esperando los selectores: {e}")
            return []

        price_elements = await self.page.query_selector_all(STORE_MULT_SELECTORS[store_name]['price'])
        name_elements = await self.page.query_selector_all(STORE_MULT_SELECTORS[store_name]['name'])

        products = []
        for price_el, name_el in zip(price_elements, name_elements):
            raw_price = await price_el.text_content()
            name = await name_el.text_content()

            cleaned_price = re.sub(r'[^\d,]', '', raw_price)
            products.append({'name': name.strip(), 'price': cleaned_price})
        
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
    with open('url_productos_pruebas.csv', 'r') as f:
        datos = pd.read_csv(f, encoding='ISO-8859-1')
        url_list = datos['URL'].tolist()

    all_data = {}
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
        for url in url_list:
            page = await browser.new_page()
            store_page = StorePage(page, max_pages=4)
            formatted_data = await store_page.navigate_and_extract(url)
            merge_data(all_data, formatted_data)
            await page.close()
        await browser.close()

    print(json.dumps(all_data, indent=4))

if __name__ == '__main__':
    asyncio.run(main())
