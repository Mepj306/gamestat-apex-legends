import os
import requests
from dotenv import load_dotenv


load_dotenv()

API_KEY = os.getenv("API_KEY")
URL = "https://api.mozambiquehe.re/bridge?"


if not API_KEY:

        print("Error: Environment variables 'API_KEY' must be set.")
        exit()

headers = {
       "Authorization": API_KEY
       
}

params = {
    "platform": "PC",                 
    "player": "Pagano94"  
}



def fetch_player_stats(URL, headers, params):
            response = requests.get(URL, headers=headers, params=params)
            response.raise_for_status()
            print(f"Status Code: {response.status_code}")
            return response.json() 

def get_data():

        try: 
                return fetch_player_stats(URL, headers, params)
        except Exception as e:
                print(f"Error fetching API data {e}")
                return None

if __name__ == '__main__':

        try:
       
                data = fetch_player_stats(URL, headers, params)
                print(data)
                all_legends = data['legends']['all']
                chosen_legend = input("Write the legend name (e.g., Pathfinder): ")
                chosen_stat = input("What stat are we looking for? (use the item KEY)")

                legend_data = all_legends[chosen_legend]

                stat_list = legend_data.get('data', [])
                data_found = None
     
                for stat_entry in stat_list:
                        if stat_entry.get('key') == chosen_stat:
                                data_found = stat_entry['value']
                                stat_name = stat_entry.get('name', chosen_stat)
                                break
                if data_found is not None:
                        print(f"\n{chosen_legend}'s {stat_name} is {data_found}")
                else:
                        print(f"\n Stat with key '{chosen_stat}' not found for {chosen_legend}, or {chosen_legend} has no stat data.")
        except KeyError:
                print(f"\n Error: Legend {chosen_legend} was not found. Check your spelling.")

        except requests.exceptions.HTTPError as e:
                print(f"HTTP Error: {e}")
        except requests.exceptions.RequestException as e:
                print("API call failed: {e}")

                
 