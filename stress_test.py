from concurrent import futures
import requests
from concurrent.futures import ThreadPoolExecutor
import time
from datetime import datetime


base_url = "https://nfc.blankwaard.eu/"



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
    "87b229e8",
]

post_headers = []

payload = {}
headers = {
  'X-CSRFToken': 'RcHnZGZJ9S81pJXnMhfj97DBQhF7adOc',
  'Cookie': 'csrftoken=RcHnZGZJ9S81pJXnMhfj97DBQhF7adOc; sessionid=lygyzt8hgw2d36bvx01dqeo1pnpgmfmo'
}


num_requests = 20




def test_single_post():
    session = requests.Session()
    response = session.get(base_url)  # create session_id
    print(response.text)
    r = session.get(base_url) # get random post id



test_single_post()


    

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



