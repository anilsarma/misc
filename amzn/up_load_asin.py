# gcloud functions deploy get_snapshot --entry-point get_snapshot --runtime python37 --trigger-http --allow-unauthenticated
import datetime

import pandas as pd
from dateutil.tz import tzlocal


def now():
    dt = pd.Timestamp(datetime.datetime.now())
    dt = dt.tz_localize(tzlocal()).tz_convert("US/Eastern").tz_localize(None)
    return dt




import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore


cred = None


def upload_data(asins):
    # Use the application default credentials
    # cred = credentials.ApplicationDefault()
    global cred
    try:
        cred = credentials.Certificate("timetransform-e722a-firebase-adminsdk-yqj1h-51ca067f21.json")
        firebase_admin.initialize_app(cred)
    except:
        pass


    db = firestore.client()

    for asin in asins:
        data = { 'asin': asin, 'date': str(now())}
        doc = db.collection("amazon").document("ASINS").collection(asin).document("details")
        doc.set(data)



import traceback


def upload_isin(request):
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
    df = pd.read_csv("asin.txt")
    asins = list(df.asin.drop_duplicates())
    asins.sort()
    print(asins)
    upload_data(asins)
