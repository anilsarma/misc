import datetime
import html
import io
import re
import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup as bs


class YahooFinance:

    url_base = "https://finance.yahoo.com/quote/{}"
    # start_epoch, end_epoch, event, crumb, interval
    url_hist_base = "https://query1.finance.yahoo.com/v7/finance/download/{symbol}?period1={start_epoch}&period2={end_epoch}&interval={interval}&events={event}&crumb={crumb}"
    def __init__(self, **kwargs):
        self.url_symbol = None
        #elf.symbol = None
        self.cookies = None
        self.crumb = None
        self.summary = {}
        self.kwargs = kwargs
        self.query_time = None

    def clear(self):
        self.crumb = None
        self.cookies = None

    def init(self, symbol):
        self.kwargs = {}
        #self.start_date = pd.to_datetime(start_date)#.replace(hour=0, minute=0, second=0)

        self.url_symbol = YahooFinance.url_base.format(symbol)
        #self.symbol = symbol
        #print(self.url_symbol," startdate=", YahooFinance.get_epoch(self.start_date), self.symbol)
        with  requests.get(self.url_symbol, *self.kwargs) as response:
            print(response.cookies)
            for x in response.cookies:
                print("Entries", x.name, x.value)
            self.cookies = response.cookies
            text = response.text

            # find this pattern "CrumbStore": {"crumb": "DCtHapvvNjt"}, "
            pat = re.compile('CrumbStore":{"crumb":"(.+?)"},')
            matcher = pat.findall(text)
            if matcher is None:
                raise Exception("cannot find crumb in the stream")
            self.crumb = html.unescape(matcher[0])
            self.crumb = self.crumb.replace(u"\\u002F", "/")


        print (self.crumb, self.cookies)

    @staticmethod
    def get_epoch(datetime):
        return int((pd.to_datetime(datetime)- pd.Timestamp("1970-01-01")).total_seconds())




    def get_hist_data(self, symbol, start_date, end_date = None, event="history", interval="1d"):
        if self.crumb is None:
            self.init(symbol)
        start_date = pd.to_datetime(start_date)
        if end_date is None:
            end_date = pd.to_datetime(datetime.datetime.now())
            end_date = pd.to_datetime(end_date)
        url = YahooFinance.url_hist_base.format(start_epoch=YahooFinance.get_epoch(start_date),
                                                end_epoch=YahooFinance.get_epoch(end_date),
                                                symbol=symbol,
                                                event=event, crumb=self.crumb, interval=interval)

        cookies = { x.name: x.value for x in self.cookies }
        response = requests.get(url, cookies=cookies, *self.kwargs)
        df = pd.read_csv(io.StringIO(response.text))
        df.loc[:, 'Symbol']=symbol
        return df

    def get_historical(self, symbol, start_date, end_date=None, interval="1d"):
        return self.get_hist_data(symbol, start_date, end_date, event="history", interval=interval)

    def get_historical_div(self, symbol, start_date, end_date=None):
        return self.get_hist_data(symbol, start_date, end_date, event="div", interval="1d")

    def get_historical_split(self, symbol, start_date, end_date=None):
        return self.get_hist_data(symbol, start_date, end_date, event="split    ", interval="1d")

    def get_details(self, symbol, timedelta=None):
        if self.crumb is None : #or self.cookies.is_expired():
            self.init(symbol)

        if timedelta is not None and self.query_time is not None:
            diff = pd.to_datetime(datetime.datetime.now()) - self.query_time
            if diff < timedelta:
                return

        url_symbol = YahooFinance.url_base.format(symbol)
        cookies = {x.name: x.value for x in self.cookies}
        response = requests.get(url_symbol, cookies=cookies, *self.kwargs)
        parser = bs(response.text, 'html.parser')

        tags = ["PREV_CLOSE-value", "OPEN-value", "BID-value", "ASK-value", "TD_VOLUME-value",
                "AVERAGE_VOLUME_3MONTH-value", "MARKET_CAP-value", "BETA_5Y-value", "PE_RATIO-value",
                "EARNINGS_DATE-value",
                "ONE_YEAR_TARGET_PRICE-value", "EX_DIVIDEND_DATE-value"]
        for t in tags:
            try:
                td = parser.find("td", { "data-test": t})
                value = td.find("span").string
                print (t, "=", value)
                self.summary[t] = value
            except:
                self.summary[t] = np.nan

        tags = ["DAYS_RANGE-value", "FIFTY_TWO_WK_RANGE-value",  "DIVIDEND_AND_YIELD-value",
                ]
        for t in tags:
            try:
                td = parser.find("td", { "data-test": t})
                value = td.string
                print (t, "=", value)
                self.summary[t] = value
            except:
                self.summary[t] = np.nan
        # get the current quotes.
        div = parser.find("div", {"id": "quote-header-info"})
        spans = div.findAll("span")
        current = spans[1].string
        self.summary['LAST_PRICE']=self.to_float(current)
        self.summary['CLOSED'] = False
        try:
            div = parser.find("div", {"id": "quote-header-info"})
            spans = div.findAll("span")
            time_field = spans[3].string
            if "At Close".upper() in str(time_field).upper():
                self.summary["CLOSED"] = True
        except:
            pass

        self.query_time = pd.to_datetime(datetime.datetime.now())
        return self.summary

    def get_query_time(self):
        return self.query_time

    def get_tuple_value(self, symbol, key, token=None):
        if not self.summary:
            self.get_details(symbol)
        if key in self.summary:
            if token is None:
                return self.summary.get(key)
            bid, qty = self.summary.get(key).split(token)
            bid = self.to_float(bid)
            qty = self.to_int(qty)
            return (bid, qty)
        if token is None:
            return "0"
        return (0,0)

    def to_float(self, v):
        try:
            if isinstance(v, str):
                v = v.replace(",", "")
            return float(v)
        except:
            pass
        return np.nan

    def to_int(self, v):
        try:
            if isinstance(v, str):
                v = v.replace(",", "")
            if isinstance(v, float):
                return v
            return int(v)
        except:
            pass
        return 0

    def get_last_price(self, symbol):
        return self.to_float(self.get_tuple_value(symbol, "LAST_PRICE"))

    def get_bid(self, symbol):
        return self.get_tuple_value(symbol, "BID-value", "x")

    def get_ask(self, symbol):
        return self.get_tuple_value(symbol, "ASK-value", "x")

    def get_open_price(self, symbol):
        return self.to_float(self.get_tuple_value(symbol, "OPEN-value"))

    def get_prev_close(self, symbol):
        return self.to_float(self.get_tuple_value(symbol, "PREV_CLOSE-value"))
    def get_thirty_day_volume(self, symbol):
        return self.to_float(self.get_tuple_value(symbol, "TD_VOLUME-value").replace(",", ""))

    def get_close_status(self, symbol):
        if self.crumb is None:
            self.init(symbol)
        if not self.summary:
            self.get_details(symbol)
        return self.summary['CLOSED']

if __name__ == "__main__":
    y = YahooFinance()
    #df = y.get_historical("2012.02.28", "2020.02.28")
    #print(df)
    y.get_details("AAPL")
    df = y.get_historical("AAPL","1970.01.01")
    df.loc[:, "30D"] = df.Volume.rolling(window=30).mean().fillna(0).astype(int)

    print(df.head(60))

    print(y.get_bid("AAPL"), y.get_ask("AAPL"))
    print(y.get_open_price("AAPL"))
    print(y.get_thirty_day_volume("AAPL"))