from pprint import pprint as print
import requests

url = 'https://bandcamp.com/api/fancollection/1/following_fans'
headers = {
    'Cookie': 'identity=7%09nLqA2egVjg7Jz%2BFUeJVefYSVlZVnUJTmVcOkrrgJkc0%3D%09%7B%22id%22%3A4131472792%2C%22ex%22%3A0%7D',
}

data = {'fan_id':'896389',"older_than_token":"1593375875:419153","count":15}
r = requests.post(url, headers=headers, json=data)
followed_fans = r.json()
followed_fans.keys() #dict_keys(['followeers', 'more_available', 'last_token'])

followeers = followed_fans["followeers"]
print(followeers[0]["is_following"])
