#!/usr/bin/env python3
"""
Update products.ts to use local images instead of Unsplash URLs
"""

import os
import re
from pathlib import Path

PRODUCTS_FILE = Path("/mnt/d/HACKATON-III/FATIMA-ZEHRA-BOUTIQUE-APP/learnflow-app/app/frontend/lib/products.ts")
IMAGES_PATH = Path("/mnt/d/HACKATON-III/FATIMA-ZEHRA-BOUTIQUE-APP/learnflow-app/app/frontend/public/images")

def get_local_image_path(category_name, image_index):
    """Get local image path for a product"""
    return f"/images/{category_name}/{category_name}-{image_index:02d}.jpg"

def count_images_in_category(category_name):
    """Count how many images are in a category folder"""
    category_dir = IMAGES_PATH / category_name
    return len(list(category_dir.glob("*.jpg")))

def main():
    print("=" * 70)
    print("📝 UPDATING PRODUCTS.TS WITH LOCAL IMAGE PATHS")
    print("=" * 70)

    # Check image counts
    categories = {
        "Fancy Suits": "fancy-suits",
        "Shalwar Qameez": "shalwar-qameez",
        "Cotton Suits": "cotton-suits",
        "Designer Brands": "designer-brands"
    }

    image_counts = {}
    for display_name, folder_name in categories.items():
        count = count_images_in_category(folder_name)
        image_counts[display_name] = count
        print(f"   📁 {display_name}: {count} images available")

    # Read products file
    with open(PRODUCTS_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    print(f"\n   📖 Reading: {PRODUCTS_FILE.name}")

    # Update images based on category and product number
    product_matches = list(re.finditer(r'image:\s*"https://images\.unsplash\.com/[^"]*"', content))
    print(f"   🔍 Found {len(product_matches)} image URLs to replace")

    replacements = 0
    product_counter = 0

    # Product mapping: products 1-10 = fancy-suits, 11-20 = shalwar-qameez, etc.
    category_ranges = [
        ("Fancy Suits", "fancy-suits", 1, 10),
        ("Shalwar Qameez", "shalwar-qameez", 11, 20),
        ("Cotton Suits", "cotton-suits", 21, 30),
        ("Designer Brands", "designer-brands", 31, 40)
    ]

    for match in product_matches:
        product_counter += 1

        # Find which category this product belongs to
        category_display = None
        category_folder = None
        image_index = None

        for disp_name, folder_name, start, end in category_ranges:
            if start <= product_counter <= end:
                category_display = disp_name
                category_folder = folder_name
                image_index = product_counter - start + 1
                break

        if category_folder and image_index:
            old_url = match.group()
            new_path = get_local_image_path(category_folder, image_index)
            new_url = f'image: "{new_path}"'

            content = content.replace(old_url, new_url, 1)
            replacements += 1

            print(f"   ✅ Product {product_counter:2d} ({category_display:15s}): → {new_path}")

    # Write updated content
    with open(PRODUCTS_FILE, 'w', encoding='utf-8') as f:
        f.write(content)

    print("\n" + "=" * 70)
    print(f"✅ COMPLETED: {replacements} image URLs updated")
    print("=" * 70)

    print("\n📊 Summary:")
    for display_name, folder_name in categories.items():
        count = count_images_in_category(folder_name)
        print(f"   • {display_name:20s}: {count}/10 images")

    print("\n💡 Next steps:")
    print("   1. Start frontend: cd learnflow-app/app/frontend && npm run dev")
    print("   2. Visit: http://localhost:3000/products")
    print("   3. Verify all images load from /public/images folder")

if __name__ == "__main__":
    main()
