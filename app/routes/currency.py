from fastapi import APIRouter, HTTPException
import requests

router = APIRouter(tags=["Currency"])


@router.get("/currency-rates")
def get_currency_rates():

    try:
        url = "https://api.exchangerate-api.com/v4/latest/INR"

        response = requests.get(url)

        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to fetch currency rates")

        data = response.json()

        rates = data["rates"]

        return {
            "base_currency": "INR",
            "USD": rates["USD"],
            "EUR": rates["EUR"],
            "GBP": rates["GBP"]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
