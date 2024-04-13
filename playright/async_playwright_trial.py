##### HAY QUE EJECUTAR ESTE CODIGO ANTES PARA QUE ANDE TODO playwright install

import asyncio
from playwright.async_api import async_playwright
import re

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
        await self.page.goto(url, wait_until="networkidle")
        data = []
        pages_visited = 0

        while True:
            await self.close_popups()  # Cierra pop-ups antes de intentar extraer datos o navegar

            current_data = await self.extract_multiple_prices_and_names(url)
            if current_data:
                # Evitar duplicados añadiendo solo nuevos productos
                for product in current_data:
                    if product not in data:
                        data.append(product)

            pages_visited += 1
            if self.max_pages is not None and pages_visited >= self.max_pages:
                break

            # Selector mejorado para el botón "Siguiente"
            next_button = await self.page.query_selector(next_button_selector)
            if next_button and await next_button.is_visible() and await next_button.is_enabled():
                await next_button.click()
                # Espera a que la página siguiente cargue completamente
                await self.page.wait_for_load_state('networkidle')
                await asyncio.sleep(3)  # Dar tiempo adicional para asegurar la carga
            else:
                print("No se encontró el botón 'Siguiente' o no está disponible.")
                break

        return data            
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



async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, args=['--no-sandbox', '--disable-setuid-sandbox'])
        page = await browser.new_page()
        store_page = StorePage(page, max_pages=2)
        # Example usage
        type_of_store = get_type_store('https://www.carrefour.com.ar/Almacen/Pastas-secas?order=')
        if type_of_store == 'all':
            products = await store_page.navigate_and_extract('https://www.carrefour.com.ar/Almacen/Pastas-secas?order=')
            print(products)
        else:
            price = await store_page.extract_price('https://www.carrefour.com.ar/fideos-monos-matarazzo-500-g/p')
            print(price)
        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
