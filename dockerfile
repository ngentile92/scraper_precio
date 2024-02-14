FROM python:3.10

WORKDIR /app

COPY . /app

RUN pip install -r requirements.txt --trusted-host pypi.python.org

# Update and upgrade packages, then attempt to fix broken installs
RUN apt-get update && apt-get upgrade -y && apt-get -f install

# Install wget, unzip, and gdebi to ensure they are installed without error
RUN apt-get install -y wget unzip gdebi-core

# Now try installing Google Chrome using gdebi for automatic dependency resolution
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    gdebi -n google-chrome-stable_current_amd64.deb && \
    rm google-chrome-stable_current_amd64.deb

RUN apt-get clean

CMD ["python", "main.py"]




