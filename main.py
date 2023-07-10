import json
from datetime import date
import os

current_date = date.today()
print(current_date)

year = str(current_date.year)
path = 'storage/data/' + year

os.makedirs(path)
filename = f'{str(current_date.month)}.json'
file_path = os.path.join(path, filename)

data = {'error': 'Hello'}

with open(file_path, 'w') as file:
    json.dump(data, file)