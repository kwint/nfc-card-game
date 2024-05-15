from concurrent import futures
import requests
from concurrent.futures import ThreadPoolExecutor
import time
from datetime import datetime


base_url = "http://localhost:8000/"



posts = [""]
posts = [
    # "e4b160ea",
    # "4e8d2605",
    # "258dfc9a",
    # "71779efc",
    # "adbb16b1",
    # "6c3d2237",
    # "25caba4f",
    # "eb67f3ba",
    # "db7e4760",
    # "9795a481",
    # "92a9314c",
    # "827c62e0",
    # "fcff0863",
    # "57972536",
    # "69fed407",
    # "207b98b0",
    # "35c458b4",
    "da71cb86",
]


players = [
    'f661fe61',
    'f661fe62',
    'f661fe63',
    'f661fe64',
    'f661fe65',
]

post_headers = []

payload = {}
headers = {
  'X-CSRFToken': 'RcHnZGZJ9S81pJXnMhfj97DBQhF7adOc',
  'Cookie': 'csrftoken=RcHnZGZJ9S81pJXnMhfj97DBQhF7adOc; sessionid=lygyzt8hgw2d36bvx01dqeo1pnpgmfmo'
}


num_requests = 20


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
        post_sessions.append(s)


def test_posts():
    for ses in post_sessions:
        for player in players:
            r = ses.get(f"{base_url}player/{player}")
            print(r.status_code)
            if r.status_code != 200:
                print(r.text[500:10000])




# create_players()
get_post_sessions()
test_posts()


    

def get_session_key(url):
    session = requests.Session()
    response = session.get(url)
    return session.cookies.get('sessionid')


def send_request(url, headers, payload):
    start_time = time.time()
    response = requests.post(url, headers=headers, data=payload)
    end_time = time.time()
    return start_time, end_time, response

exit()
for post in posts:
    s = requests.Session()
    u = f'{base_url}post/{post}'
    r = s.get(u)
    h = {'Cookie': f'csrftoken={headers["X-CSRFToken"]}; sessionid={s.cookies.get("sessionid")}', 'X-CSRFToken': 'RcHnZGZJ9S81pJXnMhfj97DBQhF7adOc'}
    post_headers.append(h)

print(post_headers[0])

start_time, end_time, result = send_request(f'{base_url}player/00cf0e42', post_headers[0], payload)
print(result.status_code)
exit()

with ThreadPoolExecutor(max_workers=num_requests) as executor:
    futures = [executor.submit(send_request, f'{base_url}player/00cf0e42' , post_headers[x % len(posts)], payload) for x in range(num_requests)]

    for future in futures:
        start_time, end_time, result = future.result()
        st_time = datetime.fromtimestamp(start_time).strftime('%H:%M:%S:%MS')
        end_time = datetime.fromtimestamp(end_time).strftime('%H:%M:%S:%MS')
        print(st_time, end_time, result.status_code)



