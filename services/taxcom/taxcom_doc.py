from services.taxcom.taxcom import Taxcom
from collections.abc import Iterable


tag_mapper = {
    "1012": "Дата формирования отчета",
    # "1013": "Заводской номер ККТ",
    "1213": "Количество оставшихся ключей",
    "1290": "Параметры работы ККТ",
}


class TaxcomDoc(Taxcom):
    def get_list(self, fn, shift):
        return self._get(
            "DocumentList", params={"fn": fn, "shift": shift, "type": 2}
        ).get("records")

    def get_info(self, fn, fd):
        return self._get("DocumentInfo", params={"fn": fn, "fd": fd})

    def get_pd_numbers(self, fn, shift_list) -> tuple[list, int | None]:
        last_check_id = None
        list_first_last_pd_number = []
        if len(shift_list) > 0:
            # shift_list = [
            #     shift_object.get("shiftNumber")
            #     for shift_object in shift_list
            #     # if shift_object["closeDateTime"] is not None
            # ]
            for shift in shift_list:
                min_max_tuple = self.get_docs_first_last_pd_numbers(
                    fn, shift.get("shiftNumber")
                )
                if not shift.get("closeDateTime"):
                    # print(f"shift is {shift}")
                    last_check_id, _ = min_max_tuple
                else:
                    list_first_last_pd_number.append(min_max_tuple)
        return list_first_last_pd_number, last_check_id

    def get_docs_first_last_pd_numbers(self, fn, shift):
        docs_list = self._get("DocumentList", params={"fn": fn, "shift": shift}).get(
            "records"
        )
        # print(f"docs_list.values() is {docs_list}")
        fd_number_list = [fd_number.get("fdNumber") for fd_number in docs_list]
        # print(f"fd_number_list is {fd_number_list}")
        return min(fd_number_list), max(fd_number_list)

    @staticmethod
    def get_numbers_for_check(list_first_last_pd_number):
        pd_numbers_for_check = [1]
        last_pd_number = None
        if len(list_first_last_pd_number):
            for idx in range(len(list_first_last_pd_number)):
                if idx == 0:
                    prev_number = 1
                else:
                    prev_item = list_first_last_pd_number[idx - 1]
                    prev_number = prev_item[1]
                current_item = list_first_last_pd_number[idx]
                # print(f"current {current_item[0]} and prev is {prev_number}")
                dp_diff = current_item[0] - prev_number
                if dp_diff > 1:
                    # print(dp_diff)
                    for out_of_range in range(1, dp_diff):
                        pd_numbers_for_check.append(prev_number + out_of_range)
                if idx == len(list_first_last_pd_number) - 1:
                    last_pd_number = current_item[1]
        return pd_numbers_for_check, last_pd_number

    def find_current(self, fn, pd_numbers_for_check, last_pd_number, last_check_id):
        print(
            f"fn is {fn}, pd_numbers_for_check is {pd_numbers_for_check}, last_pd_number is {last_pd_number}, last_check_id is {last_check_id}"
        )
        current_doc_type = None
        for pd_numbers in pd_numbers_for_check:
            try:
                doc_from_response = self.get_info_by_type(fn, pd_numbers)
                print(f"doc_from_response is {doc_from_response}")
            except Exception as err:
                print(f"pd_numbers_for_check error: {err}")
                break
            if doc_from_response:
                current_doc_type = doc_from_response
            print(current_doc_type)
        start_check_out_of_range = (
            last_pd_number if last_pd_number else max(pd_numbers_for_check)
        )
        # print(f"start_check_out_of_range is {start_check_out_of_range}")
        while True:
            start_check_out_of_range += 1
            if last_check_id and last_check_id == start_check_out_of_range:
                break
            # print(f"out of range check: {start_check_out_of_range}")
            try:
                out_of_range_document = self.get_info_by_type(
                    fn, start_check_out_of_range
                )
            except Exception as err:
                print(f"error is {err}")
                break
            if out_of_range_document:
                current_doc_type = out_of_range_document
        # self.print_mapped_info(current_doc_type)
        print(f"current_doc_type is {current_doc_type}")
        return current_doc_type

    # def get_docs_first_last_pd_numbers(self, fn, shift):
    #     docs_list = self._get("DocumentList", params={"fn": fn, "shift": shift}).get(
    #         "records"
    #     )
    #     # print(f"docs_list.values() is {docs_list}")
    #     fd_number_list = [fd_number.get("fdNumber") for fd_number in docs_list]
    #     # print(f"fd_number_list is {fd_number_list}")
    #     return min(fd_number_list), max(fd_number_list)

    def get_params_keys_number(self, doc_info):
        report_date, params_value, keys_number_value = None, None, None
        if doc_info:
            for key in tag_mapper.keys():
                doc_value = self.get_recursively(doc_info, key)
                if key == "1012":
                    report_date = doc_value
                elif key == "1213":
                    keys_number_value = doc_value
                else:
                    params_value = doc_value
                # print(f"{value}: {doc_value}")
        return report_date, params_value, keys_number_value

    def get_info_by_type(self, fn, fd):
        doc_response = self._get("DocumentInfo", params={"fn": fn, "fd": fd})
        print(f"doc_response is {doc_response}")
        if doc_response:
            print(f"doc_response_type is {doc_response.get("documentType")}")
            if doc_response.get("documentType") in ('1', '11'):
                return doc_response.get("document", {})
        else:
            raise Exception("404 error")

    def get_recursively(self, search_dict, field):
        """
        Takes a dict with nested lists and dicts,
        and searches all dicts for a key of the field
        provided.
        """

        # fields_found = []

        for key, value in search_dict.items():
            if key == field:
                return value

            elif isinstance(value, dict):
                results = self.get_recursively(value, field)
                for result in results:
                    return result

            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        more_results = self.get_recursively(item, field)
                        if more_results:
                            if isinstance(more_results, Iterable):
                                for another_result in more_results:
                                    return another_result
                            return more_results


# fn = "7281440500468769"
# pd_numbers_for_check = [1, 2, 7]
# last_pd_number = 18511
# last_check_id = 18512
#
#
# TaxcomDoc().find_current(
#     fn=fn,
#     pd_numbers_for_check=pd_numbers_for_check,
#     last_pd_number=last_pd_number,
#     last_check_id=last_check_id,
# )
