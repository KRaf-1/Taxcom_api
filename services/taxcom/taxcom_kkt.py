from services.taxcom.taxcom import Taxcom


class TaxcomKKT(Taxcom):
    def get_list(self, tt_id):
        return self._get("KKTList", params={"id": tt_id}).get("records")

    def get_info(self, fn):
        return self._get("KKTInfo", params={"fn": fn}).get("cashdesk")

    def get_filtered_list(self, tt_id):
        filtered_list = []
        kkt_list = self.get_list(tt_id)
        for kkt_object in kkt_list:
            if (
                kkt_object["kktFactoryNumber"].startswith("0128")
                and kkt_object["cashdeskState"] == "Active"
                # and kkt_object["kktFactoryNumber"] == "0128060990"
            ):
                filtered_list.append(kkt_object)
        return filtered_list

    def get_filtered_list_by_status(self, tt_id):
        filtered_list = []
        kkt_list = self.get_list(tt_id)
        for kkt_object in kkt_list:
            if (
                # kkt_object["kktFactoryNumber"].startswith("0128") and
                kkt_object["cashdeskState"]
                != "Inactive"
            ):
                filtered_list.append(kkt_object)
        return filtered_list
