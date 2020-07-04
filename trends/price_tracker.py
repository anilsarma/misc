from selectorlib import Extractor
import requests
import json
from time import sleep

# Create an Extractor by reading from the YAML file
e = Extractor.from_yaml_file('selectors.yaml')


def scrape(url):
    headers = {
        'dnt': '1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-user': '?1',
        'sec-fetch-dest': 'document',
        'referer': 'https://www.amazon.com/',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
    }

    # Download the page using requests
    print("Downloading %s" % url)
    r = requests.get(url, headers=headers)
    # Simple check to check if page was blocked (Usually 503)
    if r.status_code > 500:
        if "To discuss automated access to Amazon data please contact" in r.text:
            print("Page %s was blocked by Amazon. Please try using better proxies\n" % url)
        else:
            print("Page %s must have been blocked by Amazon as the status code was %d" % (url, r.status_code))
        return None
    # Pass the HTML of the page and create
    return e.extract(r.text)


def get_prices():
    # product_data = []
    result = []
    with open("asin.txt", 'r') as urllist, open('output.jsonl', 'w') as outfile:
        for asin in urllist.read().splitlines():
            data = scrape("https://www.amazon.com/dp/{}".format(asin))
            if data:
                json.dump(data, outfile)
                outfile.write("\n")
                data['ASIN'] = asin
                print(data)
                # sleep(5)
                result.append(data)

    print(result)

    import pandas as pd
    import datetime

    df = pd.DataFrame(result)
    now = pd.to_datetime(datetime.datetime.now())
    df.loc[:, 'date'] = now
    print(df)

    dirname = now.strftime("%Y%m%d")
    basename = now.strftime("%H%M%S")
    filename = "jump_rope/{}/{}.csv".format(dirname, basename)
    import os
    dirname = os.path.dirname(filename)

    if not os.path.exists(dirname):
        os.makedirs(dirname)

    df.to_csv(filename)


from apscheduler.schedulers.blocking import BlockingScheduler
get_prices()

def some_job():
    print ("Decorated job")

scheduler = BlockingScheduler()
scheduler.add_job(get_prices, 'interval', hours=1)
scheduler.start()