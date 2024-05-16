from concurrent import futures
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed, as_completed
import time
from datetime import datetime


base_url = "http://localhost:8000/"



posts = [
    "b34b1f4a",
    "7ea0c465",
    "a7acedbe",
    # "4cfb2443",
    # "c5e2667b",
    # "cca526ad",
    # "d99933ed",
    # "27811d59",
    # "71858760",
    # "520b3ac8",
    # "8c4bd618",
    # "b502c46c",
    # "d568a0b0",
    # "e5aa422f",
    # "122d511b",
    # "d360c482",
    # "fc9dfae6",
    # "3176197f",
]

players = [
    'f661fe61',
    'f661fe62',
    'f661fe63',
    'f661fe64',
    'f661fe65',
    'f661fe66',
    'f661fe67',
    'f661fe68',
    'f661fe69',
    'f661fe70',
    'f661fe71',
    'f661fe72',
    'f661fe73',
    'f661fe74',
    'f661fe75',
    'f661fe76',
    'f661fe77',
    'f661fe78',
    'f661fe79',
    'f661fe81',
    'f661fe82',
    'f661fe83',
    'f661fe84',
    'f661fe85',
    'f661fe86',
]

post_headers = []

payload = {}
headers = {
  'X-CSRFToken': 'RcHnZGZJ9S81pJXnMhfj97DBQhF7adOc',
  'Cookie': 'csrftoken=RcHnZGZJ9S81pJXnMhfj97DBQhF7adOc; sessionid=lygyzt8hgw2d36bvx01dqeo1pnpgmfmo'
}




def create_players():
    i = 0
    for player in players:
        headers = {
            "X-CSRFToken": "IbDXFhByqriHGZCD4edK9YYxFZrdOPx9",
            "Cookie": "csrftoken=IbDXFhByqriHGZCD4edK9YYxFZrdOPx9; sessionid=4vv3q6lhqnsquwwnuuglev6ku87ng6yg",
        }
        payload = {"card_uuid": player,  "name": f"Hans{i}", "section": "STH", "team": 1}
        r = requests.post(f'{base_url}register-player/', headers=headers, data=payload)
        print(r.status_code)
        if r.status_code != 200:
            print(r.text[500:10000])
            break
        i += 1

post_sessions = []

def get_post_sessions():
    for post in posts:
        s = requests.Session() 
        r = s.get(f"{base_url}post/{post}")
        for player in players:
            r = s.get(f"{base_url}player/{player}")
        print(r.cookies)
        print(r.cookies['sessionid'])
        s.headers = {
            "X-CSRFToken": "IbDXFhByqriHGZCD4edK9YYxFZrdOPx9",
            "Cookie": f"csrftoken=IbDXFhByqriHGZCD4edK9YYxFZrdOPx9; sessionid={r.cookies['sessionid']}",
        }
        post_sessions.append(s)


def test_posts():
    for ses in post_sessions:
        for player in players:
            r = ses.get(f"{base_url}player/{player}")
            payload = {"amount": 1}
            r = ses.post(f"{base_url}player/{player}", data=payload)
            print(r.status_code)
            if r.status_code != 200:
                print(r.text[500:10000])
                exit()


# create_players()
get_post_sessions()
# test_posts()


def send_request(post, player):
    start_time = time.time()

    # r = post.get(f"{base_url}player/{player}")

    payload = {"amount": 1}
    r = post.post(f"{base_url}player/{player}", data=payload)

    if r.status_code != 200:
        print(r.text[500:1000])
        exit()

    if "error" in r.text:
        print(r.text)

    end_time = time.time()
    return start_time, end_time, r

NUM_REQUESTS = 2
REPEATS = 10

with ThreadPoolExecutor(max_workers=NUM_REQUESTS) as executor:
    futures = []
    for _ in range(REPEATS):
        for post in post_sessions:
            for player in players:
                futures.append(executor.submit(send_request, post, player))

    for future in as_completed(futures):
        try:
            start_time, end_time, result = future.result()
            st_time = datetime.fromtimestamp(start_time).strftime('%H:%M:%S:%MS')
            en_time = datetime.fromtimestamp(end_time).strftime('%H:%M:%S:%MS')
            print(end_time - start_time, result.status_code)
        except Exception as e:
            print(f"Request failed {e}")



