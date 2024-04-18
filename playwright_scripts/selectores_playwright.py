
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
        'price': 'span.vtex-product-price-1-x-sellingPriceValue--best-price',
        'name': '.vtex-product-summary-2-x-productBrand.vtex-product-summary-2-x-brandName.t-body',
        'next_button': 'div.vtex-search-result-3-x-gallery.vtex-search-result-3-x-gallery--normal .vtex-button__label'
    },
    'carrefour': {
        'price': '.valtech-carrefourar-search-result-0-x-gallery .valtech-carrefourar-product-price-0-x-sellingPriceValue',
        'name': '.valtech-carrefourar-search-result-0-x-gallery .vtex-product-summary-2-x-productBrand.vtex-product-summary-2-x-brandName.t-body',
        'next_button' : 'div.valtech-carrefourar-search-result-0-x-paginationButtonChangePage:last-child button'
    },
    'disco': {
        'price': 'div.vtex-flex-layout-0-x-flexColChild--contentCol #priceContainer',
        'name': 'div.vtex-flex-layout-0-x-flexColChild--contentCol .vtex-product-summary-2-x-productBrand',
        'next_button': 'div.discoargentina-search-result-custom-1-x-new-btn button:not([class*="clicked"])'
    },
    'fravega': {
        'price': 'div[data-test-id="product-price"] .sc-66d25270-0.eiLwiO',  
        'name': '.sc-ca346929-0',
        'next_button': 'a[data-test-id="pagination-next-button"]'
    },
    'musimundo': {
        'price': '.mus-pro-price-number > span',
        'name': 'div.mus-pro-desc h3.mus-pro-name a[data-test-plp="item_name"]',
        'next_button': 'a[data-test-next-page-btn="next_page_btn"]'
    },
    'zonaprop': {
        'price': '[data-qa="POSTING_CARD_PRICE"]',
        'name': '[data-qa="POSTING_CARD_LOCATION"]',
        'next_button': 'div.vtex-search-result-3-x-gallery.vtex-search-result-3-x-gallery--normal .vtex-button__label'
    },
    'dexter': {
        'price': '.sales .value',
        'name': 'a.link',
        'next_button': 'div.show-more button.more'
    },
}

# Configuraciones de pop-ups
POPUP_SELECTORS = [
    '.valtech-carrefourar-minicart-repeat-order-0-x-closeDrawer', 
    '.close-popup',
    '.modal-close',
    '[data-action="close-popup"]',
    '.onetrust-close-btn-handler',
    '.dy-lb-close',
    '#btnNoIdWpnPush',
    'button[data-test-id="close-modal-button"]',
    '.vtex-modal-layout-0-x-closeButtonLabel--modal-newsletter'
]