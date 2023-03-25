import requests

url = 'https://bandcamp.com/uncollect_item_cb'
headers = {
    'Cookie': 'identity=7%09nLqA2egVjg7Jz%2BFUeJVefYSVlZVnUJTmVcOkrrgJkc0%3D%09%7B%22id%22%3A4131472792%2C%22ex%22%3A0%7D',
    'Origin': 'https://bandcamp.com',
}
band_id = 857243381
item_type = "track"
item_id = 310533014
fan_id = 896389
data=f'fan_id={fan_id}&item_id={item_id}&item_type={item_type}&band_id={band_id}&crumb=%7Cuncollect_item_cb%7C1672197053%7CCGndMQKhUy2rj4LvTXZZX43fKRI%3D'
r = requests.post(url, headers=headers, data=data)
print(r.text)
#print(r.json())

url = 'https://bandcamp.com/collect_item_cb'
data = f'fan_id={fan_id}&item_id={item_id}&item_type={item_type}&band_id={band_id}&crumb=%7Ccollect_item_cb%7C1672197010%7CAZLodJjWq5I9yB7osNWWSZal1lk%3D'
r = requests.post(url, headers=headers, data=data)
print(r.text)
#print(r.json())
