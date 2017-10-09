def get_obs_json(api_key, series_id, realtime_start = "",
            realtime_end = "", limit = "", offset = "",
            sort_order = "", observation_start = "", observation_end = "",
            units = "", frequency = "", aggregation_method = "", 
            output_type = "", vintage_dates=""):
    saved_args = locals()
    import urllib3
    http = urllib3.PoolManager()
    service_link  = "https://api.stlouisfed.org/fred/series/observations"
    
    saved_args['file_type'] = "json"
    r = http.request('GET', service_link, fields=saved_args)
    
    if (r.status != 200):
        print "Error:",r.status
        return r.status
    
    import json
    all_data = json.loads(r.data.decode('utf-8'))
    try:
        data = all_data["observations"]
    except DataRetrieveError:
        print "JSON does not have observations"
        return DataRetrieveError
    try:
        del all_data['observations']
    except KeyError:
        print "Header information is missing"
        return DataRetrieveError
            
    #header   = all_data.remove("observations") 
    header = all_data
    print header
    #header_info = data[v]
    import pandas as pd
    import numpy as np
    df = pd.DataFrame(data=data)
    df.rename(index=str, columns={"value": series_id}, inplace = True)
    # Count missing values
    len_df = len(df)
    n_missing = 0
    df['__m'] = 0
    import decimal
    for index in range(0,len_df):
        try:
            df[series_id][index] = float(decimal.Decimal(df[series_id][index]))
            df['__m'] = 1
        except KeyError:
            n_missing += 1
            df['__m'] = -1
    db_data = dict()
    db_data['name'] = series_id
    db_data['n']    = header['count']
    db_data['n_missing'] = n_missing
    db_data['Start date'] = df.iloc[0]["date"]
    db_data['End date'] = df.iloc[-1]["date"]
    db_data['Realtime Start date'] = df.iloc[0]["realtime_start"]
    db_data['Realtime End date'] = df.iloc[0]["realtime_end"]
    
    print "Name of Series         :", series_id
    print "Number of Obs          :",header['count']
    print "Number of Missing Obs  :",n_missing
    print "Start Date             :",df.iloc[0]["date"]
    print "End   Date             :",df.iloc[-1]["realtime_start"]
    print "Realtime End   Date    :",df.iloc[0]["realtime_end"]
    print 
    df = df.drop(df[df['__m'] == -1].index)
    df.drop('__m',axis = 1, inplace = True)
    print n_missing,"observations removed for analysis and graphing\n"
    
    print "Mean                   :",df[series_id].mean()
    print "Variance               :",df[series_id].var()
    print "Maximum                :",df[series_id].max()
    print "Minimum                :",df[series_id].min()
    
    import matplotlib.pyplot as plt
    graph_df = df[['date',series_id]]
    graph_df.set_index('date')
    graph = graph_df.plot(kind="line",title = series_id)
    
    xAxis = range(0,len(df))
    date = [str() for c in 'c' * len(df)]
    date[0] = df['date'].iloc[0]
    date[-1] = df['date'].iloc[-1]
    plt.xticks(xAxis,date)
    
    graph.set_xlabel("Date")
    graph.set_ylabel(series_id)
    plt.show()
    
    import collections
    Info = collections.namedtuple("Info",["df",'realtime_end','graph','db_data'])
    graph_file_name = series_id + ".png"
    db_data['graph file name'] = graph_file_name
    plt.savefig(graph_file_name, dpi = 300, bbox_inches='tight')
    rt = Info(df = df,realtime_end = header['realtime_end'],graph = graph, db_data=db_data)
    return rt