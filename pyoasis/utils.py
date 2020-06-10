from io import BytesIO
import json
import os
from pytz import timezone
import requests
import time
import xmltodict
from zipfile import BadZipfile, ZipFile


# get location of oasis_endpoints.json file
FILE_DIR = os.path.dirname(os.path.realpath(__file__))
OASIS_ENDPOINTS_JSON = FILE_DIR + "/oasis_endpoints.json"


def format_datetime(datetime_, timezone_=timezone("US/Pacific")):
    """
    Converts datetime object to yyyymmddThh24:miZ format. CAISO OASIS only
    accepts datetime timestamps in US/Pacific.

    :param datetime_: datetime object
    :param timezone_: destination timezone (pytz.timezone)
    :return: yyyymmddThh24:miZ formatted string
    """
    # set timezone if datetime_ has no timezone
    if not datetime_.tzinfo:
        datetime_ = timezone_.localize(datetime_)
    else:
        datetime_ = datetime_.astimezone(timezone_)

    return datetime_.strftime("%Y%m%dT%H:%M%z")


def create_oasis_url(report_name, start=None, end=None, query_params={}):
    """
    Queries CAISO OASIS for a report and saves the file to the
    destination_directory.

    :param report_name: (string)
    :param start: datetime object
    :param end: datetime object
    :param query_params: additional querystring parameters (dictionary)
    :return: file locations (list)
    """
    with open(OASIS_ENDPOINTS_JSON) as f:
        all_endpoints_dict = json.load(f)

    # construct base url
    oasis_url = "oasis.caiso.com"

    # add path based on oasis_endpoints.json
    single_zip_path = "/oasisapi/SingleZip"
    group_zip_path = "/oasisapi/GroupZip"
    if report_name in (all_endpoints_dict[oasis_url][single_zip_path].keys()):
        oasis_url += single_zip_path
        report_query = "queryname"
    elif report_name in (all_endpoints_dict[oasis_url][group_zip_path].keys()):
        oasis_url += group_zip_path
        report_query = "groupid"

    # construct additional paramaters
    querystring = "&".join([str(x) + "=" + str(y) for x, y in query_params.items()])
    if start:
        querystring += "&startdatetime={}".format(format_datetime(start))
    if end:
        querystring += "&enddatetime={}".format(format_datetime(end))

    # add report query
    querystring += "&" + report_query + "=" + report_name

    return "http://" + oasis_url + "?" + querystring


def download_files(url, destination_directory, max_attempts=1):
    """
    Downloads zipped files from url and saves to destination_directory. Returns
    a list of absolute file locations.

    :param url: (string)
    :param destination_directory: (string)
    :param max_attempts: maximum attempts to download file (int)
    :return: absolute paths of all files (list of strings)
    """
    destination_directory = os.path.abspath(os.path.expanduser(destination_directory))

    i = 1
    success = False
    while not success and i <= max_attempts:
        try:
            # pull data from url and save to destination_directory
            response = requests.get(url)
            zipfile = ZipFile(BytesIO(response.content))
            zipfile.extractall(destination_directory)
            success = True
        except BadZipfile as e:
            if i != max_attempts:
                time.sleep(i)
                i += 1
            else:
                raise e

    # return absolute paths of all files
    return [destination_directory + "/" + x for x in zipfile.namelist()]


def xml_to_dict(xml_path):
    """
    Converts an XML file to a Python dictionary.

    :param xml_path: path to XML file
    :return: dictionary
    """
    with open(xml_path) as f:
        return xmltodict.parse(f.read())


def get_report_names():
    """
    Returns all possible report names.
    """
    with open(OASIS_ENDPOINTS_JSON) as f:
        all_endpoints_dict = json.load(f)

    return set(
        all_endpoints_dict["oasis.caiso.com"]["/oasisapi/GroupZip"].keys()
    ) | set(all_endpoints_dict["oasis.caiso.com"]["/oasisapi/SingleZip"].keys())


def get_report_params(report_name):
    """
    Filters oasis_endpoints.json file and returns sample params for a report
    query harvested from the API docs.
    """
    with open(OASIS_ENDPOINTS_JSON) as f:
        all_endpoints_dict = json.load(f)

    for domain, domain_dict in all_endpoints_dict.items():
        for path, path_dict in domain_dict.items():
            if report_name in path_dict.keys():
                return {
                    domain: {
                        path: {
                            report_name: all_endpoints_dict[domain][path][report_name]
                        }
                    }
                }
