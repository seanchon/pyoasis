# pyoasis

Python interface to CAISO's [OASIS API](http://oasis.caiso.com/mrioasis/logon.do).

# SETUP

The following steps should be followed to set up a development environment.
```
$ python -m venv <env_name>
$ source <env_name>/bin/activate
(<env_name>)$ pip install -r requirements.txt
(<env_name>)$ pre-commit install
```

The following step should be followed if installing this package in another project.
```
$ pip install git+ssh://git@github.com/MCE-Clean-Energy/pyoasis.git
```

# DOWNLOAD REPORTS

The following functions aid in downloading single XML files as provided by CAISO. There are some limitations in the number of days that can be requested in a single query, which vary by report. To download a larger date range, see [DOWNLOAD MULTIPLE REPORTS](#download-multiple-reports).
```
In [1]: from pyoasis.utils import create_oasis_url, download_files, get_report_params
   ...: from datetime import datetime, timedelta
   ...: end = datetime.utcnow()
   ...: start = end - timedelta(days=1)                                                                                                                    

In [2]: get_report_params('PRC_LMP')                                                                                                                       
Out[2]:
{'oasis.caiso.com': {'/oasisapi/SingleZip': {'PRC_LMP': [{'enddatetime': '20130920T07:00-0000',
     'grp_type': 'ALL_APNODES',
     'market_run_id': 'DAM',
     'queryname': 'PRC_LMP',
     'startdatetime': '20130919T07:00- 0000',
     'version': '1'},
    {'enddatetime': '20130920T07:00-0000',
     'market_run_id': 'DAM',
     'node': 'LAPLMG1_7_B2',
     'queryname': 'PRC_LMP',
     'startdatetime': '20130919T07:00- 0000',
     'version': '1'}]}}}

In [3]: url = create_oasis_url(report_name='PRC_LMP', start=start, end=end, query_params={'grp_type': 'ALL_APNODES', 'market_run_id': 'DAM', 'version': 1})

In [4]: url
Out[4]: 'http://oasis.caiso.com/oasisapi/SingleZip?grp_type=ALL_APNODES&market_run_id=DAM&version=1&startdatetime=20200602T18:44-0700&enddatetime=20200603T18:44-0700&queryname=PRC_LMP'

In [5]: download_files(url, 'downloads')
Out[5]: ['./downloads/20200602_20200602_PRC_LMP_DAM_20200603_11_45_34_v1.xml']
```

# PARSE REPORTS

A class called `OASISReport` can be used to read the XML reports provided by CAISO in a pandas DataFrame format.
```
In [1]: from pyoasis.report import OASISReport                                                                                                             

In [2]: oasis_report = OASISReport('downloads/20200602_20200602_PRC_LMP_DAM_20200603_11_45_34_v1.xml')                                                     

In [3]: oasis_report.report_dataframe                                                                                                                      
Out[3]:
DATA_ITEM        RESOURCE_NAME    OPR_DATE INTERVAL_NUM         INTERVAL_START_GMT           INTERVAL_END_GMT     VALUE
0            LMP_PRC  AFPR_1_TOT_GEN-APND  2020-06-02           21  2020-06-03T03:00:00-00:00  2020-06-03T04:00:00-00:00  58.79329
1            LMP_PRC  AFPR_1_TOT_GEN-APND  2020-06-02           20  2020-06-03T02:00:00-00:00  2020-06-03T03:00:00-00:00  89.80261
2            LMP_PRC  AFPR_1_TOT_GEN-APND  2020-06-02           24  2020-06-03T06:00:00-00:00  2020-06-03T07:00:00-00:00  27.96422
3            LMP_PRC  AFPR_1_TOT_GEN-APND  2020-06-02           22  2020-06-03T04:00:00-00:00  2020-06-03T05:00:00-00:00  37.03459
4            LMP_PRC  AFPR_1_TOT_GEN-APND  2020-06-02           23  2020-06-03T05:00:00-00:00  2020-06-03T06:00:00-00:00  29.89008
...              ...                  ...         ...          ...                        ...                        ...       ...
190459  LMP_LOSS_PRC    YALE_7_UNITS-APND  2020-06-03            6  2020-06-03T12:00:00-00:00  2020-06-03T13:00:00-00:00  -0.93879
190460  LMP_LOSS_PRC    YALE_7_UNITS-APND  2020-06-03            5  2020-06-03T11:00:00-00:00  2020-06-03T12:00:00-00:00  -0.75582
190461  LMP_LOSS_PRC    YALE_7_UNITS-APND  2020-06-03            1  2020-06-03T07:00:00-00:00  2020-06-03T08:00:00-00:00  -1.12311
190462  LMP_LOSS_PRC    YALE_7_UNITS-APND  2020-06-03           16  2020-06-03T22:00:00-00:00  2020-06-03T23:00:00-00:00  -3.32574
190463  LMP_LOSS_PRC    YALE_7_UNITS-APND  2020-06-03           19  2020-06-04T01:00:00-00:00  2020-06-04T02:00:00-00:00  -7.39762

[190464 rows x 7 columns]

In [4]: oasis_report.get_unique_values("RESOURCE_NAME")                                                                                                                         Out[4]:
array(['AFPR_1_TOT_GEN-APND', 'AGRICO_6_PL3N5-APND', 'AGRICO_7_UNIT-APND',
       ..., 'WP_2_WPCC5MSG-APND', 'WSH_1_WESTSIDEHYD-APND',
       'YALE_7_UNITS-APND'], dtype=object)

In [5]: oasis_report.filter_report_dict("RESOURCE_NAME", ["TH_NP15_GEN-APND"])                                                                                                       

In [6]: oasis_report.report_dataframe.sort_values(by=["DATA_ITEM", "INTERVAL_START_GMT"])                                                                                            
Out[6]:
       DATA_ITEM     RESOURCE_NAME    OPR_DATE INTERVAL_NUM         INTERVAL_START_GMT           INTERVAL_END_GMT     VALUE
9   LMP_CONG_PRC  TH_NP15_GEN-APND  2020-06-02           20  2020-06-03T02:00:00-00:00  2020-06-03T03:00:00-00:00         0
5   LMP_CONG_PRC  TH_NP15_GEN-APND  2020-06-02           21  2020-06-03T03:00:00-00:00  2020-06-03T04:00:00-00:00         0
6   LMP_CONG_PRC  TH_NP15_GEN-APND  2020-06-02           22  2020-06-03T04:00:00-00:00  2020-06-03T05:00:00-00:00         0
7   LMP_CONG_PRC  TH_NP15_GEN-APND  2020-06-02           23  2020-06-03T05:00:00-00:00  2020-06-03T06:00:00-00:00         0
8   LMP_CONG_PRC  TH_NP15_GEN-APND  2020-06-02           24  2020-06-03T06:00:00-00:00  2020-06-03T07:00:00-00:00         0
..           ...               ...         ...          ...                        ...                        ...       ...
33       LMP_PRC  TH_NP15_GEN-APND  2020-06-03           15  2020-06-03T21:00:00-00:00  2020-06-03T22:00:00-00:00      38.5
34       LMP_PRC  TH_NP15_GEN-APND  2020-06-03           16  2020-06-03T22:00:00-00:00  2020-06-03T23:00:00-00:00  43.92021
22       LMP_PRC  TH_NP15_GEN-APND  2020-06-03           17  2020-06-03T23:00:00-00:00  2020-06-04T00:00:00-00:00  48.90323
24       LMP_PRC  TH_NP15_GEN-APND  2020-06-03           18  2020-06-04T00:00:00-00:00  2020-06-04T01:00:00-00:00  64.53166
21       LMP_PRC  TH_NP15_GEN-APND  2020-06-03           19  2020-06-04T01:00:00-00:00  2020-06-04T02:00:00-00:00  99.90272

[96 rows x 7 columns]
```

# DOWNLOAD MULTIPLE REPORTS

The following function will download multiple reports, stitch them together into a single report, and save it as a CSV file.

NOTE: There are some issues when querying the OASIS API repeatedly, which can cause this function to fail. Some endpoints allow specifying a `node`, which allows OASIS to return smaller reports that are filtered on the node. Another mechanism to address this is to decrease the `chunk_size` (fewer days in a single request) or increase the `max_attempts` (more attempts to download each constituent file).

```
In [1]: from datetime import datetime, timedelta                                                                                                           

In [2]: import pandas as pd                                                                                                      

In [3]: from pyoasis.repeat_calls import fetch_report                                                                                                      

In [4]: fetch_report(report_name="PRC_LMP", query_params={'node': "TH_NP15_GEN-APND", 'market_run_id': 'DAM', 'version': 1}, start=datetime(2019, 1, 1), end_limit=datetime(2019, 2, 1), chunk_size=timedelta(days=15), max_attempts=10, destination_directory="caiso_downloads")                                                                      
Out[4]: '.../caiso_downloads/20190101-0000_20190201-0000_PRC_LMP.csv'

In [5]: pd.read_csv(".../caiso_downloads/20190101-0000_20190201-0000_PRC_LMP.csv")                                 
Out[5]:
      Unnamed: 0     DATA_ITEM     RESOURCE_NAME    OPR_DATE  INTERVAL_NUM         INTERVAL_START_GMT           INTERVAL_END_GMT     VALUE
0             27  LMP_CONG_PRC  TH_NP15_GEN-APND  2019-01-01             1  2019-01-01 08:00:00+00:00  2019-01-01 09:00:00+00:00   0.00000
1             28  LMP_CONG_PRC  TH_NP15_GEN-APND  2019-01-01             2  2019-01-01 09:00:00+00:00  2019-01-01 10:00:00+00:00   0.00000
2             34  LMP_CONG_PRC  TH_NP15_GEN-APND  2019-01-01             3  2019-01-01 10:00:00+00:00  2019-01-01 11:00:00+00:00   0.00000
3             35  LMP_CONG_PRC  TH_NP15_GEN-APND  2019-01-01             4  2019-01-01 11:00:00+00:00  2019-01-01 12:00:00+00:00   0.00000
4             38  LMP_CONG_PRC  TH_NP15_GEN-APND  2019-01-01             5  2019-01-01 12:00:00+00:00  2019-01-01 13:00:00+00:00   0.00000
...          ...           ...               ...         ...           ...                        ...                        ...       ...
2971          10       LMP_PRC  TH_NP15_GEN-APND  2019-01-31            20  2019-02-01 03:00:00+00:00  2019-02-01 04:00:00+00:00  53.29588
2972           1       LMP_PRC  TH_NP15_GEN-APND  2019-01-31            21  2019-02-01 04:00:00+00:00  2019-02-01 05:00:00+00:00  48.09075
2973          11       LMP_PRC  TH_NP15_GEN-APND  2019-01-31            22  2019-02-01 05:00:00+00:00  2019-02-01 06:00:00+00:00  43.19151
2974          15       LMP_PRC  TH_NP15_GEN-APND  2019-01-31            23  2019-02-01 06:00:00+00:00  2019-02-01 07:00:00+00:00  41.65750
2975          21       LMP_PRC  TH_NP15_GEN-APND  2019-01-31            24  2019-02-01 07:00:00+00:00  2019-02-01 08:00:00+00:00  39.41805

[2976 rows x 8 columns]
```
