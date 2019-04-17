def time_function(func):
    def wrapped_function(*args, **kwargs):
        start_time = pd.Timestamp.now()
        ret =  func(*args, **kwargs)
        stop_time = pd.Timestamp.now()
        print("total time cost:", stop_time - start_time)
        return ret
    return wrapped_function
    
    
sql_query = '''select stop_times.trip_id, stop_times.arrival_time,  stop_times.stop_id,  stop_times.stop_sequence, stops.stop_name   
               from  stop_times, stops where stop_times.stop_id in ( select stop_id from stops where stop_name like '%{station}%' )
                and stops.stop_id = stop_times.stop_id 
               '''

sql_start = sql_query.format( station="race track", today_trips=today_trips)
sql_stop = sql_query.format( station="washington blvd", today_trips=today_trips)
cols = ''' st.trip_id as trip_id,
st.arrival_time as start_time,
sp.arrival_time as stop_time,
trip_headsign,
route_short_name
'''
#st.stop_name as start_name,
#sp.stop_name as stop_name,
#st.stop_sequence as start_sequence,
#sp.stop_sequence as stop_sequence,
sql_query = '''
select {cols} from 
              ( {sql_start} ) as st,
              ( {sql_stop}  ) as sp,
              trips,
              routes,
              calendar_dates where
              calendar_dates.date='20190415'  and        
              trips.trip_id = sp.trip_id and
              st.trip_id = sp.trip_id and
              st.stop_sequence < sp.stop_sequence
              trips.route_id = routes.route_id      
                  calendar_dates.service_id = trips.service_id and             
                                                        
'''

cols = ''' st.trip_id as trip_id,
st.arrival_time as start_time,
sp.arrival_time as stop_time,
trip_headsign,
route_short_name
'''

sql_query = '''
select * from ( {sql_start} ) as st,
              ( {sql_stop}  ) as sp, 
              trips,   
              routes,
              calendar_dates           
              where        
              st.trip_id = sp.trip_id and
              st.stop_sequence < sp.stop_sequence and
              st.trip_id = trips.trip_id and
              trips.route_id = routes.route_id   and
              calendar_dates.service_id = trips.service_id and
              calendar_dates.date='20190415'         
'''

sql_query = sql_query.format(sql_start=sql_start, sql_stop=sql_stop, cols=cols)
sql(conn, sql_query)
