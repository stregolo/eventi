import os
import requests
from bs4 import BeautifulSoup
import json
import re
from collections import defaultdict
from dictionaries.tvInfo import CHANNELS_INFO

# File e URL statici
daddyLiveChannelsFileName = '247channels.html'
daddyLiveChannelsURL = 'https://daddylive.mp/24-7-channels.php'

# Estrai i dati dai canali in CHANNELS_INFO
STATIC_TVG_IDS = {}
STATIC_LOGOS = {}
STATIC_CATEGORIES = {}

# Popola i dizionari
for channel in CHANNELS_INFO['channels']:
    STATIC_TVG_IDS[channel['name']] = channel['tvgid']
    STATIC_LOGOS[channel['name']] = channel['logo']
    STATIC_CATEGORIES[channel['name']] = channel['category']

def delete_file_if_exists(file_path):
    """Cancella un file se esiste."""
    if os.path.isfile(file_path):
        os.remove(file_path)
        print(f'File {file_path} deleted.')

def fetch_with_debug(filename, url):
    """Scarica un file da un URL e gestisce errori di download."""
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
    """Restituisce la categoria di un canale."""
    return STATIC_CATEGORIES.get(channel_name, "Other")

excludeChannels = ["18+", "adult"] 

def search_streams(file_path, keyword, channels_data):
    """Estrai i canali dalla pagina HTML e recupera i serverKey dal dizionario `channels_data`."""
    matches = {}  # Utilizzo un dizionario per i risultati
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            soup = BeautifulSoup(file.read(), 'html.parser')
            links = soup.find_all('a', href=True)

            for link in links:
                if keyword.lower() in link.text.lower():
                    href = link['href']
                    stream_number = href.split('-')[-1].replace('.php', '')
                    stream_name = link.text.strip()

                    # Verifica che il numero di stream sia numerico e che non sia escluso
                    if stream_number.isnumeric() and not any(x in stream_name.lower() for x in excludeChannels):
                        # Trova il serverKey dal dizionario channels_data
                        server_key = None
                        for channel in channels_data['channels']:
                            if channel['id'] == stream_number:
                                server_key = channel.get('serverKey')
                                break
                                
                        # Aggiungi il canale al dizionario 'matches'
                        matches[stream_number] = {
                            'streamNumber': stream_number,
                            'streamName': stream_name,
                            'serverKey': server_key  # Ottieni serverKey dal dizionario
                        }

    except FileNotFoundError:
        print(f'The file {file_path} does not exist.')

    return matches

def search_logo(channel_name):
    """Restituisce l'URL del logo per un canale."""
    logo = STATIC_LOGOS.get(channel_name)
    if logo:
        return logo

    # Se non trovato, cerca per corrispondenza parziale
    for key, url in STATIC_LOGOS.items():
        if key.lower() in channel_name.lower():  # case-insensitive match
            return url

    return defaultLogo

def search_tvg_id(channel_name):
    """Restituisce il TVG ID per un canale."""
    tvgId = STATIC_TVG_IDS.get(channel_name)
    #primo controllo se matchano esattamente
    if tvgId != "unknown":
        return tvgId
    else:
        print(channel_name)
    
    #primo controllo se matchano parzialmente
    for key, tvg_id in STATIC_TVG_IDS.items():
        if key.lower() in channel_name.lower():  # case-insensitive match
            return tvg_id
    
    return "unknown"

def generate_m3u8(matches):
    """Genera il file M3U8 con i canali."""
    if not matches:
        print("No matches found. Skipping M3U8 generation.")
        return

    with open(fileVlc, 'w', encoding='utf-8') as fileVLC, open(fileTiv, 'w', encoding='utf-8') as fileTIV, open(filePro, 'w', encoding='utf-8') as filePRO:
        fileVLC.write('#EXTM3U url-tvg="https://github.com/stregolo/eventi/raw/refs/heads/main/epg.xml.gz"\n')
        fileTIV.write('#EXTM3U url-tvg="https://github.com/stregolo/eventi/raw/refs/heads/main/epg.xml.gz"\n')

        for channel in matches.values():
            channel_id = channel['streamNumber']
            channel_name = channel['streamName']
            server_key = channel['serverKey']
            tvicon_path = search_logo(channel_name)
            tvg_id = search_tvg_id(channel_name)
            category = search_category(channel_name)

            if server_key != "top1":
                url = (f"https://{server_key}new.newkso.ru/{server_key}/premium{channel_id}/mono.m3u8")
            else:
                url = (f"https://top1.newkso.ru/top1/cdn/{channel_id}/mono.m3u8")

            fileVLC.write(f"#EXTINF:-1 tvg-id=\"{tvg_id}\" tvg-name=\"{channel_name}\" tvg-logo=\"{tvicon_path}\" group-title=\"{category}\", {channel_name}\n")
            fileVLC.write(f'#EXTVLCOPT:http-referer=https://forcedtoplay.xyz/\n')
            fileVLC.write(f'#EXTVLCOPT:http-user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:140.0) Gecko/20100101 Firefox/140.0\n')
            fileVLC.write(f'#EXTVLCOPT:http-origin=https://forcedtoplay.xyz\n')
            fileVLC.write(f"{url}\n")
            
            fileTIV.write(f"#EXTINF:-1 tvg-id=\"{tvg_id}\" tvg-name=\"{channel_name}\" tvg-logo=\"{tvicon_path}\" group-title=\"{category}\", {channel_name}\n")
            fileTIV.write(f"{url}|Referer=\"https://forcedtoplay.xyz/\"|Origin=\"https://forcedtoplay.xyz\"|User-Agent=\"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:140.0) Gecko/20100101 Firefox/140.0\"\n")

    print("M3U8 files generated successfully.")


fileVlc = "out_vlc.m3u8"
fileTiv = "out_tivimate.m3u8"

defaultLogo = "https://raw.githubusercontent.com/stregolo/eventi/refs/heads/main/bg/ddy-logo.jpg"

# Cleanup e Fetch dati
delete_file_if_exists(daddyLiveChannelsFileName)
fetch_with_debug(daddyLiveChannelsFileName, daddyLiveChannelsURL)

# Cancella anche out.m3u8 prima di crearne uno nuovo
delete_file_if_exists(fileVlc)
delete_file_if_exists(fileTiv)


# Elaborazione dei canali
matches = search_streams(daddyLiveChannelsFileName, "", CHANNELS_INFO)
generate_m3u8(matches)
