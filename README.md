# pyoasis

Python interface to CAISO's OASIS API.

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
$ pip install git+ssh://git@github.com/TerraVerdeRenewablePartners/pyoasis.git
```

# DOWNLOAD REPORTS
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
