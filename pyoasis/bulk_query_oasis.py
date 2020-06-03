import json
import os

from .utils import create_oasis_url, download_files, get_report_params


# get location of oasis_endpoints.json file
FILE_DIR = os.path.dirname(os.path.realpath(__file__))
OASIS_ENDPOINTS_JSON = FILE_DIR + "/oasis_endpoints.json"


def generate_test_oasis_urls(start=None, end=None, report_name=None):
    """
    Generates a list of all OASIS endpoint urls scraped from API docs with
    custom start and end datetimes.

    :param start: start (datetime)
    :param end: end (datetime)
    :param report_name: filter sample endpoints by report_name
    :return: list of urls
    """
    endpoint_urls = []

    # load endpoint params into dictionary
    if report_name:
        endpoints_dict = get_report_params(report_name)
    else:
        with open(OASIS_ENDPOINTS_JSON) as f:
            endpoints_dict = json.load(f)

    for domain, path_dict in endpoints_dict.items():
        for path, report_dict in path_dict.items():
            for report, param_dicts in report_dict.items():
                for param_dict in param_dicts:
                    # delete start datetime from sample params
                    if param_dict.get("startdatetime"):
                        del param_dict["startdatetime"]

                    # delete end datetime from sample params
                    if param_dict.get("enddatetime"):
                        del param_dict["enddatetime"]

                    # delete report name from sample params
                    if param_dict.get("queryname"):
                        del param_dict["queryname"]
                    if param_dict.get("groupid"):
                        del param_dict["groupid"]

                    # generate url
                    endpoint_urls.append(
                        create_oasis_url(report, start, end, query_params=param_dict)
                    )

    return endpoint_urls


def download_all_oasis_reports(start, end, destination_directory, report_name=None):
    """
    Downloads all OASIS reports from a certain time period. This is a heavy
    query on the OASIS API and should only be run seldomly for validation
    purposes.

    From OASIS API docs:
    Recommended Usage

    By observing the Publication and Revisions Log and Publication Schedule
    reports, users can submit the requests more efficiently. We strongly
    recommend first to find out whether the data is already published to the
    OASIS database. Once the required data is published then submit the
    requests for the required reports. This way the user can eliminate
    unnecessary requests for the required data.

    :param start: start datetime
    :param end: end datetime
    :param destination_directory: location to store downloaded reports
    :param report_name: filter sample endpoints by report_name
    :param oasis_endpoints_json: JSON file containing all sample endpoints
    """
    oasis_urls = generate_test_oasis_urls(start, end, report_name)

    for url in oasis_urls:
        print("\n", url)
        try:
            downloaded_files = download_files(url, destination_directory)
        except Exception:
            print("COULD NOT DOWNLOAD FILE: ", url)
            continue

        if any([x for x in downloaded_files if "INVALID_REQUEST.xml" in x]):
            print("INVALID URL: ", url)
            continue
