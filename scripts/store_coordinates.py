
def get_store_coordinates():
    """Get approximate coordinates for Williams Sonoma stores based on their locations."""
    # This is a simplified mapping - in production you'd use a geocoding service
    coordinates = {
        "ws_001": {"lat": 39.1157, "lon": -77.5636, "city": "Leesburg", "state": "VA"},
        "ws_002": {"lat": 38.8618, "lon": -77.3569, "city": "Fairfax", "state": "VA"},
        "ws_003": {"lat": 38.8618, "lon": -77.3569, "city": "Fairfax", "state": "VA"},
        "ws_004": {"lat": 30.6954, "lon": -88.0399, "city": "Mobile", "state": "AL"},
        "ws_005": {"lat": 32.7767, "lon": -96.7970, "city": "Dallas", "state": "TX"},
        "ws_006": {"lat": 30.2672, "lon": -97.7431, "city": "Austin", "state": "TX"},
        "ws_007": {"lat": 29.7604, "lon": -95.3698, "city": "Houston", "state": "TX"},
        "ws_008": {"lat": 34.0522, "lon": -118.2437, "city": "Los Angeles", "state": "CA"},
        "ws_009": {"lat": 37.7749, "lon": -122.4194, "city": "San Francisco", "state": "CA"},
        "ws_010": {"lat": 32.7157, "lon": -117.1611, "city": "San Diego", "state": "CA"},
        "ws_011": {"lat": 28.3702, "lon": -81.5182, "city": "Orlando", "state": "FL"},
        "ws_012": {"lat": 37.4436, "lon": -122.1713, "city": "Palo Alto", "state": "CA"},
        "ws_013": {"lat": 34.0722, "lon": -118.3572, "city": "Los Angeles", "state": "CA"},
        "ws_014": {"lat": 41.9103, "lon": -87.6496, "city": "Chicago", "state": "IL"},
        "ws_015": {"lat": 40.0886, "lon": -75.3941, "city": "King of Prussia", "state": "PA"},
        "ws_016": {"lat": 40.7243, "lon": -74.3279, "city": "Short Hills", "state": "NJ"},
        "ws_017": {"lat": 39.7175, "lon": -104.9536, "city": "Denver", "state": "CO"},
        "ws_018": {"lat": 47.6164, "lon": -122.2019, "city": "Bellevue", "state": "WA"},
        "ws_019": {"lat": 33.8461, "lon": -84.3633, "city": "Atlanta", "state": "GA"},
        "ws_020": {"lat": 28.4856, "lon": -81.4309, "city": "Orlando", "state": "FL"},
        "ws_021": {"lat": 32.9307, "lon": -96.8197, "city": "Dallas", "state": "TX"},
        "ws_022": {"lat": 33.5022, "lon": -111.9286, "city": "Scottsdale", "state": "AZ"},
        "ws_023": {"lat": 32.7698, "lon": -117.1664, "city": "San Diego", "state": "CA"},
        "ws_024": {"lat": 38.9174, "lon": -77.2198, "city": "Tysons", "state": "VA"},
        "ws_025": {"lat": 32.8679, "lon": -96.7738, "city": "Dallas", "state": "TX"},
    }
    return coordinates
