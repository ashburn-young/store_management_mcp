import json
import random
from datetime import datetime, timedelta
import os

# Define paths
current_path = os.path.dirname(os.path.abspath(__file__))
parent_path = os.path.dirname(current_path)
data_path = os.path.join(parent_path, "data")
stores_file = os.path.join(data_path, "williams_sonoma_stores.json")

# Load existing stores
with open(stores_file, 'r') as f:
    existing_stores = json.load(f)

# Extract existing store IDs to avoid duplicates
existing_ids = set()
existing_addresses = set()
for store in existing_stores:
    existing_ids.add(store["store_id"])
    existing_addresses.add(store["address"].lower())

# New store data
new_stores = [
    {
        "name": "Williams Sonoma - Disney Springs",
        "address": "1620 E Buena Vista Dr, Lake Buena Vista, FL 32830",
        "phone": "(407) 938-9080",
        "category": "Cookware & Kitchen",
        "services": ["In-Store Pickup", "Store Events", "Knife Sharpening", "Gift Registry", "Personal Shopping"],
        "store_number": "#6230"
    },
    {
        "name": "Williams Sonoma - Stanford Shopping Center",
        "address": "180 El Camino Real, Palo Alto, CA 94304",
        "phone": "(650) 321-3486",
        "category": "Cookware & Kitchen",
        "services": ["In-Store Pickup", "Store Events", "Knife Sharpening", "Cooking Classes", "Gift Registry"],
        "store_number": "#6125"
    },
    {
        "name": "Williams Sonoma - The Grove",
        "address": "189 The Grove Dr, Los Angeles, CA 90036",
        "phone": "(323) 954-9220",
        "category": "Cookware & Kitchen",
        "services": ["In-Store Pickup", "Store Events", "Knife Sharpening", "Cooking Classes", "Gift Registry", "Personal Shopping"],
        "store_number": "#6108"
    },
    {
        "name": "Williams Sonoma - Lincoln Park",
        "address": "1550 N Fremont St, Chicago, IL 60622",
        "phone": "(312) 255-0643",
        "category": "Cookware & Kitchen",
        "services": ["In-Store Pickup", "Store Events", "Knife Sharpening", "Gift Registry"],
        "store_number": "#6182"
    },
    {
        "name": "Williams Sonoma - King of Prussia",
        "address": "160 N Gulph Rd, King of Prussia, PA 19406",
        "phone": "(610) 265-5970",
        "category": "Cookware & Kitchen",
        "services": ["In-Store Pickup", "Store Events", "Knife Sharpening", "Gift Registry", "Personal Shopping"],
        "store_number": "#6315"
    },
    {
        "name": "Williams Sonoma - Short Hills",
        "address": "1200 Morris Turnpike, Short Hills, NJ 07078",
        "phone": "(973) 467-3641",
        "category": "Cookware & Kitchen",
        "services": ["In-Store Pickup", "Store Events", "Knife Sharpening", "Cooking Classes", "Gift Registry"],
        "store_number": "#6210"
    },
    {
        "name": "Williams Sonoma - Cherry Creek",
        "address": "3000 E 1st Ave, Denver, CO 80206",
        "phone": "(303) 394-2662",
        "category": "Cookware & Kitchen",
        "services": ["In-Store Pickup", "Store Events", "Knife Sharpening", "Gift Registry", "Design Services"],
        "store_number": "#6250"
    },
    {
        "name": "Williams Sonoma - Bellevue Square",
        "address": "221 Bellevue Square, Bellevue, WA 98004",
        "phone": "(425) 454-0020",
        "category": "Cookware & Kitchen",
        "services": ["In-Store Pickup", "Store Events", "Knife Sharpening", "Cooking Classes", "Gift Registry"],
        "store_number": "#6295"
    },
    {
        "name": "Williams Sonoma - Lenox Square",
        "address": "3393 Peachtree Rd NE, Atlanta, GA 30326",
        "phone": "(404) 812-1703",
        "category": "Cookware & Kitchen",
        "services": ["In-Store Pickup", "Store Events", "Knife Sharpening", "Gift Registry", "Personal Shopping"],
        "store_number": "#6145"
    },
    {
        "name": "Williams Sonoma - The Mall at Millenia",
        "address": "4200 Conroy Rd, Orlando, FL 32839",
        "phone": "(407) 226-7575",
        "category": "Cookware & Kitchen",
        "services": ["In-Store Pickup", "Store Events", "Knife Sharpening", "Gift Registry", "Design Services"],
        "store_number": "#6235"
    },
    {
        "name": "Williams Sonoma - Galleria Dallas",
        "address": "13350 Dallas Pkwy, Dallas, TX 75240",
        "phone": "(972) 450-9560",
        "category": "Cookware & Kitchen",
        "services": ["Store Events", "Knife Sharpening", "Gift Registry", "Personal Shopping"],
        "store_number": "#6150"
    },
    {
        "name": "Williams Sonoma - Scottsdale Fashion Square",
        "address": "7014 E Camelback Rd, Scottsdale, AZ 85251",
        "phone": "(480) 425-7912",
        "category": "Cookware & Kitchen",
        "services": ["In-Store Pickup", "Store Events", "Knife Sharpening", "Cooking Classes", "Gift Registry"],
        "store_number": "#6228"
    },
    {
        "name": "Williams Sonoma - Fashion Valley",
        "address": "7007 Friars Rd, San Diego, CA 92108",
        "phone": "(619) 295-0643",
        "category": "Cookware & Kitchen",
        "services": ["In-Store Pickup", "Store Events", "Knife Sharpening", "Gift Registry", "Personal Shopping"],
        "store_number": "#6110"
    },
    {
        "name": "Williams Sonoma - Tysons Corner Center",
        "address": "1961 Chain Bridge Rd, Tysons Corner, VA 22102",
        "phone": "(703) 288-1115",
        "category": "Cookware & Kitchen",
        "services": ["In-Store Pickup", "Store Events", "Knife Sharpening", "Gift Registry", "Design Services"],
        "store_number": "#6216"
    },
    {
        "name": "Williams Sonoma - NorthPark Center",
        "address": "8687 N Central Expy, Dallas, TX 75225",
        "phone": "(214) 378-6216",
        "category": "Cookware & Kitchen",
        "services": ["In-Store Pickup", "Store Events", "Knife Sharpening", "Cooking Classes", "Gift Registry"],
        "store_number": "#6152"
    }
]

# Generate random but plausible store data
def generate_random_date(start_year=2012, end_year=2021):
    start_date = datetime(start_year, 1, 1)
    end_date = datetime(end_year, 12, 31)
    days_between = (end_date - start_date).days
    random_days = random.randint(0, days_between)
    random_date = start_date + timedelta(days=random_days)
    return random_date.strftime("%Y-%m-%d")

# Process new stores
processed_stores = []
for i, store_data in enumerate(new_stores):
    # Skip if the address already exists (case-insensitive comparison)
    if store_data["address"].lower() in existing_addresses:
        print(f"Skipping duplicate address: {store_data['address']}")
        continue
    
    # Generate next available store ID
    next_id = 11  # Start from the next ID after the existing ones
    while f"ws_{next_id:03d}" in existing_ids:
        next_id += 1
    
    store_id = f"ws_{next_id:03d}"
    existing_ids.add(store_id)
    existing_addresses.add(store_data["address"].lower())
    
    # Create full store entry
    full_store = {
        "store_id": store_id,
        "name": store_data["name"],
        "address": store_data["address"],
        "phone": store_data["phone"],
        "manager": random.choice([
            "Michael Johnson", "Jessica Williams", "David Thompson", 
            "Amanda Brown", "Christopher Davis", "Elizabeth Miller",
            "Matthew Wilson", "Stephanie Taylor", "Jonathan Anderson",
            "Rebecca Martinez", "Brandon Thomas", "Melissa Jackson"
        ]),
        "category": store_data["category"],
        "opening_date": generate_random_date(),
        "square_footage": random.choice([3200, 3500, 3800, 4000, 4200, 4500, 4800, 5000, 5500]),
        "employee_count": random.randint(16, 30),
        "services": store_data["services"],
        "store_number": store_data["store_number"]
    }
    
    processed_stores.append(full_store)
    print(f"Added new store: {full_store['name']}")

# Combine existing and new stores
updated_stores = existing_stores + processed_stores

# Save updated data
with open(stores_file, 'w') as f:
    json.dump(updated_stores, f, indent=2)

print(f"Updated Williams Sonoma store data: {len(existing_stores)} existing + {len(processed_stores)} new = {len(updated_stores)} total stores")
