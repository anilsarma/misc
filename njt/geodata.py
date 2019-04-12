
import  pandas as pd
from math import radians, cos, sin, asin, sqrt
import sqlite3
import numpy as np

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

def dump_table(conn, name):
    df = pd.read_sql_query("select * from {} ".format(name), conn)
    print("Table " +  name )
    print(df.head(6))
    return df

def sql(conn, query):
    df = pd.read_sql_query(query, conn)
    print(query )
    print(df.head(2))
    return df

def sqlstr(data):
    return ",".join([ "'{}'".format(x) for x in data ])



def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians
    #lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    lon1 = np.radians(lon1)
    lon2 = np.radians(lon2)
    lat1 = np.radians(lat1)
    lat2 = np.radians(lat2)

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2

    c = 2 * np.arcsin(np.sqrt(a))
    #r = 6371 # Radius of earth in kilometers. Use 3956 for miles
    r = 3956

    return c * r


df = pd.read_csv(r'C:\Users\Anil Sarma\git\svc\US.postal.txt', sep='\t', header=None)
#http://download.geonames.org/export/zip/
cols = [ 'country', "zip", "city", "state_long", "state_short", "county", "distance", "un0", "un1", "lat", "lon", "accuracy"]
df.columns = cols
df = df[df.state_short=="NJ"]

df.loc[:, 'distance'] = 0
# GeoLocation(lat=40.726087, lon=-74.038831),
lat=40.726087
lon=-74.038831
df.distance = df.apply( lambda row: haversine(row.lon, row.lat, lon, lat), axis=1 )
df = df.sort_values( ['distance'])
conn = sqlite3.connect('bus_data.db')

df_stops = sql(conn, "select * from stops")
df_stops.loc[:, 'county'] = 0
df_stops.loc[:, 'state'] = 0
df_stops.loc[:, 'city'] = 0
df_stops.loc[:, 'city'] = 0
data = []
import  datetime
s = datetime.datetime.now()
df_stops.loc[:, 'start_lon'] = lon
df_stops.loc[:, 'start_lat'] = lat

#print(haversine(df_stops.start_lon, df_stops.start_lat, df_stops.stop_lon, df_stops.stop_lat))

df_stops
for key, row in df_stops.iterrows():
    df.loc[:, 'start_lon'] = row.stop_lon
    df.loc[:, 'start_lat'] = row.stop_lat

    df.distance = haversine(df.start_lon, df.start_lat, df.lon, df.lat)
    df = df.sort_values(['distance'])
    df_stops.loc[key, 'county'] = df.iloc[0].county
    df_stops.loc[key, 'state'] = df.iloc[0].state_short
    df_stops.loc[key, 'city'] = df.iloc[0].city
    row.county=df.iloc[0].county
    #print(df.iloc[0].state_short)
    #data.append(row)

st = datetime.datetime.now()
print("diff", st-s)
#df_stops=pd.DataFrame(data).head()
print (df_stops.head(4))
df_stops.to_csv("stops_cities.txt", index=False)

