import time
from datetime import datetime
import csv
from multiprocessing.pool import ThreadPool

from schemas import KKTResponse, TTResponse
from services.taxcom.taxcom_tt import TaxcomTT
from services.taxcom.taxcom_kkt import TaxcomKKT
from services.taxcom.taxcom_shift import TaxcomShift
from services.taxcom.taxcom_doc import TaxcomDoc

taxcom_tt = TaxcomTT()
taxcom_kkt = TaxcomKKT()
taxcom_shift = TaxcomShift()
taxcom_doc = TaxcomDoc()


def working_with_threadpool(kkt_list: list) -> list:
    # threads = [threading.Thread(target=get_kkt_response, args=(tt_data, )) for tt_data in tt_list]
    response_list = []
    with ThreadPool(12) as pool:
        # call a function on each item in a list and handle results
        for doc_list in pool.map(get_kkt_response, kkt_list):
            print(f"add from thread: {doc_list}")
            response_list.append(doc_list)
    print(f"Total list response is {response_list}")
    return response_list


def get_tt_response(tt_object) -> TTResponse:
    start_all_tt = time.time()
    kkt_list = taxcom_kkt.get_filtered_list(tt_object["id"])
    print(f"TT name is {tt_object.get("name")}")
    print("==============================")
    print(f"len of kkt_list: ({len(kkt_list)})")
    kkt_list = working_with_threadpool(kkt_list)
    print(f"TT time is: {time.time() - start_all_tt} ({tt_object.get('name')})")
    return TTResponse(name=tt_object.get("name"), kkt_list=kkt_list)


def get_kkt_response(kkt_object):
    start = time.time()
    kkt_info = taxcom_kkt.get_info(kkt_object["fnFactoryNumber"])
    print(f"kkt_info is {kkt_info}")
    shift_list = taxcom_shift.get_list(
        kkt_object["fnFactoryNumber"],
        kkt_info["fnRegDateTime"],
        kkt_info["lastDocumentDateTime"],
    )
    pd_number_list, last_check_id = taxcom_doc.get_pd_numbers(
        kkt_object["fnFactoryNumber"], shift_list
    )
    numbers_for_check, last_pd_number = taxcom_doc.get_numbers_for_check(
        pd_number_list
    )
    print(f"numbers_for_check is {numbers_for_check}")
    # print(f"last_pd_number is {last_pd_number}")
    current_doc = taxcom_doc.find_current(
        kkt_object["fnFactoryNumber"],
        numbers_for_check,
        last_pd_number,
        last_check_id,
    )
    # print(f"Current doc is {current_doc}")
    report_date, kkt_params, keys_number = taxcom_doc.get_params_keys_number(current_doc)
    print(f"KKT time is: {time.time() - start}")
    return KKTResponse(
        reg_number=kkt_info.get("kktRegNumber"),
        number=kkt_info.get("kktFactoryNumber"),
        fn_number=kkt_object["fnFactoryNumber"],
        doc_date=report_date,
        params=kkt_params,
        keys_count=keys_number,
        status=kkt_info.get("cashdeskState")
    )


def get_docs_params_from_tt_list():
    start = datetime.now()
    tt_list = taxcom_tt.get_filtered_tt()
    print(f"Len of tt_list is {len(tt_list)}")
    doc_list = []
    for tt_object in tt_list:
        doc_list.append(get_tt_response(tt_object))
    save_data_in_file(doc_list)
    print("Data saved to file")
    print(f"Total time is {datetime.now() - start}")


def save_data_in_file(data: list[TTResponse]):
    print(f"data is {data}")
    with open("params_new.csv", "w", encoding="utf-8-sig", newline="\n") as file:
        writer = csv.writer(file, delimiter=";")
        writer.writerow(("Название", "Рег. номер", "Номер ККТ",  "Номер ФН",  "Дата документа",  "Параметры",  "Кол-во ключей",  "Статус"))
        for row in data:
            print(f"row is {row} {type(row)}")
            for kkt in row.kkt_list:
                writer.writerow((row.name, kkt.reg_number, kkt.number, kkt.fn_number, kkt.doc_date, kkt.params, kkt.keys_count, kkt.status))


if __name__ == "__main__":
    get_docs_params_from_tt_list()
