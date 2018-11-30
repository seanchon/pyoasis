from io import BytesIO
import json
import os
from pytz import timezone
import requests
import xmltodict
from zipfile import ZipFile


# get location of oasis_endpoints.json file
FILE_DIR = os.path.dirname(os.path.realpath(__file__))
OASIS_ENDPOINTS_JSON = FILE_DIR + "/endpoints/oasis_endpoints.json"


def format_datetime(datetime_, _timezone=timezone("US/Pacific")):
    """
    Converts datetime object to yyyymmddThh24:miZ format.

    :param datetime_: datetime object
    :param timezone_: pytz.timezone object
    :return: yyyymmddThh24:miZ formatted string
    """
    # set timezone if datetime_ has no timezone
    if not datetime_.tzinfo:
        datetime_ = _timezone.localize(datetime_)

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
    querystring = "&".join(
        [str(x) + "=" + str(y) for x, y in query_params.items()]
    )
    if start:
        querystring += "&startdatetime={}".format(format_datetime(start))
    if end:
        querystring += "&enddatetime={}".format(format_datetime(end))

    # add report query
    querystring += "&" + report_query + "=" + report_name

    return "http://" + oasis_url + "?" + querystring


def download_files(url, destination_directory):
    """
    Downloads zipped files from url and saves to destination_directory. Returns
    a list of absolute file locations.

    :param url: (string)
    :param destination_directory: (string)
    :return: absolute paths of all files (list of strings)
    """

    # pull data from url and save to destination_directory
    response = requests.get(url)
    zipfile = ZipFile(BytesIO(response.content))
    zipfile.extractall(destination_directory)

    # return absolute paths of all files
    return [
        os.path.abspath(destination_directory) + "/" + x
        for x in zipfile.namelist()
    ]


def xml_to_dict(xml_path):
    """
    Converts an XML file to a Python dictionary.

    :param xml_path: path to XML file
    :return: dictionary
    """
    with open(xml_path) as f:
        return xmltodict.parse(f.read())


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
                            report_name: all_endpoints_dict[domain][path][
                                report_name
                            ]
                        }
                    }
                }
