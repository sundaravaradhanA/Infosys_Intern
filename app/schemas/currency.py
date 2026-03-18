from pydantic import BaseModel

class CurrencyConvertRequest(BaseModel):
    from_currency: str
    to_currency: str
    amount: float


class CurrencyConvertResponse(BaseModel):
    from_currency: str
    to_currency: str
    amount: float
    converted_amount: float
    exchange_rate: float