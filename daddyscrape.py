import os
import requests
from bs4 import BeautifulSoup
import json
import gzip
from dictionaries.tvLogos import STATIC_LOGOS
from dictionaries.tvGids import STATIC_TVG_IDS
from dictionaries.tvCategories import STATIC_CATEGORIES

# File e URL statici
daddyLiveChannelsFileName = '247channels.html'
daddyLiveChannelsURL = 'https://thedaddy.to/24-7-channels.php'

def delete_file_if_exists(file_path):
    if os.path.isfile(file_path):
        os.remove(file_path)
        print(f'File {file_path} deleted.')

def fetch_with_debug(filename, url):
    try:
        print(f'Downloading {url}...')
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        with open(filename, 'wb') as file:
            file.write(response.content)

        print(f'File {filename} downloaded successfully.')
    except requests.exceptions.RequestException as e:
        print(f'Error downloading {url}: {e}')


def search_category(channel_name):
    return STATIC_CATEGORIES.get(channel_name, "Other")


excludeChannels = ["18+", "adult"] 

def search_streams(file_path, keyword):
    matches = []
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            soup = BeautifulSoup(file.read(), 'html.parser')
            links = soup.find_all('a', href=True)

            for link in links:
                if keyword.lower() in link.text.lower():
                    href = link['href']
                    stream_number = href.split('-')[-1].replace('.php', '')
                    stream_name = link.text.strip()
                    match = (stream_number, stream_name)
                    
                    if match not in matches and match[0].isnumeric() and not any(x in match[1].lower() for x in excludeChannels):
                        matches.append(match)
    except FileNotFoundError:
        print(f'The file {file_path} does not exist.')
    return matches

def search_logo(channel_name):

    logo = STATIC_LOGOS.get(channel_name)

    if logo:
        return logo

     # Se non trovato, cerca per corrispondenza parziale
    for key, url in STATIC_LOGOS.items():
        if key.lower() in channel_name.lower():  # case-insensitive match
            return url

    return defaultLogo
    

def search_tvg_id(channel_name):

    # Prima prova a trovare direttamente il canale
    tvgId = STATIC_TVG_IDS.get(channel_name)
    
    if tvgId:
        return tvgId

    # Se non trovato, cerca per corrispondenza parziale
    for key, tvg_id in STATIC_TVG_IDS.items():
        if key.lower() in channel_name.lower():  # case-insensitive match
            return tvg_id
    
    #print(channel_name)
    return "unknown"  # Restituisce "unknown" se non trovato
    

def generate_m3u8(matches):
    if not matches:
        print("No matches found. Skipping M3U8 generation.")
        return

    with open(fileVlc, 'w', encoding='utf-8') as fileVLC, open(fileKodi, 'w', encoding='utf-8') as fileKODI , open(fileTivimate, 'w', encoding='utf-8') as fileTVMATE, open(fileOxyroid, 'w', encoding='utf-8') as fileOX:
        fileVLC.write('#EXTM3U\n')
        fileKODI.write('#EXTM3U\n')
        fileTVMATE.write('#EXTM3U\n')
        fileOX.write('#EXTM3U\n')

        for channel in matches:
            channel_id = channel[0]
            channel_name = channel[1]
            tvicon_path = search_logo(channel_name)
            tvg_id = search_tvg_id(channel_name)
            category = search_category(channel_name)

            fileVLC.write(f"#EXTINF:-1 tvg-id=\"{tvg_id}\" tvg-name=\"{channel_name}\" tvg-logo=\"{tvicon_path}\" group-title=\"{category}\", {channel_name}\n")
            fileVLC.write(f'#EXTVLCOPT:http-referrer=https://ilovetoplay.xyz/\n')
            fileVLC.write(f'#EXTVLCOPT:http-user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 17_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1\n')
            fileVLC.write(f'#EXTVLCOPT:http-origin=https://ilovetoplay.xyz/\n')
            fileVLC.write(f"https://xyzdddd.mizhls.ru/lb/premium{channel_id}/index.m3u8\n")

            fileKODI.write(f"#EXTINF:-1 tvg-id=\"{tvg_id}\" tvg-name=\"{channel_name}\" tvg-logo=\"{tvicon_path}\" group-title=\"{category}\", {channel_name}\n")
            fileKODI.write(f'#KODIPROP:inputstream.adaptive.license_key={{"Referer":"https://ilovetoplay.xyz/","User-Agent":"Mozilla/5.0 (iPhone; CPU iPhone OS 17_6_0 like Mac OS X) AppleWebKit/605.2.10 (KHTML, like Gecko) Version/17.6.0 Mobile/16F152 Safari/605.2","Origin":"https://ilovetoplay.xyz"}}\n')
            fileKODI.write(f"https://xyzdddd.mizhls.ru/lb/premium{channel_id}/index.m3u8\n")

            fileTVMATE.write(f"#EXTINF:-1 tvg-id=\"{tvg_id}\" tvg-name=\"{channel_name}\" tvg-logo=\"{tvicon_path}\" group-title=\"{category}\", {channel_name}\n")
            fileTVMATE.write(f"https://xyzdddd.mizhls.ru/lb/premium{channel_id}/index.m3u8|Referer=\"https://ilovetoplay.xyz/\"|User-Agent=\"Mozilla/5.0 iPhone; CPU iPhone OS 17_6_0 like Mac OS X AppleWebKit/605.2.10 KHTML, like Gecko Version/17.6.0 Mobile/16F152 Safari/605.2\"|Origin=\"https://ilovetoplay.xyz\"\n")

            fileOX.write(f"#EXTINF:-1 tvg-id=\"{tvg_id}\" tvg-name=\"{channel_name}\" tvg-logo=\"{tvicon_path}\" group-title=\"{category}\", {channel_name}\n")
            fileOX.write(f"https://xyzdddd.mizhls.ru/lb/premium{channel_id}/index.m3u8&h_Referer=https://ilovetoplay.xyz/&h_Origin=https://ilovetoplay.xyz&h_User-Agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3\n")

    print("M3U8 files generated successfully.")


fileVlc = "out_vlc.m3u8"
fileKodi = "out_kodi.m3u8"
fileTivimate = "out_tivimate.m3u8"
fileOxyroid = "out_oxy.m3u8"

defaultLogo = "https://raw.githubusercontent.com/stregolo/eventi/refs/heads/main/bg/ddy-logo.jpg"

# Cleanup e Fetch dati
delete_file_if_exists(daddyLiveChannelsFileName)
fetch_with_debug(daddyLiveChannelsFileName, daddyLiveChannelsURL)

# Cancella anche out.m3u8 prima di crearne uno nuovo
delete_file_if_exists(fileVlc)
delete_file_if_exists(fileKodi)
delete_file_if_exists(fileTivimate)
delete_file_if_exists(fileOxyroid)

# Elaborazione dati
matches = search_streams(daddyLiveChannelsFileName, "")
generate_m3u8(matches)

# Parte EPG commentata
"""
epgs = [
    {'filename': 'epgShare1.xml', 'url': 'https://epgshare01.online/epgshare01/epg_ripper_IT1.xml.gz'}
]

for epg in epgs:
    delete_file_if_exists(epg['filename'])
    fetch_with_debug(epg['filename'], epg['url'])
"""
