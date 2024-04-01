import requests
from pymongo import MongoClient

def parse(data, service):
    parsed = []
    
    if isinstance(data, dict):
        if service == "glovo" and all(key in data for key in ("name", "primeAvailable", "slug", "serviceFee")):
            parsed.append({
                "name": data["name"],
                "services": [{
                    "name": "Glovo",
                    "link": "https://glovoapp.com/rs/en/novi-sad/" + data["slug"],
                    "price": "{:.2f}".format(data["serviceFee"]),
                    "free_delivery": data["primeAvailable"]
                }]
            })
        elif service == "wolt" and all(key in data for key in ("name", "show_wolt_plus", "slug", "delivery_price_int")):
            parsed.append({
                "name": data["name"],
                "services": [{
                    "name": "Wolt",
                    "link": "https://wolt.com/en/srb/novi_sad/restaurant/" + data["slug"],
                    "price": "{:.2f}".format(float(data["delivery_price_int"]) / 100),
                    "free_delivery": data["show_wolt_plus"]
                }]
            })
        elif service == "misterd" and all(key in data for key in ("name", "slug", "originalDeliveryCost")):
            parsed.append({
                "name": data["name"],
                "services": [{
                    "name": "MisterD",
                    "link": "https://misterd.rs/place/" + data["slug"],
                    "price": "{:.2f}".format(float(data["originalDeliveryCost"])),
                    "free_delivery": False
                }]
            })        

        for value in data.values():
            parsed.extend(parse(value, service))
            
    elif isinstance(data, list):
        for item in data:
            parsed.extend(parse(item, service))
    
    return parsed

def merge(data_list):
    combined_data = [item for sublist in data_list for item in sublist]
    merged_data = {}

    for item in combined_data:
        name = item['name'].lower()
        if name in merged_data:
            existing_services = [service['name'] for service in merged_data[name]['services']]
            for service in item['services']:
                if service['name'] not in existing_services:
                    merged_data[name]['services'].append(service)
        else:
            merged_data[name] = item

    merged_list = list(merged_data.values())

    return merged_list

def db_insert(data):
    client = MongoClient('mongodb://localhost:27017/')
    db = client['dostava_detektiv']
    restaurants_collection = db['restaurants']
    restaurants_collection.drop()
    restaurants_collection.insert_many(data)

def get_data():
    wolt = {
        'url': 'https://consumer-api.wolt.com/v1/pages/restaurants',
        'params': {
            'lat': '45.252317',
            'lon': '19.8335496',
        },
        'headers': {
            'Authorization': 'Bearer eyJhbGciOiJFUzI1NiIsImtpZCI6IjY1ZmNkOTg2MDAwMDAwMDAwMDAwMDAwMCIsInR5cCI6IngudXNlcitqd3QifQ.eyJhdWQiOlsiY29uc3VtZXItYXNzb3J0bWVudCIsImxveWFsdHktcHJvZ3JhbS1hcGkiLCJpbnRlZ3JhdGlvbi1jb25maWctc2VydmljZSIsInBheW1lbnRzLXRpcHMtc2VydmljZSIsImNvcnBvcmF0ZS1wb3J0YWwtYXBpIiwidG9wdXAtc2VydmljZSIsInBheW1lbnQtc2VydmljZSIsImFkLWluc2lnaHRzIiwib3JkZXIteHAiLCJyZXR1cm5zLWFwaSIsImxveWFsdHktZ2F0ZXdheSIsInJlc3RhdXJhbnQtYXBpIiwiY291cmllcmNsaWVudCIsInN1cHBvcnQtZnVubmVsIiwidmVudWUtY29udGVudC1hcGkiLCJ3b2x0YXV0aCIsIm9yZGVyLXRyYWNraW5nIiwiY29udmVyc2Utd2lkZ2V0LWNvbnN1bWVyIl0sImlzcyI6IndvbHRhdXRoIiwianRpIjoiN2FkOTRiZjZmMDFhMTFlZWIzYjIxMjY1YjgyMTQ0ZjMiLCJ1c2VyIjp7ImlkIjoiNWRlZTE0MTBjMTRkMjcyMDhkOGYyZTc4IiwibmFtZSI6eyJmaXJzdF9uYW1lIjoiTmlrb2xhIiwibGFzdF9uYW1lIjoiRHJhZ29taXJvdmljIn0sImVtYWlsIjoibmlrb2xhZHJhZ29taXJvdmljQGljbG91ZC5jb20iLCJyb2xlcyI6WyJ1c2VyIl0sImVtYWlsX3ZlcmlmaWVkIjp0cnVlLCJwaG9uZV9udW1iZXJfdmVyaWZpZWQiOnRydWUsImNvdW50cnkiOiJTUkIiLCJsYW5ndWFnZSI6ImVuIiwicGVybWlzc2lvbnMiOltdLCJwaG9uZV9udW1iZXIiOiIrMzgxNjEyMTE4ODc3In0sImlhdCI6MTcxMTk3MDcwMSwiZXhwIjoxNzExOTcyNTAxLCJhbXIiOlsiZW1haWwiXX0.XdbRgESpRe1eTp7zqdbp6gYw1ez1H73T-tJQ9dABffANPMP8Do2wOe604-CA0Z7A2vgdDUqslT8JS4G6kAO9Vg'
        }
    }

    glovo = {
        'url': 'https://api.glovoapp.com/v3/feeds/categories/1',
        'headers': {
            'Glovo-Delivery-Location-Longitude': '19.8335496',
            'Glovo-Delivery-Location-Latitude': '45.252317',
            'Glovo-Location-City-Code': 'QND',
            'Glovo-Delivery-Location-Timestamp': '1711636608028',
            'Glovo-Delivery-Location-Accuracy': '0',
            'Glovo-App-Platform': 'web'
        }
    }

    misterd = {
        'url': 'https://api.mrdonesi.com/api/public/store/explore-v3',
        'params': {
            'lat': '45.252317',
            'lng': '19.8335496',
        },
        'headers': {
            
        }
    }

    glovo_response = requests.get(glovo['url'], headers=glovo["headers"])
    glovo_data = glovo_response.json()

    wolt_response = requests.get(wolt["url"], params=wolt["params"], headers=wolt["headers"])
    wolt_data = wolt_response.json()

    misterd_response = requests.get(misterd['url'], params=misterd['params'])
    misterd_data = misterd_response.json()

    glovo_parsed_data = parse(glovo_data, "glovo")
    wolt_parsed_data = parse(wolt_data, "wolt")
    misterd_parsed_data = parse(misterd_data, "misterd")

    output_data = merge([glovo_parsed_data, wolt_parsed_data, misterd_parsed_data])

    return output_data

db_insert(get_data())
