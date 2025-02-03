import os
import json
import requests
import logging
from bs4 import BeautifulSoup
import re
from time import sleep
from urllib.parse import urlparse
import argparse
import sys
import tldextract
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from colorama import Fore, Back, Style, init

# Initialize colorama
init(autoreset=True)

# Configuration file for saving sessions
config_file = "session_config.json"
path = os.getcwd()

# Define the path for the input file (where URLs are read and written)
input_file = os.path.join(path, "urls.txt")

# Define the path for the Results directory where files will be stored
results_dir = os.path.join(path, "Results")

# Create Results directory if it doesn't exist
if not os.path.exists(results_dir):
    os.makedirs(results_dir)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Function to load session from the configuration file
def load_session():
    if os.path.exists(config_file):
        with open(config_file, "r") as file:
            session_data = json.load(file)
            return session_data.get("phpsessid"), session_data.get("zhetoken")
    return None, None

# Function to save the session to the configuration file
def save_session(phpsessid, zhetoken):
    session_data = {
        "phpsessid": phpsessid,
        "zhetoken": zhetoken
    }
    with open(config_file, "w") as file:
        json.dump(session_data, file)
    logging.info("Session saved successfully.")

# Function to prompt the user for session information
def prompt_for_session():
    print(Fore.GREEN + "\n[INFO] Please enter your Zone-H session information.")
    phpsessid = input(Fore.CYAN + "\n[] Enter PHPSESSID (e.g., iqhg1hpl6u3h9pramlkjaur1s3): ").strip()
    zhetoken = input(Fore.CYAN + "\n[] Enter ZHE Token (e.g., a78656eb0643e749d79808e64eade4f7): ").strip()

    if phpsessid and zhetoken:
        save_session(phpsessid, zhetoken)
        return phpsessid, zhetoken
    else:
        print(Fore.RED + "\n[] Invalid information. Please try again.")
        return prompt_for_session()

# Function to display the banner
def print_banner():
    print(Fore.GREEN + " " * 35 + "" * 50)
    print(Fore.RED + " " * 50 + "#Author: Hackfut\n" + " " * 50 + "#Tg: https://t.me/H4ckfutSec\n" + " " * 50 + "#Github: https://github.com/HackfutSec\n" + " " * 50 + "#License : MIT")
    print(Fore.GREEN + " " * 35 + "-" * 50)
    banner = """
    {0:^50}
    {1:^50}
    """.format(Fore.GREEN + " " * 50 + "ZoneSpy" + " " * 50, Fore.YELLOW  + " " * 47 + "Zone-H Grabber")
    print(banner)
    print(Fore.GREEN + " " * 3 + "-" * 100)
    print(Fore.RED + " " * 12 + "[Warning] I am not responsible for the way you will use this program [Warning]")
    print(Fore.GREEN + " " * 3 + "-" * 100)

# Function to count the number of lines in a file
def number_of_lines(file_path):
    with open(file_path, "r") as file:
        return sum(1 for line in file)

# Function to extract and validate the URL
def extract_and_validate_url(url):
    extracted = tldextract.extract(url)
    if extracted.domain and extracted.suffix:
        return f"{extracted.domain}.{extracted.suffix}"
    else:
        return None

# Function to save the results to a file
def save_to_file(data, file_type):
    output_file = os.path.join(results_dir, f"{file_type}_results.txt")
    with open(output_file, "a+") as file:
        file.write(data + "\n")

# Function to process a single page
def process_page(url, cookies, headers, file_type):
    try:
        response = requests.get(url, headers=headers, cookies=cookies, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        urls = set()
        for tag in soup.find_all('td'):
            if tag.string and "http" not in tag.string:
                validated_url = extract_and_validate_url(tag.string)
                if validated_url:
                    urls.add(validated_url)
        return urls
    except requests.exceptions.RequestException as e:
        logging.error(f"Request error for {url}: {e}")
        return set()

# Function to check notifiers
def check_notifier(defacer_username, phpsessid, zhetoken):
    cookies = {'PHPSESSID': phpsessid, 'ZHE': zhetoken}
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    base_url = f"http://www.zone-h.org/archive/notifier={defacer_username}"
    urls = set()

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = []
        for page_number in range(1, 100):  # Adjust the range as needed
            url = f"{base_url}/page={page_number}" if page_number > 1 else base_url
            futures.append(executor.submit(process_page, url, cookies, headers, "notifier"))

        for future in tqdm(as_completed(futures), total=len(futures), desc=f"Processing {defacer_username}"):
            urls.update(future.result())

    for url in urls:
        save_to_file(url, "notifier")

# Function to check OnHold archives
def check_onhold(phpsessid, zhetoken):
    cookies = {'PHPSESSID': phpsessid, 'ZHE': zhetoken}
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    base_url = "http://www.zone-h.org/archive/published=0"
    urls = set()

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = []
        for page_number in range(1, 100):  # Adjust the range as needed
            url = f"{base_url}/page={page_number}" if page_number > 1 else base_url
            futures.append(executor.submit(process_page, url, cookies, headers, "onhold"))

        for future in tqdm(as_completed(futures), total=len(futures), desc="Processing OnHold"):
            urls.update(future.result())

    for url in urls:
        save_to_file(url, "onhold")

# Function to check a specific archive
def check_archive(archive_url, phpsessid, zhetoken):
    cookies = {'PHPSESSID': phpsessid, 'ZHE': zhetoken}
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    base_url = f"http://www.zone-h.org/archive/{archive_url}"
    urls = set()

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = []
        for page_number in range(1, 100):  # Adjust the range as needed
            url = f"{base_url}/page={page_number}" if page_number > 1 else base_url
            futures.append(executor.submit(process_page, url, cookies, headers, "archive"))

        for future in tqdm(as_completed(futures), total=len(futures), desc=f"Processing {archive_url}"):
            urls.update(future.result())

    for url in urls:
        save_to_file(url, "archive")

# Function to display the menu and interact with the user
def display_menu():
    while True:
        print(Fore.GREEN + "\n[INFO] Select an option:\n")
        print(Fore.YELLOW + "1. Check a notifier")
        print(Fore.YELLOW + "2. Check multiple notifiers")
        print(Fore.YELLOW + "3. Check a specific archive")
        print(Fore.YELLOW + "4. Check multiple archives")
        print(Fore.YELLOW + "5. Check OnHold archives")
        print(Fore.YELLOW + "6. Check everything (Notifiers, Archives, OnHold)")
        print(Fore.RED + "7. Exit")

        choice = input(Fore.CYAN + "\n[] Your choice: ").strip()

        if choice == "1":
            notifier = input(Fore.CYAN + "\n[] Enter the defacer's username: ").strip()
            phpsessid, zhetoken = load_session()
            if not phpsessid or not zhetoken:
                phpsessid, zhetoken = prompt_for_session()
            check_notifier(notifier, phpsessid, zhetoken)
        
        elif choice == "2":
            file_list = input(Fore.CYAN + "\n[] Enter the path to the notifier list file: ").strip()
            try:
                with open(file_list, "r") as f:
                    usernames = [line.strip() for line in f.readlines()]
                phpsessid, zhetoken = load_session()
                if not phpsessid or not zhetoken:
                    phpsessid, zhetoken = prompt_for_session()
                for username in usernames:
                    check_notifier(username, phpsessid, zhetoken)
            except FileNotFoundError:
                print(Fore.RED + f"\n[] The file {file_list} was not found.")

        elif choice == "3":
            archive_url = input(Fore.CYAN + "\n[] Enter the archive URL: ").strip()
            phpsessid, zhetoken = load_session()
            if not phpsessid or not zhetoken:
                phpsessid, zhetoken = prompt_for_session()
            check_archive(archive_url, phpsessid, zhetoken)
        
        elif choice == "4":
            file_list = input(Fore.CYAN + "\n[] Enter the path to the archive list file: ").strip()
            try:
                with open(file_list, "r") as f:
                    archive_urls = [line.strip() for line in f.readlines()]
                phpsessid, zhetoken = load_session()
                if not phpsessid or not zhetoken:
                    phpsessid, zhetoken = prompt_for_session()
                for archive_url in archive_urls:
                    check_archive(archive_url, phpsessid, zhetoken)
            except FileNotFoundError:
                print(Fore.RED + f"\n[] The file {file_list} was not found.")
        
        elif choice == "5":
            phpsessid, zhetoken = load_session()
            if not phpsessid or not zhetoken:
                phpsessid, zhetoken = prompt_for_session()
            check_onhold(phpsessid, zhetoken)
        
        elif choice == "6":
            phpsessid, zhetoken = load_session()
            if not phpsessid or not zhetoken:
                phpsessid, zhetoken = prompt_for_session()
            print(Fore.CYAN + "\n[INFO] Checking everything...\n")
            check_onhold(phpsessid, zhetoken)
            # Add checks for notifiers and archives here if needed
        
        elif choice == "7":
            print(Fore.RED + "\n[] Exiting the program...\n")
            sys.exit()
        else:
            print(Fore.RED + "\n[] Invalid option. Please try again.")

def main():
    print_banner()
    display_menu()

if __name__ == "__main__":
    main()
