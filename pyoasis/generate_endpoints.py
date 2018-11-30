import os
import pdftotext
import re


# get location of API docs
FILE_DIR = os.path.dirname(os.path.realpath(__file__))
OASIS_API_DOC = (
    FILE_DIR
    + "/api_docs/InterfaceSpecification_v4_3_5Clean_Spring2017Release.pdf"
)
ENDPOINT_FILE = FILE_DIR + "/endpoints/oasis_endpoints.txt"


def match_pages(search_string, oasis_api_doc=OASIS_API_DOC):
    """
    Return pages in oasis_api_doc matching search_string.

    :param search_string: string
    :param oasis_api_doc: location of OASIS API docs
    :return: list of pages (string) containing search_string
    """
    with open(oasis_api_doc, "rb") as f:
        pdf = pdftotext.PDF(f)

    return [x for x in pdf if search_string in x]


def scrape_endpoint_urls(
    min_page_num=47, max_page_num=65, oasis_api_doc=OASIS_API_DOC
):
    """
    This function makes a best attempt to extract endpoint urls from
    oasis_api_doc and returns found endpoints as a list. The list needs a
    final review since some of the data in the docs have irregular formatting.

    :param min_page_num: filter on minimum page number
    :param max_page_num: filter on maximum page number
    :param oasis_api_doc: location of OASIS API docs
    :return: list of found endpoints
    """
    with open(oasis_api_doc, "rb") as f:
        pdf = pdftotext.PDF(f)

    # get all endpoints with SingleZip or GroupZip
    endpoints = []
    for page_number, page in enumerate(pdf):
        if min_page_num <= page_number <= max_page_num:
            # clean up text between endpoints
            for regex in ["\n\s*OR", "\n\s*Note", "\n\s*NOTE"]:
                page = "".join(re.compile(regex).split(page))

            # remove newlines
            page = "".join(re.compile("\n\s+").split(page))

            # find all urls
            matches = re.findall("(?P<url>https?://[^\s]+)", page)

            # filter by SingleZip or GroupZip
            matches = [
                x
                for x in matches
                if ("GroupZip" in x and "groupid" in x)
                or ("SingleZip" in x and "queryname" in x)
            ]

            for string in matches:
                for url in string.split("http://"):
                    if url:
                        endpoints.append(url)

    return endpoints


def endpoint_to_dict(url):
    """
    Create a dictionary of domain, path, and params from endpoint.

    Example:
        oasis.caiso.com/oasisapi/SingleZip
        ?queryname=PRC_INTVL_LMP&startdatetime=20130919T07:00-0000
        &enddatetime=20130919T08:00-0000&version=2&market_run_id=RTM
        &node=LAPLMG1_7_B2

    Yields:
        {
            'domain': 'oasis.caiso.com',
            'path': '/oasisapi/SingleZip',
            'params': {
                'queryname': 'PRC_INTVL_LMP',
                'startdatetime': '20130919T07:00-0000',
                'enddatetime': '20130919T08:00-0000',
                'version': '2',
                'market_run_id': 'RTM',
                'node': 'LAPLMG1_7_B2'
            }
        }

    :param url: OASIS endpoint (string)
    :return: components of endpoint in a dictionary
    """
    endpoint_dict = {"domain": None, "path": None, "params": {}}

    # get domain
    domain = url.split("/")[0]
    endpoint_dict["domain"] = domain

    # get SingleZip or GroupZip value
    endpoint_dict["path"] = url.replace(domain, "").split("?")[0]

    # extract querystring params
    params = url.split("?")[-1]
    for key_value in params.split("&"):
        key, value = key_value.split("=")
        endpoint_dict["params"][key] = value

    return endpoint_dict


def create_endpoints_dict(endpoint_file=ENDPOINT_FILE):
    """
    Turns a file with OASIS endpoints into a dictionary organized by endpoint
    paths and params. The output of this function is used to generate
    endpoints/oasis_endpoints.json.

    :param endpoint_file: file of OASIS endpoints separated by newlines
    :return: dictionary
    """
    with open(endpoint_file, "r") as f:
        endpoints = [x for x in f.read().split("\n") if x]

    all_endpoints_dict = {}
    for endpoint in endpoints:
        endpoint_dict = endpoint_to_dict(endpoint)

        # initialize domain
        domain = endpoint_dict["domain"]
        if not all_endpoints_dict.get(domain):
            all_endpoints_dict[domain] = {}

        # initialize path
        path = endpoint_dict["path"]
        if not all_endpoints_dict[domain].get(path):
            all_endpoints_dict[domain][path] = {}

        # initialize report
        report = endpoint_dict["params"].get("queryname")
        if not report:
            report = endpoint_dict["params"].get("groupid")
        if not all_endpoints_dict[domain][path].get(report):
            all_endpoints_dict[domain][path][report] = {}

        # add params
        if not all_endpoints_dict[domain][path].get(report):
            all_endpoints_dict[domain][path][report] = []
        all_endpoints_dict[domain][path][report].append(
            endpoint_dict["params"]
        )

    return all_endpoints_dict
