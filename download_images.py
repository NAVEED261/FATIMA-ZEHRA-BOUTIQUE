#!/usr/bin/env python3
"""
Autonomous Image Download Script
Downloads 40 ladies fashion images and organizes by category
"""

import os
import requests
import time
from pathlib import Path

# Base paths
BASE_PATH = Path("/mnt/d/HACKATON-III/FATIMA-ZEHRA-BOUTIQUE-APP/learnflow-app/app/frontend/public/images")
CATEGORIES = {
    "fancy-suits": 10,
    "shalwar-qameez": 10,
    "cotton-suits": 10,
    "designer-brands": 10
}

# Unsplash API (using public search without auth key for demo)
UNSPLASH_API = "https://api.unsplash.com/search/photos"

def download_images_for_category(category_name, count, query):
    """Download images for a specific category using Unsplash"""

    category_dir = BASE_PATH / category_name
    category_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n🔍 Downloading {count} images for '{category_name}'...")
    print(f"   Query: {query}")

    # Build search URL
    url = f"{UNSPLASH_API}?query={query}&per_page={count}&orientation=portrait"

    try:
        response = requests.get(url, timeout=10)
        data = response.json()

        if 'results' not in data:
            print(f"   ⚠️  No API key - using fallback URLs")
            return False

        images = data.get('results', [])
        print(f"   ✅ Found {len(images)} images")

        # Download each image
        for i, img in enumerate(images[:count], 1):
            try:
                img_url = img['urls']['regular']
                filename = f"{category_name}-{i:02d}.jpg"
                filepath = category_dir / filename

                # Download image
                img_response = requests.get(img_url, timeout=15)
                img_response.raise_for_status()

                # Save image
                with open(filepath, 'wb') as f:
                    f.write(img_response.content)

                print(f"   ✅ Downloaded: {filename} ({img_response.headers.get('content-length', '?')} bytes)")
                time.sleep(0.5)  # Rate limiting

            except Exception as e:
                print(f"   ❌ Failed: {filename} - {str(e)}")
                continue

        return True

    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False

def main():
    print("=" * 70)
    print("🚀 AUTONOMOUS IMAGE DOWNLOAD SYSTEM")
    print("=" * 70)

    # Search queries for each category
    search_queries = {
        "fancy-suits": "elegant ladies fancy suits embroidered formal wear",
        "shalwar-qameez": "traditional shalwar qameez pakistani clothes women",
        "cotton-suits": "casual cotton suits comfortable ladies wear",
        "designer-brands": "premium designer brand luxury ladies fashion suits"
    }

    total_downloaded = 0

    for category, count in CATEGORIES.items():
        query = search_queries.get(category, category)
        success = download_images_for_category(category, count, query)

        # Count actual files
        category_dir = BASE_PATH / category
        actual_count = len(list(category_dir.glob("*.jpg")))
        total_downloaded += actual_count

        if actual_count > 0:
            print(f"   📊 Total in {category}: {actual_count} files")

    print("\n" + "=" * 70)
    print(f"✅ COMPLETED: {total_downloaded} images downloaded and organized")
    print("=" * 70)
    print("\n📁 Folder structure:")

    for category in CATEGORIES.keys():
        category_dir = BASE_PATH / category
        count = len(list(category_dir.glob("*.jpg")))
        print(f"   • {category}: {count} images")

    print("\n💡 Next step: Run 'python3 update_products.py' to use local images in app")

if __name__ == "__main__":
    main()
