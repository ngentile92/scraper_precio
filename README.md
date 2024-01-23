# scraper de precios
## Installation

- On Mac:

```bash
virtualenv venv
source venv/bin/activate
pip3 install -r requirements.txt
pip3 install -r dev-requirements.txt
```

- On Windows:
```bash
python -m venv venv
source venv/Scripts/activate
```
```bash install requirements
pip install -r requirements.txt
pip install -r dev-requirements.txt
```
``` bash install temis
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
