import requests
import json
import random
from datetime import datetime

"""fetch country data """

async def fetch_countries():

    try:
        url = "https://restcountries.com/v2/all?fields=name,capital,region,population,flag,currencies"

        response = requests.get(url, timeout = 5)
        country_data = response.json()

        return country_data
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail={
                "error": "External data source unavailable", 
                "details": f"Could not fetch data from {https://restcountries.com/v2/all?fields=name,capital,region,population,flag,currencies}"
            }
        )

async def fetch_countries_with_rates():

    try:
        url = "https://open.er-api.com/v6/latest/USD"

        rates_response = requests.get(url, timeout = 5)
        rates_data = rates_response.json()
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail={
                "error": "External data source unavailable", 
                "details": f"Could not fetch data from {https://restcountries.com/v2/all?fields=name,capital,region,population,flag,currencies}"
            }
        )

    country_data = await fetch_countries()

    rates = rates_data.get("rates", {})

    results = []
    for country in country_data:
        name = country.get("name")
        capital = country.get("capital")
        region= country.get("region")
        population = country.get("population")
        currencies = country.get("currencies", [])
        flag = country.get("flag")


        currency_code = None
        exchange_rate = None
        estimated_gdp = 0


        if currencies and len(currencies) > 0:
            currency_code = currencies[0].get("code")

            rate = rates.get(currency_code)

            if rate:
                exchange_rate = rate
                estimated_gdp = (population * random.randint(1000, 2000) / exchange_rate)
            else:
                exchange_rate = None
                estimated_gdp = None
        else:
            currency_code = None
            exchange_rate = None
            estimated_gdp = 0 
        
        results.append({
            "name": name,
            "capital": capital,
            "region": region,
            "population": population, 
            "currency_code": currency_code,
            "exchange_rate": exchange_rate,
            "estimated_gdp": estimated_gdp,
            "flag_url": flag,
            "last_refreshed_at": datetime.utcnow().isoformat()
        })

    return results

