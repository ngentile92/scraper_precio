##### HAY QUE EJECUTAR ESTE CODIGO ANTES PARA QUE ANDE TODO playwright install

import asyncio
from playwright.async_api import async_playwright
import re

class StorePage:
    def __init__(self, page, max_pages=None):
        self.page = page
        self.max_pages = max_pages

    async def get_type_store(self, url):
        if any(word in url.lower() for word in ['order', 'sort', 'depar']):
            return 'all'
        else:
            return 'single'

    async def get_store_name_from_url(self, url):
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

    async def extract_price(self, url):
        store_name = await self.get_store_name_from_url(url)
        store_selectors = {
            'disco': 'discoargentina-store-theme-1dCOMij_MzTzZOCohX1K7w',
            'carrefour': 'valtech-carrefourar-product-price-0-x-sellingPriceValue',
            'chango_mas': 'valtech-gdn-dynamic-product-0-x-dynamicProductPrice',
            'MELI': 'andes-money-amount__fraction',
            'dexter': 'value'
        }

        max_retries = 5
        retry_wait = 3

        for attempt in range(max_retries):
            try:
                await self.page.goto(url)
                if store_name in store_selectors:
                    price_div = await self.page.wait_for_selector(f'.{store_selectors[store_name]}', timeout=retry_wait*1000)
                else:
                    return None

                if price_div:
                    return await price_div.text_content()
            except Exception as e:
                print(f"Error on attempt {attempt+1}: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_wait)
                    retry_wait *= 2
        return None
    
    async def navigate_and_extract(self, url):
        await self.page.goto(url, wait_until="networkidle")
        data = []
        pages_visited = 0

        while True:
            # Extraer datos de la página actual
            current_data = await self.extract_multiple_prices_and_names(url)
            data.extend(current_data)
            pages_visited += 1

            # Comprobación del número máximo de páginas
            if self.max_pages is not None and pages_visited >= self.max_pages:
                break

            # Buscar el botón "Siguiente"
            next_button = await self.page.query_selector('.vtex-button__label')
            if next_button and await next_button.is_enabled() and await next_button.is_visible():
                # Asegúrate de que el botón realmente navegue a una nueva página
                previous_url = self.page.url
                await next_button.click()
                await self.page.wait_for_load_state('networkidle')
                # Verifica si la URL ha cambiado
                if self.page.url == previous_url:
                    break
            else:
                break  # No más páginas o botón "Siguiente" no disponible

        return data
    
    async def extract_multiple_prices_and_names(self, url):
        store_name = await self.get_store_name_from_url(url)
        # Define selectors for multiple product scraping based on the store
        selectors = {
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
        
        if store_name not in selectors:
            print(f"Store '{store_name}' not supported.")
            return []
        # Método de scrolling para asegurar la carga de todos los productos
        last_height = await self.page.evaluate("document.body.scrollHeight")
        while True:
            await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(2)  # Tiempo para que la página cargue más productos
            new_height = await self.page.evaluate("document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        await self.page.goto(url, wait_until="networkidle")
        # Incrementar los intentos de scrolling
        for _ in range(10):  # Aumentar si es necesario
            await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(1)  # Tiempo para que la página cargue más productos

        # Esperar a que los selectores de precio y nombre estén visibles
        await self.page.wait_for_selector(selectors[store_name]['price'], state="visible", timeout=5000)
        await self.page.wait_for_selector(selectors[store_name]['name'], state="visible", timeout=5000)

        price_elements = await self.page.query_selector_all(selectors[store_name]['price'])
        name_elements = await self.page.query_selector_all(selectors[store_name]['name'])

        products = []
        for price_el, name_el in zip(price_elements, name_elements):
            raw_price = await price_el.text_content()
            name = await name_el.text_content()

            # Limpiar el precio usando una expresión regular para eliminar caracteres no deseados
            cleaned_price = re.sub(r'[^\d,]', '', raw_price)  # Elimina todo excepto dígitos y comas

            products.append({'name': name.strip(), 'price': cleaned_price})
        
        return products


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, args=['--no-sandbox', '--disable-setuid-sandbox'])
        page = await browser.new_page()
        store_page = StorePage(page, max_pages=2)
        # Example usage
        type_of_store = await store_page.get_type_store('https://www.carrefour.com.ar/Almacen/Pastas-secas?order=')
        if type_of_store == 'all':
            products = await store_page.navigate_and_extract('https://www.carrefour.com.ar/Almacen/Pastas-secas?order=')
            print(products)
        else:
            price = await store_page.extract_price('https://www.carrefour.com.ar/fideos-monos-matarazzo-500-g/p')
            print(price)
        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
