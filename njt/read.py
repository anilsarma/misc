#!/usr/bin/python

import sqlite3
import pandas as pd

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)
from math import radians, cos, sin, asin, sqrt


def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2

    c = 2 * asin(sqrt(a))
    # r = 6371 # Radius of earth in kilometers. Use 3956 for miles
    r = 3956

    return c * r


conn = sqlite3.connect('bus_data.db')
print "Opened database successfully";

df = pd.read_sql_query('''
SELECT  name FROM sqlite_master WHERE   type ='table' ''', conn)
print(df.head())


# for x in conn.execute('''select * from stops'''):
#     print (x)
#     print x.names
def dump_table(conn, name):
    df = pd.read_sql_query("select * from {} ".format(name), conn)
    print("Table " + name)
    print(df.head(6))
    return df


def sql(conn, query):
    df = pd.read_sql_query(query, conn)
    print(query)
    print(df.head(2))
    return df


def sqlstr(data):
    return ",".join(["'{}'".format(x) for x in data])


dump_table(conn, "stops where stop_name like '%WASHINGTON B%' ")
df = pd.read_sql_query('''select * from routes where route_id='64' ''', conn)
print(df.head())

dump_table(conn, "stops limit 10")
dump_table(conn, "trips where route_id='64'")
dump_table(conn, "stop_times limit 10")
dump_table(conn, "calendar_dates limit 10")

# df = dump_table(conn, "stop_times where stop_id in ( '2864', '2865', '2866', '2867') ")
#
#
# df_stop = pd.read_csv( "bus_data/stops.txt")
# df_stop = df_stop[ df_stop.stop_name.str.contains('WASHINGTON BL') ]
# print(df_stop)
# df_stop_times = pd.read_csv( "bus_data/stop_times.txt")
# df_stop_times = df_stop_times[ df_stop_times.stop_id.isin(df_stop.stop_id)]
# #print(df.trip_id.astype(str).unique())
# trips = ["'{}'".format(x) for x in df.trip_id.astype(str).unique()]
# trips = ", ".join(trips)

df_trips = pd.read_csv("bus_data/trips.txt")


# df =  dump_table( conn, "trips where  trip_id in ({})".format(trips))

# df_my_routes = dump_table(conn, "routes where route_short_name='64' ")
# df_trips = df_trips[df_trips.trip_id.isin( df_stop_times.trip_id)]
# print(df_trips[df_trips.route_id.isin(df_my_routes.route_id)]) # route short name
# df_trips = pd.read_csv( "bus_data/stop_times.txt")
# df_trips = df_trips[ df_trips.trip_id.isin( [45632])]
# print(df_trips)
# print(dump_table(conn, "stop_times where trip_id='45632' "))
class GeoLocation(object):
    def __init__(self, lon, lat):
        self.lon = lon
        self.lat = lat


def get_routes(conn, date, start, stop):
    df_stops = sql(conn, "select * from stops")
    df_stops.loc[:, 'distance_start'] = 0
    df_stops.loc[:, 'distance_stop'] = 0
    df_stops['distance_start'] = df_stops.apply(lambda row: haversine(start.lon, start.lat, row.stop_lon, row.stop_lat),
                                                axis=1)
    df_stops['distance_stop'] = df_stops.apply(lambda row: haversine(stop.lon, stop.lat, row.stop_lon, row.stop_lat),
                                               axis=1)
    # print("nearby\n\n")
    # print(df_stops.head())
    df_start_stops_nearby = df_stops[df_stops.distance_start < 0.4].sort_values(['distance_start'])
    df_stop_stops_nearby = df_stops[df_stops.distance_stop < 0.4].sort_values(['distance_stop'])
    # print("nearby\n\n")
    print(df_stop_stops_nearby)

    sql_services_today = "select service_id from calendar_dates where date='{}'".format(date)
    sql_today_trips = "select trip_id from trips where service_id in ({})".format(sql_services_today)
    sql_my_stop_times = "select * from stop_times where stop_id in ( {} ) and trip_id in ( {} ) order by arrival_time".format(
        sqlstr(df_start_stops_nearby.stop_id), sql_today_trips)
    sql_dest_stops = "select stop_id from stops where stop_name like '%Race Track%'"
    print(sql_dest_stops)

    sql_my_stops = "select distinct x.* from ({x}) as x, ({y}) as y where x.trip_id = y.trip_id and x.stop_sequence < y.stop_sequence and y.stop_id in ( {dest_stops})"
    sql_my_stops = sql_my_stops.format(x=sql_my_stop_times, y="stop_times",
                                       dest_stops=sqlstr(df_stop_stops_nearby.stop_id))

    # sql(conn, sql_my_stops)
    return sql(conn, sql_my_stops)


# print( get_routes(conn, 20190401, GeoLocation(lat=40.726087, lon=-74.038831),  GeoLocation( lat=40.429078, lon=-74.383743  )))
# print( get_routes(conn, 20190401, stop=GeoLocation(lat=40.726087, lon=-74.038831),  start=GeoLocation( lat=40.429078, lon=-74.383743  ) ))

# print(sql(conn,  "select * from stops where stop_name like '%Race Track%'"))
# print(sql(conn,  "select * from stops where stop_name like '%NewPort%'"))

sql(conn, "select * from routes where route_short_name='68' limit 2")
sql(conn, "select * from calendar_dates limit 2")
# print(sql( conn, "select stop.*, trip.route_id, rt.route_short_name from stop_times as stop, trips as trip, routes as rt where stop.stop_id = {} and stop.trip_id = trip.trip_id and trip.route_id = rt.route_id".format(29619)))

print(sql(conn,
          "select distinct trip.*, cal.date from trips trip, calendar_dates cal where trip.route_id = {} and cal.service_id = trip.service_id and cal.date={} and trip.trip_id={}".format(
              169, 20190401, 23040)))

print(sql(conn,
          "select trip.trip_headsign, st.*, sp.stop_lat, sp.stop_lon, sp.stop_name from stop_times st, trips as trip, stops sp where sp.stop_id = st.stop_id and st.trip_id = {trip_id} and trip.trip_id=st.trip_id order by stop_sequence".format(
              trip_id=333)))
# stop = 42309
sql(conn, "select * from routes where route_id='1'")
sql(conn, "select * from trips where route_id='1'")
# df = sql(conn, "select * from stop_times, stops, routes, trips where stops.stop_id = stop_times.stop_id and routes.route_id = trips.route_id and  trips.trip_id = stop_times.trip_id and routes.route_short_name='1' order by trips.trip_id, stop_times.arrival_time ")

# print (df[df.trip_headsign.str.contains("PENN")])



# print(sql(conn, "select * from routes where route_short_name='68' order by route_short_name"))
# print(sql(conn, "select distinct trip_id, route_id, trip_headsign from trips where route_id=169"))
# sql(conn, "select * from stops where stop_name like '%GRAND ST%'")


df_stop0 = sql(conn, "select * from stops where stop_name like '%willow ave at 19th st%' ")
df_stop1 = sql(conn, "select * from stops where stop_name like '%willow ave at 15th st%' ")
sql_services = "select service_id from calendar_dates where date='20190408'"
sql_trips = "select distinct trip_id from trips, routes where routes.route_short_name='126' and routes.route_id = trips.route_id and service_id in ({services}) "
sql_stop_times = "select * from stop_times where trip_id in ({sql_trips})"
sql_stop_times = sql_stop_times.replace("{sql_trips}", sql_trips).replace("{services}", sql_services)
df_stop_times = sql(conn, sql_stop_times)
for key, df in df_stop_times.groupby('trip_id'):
    df = df.sort_values("stop_sequence")
    dfx = df[df.stop_id.isin(df_stop0.stop_id)]
    dfy = df[df.stop_id.isin(df_stop1.stop_id)]
    if not dfx.empty and not dfy.empty:
        if (dfx.iloc[0].stop_sequence < dfy.iloc[0].stop_sequence):
            print(pd.concat([dfx, dfy]))

sql_dx = "select stop_id from stops where stop_name like '%willow ave at 19th st%' "
sql_dy = "select stop_id from stops where stop_name like '%willow ave at 15th st%' "
sql_stop_times_dx = "select * from stop_times where trip_id in ({sql_trips}) and stop_id in ( {sql_dx} )"
sql_stop_times_dy = "select * from stop_times where trip_id in ({sql_trips}) and stop_id in ( {sql_dy} )"

sql_query = "select dx.trip_id, * from ( {stop_times_dx} )as dx, ( {stop_times_dy} )as dy  where  dx.stop_sequence < dy.stop_sequence and dx.trip_id = dy.trip_id"

var = {
    '{sql_trips}': sql_trips,
    "{services}": sql_services,
    "{sql_dx}": sql_dx,
    "{sql_dy}": sql_dy,
    "{stop_times_dy}": sql_stop_times_dy,
    "{stop_times_dx}": sql_stop_times_dx
}
#sql_query = sql_query.replace("{sql_trips}", sql_trips).replace("{services}", sql_services).replace("{dx}",
#                                                                                                    sql_dx).replace(
#    "{dy}", sql_dy).replace("{stop_times_dy}", sql_stop_times_dy).replace("{stop_times_dx}", sql_stop_times_dx)
while  True:
    found = False
    for x in var:
        if x in sql_query:
            sql_query = sql_query.replace(x, var[x])
            #print (sql_query)
            found = True
    if not found:
        break

# sql_stop_times_dy = sql_stop_times_dy.replace("{sql_trips}", sql_trips).replace("{services}", sql_services).replace("{dx}", sql_dx).replace("{dy}", sql_dy)

print(sql(conn, sql_query))

conn.close()
