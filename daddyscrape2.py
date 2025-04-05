import os
import requests
from bs4 import BeautifulSoup
import json
import re
from collections import defaultdict
from dictionaries.tvLogos import STATIC_LOGOS
from dictionaries.tvGids import STATIC_TVG_IDS
from dictionaries.tvCategories import STATIC_CATEGORIES
from concurrent.futures import ThreadPoolExecutor, as_completed

# File e URL statici
daddyLiveChannelsFileName = '247channels.html'
daddyLiveChannelsURL = 'https://thedaddy.to/24-7-channels.php'

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

def search_streams(file_path, keyword):
    """Estrai i canali dalla pagina HTML."""
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
                        # Aggiungi il canale al dizionario 'matches'
                        matches[stream_number] = {
                            'streamNumber': stream_number,
                            'streamName': stream_name,
                            'serverKey': None  # Server key placeholder
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
    if tvgId:
        return tvgId

    for key, tvg_id in STATIC_TVG_IDS.items():
        if key.lower() in channel_name.lower():  # case-insensitive match
            return tvg_id
    
    print(channel_name)
    return "unknown"

def generate_m3u8(matches):
    """Genera il file M3U8 con i canali."""
    if not matches:
        print("No matches found. Skipping M3U8 generation.")
        return

    with open(fileVlc, 'w', encoding='utf-8') as fileVLC, open(fileTiv, 'w', encoding='utf-8') as fileTIV:
        fileVLC.write('#EXTM3U\n')
        fileTIV.write('#EXTM3U\n')

        for channel in matches.values():
            channel_id = channel['streamNumber']
            channel_name = channel['streamName']
            server_key = channel['serverKey']
            tvicon_path = search_logo(channel_name)
            tvg_id = search_tvg_id(channel_name)
            category = search_category(channel_name)

            "https://" + serverKey + "new.koskoros.ru/" + serverKey + "/" + channelKey + "/mono.m3u8";

            fileVLC.write(f"#EXTINF:-1 tvg-id=\"{tvg_id}\" tvg-name=\"{channel_name}\" tvg-logo=\"{tvicon_path}\" group-title=\"{category}\", {channel_name}\n")
            fileVLC.write(f'#EXTVLCOPT:http-referrer=https://ilovetoplay.xyz/\n')
            fileVLC.write(f'#EXTVLCOPT:http-user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 17_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1\n')
            fileVLC.write(f'#EXTVLCOPT:http-origin=https://ilovetoplay.xyz/\n')
            if server_key:  # Se server_key è presente, usa la URL con il server_key
                fileVLC.write(f"https://{server_key}new.newkos.ru/{server_key}/{channel_id}/mono.m3u8\n\n")
            else:  # Se server_key non è presente, usa la URL alternativa
                fileVLC.write(f"https://top1.newkso.ru/top1/cdn/{channel_id}/mono.m3u8\n\n")

            fileTIV.write(f"#EXTINF:-1 tvg-id=\"{tvg_id}\" tvg-name=\"{channel_name}\" tvg-logo=\"{tvicon_path}\" group-title=\"{category}\", {channel_name}\n")
            if server_key:  # Se server_key è presente, usa la URL con il server_key
                fileTIV.write(f"https://{server_key}new.newkos.ru/{server_key}/{channel_id}/mono.m3u8|Referer=\"https://ilovetoplay.xyz/\"|User-Agent=\"Mozilla/5.0 iPhone; CPU iPhone OS 17_6_0 like Mac OS X AppleWebKit/605.2.10 KHTML, like Gecko Version/17.6.0 Mobile/16F152 Safari/605.2\"|Origin=\"https://ilovetoplay.xyz\"\n")
            else:  # Se server_key non è presente, usa la URL alternativa
                fileTIV.write(f"https://top1.newkso.ru/top1/cdn/{channel_id}/mono.m3u8|Referer=\"https://ilovetoplay.xyz/\"|User-Agent=\"Mozilla/5.0 iPhone; CPU iPhone OS 17_6_0 like Mac OS X AppleWebKit/605.2.10 KHTML, like Gecko Version/17.6.0 Mobile/16F152 Safari/605.2\"|Origin=\"https://ilovetoplay.xyz\"\n")

    print("M3U8 files generated successfully.")

def get_server_key(stream_number):
    """Recupera il server_key per uno stream_number."""
    try:
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "it-IT,it;q=0.8,en-US;q=0.5,en;q=0.3",
            "Connection": "keep-alive",
            "Host": "newembedplay.xyz",
            "Priority": "u=0, i",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "TE": "trailers",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0"
        }

        url = f"https://pkpakiplay.xyz/server_lookup.php?channel_id=premium{stream_number}"

        # Fai la richiesta GET con un timeout
        response = requests.get(url, headers=headers, timeout=0.5)
        response.raise_for_status()

        decoded_data = response.content.decode('utf-8', errors='ignore')
        match = re.search(r'\{.*\}', decoded_data)  # Cerca il blocco JSON

        if match:
            json_data = json.loads(match.group(0))
            return json_data.get('server_key')

    except requests.exceptions.RequestException as e:
        print(f"Error fetching server_key for {stream_number}: {e}")
    return None

def fetch_server_keys_in_parallel(matches):
    """Recupera i server_keys in parallelo per i canali."""
    with ThreadPoolExecutor() as executor:
        futures = {executor.submit(get_server_key, stream_number): stream_number for stream_number in matches}
        for future in as_completed(futures):
            stream_number = futures[future]
            try:
                server_key = future.result()
                if server_key:
                    matches[stream_number]['serverKey'] = server_key
            except Exception as e:
                print(f"Error retrieving server key for {stream_number}: {e}")

fileVlc = "out_new.m3u8"
fileTiv = "out_newTiv.m3u8"
defaultLogo = "https://raw.githubusercontent.com/sesukyole/dtankdempse-daddylive-m3u/refs/heads/main/bg/ddy-logo.jpg"

# Cleanup e Fetch dati
delete_file_if_exists(daddyLiveChannelsFileName)
fetch_with_debug(daddyLiveChannelsFileName, daddyLiveChannelsURL)

# Cancella anche out.m3u8 prima di crearne uno nuovo
delete_file_if_exists(fileVlc)
delete_file_if_exists(fileTiv)

# Elaborazione dei canali
matches = search_streams(daddyLiveChannelsFileName, "")
fetch_server_keys_in_parallel(matches)
generate_m3u8(matches)
