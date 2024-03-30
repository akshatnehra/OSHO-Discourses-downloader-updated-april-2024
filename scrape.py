import os
import requests
from bs4 import BeautifulSoup
from pySmartDL import SmartDL
import logging
import sys
import ssl

# Disable SSL certificate verification
ssl._create_default_https_context = ssl._create_unverified_context

# Disable SSL certificate verification
requests.packages.urllib3.disable_warnings()

baseURL = 'https://oshoworld.com/osho-audio-discourse-english-'
# baseURL = 'https://oshoworld.com/audio-discourse-hindi-'

download_dir = 'downloads/English'

if baseURL.endswith('hindi-'):
    download_dir = 'downloads/Hindi'

# Select Hindi directory if baseurl is Hindi

if not os.path.exists(download_dir):
    os.makedirs(download_dir)

headers = {
     "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0"
}

# alphabets = ['g']
alphabets = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler(sys.stdout))

def download_discourse(url: str, base_dir: str):
    logger.info('Finding tracks for Discourse ' + url + '...')
    try:
        soup = BeautifulSoup(requests.get(url, headers=headers, verify=False).text, 'html.parser')
        discourse = soup.find('meta', attrs={'property': 'og:title'})['content'].split(' # ')[0]
        discourse_dir = os.path.join(base_dir, discourse)
        
        if not os.path.exists(discourse_dir):
            os.makedirs(discourse_dir)
        
        table = soup.find('figure', class_='wp-block-table')
        rows = table.find_all('tr')
        
        for row in rows:
            cells = row.find_all('td')
            if len(cells) == 2:
                url = cells[1].find('a')['href']
                soup = BeautifulSoup(requests.get(url, headers=headers, verify=False).text, 'html.parser')
                title = cells[1].text.strip()
                audio_tag = soup.find('div', class_="audio_frame audio_local")
                download_link = audio_tag.find('source')['src']
                file_name = title + '.mp3'  # Extracting the discourse number from the title
                file_path = os.path.join(discourse_dir, file_name)
                
                if os.path.isfile(file_path):
                    logger.info('Track ' + title + ' already exists. Skipping...')
                    continue
                
                logger.info('>> Downloading ' + file_name + ' : ' + download_link)
                dl = SmartDL(download_link, dest=file_path, timeout=600)
                try:
                    dl.start()
                    if dl.isFinished() and dl.isSuccessful():
                        logger.info('>> Downloaded ' + file_name)
                    else:
                        logger.error('>> Failed to download ' + file_name)
                except Exception as e:
                    logger.exception(e)
    except Exception as e:
        logger.exception(e)

for alphabet in alphabets:
    dir_alpha = os.path.join(download_dir, alphabet)

    if not os.path.exists(dir_alpha):
        os.makedirs(dir_alpha)

    logger.info('Finding discourses with ' + alphabet.capitalize() + '...')
    url = baseURL + alphabet + '/'
    soup = BeautifulSoup(requests.get(url, headers=headers, verify=False).text, 'html.parser')
    discourses = soup.find_all('a', string="Play & Download", href=True)
    discourse_links = [discourse['href'] for discourse in discourses]

    for discourse in discourse_links:
        download_discourse(discourse, dir_alpha)

logger.info('>>>> Completed all downloads! <<<<')
