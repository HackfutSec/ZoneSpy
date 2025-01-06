## ZoneSpy: A Powerful Zone-H Archive Scraper and Notifier Checker

**ZoneSpy** is a Python-based script designed to scrape and extract information from Zone-H archives and notifiers. This tool allows users to monitor defacements and extract domain URLs from Zone-H's publicly available archives, including **published** and **OnHold** defacements. It also supports bulk operations, allowing users to check multiple notifiers or archives at once.

### Features
- **Notifier Checker:** Fetch URLs associated with a specific defacer's username from the Zone-H archive.
- **Bulk Notifier Checker:** Allows you to process multiple defacers from a list of usernames stored in a text file.
- **OnHold Archive Checker:** Scrapes URLs from Zone-H’s OnHold defacements.
- **Archive URL Checker:** Check and extract URLs from any specific Zone-H archive.
- **Session Management:** Stores your session information securely in a configuration file, so you don’t need to enter your credentials every time you run the script.
- **Multi-threading Support:** Efficiently processes multiple requests using **ThreadPoolExecutor**, making it suitable for large-scale scrapping.
- **Results Storage:** Automatically stores valid URLs to a results file for further use or analysis.

### Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/HackfutSec/ZoneSpy.git
    cd ZoneSpy
    ```

2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

### Usage

1. **Start the Program:**
   ```bash
   python zoneSpy.py
   ```

2. **Menu Options:**
   Once the program is running, you will be presented with a menu to choose from several options:
   - **1:** Check a specific notifier by a defacer's username.
   - **2:** Check multiple notifiers from a list of usernames.
   - **3:** Check a specific archive URL.
   - **4:** Check multiple archives from a list of archive URLs.
   - **5:** Check the OnHold archives.
   - **6:** Check everything (Notifiers, Archives, OnHold).
   - **7:** Exit the program.

3. **Session Management:**  
   The first time you run the program, you will be prompted to enter your **PHPSESSID** and **ZHE token** for authentication. These values will be saved in a session configuration file (`session_config.json`) for future use.

### Example

```bash
[INFO] Please enter your Zone-H session information.
[] Enter PHPSESSID (e.g., iqhg1hpl6u3h9pramlkjaur1s3): iqhg1hpl6u3h9pramlkjaur1s3
[] Enter ZHE Token (e.g., a78656eb0643e749d79808e64eade4f7): a78656eb0643e749d79808e64eade4f7
```

Once the session is set, you can start scraping specific notifiers or archives, and the URLs will be saved to a results file.

### Dependencies
- `requests` – for making HTTP requests to the Zone-H site.
- `beautifulsoup4` – for parsing HTML content and extracting information.
- `tldextract` – for validating and extracting domain names.
- `concurrent.futures` – for handling multi-threaded operations.
- `colorama` – for colored terminal output to improve UX.

### License

This project is licensed under the MIT License.
