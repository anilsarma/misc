# gcloud functions deploy get_snapshot --entry-point get_snapshot --runtime python37 --trigger-http --allow-unauthenticated
import datetime

import pandas as pd
import requests
from apscheduler.schedulers.blocking import BlockingScheduler
from bs4 import BeautifulSoup as bs
from dateutil.tz import tzlocal


def now():
    dt = pd.Timestamp(datetime.datetime.now())
    dt = dt.tz_localize(tzlocal()).tz_convert("US/Eastern").tz_localize(None)
    return dt


import re

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
    'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8'
}

header2 = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'max-age=0',
    'dnt': '1',
    'downlink': '10',
    'ect': '4g',
    'rtt': '50',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'
}


def download_file(asin):
    url = "https://www.amazon.com/dp/{}".format(asin)
    with requests.session() as s:
        # response_post = s.post(url, data=payload)
        response_post = s.get(url, headers=header2)
        # print response_post.text
        soup = bs(response_post.text, 'html.parser')
        print(now(), "received response ", asin)
        good = False
        data = {}
        for i, li in enumerate(soup.findAll('li')):
            id = li.get('id')
            if id is None:
                continue
            if id == "SalesRank":
                # print(li)
                pat = re.compile("#(.+?) in (.+?)\(")
                m = pat.findall(str(li))
                if m is None or len(m) != 1:
                   continue
                (rank, group) = m[0]

                rank = rank.replace(",", "")
                data['rank'] = rank
                data['group'] = group
                break
        if not data:
            for i, li in enumerate(soup.findAll('span')):
                v = str(li)
                if 'bestsellers' in v:
                    pat = re.compile("#(.+?) in (.+?)\(")
                    m = pat.findall(str(li))
                    if m is None or len(m) != 1:
                        continue
                    (rank, group) = m[0]

                    rank = rank.replace(",", "")
                    data['rank'] = rank
                    data['group'] = group
                    break
        if not data:
            print(now(), "seller rank details not found for ", asin)

        # go through the anchors in the page and find the one we want.
        for i, div in enumerate(soup.findAll('div')):
            _FULLURL = div.get('id')
            if _FULLURL is None:
                continue
            # id
            # style
            # data-asin
            # data-asin-price
            # data-asin-shipping
            # data-asin-currency-code
            # data-substitute-count
            # data-device-type
            # data-display-code

            if 'cerberus-data-metrics' in _FULLURL:
                # print now(), (_FULLURL)
                print(now(), "found the download link", div)
                good = True

                for x in div.attrs:
                    # print(x)
                    data[x] = div.get(x)
                return data

        if not good:
            with open("error_{}.html".format(asin), "w") as fp:
                print("soup", str(soup))
                try:
                    fp.write(str(soup))
                except:
                    try:
                        fp.write(str(soup).decode("utf-8"))
                    except:
                        print(now(), "write failed for ", asin)

            print("we did not get a valid response from the server or the server has changed.")
    return None


import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import random

cred = None


def save_data(asins):
    # Use the application default credentials
    # cred = credentials.ApplicationDefault()
    global cred
    try:
        cred = credentials.Certificate("timetransform-e722a-firebase-adminsdk-yqj1h-51ca067f21.json")
        firebase_admin.initialize_app(cred)
    except:
        pass

    saved = []
    db = firestore.client()
    import time

    # for asin in ["B07G2DFZZG"]:
    for asin in asins:
        for i in range(0, 5):
            data = download_file(asin)
            if data is None:
                r = random.random()
                print(r, asin)
                time.sleep((random.random() + 1) * 5 * i)
            else:
                break

        if data is None:
            print("unable to retrieve {}".format(asin))
            time.sleep(5)
            continue

        time.sleep(1 + random.random())
        dt = now()
        data['date'] = str(dt)
        data['asin'] = asin
        doc = db.collection("amazon").document("ASINDB").collection(asin.upper()).document(str(dt))
        doc.set(data)
        print(now(), data)
        saved.append(asin)
    return saved


import traceback


def get_snapshot(request):
    """HTTP Cloud Function.
    Args:
        request (flask.Request): The request object.
        <http://flask.pocoo.org/docs/1.0/api/#flask.Request>
    Returns:
        The response text, or any set of values that can be turned into a
        Response object using `make_response`
        <http://flask.pocoo.org/docs/1.0/api/#flask.Flask.make_response>.
    """
    try:
        request_json = request.get_json(silent=True)
        request_args = request.args

        if request_json and 'asin' in request_json:
            asin = request_json['asin'].split(",")
        elif request_args and 'asin' in request_args:
            asin = request_args['asin'].split(",")
        else:
            asin = None
        if asin is None:
            return "NO Work"
        # return 'Hello {}!'.format(escape(name))
        r = save_data(list(set(asin)))
        return "done " + " ".join(r)
    except:
        import io
        strs = io.StringIO()
        traceback.print_exc(file=strs)
        return str(strs.getvalue())


if __name__ == "__main__":
    def get_prices():
        df = pd.read_csv("asin.txt")
        asins = list(df.asin.drop_duplicates())
        # asins = asins[]
        t0 = now()
        for i in range(0, 5):
            random.shuffle(asins)
            print(asins)
        save_data(asins)
        print(tzlocal())
        print(now())
        print(now(), "round complete started ", t0, now()-t0)
        #3save_data( ["B088RCZZLM"])


    get_prices()
    scheduler = BlockingScheduler()
    scheduler.add_job(get_prices, 'interval', hours=1)
    scheduler.start()