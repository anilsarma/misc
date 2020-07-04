import firebase_admin
from firebase_admin import credentials, firestore
from firebase_admin import db
import pandas as pd
import matplotlib.pyplot as plt

cred = credentials.Certificate("timetransform-e722a-firebase-adminsdk-yqj1h-51ca067f21.json")
firebase_admin.initialize_app(cred)
db = firestore.client()
#db = firestore.client()
doc_ref = db.collection("amazon").document('ASINDB')

doc = doc_ref.collections()
# for x in dir(doc_ref):
#     print(x)
#print(doc.to_dict())
dfs = []
for x in doc:
    #for y in x.where('asin', '==', 'B088BTZ77F').stream():
    for y in x.stream():
        dfs.append(y.to_dict())

pd.set_option('display.max_rows', 1000)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)
#print(dfs)
df = pd.DataFrame(dfs)
df.date = pd.to_datetime(df.date)
df = df.set_index(['date', 'asin'])

df["rank"] = pd.to_numeric(df["rank"])


#df = df[df["rank"] < 20000]
def clean(df, name):

    df[name] = pd.to_numeric(df[name])
    df = df[[name]]

    df0 = df.unstack(level=-1)
    df0.columns = df0.columns.droplevel()
    df0 = df0.ffill().bfill()
    df0 = df0.resample('15min').last()
    df0 = df0.ffill().bfill()
    df0 = df0.drop_duplicates()
    return df0

df0 = clean(df, 'data-asin-price')
print(df0)


df0.plot(title='Price')
#print(df0)

df1 = clean(df, 'rank')
df1.plot(title='rank')
print(df1)
plt.show()
