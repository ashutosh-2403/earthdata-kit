import requests

def fetch_sentinel1a_granules(start_date, end_date, bbox):
    """
    Fetch Sentinel-1A SLC granules from NASA Earthdata API based on date range and bounding box,
    and display their download URLs.
    """
    CMR_URL = "https://cmr.earthdata.nasa.gov/search/granules.json"
    COLLECTION_ID = "C1214470488-ASF"
    
    params = {
        "concept_id": COLLECTION_ID,
        "temporal": f"{start_date}T00:00:00Z,{end_date}T23:59:59Z",
        "bounding_box": f"{bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]}",
        "page_size": 10,
        "sort_key": "-start_date",
    }
    
    response = requests.get(CMR_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        granules = data.get("feed", {}).get("entry", [])
        
        if granules:
            print("\nMatching Granules:")
            for granule in granules:
                title = granule.get('title', 'Unknown')
                start = granule.get('time_start', 'N/A')
                end = granule.get('time_end', 'N/A')
                links = granule.get('links', [])
                
                download_links = [link['href'] for link in links if 'href' in link and link.get('rel') == 'http://esipfed.org/ns/fedsearch/1.1/data#']
                
                print(f"  - {title}\n    Start: {start}\n    End: {end}")
                if download_links:
                    for url in download_links:
                        print(f"    Download URL: {url}")
                else:
                    print("    No download URL found.")
                print()
        else:
            print("No granules found for the given date range and bounding box.")
    else:
        print(f"API Error {response.status_code}: {response.text}")

if __name__ == "__main__":
    start_date = input("Enter start date (YYYY-MM-DD): ").strip()
    end_date = input("Enter end date (YYYY-MM-DD): ").strip()
    
    bbox_input = input("Enter bounding box (min_lon, min_lat, max_lon, max_lat) comma-separated: ").strip()
    bbox = [float(coord) for coord in bbox_input.split(",")]
    
    if len(start_date) != 10 or len(end_date) != 10:
        print("Invalid date format. Use YYYY-MM-DD.")
    elif len(bbox) != 4:
        print("Invalid bounding box format. Provide exactly four comma-separated values.")
    else:
        fetch_sentinel1a_granules(start_date, end_date, bbox)
