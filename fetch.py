import os
import uuid
import json
import requests
from concurrent.futures import ThreadPoolExecutor

# Number of worker threads to use for downloading web pages
NUM_WORKERS = 5

# Maximum number of retries for downloading a webpage
MAX_RETRIES = 10

# Cache to store the pages that have been requested in the last 24 hours
page_cache = {}

# Endpoint for retrieving the source of a webpage
def pagesource(request):
    # Parse the request body
    body = json.loads(request.body)
    uri = body['uri']
    retry_limit = body['retryLimit']

    # Check the cache
    if uri in page_cache:
        # Return the cached page
        return {
            'id': page_cache[uri]['id'],
            'uri': uri,
            'sourceUri': page_cache[uri]['sourceUri']
        }

    # Create a unique identifier for the page
    page_id = str(uuid.uuid4())

    # Download the page in a separate thread
    with ThreadPoolExecutor(max_workers=NUM_WORKERS) as executor:
        future = executor.submit(download_page, uri, retry_limit)
        source = future.result()

    # Save the page to the local file system
    filename = f"{page_id}.html"
    with open(filename, "w") as f:
        f.write(source)

    # Add the page to the cache
    page_cache[uri] = {
        'id': page_id,
        'sourceUri': filename
    }

    # Return the page information
    return {
        'id': page_id,
        'uri': uri,
        'sourceUri': filename
    }

# Function for downloading a webpage
def download_page(uri, retry_limit):
    # Set the initial number of retries
    retries = 0

    # Loop until the page is successfully downloaded or the retry limit is reached
    while True:
        try:
            # Make the request to retrieve the webpage
            response = requests.get(uri)

            # Return the page source if the request was successful
            if response.status_code == 200:
                return pagesource(response)

            # Increase the number of retries
            retries += 1

            # Check if the retry limit has been reached
            if retries >= retry_limit:
                break
        except:
            # Increase the number of retries
            retries += 1

            # Check if the retry limit has been reached
            if retries >= retry_limit:
                break
    # Return an empty string if the page could not be downloaded
    return ""
