from services.taxcom.taxcom import Taxcom


class TaxcomTT(Taxcom):
    def get_list(self):
        return list(self._get("OutletList").get("records"))[:13]

    def get_info(self, id_tt):
        return self._get("OutletInfo", params={"id": id_tt}).get("outlet")

    def get_filtered_tt(self):
        filtered_list = []
        for tt_object in self.get_list():
            tt_info = self.get_info(tt_object["id"])
            if int(tt_info.get("cashdeskCount")) > int(
                tt_info.get("cashdeskStateSummary", {}).get("kktProblemCount", 0)
            ):
                filtered_list.append(tt_info)
        return filtered_list
