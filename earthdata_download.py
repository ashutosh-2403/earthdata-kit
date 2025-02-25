import os
import requests
from tqdm import tqdm
from dotenv import load_dotenv
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from urllib.parse import urlparse


class EarthDataWrapper:
    CMR_URL = "https://cmr.earthdata.nasa.gov/search/granules.json"
    def __init__(self, token=None, edk_path="edk_data"):
        load_dotenv()
        self.session = requests.Session()
        self.edk_path = edk_path
        self.token = token or os.getenv("EARTHDATA_TOKEN")
        if not self.token:
            raise ValueError("[✘] Earthdata token is missing.")
        os.makedirs(edk_path, exist_ok=True)
        self.setup_retries()
        self.authenticate()

    def setup_retries(self):
        retries = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
        self.session.mount("https://", HTTPAdapter(max_retries=retries))

    def authenticate(self):
        headers = {"Authorization": f"Bearer {self.token}"}
        try:
            response = self.session.get(self.CMR_URL, headers=headers, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            raise RuntimeError(f"[✘] Authentication failed: {e}")

    def search(self, start_date=None, end_date=None, bbox=None, page_size=10, collection_concept_id=None):
        if not collection_concept_id:
            raise ValueError("[✘] A 'collection_concept_id' is required for searching.")
        params = {
            "page_size": page_size,
            "collection_concept_id": collection_concept_id,
            "token": self.token,
        }
        if start_date and end_date:
            params["temporal"] = f"{start_date}T00:00:00Z/{end_date}T23:59:59Z"
        if bbox:
            params["bounding_box"] = bbox
        try:
            response = self.session.get(self.CMR_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as e:
            print(f"[✘] API request failed: {e}")
            return []
        urls = [
            link["href"]
            for granule in data.get("feed", {}).get("entry", [])
            for link in granule.get("links", [])
            if "https" in link.get("href", "")
        ]
        if not urls:
            return []
        self.log_results(urls)
        return urls

    def log_results(self, urls, filename="downloaded_urls.txt"):
        with open(filename, "w") as file:
            for url in urls:
                file.write(url + "\n")

    def extract_filename(self, url):
        parsed_url = urlparse(url)
        return os.path.basename(parsed_url.path) or "unknown_file.tif"

    def download(self, urls):
        if not urls:
            return
        for url in urls:
            filename = self.extract_filename(url)
            filepath = os.path.join(self.edk_path, filename)
            try:
                response = self.session.get(url, stream=True, timeout=20)
                response.raise_for_status()
                total_size = int(response.headers.get("content-length", 0))
                with open(filepath, "wb") as file, tqdm(
                    desc=filename, total=total_size, unit="B", unit_scale=True, unit_divisor=1024
                ) as bar:
                    for chunk in response.iter_content(chunk_size=1024):
                        file.write(chunk)
                        bar.update(len(chunk))
            except requests.RequestException as e:
                print(f" Failed to download {url}: {e}")


if __name__ == "__main__":
    token = os.getenv("EARTHDATA_TOKEN")
    if not token:
        print(" Missing Earthdata token! Check your .env file.")
    else:
        earthdata = EarthDataWrapper(token=token)
        results = earthdata.search(
            start_date="2024-01-01",
            end_date="2024-02-01",
            bbox="-180,-90,180,90",
            page_size=3,
            collection_concept_id="C1214470488-ASF"
        )
        if results:
            earthdata.download(results)
import logging

class EarthDataWrapper:
    CMR_URL = "https://cmr.earthdata.nasa.gov/search/granules.json"
    def __init__(self, token=None, edk_path="edk_data"):
        load_dotenv()
        self.session = requests.Session()
        self.edk_path = edk_path
        self.token = token or os.getenv("EARTHDATA_TOKEN")
        if not self.token:
            raise ValueError("[✘] Earthdata token is missing.")
        os.makedirs(edk_path, exist_ok=True)
        self.setup_retries()
        self.authenticate()
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler = logging.FileHandler('earthdata.log')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    def setup_retries(self):
        retries = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
        self.session.mount("https://", HTTPAdapter(max_retries=retries))

    def authenticate(self):
        headers = {"Authorization": f"Bearer {self.token}"}
        try:
            response = self.session.get(self.CMR_URL, headers=headers, timeout=10)
            response.raise_for_status()
            self.logger.info("Authentication successful")
        except requests.RequestException as e:
            self.logger.error(f"Authentication failed: {e}")
            raise RuntimeError(f"[✘] Authentication failed: {e}")

    def search(self, start_date=None, end_date=None, bbox=None, page_size=10, collection_concept_id=None):
        if not collection_concept_id:
            self.logger.error("A 'collection_concept_id' is required for searching.")
            raise ValueError("[✘] A 'collection_concept_id' is required for searching.")
        params = {
            "page_size": page_size,
            "collection_concept_id": collection_concept_id,
            "token": self.token,
        }
        if start_date and end_date:
            params["temporal"] = f"{start_date}T00:00:00Z/{end_date}T23:59:59Z"
        if bbox:
            params["bounding_box"] = bbox
        try:
            response = self.session.get(self.CMR_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            self.logger.info("API request successful")
        except requests.RequestException as e:
            self.logger.error(f"API request failed: {e}")
            return []
        urls = [
            link["href"]
            for granule in data.get("feed", {}).get("entry", [])
            for link in granule.get("links", [])
            if "https" in link.get("href", "")
        ]
        if not urls:
            self.logger.info("No URLs found")
            return []
        self.log_results(urls)
        return urls

    def log_results(self, urls, filename="downloaded_urls.txt"):
        with open(filename, "w") as file:
            for url in urls:
                file.write(url + "\n")
        self.logger.info("Results logged to file")

    def extract_filename(self, url):
        parsed_url = urlparse(url)
        return os.path.basename(parsed_url.path) or "unknown_file.tif"

    def download(self, urls):
        if not urls:
            self.logger.info("No URLs to download")
            return
        for url in urls:
            filename = self.extract_filename(url)
            filepath = os.path.join(self.edk_path, filename)
            try:
                response = self.session.get(url, stream=True, timeout=20)
                response.raise_for_status()
                total_size = int(response.headers.get("content-length", 0))
                with open(filepath, "wb") as file, tqdm(
                    desc=filename, total=total_size, unit="B", unit_scale=True, unit_divisor=1024
                ) as bar:
                    for chunk in response.iter_content(chunk_size=1024):
                        file.write(chunk)
                        bar.update(len(chunk))
                self.logger.info(f"Downloaded {filename}")
            except requests.RequestException as e:
                self.logger.error(f"Failed to download {url}: {e}")


if __name__ == "__main__":
    token = os.getenv("EARTHDATA_TOKEN")
    if not token:
        print("Missing Earthdata token! Check your .env file.")
    else:
        earthdata = EarthDataWrapper(token=token)
        results = earthdata.search(
            start_date="2024-01-01",
            end_date="2024-02-01",
            bbox="-180,-90,180,90",
            page_size=3,
            collection_concept_id="C1214470488-ASF"
        )
        if results:
            earthdata.download(results)