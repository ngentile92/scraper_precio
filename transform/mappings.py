INDICE_MAPPING = {
    'electrodomesticos y tecnologia': {
        'celulares': 'celulares y pequenos electrodomesticos',
        'pequenos electrodomesticos': 'celulares y pequenos electrodomesticos',
        'informatica': 'informatica'
    },
    'fiambres y quesos': {
        'quesos': 'Leche/ productos lacteos/ huevos y alimentos vegetales'
    },
    'perfumeria': {
        'farmacia': 'farmacia',
        'cuidado oral': 'cuidado oral'
    },
    'lacteos': {
        'yogures': 'Leche/ productos lacteos/ huevos y alimentos vegetales',
        'leches': 'Leche/ productos lacteos/ huevos y alimentos vegetales'
    },
    'desayuno': {
        'infusiones': 'Bebidas no alcoholicas'
    },
    'prendas y calzado': {
        'camisas': 'Prendas de vestir',
        'jeans': 'Prendas de vestir',
        'sweaters y buzos': 'Prendas de vestir',
        'remeras': 'Prendas de vestir',
        'calzado': 'Calzado',
        'pantalon': 'Prendas de vestir',
        'medias': 'Calzado'
    },
    'sin TACC': {
        'sin TACC': 'sin TACC'
    },
    'carnes': {
        'cerdo': 'Carnes y derivados',
        'vaca': 'Carnes y derivados'
    },
    'almacen': {
        'pastas': 'Pan / pastas y cereales',
        'aceites': 'Aceites/ aderezos/ grasas y manteca',
        'conservas': 'Otros alimentos'
    },
    'frutas y verduras': {
        'frutas': 'Frutas',
        'verduras': 'Verduras/ tuberculos y legumbres'
    },
    'libreria': {
        'cuadernos': 'libreria',
        'lapiceras': 'libreria',
        'lapices': 'libreria',
        'marcadores': 'libreria',
        'gomas': 'libreria',
        'mochilas': 'libreria',
        'otro': 'libreria'
    },
    'bazar y textil': {
        'indumentaria': 'Prendas de vestir',
        'libreria': 'libreria'
    },
    'congelados': {
        'congelados': 'Otros alimentos'
    },
    'bebidas': {
        'alcoholica': 'Bebidas alcoholicas y tabaco',
        'no alcoholica': 'Bebidas no alcoholicas'
    },
    'alimentos': {
        'pan y lacteos': 'Pan / pastas y cereales',
        'aderezos': 'Aceites/ aderezos/ grasas y manteca',
        'carnes y huevo': 'Carnes y derivados',
        'otros': 'Otros alimentos'
    },
    'limpieza': {
        'casa': 'limpieza',
        'personal': 'limpieza'
    }
}

# pequenos electrodomesticos deberia ser celulares y pequenos electrodomesticos junto a celulares
PRODUCTO_A_CATEGORIA = {
    'tomate': 'Verduras/ tuberculos y legumbres',
    'papas': 'Verduras/ tuberculos y legumbres',
    'arvejas': 'Verduras/ tuberculos y legumbres',
    'lentejas': 'Verduras/ tuberculos y legumbres',
    'jardinera': 'Verduras/ tuberculos y legumbres',
    'garbanzos': 'Verduras/ tuberculos y legumbres',
    'atun': 'Pescados y mariscos',
    'arroz': 'Pan / pastas y cereales',
    'zucaritas': 'Pan / pastas y cereales',
    'maiz': 'Pan / pastas y cereales',
    'soja': 'Leche/ productos lacteos/ huevos y alimentos vegetales',
    'duraznos': 'Frutas',
    'hamburguesa': 'Carnes y derivados',
    'carne': 'Carnes y derivados',
    'pollo': 'Carnes y derivados',
    'salmon': 'Pescados y mariscos',
    'dolca': 'Bebidas no alcoholicas',
    'sonrisas': 'Azucar/ dulces/ chocolate/golosinas/ etc.',
    'bombon': 'Azucar/ dulces/ chocolate/golosinas/ etc.',
    'alfajor': 'Azucar/ dulces/ chocolate/golosinas/ etc.',
    'chocolate': 'Azucar/ dulces/ chocolate/golosinas/ etc.',
}
CATEGORIA_MAPPING = {
    'electro': 'electrodomesticos y tecnologia',
    'perfumeria': 'perfumeria',
    'sweaters|jeans|camisas': 'prendas y calzado',
    '/Bazar-y-textil/Libreria': 'libreria',
    'lacteos': 'lacteos',
    'desayuno': 'desayuno',
    'map=productclusterids.*163': 'sin TACC',
    'quesos|fiambres': 'fiambres y quesos',
    'carnes': 'carnes',
    'depart': 'departamentos',
    'frutas|verduras': 'frutas y verduras',
    'almacen': 'almacen',
    'congelados': 'congelados',
    'bazar|textil': 'bazar y textil'
}

SUBCATEGORIA_MAPPING = {
    'electros': 'pequenos electrodomesticos',
    '/frutas-y-verduras/frutas': 'frutas',
    '/frutas-y-verduras/verduras': 'verduras',
    '/indumentaria': 'indumentaria',
    '/aceites': 'aceites',
    '/congelados': 'congelados',
    '/quesos': 'quesos',
    '/fiambres': 'fiambres',
    'cerdo': 'cerdo',
    'vacuna': 'vaca',
    'cuidado-oral': 'cuidado oral',
    'farmacia': 'farmacia',
    'sweaters|buzos': 'sweaters y buzos',
    'jeans': 'jeans',
    'camisas': 'camisas',
    'libreria': 'libreria',
    'celulares': 'celulares',
    'informatica': 'informatica',
    'yogures': 'yogures',
    'leches': 'leches',
    'infusiones': 'infusiones',
    'galletitas': 'galletitas',
    'map=productclusterids.*163': 'sin TACC',
    'federal': 'capital federal',
    '/conservas': 'conservas',
    'pastas': 'pastas'
}
