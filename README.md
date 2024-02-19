# scraper de precios
## Installation

- On Mac:

```bash
virtualenv venv
source venv/bin/activate
pip3 install -r requirements.txt
```

- On Windows:
```bash
python -m venv venv
source venv/Scripts/activate
```
```bash install requirements
pip install -r requirements.txt
```
``` bash install scraper precio
or 
pip install -e .
```

Set up your environment variables.

```bash
cp .env.EXAMPLE .env
```

Edit the variables within `.env`.

Export the environmental variables:

```bash
export $(cat .env | xargs)
```


## Docker

Download and install Docker from [Docker's website](https://www.docker.com/products/docker-desktop).

Build docket image

```bash
docker build --platform linux/amd64 -t scraper_precios .
```

Run docker image

```bash
docker run scraper_precios
```


# zona-prop-scraping

Scraper de Zonaprop.

## Modo de uso:

1- Instalar las dependencias declaradas en el archivo `requirements.txt`:

Con pip:

```bash
pip install -r requirements.txt
```

Con conda:

```bash
conda install --file requirements.txt
```

2- Ejecutar el script `zonaprop-scraping.py` pasando como argumento la url de la página de Zonaprop que se desea scrapear (por default se utilizará la url: https://www.zonaprop.com.ar/departamentos-alquiler.html):

```bash
python zonaprop-scraping.py <url>
```

Por ejemplo:

```bash
python zonaprop-scraping.py https://www.zonaprop.com.ar/departamentos-alquiler.html
```

3- El script generará un archivo `.csv` en el directorio `data` con los datos de los inmuebles obtenidos.

## Análisis de los datos:

Se puede ver un análisis de los datos obtenidos por el scraper en el archivo `/analysis/exploratory-analysis.ipynb`.

Tomar este análisis como un ejemplo de cómo se puede utilizar el scraper para obtener datos y analizarlos.
