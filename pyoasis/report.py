from cached_property import cached_property
from collections import OrderedDict
import itertools
import pandas as pd
import xmltodict

from .utils import xml_to_dict


class OASISReport:
    def __init__(self, xml_path):
        self.xml_path = xml_path
        self.filters = []

        self.report_dict = xml_to_dict(xml_path)

        if not self.error_key:
            self.normalize_report_dict()
            self.report_dataframe = self.to_dataframe()

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return (
            "OASISReport: "
            + self.xml_path
            + " filtered on "
            + str(self.filters)
        )

    @cached_property
    def master_key(self):
        """
        self.report_dict key at master level.
        """
        return [x for x in self.report_dict.keys()][0]

    @cached_property
    def payload_key(self):
        """
        self.report_dict key at MessagePayload level.
        """
        master_key = self.master_key

        for key in self.report_dict[master_key].keys():
            if "MessagePayload" in key:
                return key

    @cached_property
    def rto_key(self):
        """
        self.report_dict key at RTO level.
        """
        master_key = self.master_key
        payload_key = self.payload_key

        for key in self.report_dict[master_key][payload_key].keys():
            if "RTO" in key:
                return key

    @cached_property
    def error_key(self):
        """
        self.report_dict key if ERROR exists in report.
        """
        master_key = self.master_key
        payload_key = self.payload_key
        rto_key = self.rto_key

        for key in self.report_dict[master_key][payload_key][rto_key].keys():
            if "ERROR" in key:
                return key

        return None

    @cached_property
    def item_key(self):
        """
        self.report_dict key at ITEM level.
        """
        master_key = self.master_key
        payload_key = self.payload_key
        rto_key = self.rto_key

        if self.error_key:
            return None

        for key in self.report_dict[master_key][payload_key][rto_key].keys():
            if "ITEM" in key and key != "DISCLAIMER_ITEM":
                return key

        return None

    @cached_property
    def data_key(self):
        """
        self.report_dict key at DATA level.
        """
        master_key = self.master_key
        payload_key = self.payload_key
        rto_key = self.rto_key
        item_key = self.item_key

        if self.error_key:
            return None

        for key in self.report_dict[master_key][payload_key][rto_key][
            item_key
        ][0].keys():
            if "DATA" in key:
                return key

        return None

    @property
    def flattened_report_dict(self):
        """
        Creates a list of item OrderedDict values for easy ingestion into a
        pandas Dataframe.

        :return: list of OrderedDict values
        """
        master_key = self.master_key
        payload_key = self.payload_key
        rto_key = self.rto_key
        item_key = self.item_key
        data_key = self.data_key

        items = self.report_dict[master_key][payload_key][rto_key][item_key]

        # collapse all data values into list
        items = list(
            itertools.chain.from_iterable([x[data_key] for x in items])
        )

        return items

    def normalize_report_dict(self):
        """
        When there is only a single nested XML element, xmltodict does not put
        the value into a list, which makes parsing the data difficult. Any
        single nested XML elements are put into a list to fix this.

        A normalized report_dict has the following format:

        {
            master_key: {
                payload_key: {
                    rto_key: {
                        item_key: [
                            {
                                data_key: [
                                    interval_dict,
                                ]
                            },
                        ]
                    }
                }
            }
        }
        """
        master_key = self.master_key
        payload_key = self.payload_key
        rto_key = self.rto_key
        item_key = self.item_key

        updated_items = []
        data_key = None

        # nest item elements in a list
        if isinstance(
            self.report_dict[master_key][payload_key][rto_key][item_key],
            OrderedDict,
        ):
            self.report_dict[master_key][payload_key][rto_key][item_key] = [
                self.report_dict[master_key][payload_key][rto_key][item_key]
            ]

        # move single data element into list
        for item in self.report_dict[master_key][payload_key][rto_key][
            item_key
        ]:
            if not data_key:
                data_key = [x for x in item.keys() if "DATA" in x][0]
            if isinstance(item[data_key], OrderedDict):
                updated_items.append(
                    OrderedDict((x, [y]) for x, y in item.items())
                )
            else:
                updated_items.append(item)

        self.report_dict[master_key][payload_key][rto_key][
            item_key
        ] = updated_items

    def filter_report_dict(self, search_key, search_values=[]):
        """
        Filters message by search_key matching search_values. Updates
        self.report_dict and self.report_dataframe with updated values.

        :param search_key: key to search on
        :param search_values: list of values to match
        """
        master_key = self.master_key
        payload_key = self.payload_key
        rto_key = self.rto_key
        item_key = self.item_key
        data_key = self.data_key

        # filter data on search criteria
        item_list = []
        for item in self.report_dict[master_key][payload_key][rto_key][
            item_key
        ]:
            data_list = []
            for data in item[data_key]:
                if data[search_key] in search_values:
                    data_list.append(data)
            item_list.append({data_key: data_list})

        # update report_dict and report_dataframe
        self.report_dict[master_key][payload_key][rto_key][
            item_key
        ] = item_list
        self.report_dataframe = self.to_dataframe()
        self.filters.append({search_key: search_values})

    def to_dataframe(self):
        """
        Returns self.report_dict as a pandas Dataframe.
        """
        return pd.DataFrame(self.flattened_report_dict)

    def to_xml(self):
        """
        Returns self.report_dict as XML.
        """
        return xmltodict.unparse(self.report_dict, pretty=True)
