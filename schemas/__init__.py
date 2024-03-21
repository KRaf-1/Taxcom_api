from pydantic import BaseModel


class KKTResponse(BaseModel):
    reg_number: str
    number: str
    fn_number: str
    doc_date: str
    params: int | None = 0
    keys_count: int | None = 0
    status: str


class TTResponse(BaseModel):
    name: str
    kkt_list: list[KKTResponse]
