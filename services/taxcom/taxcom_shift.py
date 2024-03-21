from services.taxcom.taxcom import Taxcom


class TaxcomShift(Taxcom):
    def get_list(self, fn, begin, end):
        return self._get(
            "ShiftList",
            params={
                "fn": fn,
                "begin": begin,
                "end": end,
            },
        ).get("records")
