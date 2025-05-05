import requests
from concord232.client.client import Client

client = Client("http://192.168.2.80:5008")
client.send_keys("*", partition=1)

# New commands (direct HTTP GETs since Client does not have wrappers)

# Request all equipment data from the panel
requests.get("http://192.168.2.80:5008/equipment")

# Request a dynamic data refresh from the panel
requests.get("http://192.168.2.80:5008/all_data")
