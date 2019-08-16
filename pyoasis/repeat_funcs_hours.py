import datetime
from datetime import timedelta
from pyoasis.utils import create_oasis_url, download_files
from pyoasis.report import OASISReport

def repeat_download():
    from datetime import timedelta

    start = datetime.datetime(2018,1,1,0)
    end = datetime.datetime(2018,1,3,0)

    #day_delta = 1

    start_temp = start
    end_temp = min(start + timedelta(days=day_delta), end)

    query_params = {'grp_type': 'ALL_APNODES', 'market_run_id': 'RTM', 'version': 3}

    while end_temp <= end:

        url = create_oasis_url(report_name="PRC_INTVL_LMP", start=start_temp, end=end_temp, query_params=query_params)
        location = download_files(url, 'downloads')
        oasis_report = OASISReport(location[0])

        df = oasis_report.report_dataframe

        df_filtered = df[df['RESOURCE_NAME'].str.contains("NP15")]

        df_filtered.to_csv('downloads/CSVs/'+str(start_temp.month)+"-"+str(start_temp.day)+"_"+str(end_temp.month)+"-"+str(end_temp.day-1)+".csv")

        start_temp = end_temp

        if end_temp>=end:
            break
        else:
            end_temp = min(start_temp + timedelta(days=day_delta), end)