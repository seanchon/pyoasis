import datetime
import os
from datetime import timedelta
from pyoasis.utils import create_oasis_url, download_files
from pyoasis.report import OASISReport

'''
OASIS only allows the user to call up to 31 days fo data at a time -- though in my experience calling anywhere near 31 days fails.
This script allows the user to provide a date range (by modifying the "start" and "end" paramters
The script user download_files to download the data in XML format,
converts the XML to an OASISReport using Oasis_report and deletes the large XML file
converts OASISReport to a dataframe, filters the dataframe  (by default to includ only NP15 data), and saves as a CSV
It works for Day Ahead Market (DAM) and Real Time Market (RTM) data.
In my experience OASIS fails to pull more than 1 hour of RTM data at a time - ignoring the end paramter.
This means making 8760 separate calls to retrieve a year of DAM data, which can take ~1.5 days of running time.
'''


def repeat_download():
    from datetime import timedelta


    # set start and end dates
    start = datetime.datetime(2018,1,1,0)
    end = datetime.datetime(2019,1,1,0)

    day_delta = 4  # for DAM
    hour_delta = 1  # for RTM

    # set whether we're interested in RTM or DAM with parameter market_run_id
    query_params = {'grp_type': 'ALL_APNODES', 'market_run_id': 'RTM', 'version': 3}

    start_temp = start

    if query_params['market_run_id']='RTM':
        end_temp = min(start + timedelta(hours=hour_delta), end)
    else:
        end_temp = min(start + timedelta(days=day_delta), end)



    while end_temp <= end:

        url = create_oasis_url(report_name="PRC_INTVL_LMP", start=start_temp, end=end_temp, query_params=query_params)
        location = download_files(url, 'downloads')
        oasis_report = OASISReport(location[0])
        os.remove(location[0])

        df = oasis_report.report_dataframe

        df_filtered = df[df['RESOURCE_NAME'].str.contains("NP15")]

        df_filtered.to_csv('downloads/CSVs/'+str(start_temp.month)+"-"+str(start_temp.day)+"-"+str(start_temp.hour)+"_"+str(end_temp.month)+"-"+str(end_temp.day)+"-"+str(start_temp.hour)+".csv")

        start_temp = end_temp

        if end_temp>=end:
            break
        else:
            if query_params['market_run_id']='RTM':
                end_temp = min(start_temp + timedelta(hours=hour_delta), end)
            else:
                end_temp = min(start + timedelta(days=day_delta), end)