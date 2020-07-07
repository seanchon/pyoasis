from datetime import datetime, timedelta
import os
import pandas as pd
from pytz import timezone

from pyoasis.utils import create_oasis_url, download_files
from pyoasis.report import OASISReport


def repeat_download():
    """
    OASIS only allows the user to call up to 31 days fo data at a time -- though in my experience calling anywhere near 31 days fails.
    This script allows the user to provide a date range (by modifying the "start" and "end" paramters
    The script user download_files to download the data in XML format,
    converts the XML to an OASISReport using Oasis_report and deletes the large XML file
    converts OASISReport to a dataframe, filters the dataframe  (by default to includ only NP15 data), and saves as a CSV
    It works for Day Ahead Market (DAM) and Real Time Market (RTM) data.
    In my experience OASIS fails to pull more than 1 hour of RTM data at a time - ignoring the end paramter.
    This means making 8760 separate calls to retrieve a year of DAM data, which can take ~1.5 days of running time.
    """
    # set start and end dates
    start = datetime(2018, 1, 1, 0)
    end = datetime(2019, 1, 1, 0)

    day_delta = 4  # for DAM
    hour_delta = 1  # for RTM

    # set whether we're interested in RTM or DAM with parameter market_run_id
    query_params = {"grp_type": "ALL_APNODES", "market_run_id": "RTM", "version": 3}

    start_temp = start

    if query_params["market_run_id"] == "RTM":
        end_temp = min(start + timedelta(hours=hour_delta), end)
    else:
        end_temp = min(start + timedelta(days=day_delta), end)

    while end_temp <= end:

        url = create_oasis_url(
            report_name="PRC_INTVL_LMP",
            start=start_temp,
            end=end_temp,
            query_params=query_params,
        )
        location = download_files(url, "downloads")
        oasis_report = OASISReport(location[0])
        os.remove(location[0])

        df = oasis_report.report_dataframe

        df_filtered = df[df["RESOURCE_NAME"].str.contains("NP15")]

        df_filtered.to_csv(
            "downloads/CSVs/"
            + str(start_temp.month)
            + "-"
            + str(start_temp.day)
            + "-"
            + str(start_temp.hour)
            + "_"
            + str(end_temp.month)
            + "-"
            + str(end_temp.day)
            + "-"
            + str(start_temp.hour)
            + ".csv"
        )

        start_temp = end_temp

        if end_temp >= end:
            break
        else:
            if query_params["market_run_id"] == "RTM":
                end_temp = min(start_temp + timedelta(hours=hour_delta), end)
            else:
                end_temp = min(start + timedelta(days=day_delta), end)


def fetch_report(
    report_name,
    start,
    end_limit,
    query_params,
    chunk_size=timedelta(days=1),
    max_attempts=10,
    destination_directory="caiso_downloads",
    keep_temp_files=False,
    timezone_=timezone("US/Pacific"),
    start_column="INTERVAL_START_GMT",
    end_column="INTERVAL_END_GMT",
    sort_by=["DATA_ITEM", "INTERVAL_START_GMT"],
):
    """
    Fetch reports from OASIS and stitch together to create a single report
    beginning on start and ending on end_limit.

    :param report_name: see pyoasis.utils.get_report_names()
    :param start: datetime
    :param end_limit: datetime
    :param query_params: see pyoasis.utils.get_report_params()
    :param chunk_size: length of report to request (timedelta)
    :param max_attempts: number of back-off attempts (int)
    :param destination_directory: directory to store temporary files
    :param keep_temp_files: True to keep intermediary CAISO files
    :param timezone_: pytz.timezone object used for naive start and
        end_limit datetime objects
    :param start_column: column name of start timestamps
    :param end_column: column name of end timestamps
    :param sort_by: sort order of resultant dataframe
    :return: DataFrame
    """
    report_dataframe = pd.DataFrame()

    # localize naive datetime
    if not start.tzinfo:
        start = timezone_.localize(start)
    if not end_limit.tzinfo:
        end_limit = timezone_.localize(end_limit)

    chunk_start = start
    chunk_end = chunk_start + chunk_size
    while chunk_end < end_limit + chunk_size:
        url = create_oasis_url(
            report_name=report_name,
            start=chunk_start,
            end=chunk_end,
            query_params=query_params,
        )
        file_locations = download_files(
            url=url,
            destination_directory=destination_directory,
            max_attempts=max_attempts,
        )
        for file_location in file_locations:
            oasis_report = OASISReport(file_location)
            if hasattr(oasis_report, "report_dataframe"):
                report_dataframe = report_dataframe.append(
                    oasis_report.report_dataframe
                )
            if not keep_temp_files:
                os.remove(file_location)

        chunk_start = chunk_end
        chunk_end = chunk_end + chunk_size

    report_dataframe[start_column] = pd.to_datetime(report_dataframe[start_column])
    report_dataframe[end_column] = pd.to_datetime(report_dataframe[end_column])

    report_dataframe = report_dataframe[
        (report_dataframe[start_column] >= start)
        & (report_dataframe[end_column] <= end_limit)
    ].sort_values(by=sort_by)

    filename = "{}_{}_{}.csv".format(
        start.strftime(format="%Y%m%d-%M%H"),
        end_limit.strftime(format="%Y%m%d-%M%H"),
        report_name,
    )
    filename = os.path.join(os.path.abspath(destination_directory), filename)
    report_dataframe.to_csv(filename)

    return filename
