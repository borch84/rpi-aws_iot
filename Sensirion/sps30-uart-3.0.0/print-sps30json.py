import json

with open('sps30.json', 'r') as f:
    array = json.load(f)
f.close()
print (array)
