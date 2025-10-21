import os
import requests
from dotenv import load_dotenv


load_dotenv()

API_KEY = os.getenv("APEX_API_KEY")
URL = "https://api.mozambiquehe.re/bridge?"


if not API_KEY:

        print("Error: Environment variables 'APEX_API_KEY' must be set.")
        exit()

headers = {
       "Authorization": API_KEY
       
}

params = {
    "platform": "PC",                 
    "player": "ItzPagano94"  
}

def fetch_player_stats(URL, headers, params):
            response = requests.get(URL, headers=headers, params=params)
            response.raise_for_status()
            print(f"Status Code: {response.status_code}")
            return response.json() 

try:
       
        data = fetch_player_stats(URL, headers, params)
        print("Request successful!")
        print("--- Player Data ---")
        if 'Pathfinder' in data:
                print(f"Values for 'Pathfinder': {data['Legends']}")
        else:
                print(data)

except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
except requests.exceptions.RequestException as e:
        print("API call failed: {e}")

        