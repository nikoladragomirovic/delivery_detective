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
            'Authorization': 'Bearer eyJhbGciOiJFUzI1NiIsImtpZCI6IjY1ZjM5MGY3MDAwMDAwMDAwMDAwMDAwMCIsInR5cCI6IngudXNlcitqd3QifQ.eyJhdWQiOlsiY29ycG9yYXRlLXBvcnRhbC1hcGkiLCJyZXR1cm5zLWFwaSIsImNvdXJpZXJjbGllbnQiLCJwYXltZW50cy10aXBzLXNlcnZpY2UiLCJvcmRlci10cmFja2luZyIsImNvbnN1bWVyLWFzc29ydG1lbnQiLCJzdXBwb3J0LWZ1bm5lbCIsInJlc3RhdXJhbnQtYXBpIiwidG9wdXAtc2VydmljZSIsImludGVncmF0aW9uLWNvbmZpZy1zZXJ2aWNlIiwid29sdGF1dGgiLCJjb252ZXJzZS13aWRnZXQtY29uc3VtZXIiLCJhZC1pbnNpZ2h0cyIsInBheW1lbnQtc2VydmljZSIsInZlbnVlLWNvbnRlbnQtYXBpIiwibG95YWx0eS1nYXRld2F5IiwibG95YWx0eS1wcm9ncmFtLWFwaSIsIm9yZGVyLXhwIl0sImlzcyI6IndvbHRhdXRoIiwianRpIjoiZDZhNDliNGNlZDUwMTFlZTliZmM5NmQ2MjgxMTM2ODMiLCJ1c2VyIjp7ImlkIjoiNWRlZTE0MTBjMTRkMjcyMDhkOGYyZTc4IiwibmFtZSI6eyJmaXJzdF9uYW1lIjoiTmlrb2xhIiwibGFzdF9uYW1lIjoiRHJhZ29taXJvdmljIn0sImVtYWlsIjoibmlrb2xhZHJhZ29taXJvdmljQGljbG91ZC5jb20iLCJyb2xlcyI6WyJ1c2VyIl0sImVtYWlsX3ZlcmlmaWVkIjp0cnVlLCJwaG9uZV9udW1iZXJfdmVyaWZpZWQiOnRydWUsImNvdW50cnkiOiJTUkIiLCJsYW5ndWFnZSI6ImVuIiwicGVybWlzc2lvbnMiOltdLCJwaG9uZV9udW1iZXIiOiIrMzgxNjEyMTE4ODc3In0sImlhdCI6MTcxMTY2NDE5NCwiZXhwIjoxNzExNjY1OTk0LCJhbXIiOlsiZW1haWwiXX0.imQaTp-jgElAJFh0UxEFkHHYhq9yzr-siCvzlvEPrnXURDvFuwnv9f0Jr0p3pIq2U9XHB-ih61d802LppFn-BQ'
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

    glovo_response = requests.get(glovo['url'], headers=glovo["headers"])
    glovo_data = glovo_response.json()

    wolt_response = requests.get(wolt["url"], params=wolt["params"], headers=wolt["headers"])
    wolt_data = wolt_response.json()

    glovo_parsed_data = parse(glovo_data, "glovo")
    wolt_parsed_data = parse(wolt_data, "wolt")

    output_data = merge([glovo_parsed_data, wolt_parsed_data])

    return output_data

db_insert(get_data())
