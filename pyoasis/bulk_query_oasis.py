import json
import os

from .utils import create_oasis_url, download_files


# get location of oasis_endpoints.json file
FILE_DIR = os.path.dirname(os.path.realpath(__file__))
OASIS_ENDPOINTS_JSON = FILE_DIR + "/endpoints/oasis_endpoints.json"


def generate_test_oasis_urls(
    start=None, end=None, oasis_endpoints_json=OASIS_ENDPOINTS_JSON
):
    """
    Generates a list of all OASIS endpoint urls scraped from API docs with
    custom start and end datetimes.

    :param start: start (datetime)
    :param end: end (datetime)
    :param oasis_endpoints_json: location of OASIS endpoints in JSON format
    :return: list of urls
    """
    endpoint_urls = []

    # load endpoint params into dictionary
    with open(oasis_endpoints_json) as f:
        all_endpoints_dict = json.load(f)

    for domain, path_dict in all_endpoints_dict.items():
        for path, report_dict in path_dict.items():
            for report, param_dict in report_dict.items():
                # delete start datetime from sample params
                if param_dict.get("startdatetime"):
                    del (param_dict["startdatetime"])

                # delete end datetime from sample params
                if param_dict.get("enddatetime"):
                    del (param_dict["enddatetime"])

                # delete report name from sample params
                if param_dict.get("queryname"):
                    del (param_dict["queryname"])
                if param_dict.get("groupid"):
                    del (param_dict["groupid"])

                # generate url
                endpoint_urls.append(
                    create_oasis_url(
                        report, start, end, query_params=param_dict
                    )
                )

    return endpoint_urls


def download_all_oasis_reports(
    start,
    end,
    destination_directory,
    oasis_endpoints_json=OASIS_ENDPOINTS_JSON,
):
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
    :param oasis_endpoints_json: JSON file containing all sample endpoints
    """
    oasis_urls = generate_test_oasis_urls(oasis_endpoints_json, start, end)

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
