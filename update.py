import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import os


def download_file(url, local_path):
    response = requests.get(url)
    os.makedirs(os.path.dirname(local_path), exist_ok=True)
    with open(local_path, "wb") as f:
        f.write(response.content)


def download_website(url, output_dir):
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Download main page
    response = requests.get(url)
    response.encoding = "utf-8"
    soup = BeautifulSoup(response.text, "html.parser")

    # Save main HTML
    with open(os.path.join(output_dir, "index.html"), "w", encoding="utf-8") as f:
        html = response.text
        html = html.replace("edvancium.carrd.co", "edvancium.com")
        f.write(html)

    # Find and download all assets
    for tag in soup.find_all(["img", "script", "link", "meta"]):
        # Handle different asset types
        asset_urls = []
        if tag.name == "img":
            if tag.get("src"):
                asset_urls.append(tag.get("src"))
            if tag.get("data-src"):
                asset_urls.append(tag.get("data-src"))
        elif tag.name == "script" and tag.get("src"):
            asset_urls.append(tag.get("src"))
        elif tag.name == "link" and tag.get("href"):
            asset_urls.append(tag.get("href"))
        elif tag.name == "meta" and tag.get("content"):
            # Check if content contains a URL
            content = tag.get("content")
            if content and (content.startswith("http") or content.startswith("//")):
                asset_urls.append(content)

        for asset_url in asset_urls:
            # Make absolute URL if relative
            asset_url = urljoin(url, asset_url)

            # Skip external resources
            if not asset_url.startswith(url):
                continue

            # Create local path
            parsed_url = urlparse(asset_url)
            local_path = os.path.join(output_dir, parsed_url.path.lstrip("/"))

            # Download asset
            try:
                download_file(asset_url, local_path)
                print(f"Downloaded: {asset_url}")
            except Exception as e:
                print(f"Failed to download {asset_url}: {str(e)}")


# Execute the download
website_url = "https://edvancium.carrd.co"
output_directory = "docs"
download_website(website_url, output_directory)
