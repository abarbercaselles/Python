Asynchronous execution for improving performance is easier to implement with threads(concurrent.futures library) than with (asyncio library).
Also you cannot use requests library nested with asyncio because requests is a synchronous module(aiohttp is used instead),
so at the end it ends that if you are using requests library, a good option would be using threads for the asynchronous part.
 
Bear in mind that some APIs won't let you make that many requests in such a short time
```
requests.exceptions.ConnectionError: ERROR 443: Max retries exceeded with url...
```
so async/threading could be useful for the APIs that would allow lot of requests/second, otherwise the script can collapse because too many simultaneous requests in such a short period of time
 
# ASYNCIO
 
https://python.plainenglish.io/how-i-decreased-api-response-time-by-89-30-in-python-7057d20f6aef
DECREASE API RESPONSE TIME
 
 
# CONCURRENT.FUTURES
 
A way to improve the API response time would be using Threads -> using concurrent.futures library. Here an example:
```
import concurrent.futures
import requests

def list_all_campaigns(account_id):
    url = f"https://api.criteo.com/preview/retail-media/accounts/{​​​account_id}​​​​​​​​​​/campaigns"
    response = requests.get(url)
    return response

def list_all_campaign_responses():
    list_campaigns_responses = []
    accounts = ['7894546','54859845','45894585']
    with concurrent.futures.ThreadPoolExecutor() as executor:
        for campaigns in executor.map(list_all_campaigns, accounts):
            list_campaigns_responses.append(campaigns)
    return campaigns

list_all_campaign_responses()
```
executor.map would take as an arguments :
 
list_all_campaigns -> the targeted function 
accounts -> A list of accounts_id that would be passed as an argument to 'list_all_campaigns' function
 
Another example explained with executor.submit: https://www.youtube.com/watch?v=IEEhzQoKtQU
