import requests
from pymongo import MongoClient

def parse(data, service):
    parsed = []
    if isinstance(data, dict):
        if service == "glovo":
            if "name" in data and "primeAvailable" in data:
                if data["primeAvailable"]:
                    parsed.append({"name": data["name"], "service": ["Glovo"], "free_delivery": ["Glovo"]})
                else:
                    parsed.append({"name": data["name"], "service": ["Glovo"], "free_delivery": []})
        elif service == "wolt":
            if "name" in data and "show_wolt_plus" in data:
                if data["show_wolt_plus"]:
                    parsed.append({"name": data["name"], "service": ["Wolt"], "free_delivery": ["Wolt"]})
                else:
                    parsed.append({"name": data["name"], "service": ["Wolt"], "free_delivery": []})
        for value in data.values():
            parsed.extend(parse(value, service))
    elif isinstance(data, list):
        for item in data:
            parsed.extend(parse(item, service)) 
    return parsed

def merge(glovo_data, wolt_data):
    combined_data = glovo_data + wolt_data
    merged_data = {}

    for item in combined_data:
        name = item['name'].lower()
        if name in merged_data:
            merged_data[name]['service'].extend(item['service'])
            merged_data[name]['free_delivery'].extend(item['free_delivery'])
        else:
            merged_data[name] = item

    for name, data in merged_data.items():
        data['service'] = list(set(data['service']))

    merged_list = list(merged_data.values())

    return merged_list

def db_insert(data):
    client = MongoClient('mongodb://localhost:27017/')
    db = client['dostava_detektiv']
    restaurants_collection = db['restaurants']
    restaurants_collection.drop()
    restaurants_collection.insert_many(data)

glovo_url = 'https://api.glovoapp.com/v3/feeds/categories/1'
wolt_url = 'https://consumer-api.wolt.com/v1/pages/restaurants'

glovo_headers = {
    'Glovo-Delivery-Location-Longitude': '19.8467405',
    'Glovo-Delivery-Location-Latitude': '45.26694579999999',
    'Glovo-Location-City-Code': 'QND',
    'Glovo-Delivery-Location-Timestamp': '1711636608028',
    'Glovo-Delivery-Location-Accuracy': '0'

}

wolt_params = {
    'lat': '45.26702450882689',
    'lon': '19.846813157200813',
}

glovo_response = requests.get(glovo_url, headers=glovo_headers)
glovo_data = glovo_response.json()

wolt_response = requests.get(wolt_url, params=wolt_params)
wolt_data = wolt_response.json()

glovo_parsed_data = parse(glovo_data, "glovo")
wolt_parsed_data = parse(wolt_data, "wolt")

output_data = merge(glovo_parsed_data, wolt_parsed_data)

db_insert(output_data)