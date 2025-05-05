from concord232.client.client import Client

client = Client("http://192.168.4.180:5007")
client.send_keys("*", partition=3)