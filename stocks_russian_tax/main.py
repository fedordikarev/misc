import argparse
from email import header
import json
from typing import Any, Dict, List
from datetime import datetime as dt


def parse_args():
    parser = argparse.ArgumentParser(
        description="Calculate russian tax for Stocks vested after relocation out of Russia")
    parser.add_argument("grant_date", help="Date when stocks were granted")
    parser.add_argument("relocate_date", help="Date when moved out of Russia")
    parser.add_argument(
        "vestings", nargs="+", help="Vestings in format 'date:amount'")
    parser.add_argument("--tax_rate", default=13.0, type=float)

    return parser.parse_args()


def read_usd_rates(fname: str = 'usd_rates.json') -> Dict[str, float]:
    try:
        with open(fname, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        # TODO: load from CBR
        # https://www.cbr.ru/scripts/XML_dynamic.asp?date_req1=01/01/2021&date_req2=01/01/2022&VAL_NM_RQ=R01235
        import xml.etree.ElementTree as ET
        mytree = ET.parse("usd_rates.xml")
        myroot = mytree.getroot()
        out = dict()
        for rec in myroot.findall("Record"):
            date = dt.strptime(rec.get("Date"), "%d.%m.%Y").strftime("%Y-%m-%d")
            value = float(rec.find("Value").text.replace(",", "."))
            out[date] = value

        with open(fname, "w") as f:
            json.dump(out, f, indent=2)
        # print(out)
        return out


def read_stock_prices(fname: str = 'goog_prices.json') -> Dict[str, float]:
    try:
        with open(fname, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        # TODO: load from MarketStack
        # https://marketstack.com/documentation#historical_data
        # 'http://api.marketstack.com/v1/eod?symbols=GOOG&access_key={access_key}&date_from=2021-01-02&date_to=2022-01-01&limit=200'.format(access_key=os.GetEnv('MARKETSTACK_ACCESS_KEY'))
        # MarketStack return only last 6 months (maybe due to "Free account")
        # So get price from Nasdaq Historical Data instead
        out = dict()
        import csv
        with open("HistoricalData_1650108691369.csv", "r") as f:
            f.readline() # Skip header
            hist_data = csv.reader(f)
            for rec in hist_data:
                # print(rec)
                date = dt.strptime(rec[0], "%m/%d/%Y").strftime("%Y-%m-%d")
                value = float(rec[1][1:])
                out[date] = value
        """
        with open("goog_full.json", "r") as f:
            stocks_data = json.load(f)
        for rec in stocks_data['data']:
            date = rec['date'].split("T", 2)[0]
            value = float(rec['close'])
            out[date] = value
        """
        with open(fname, "w") as f:
            json.dump(out, f, indent=2)

        return out


def make_calc(args: argparse.Namespace, stock_prices: Dict[str, float], usd_rates: Dict[str, float]) -> List[Any]:
    beg_date = dt.strptime(args.grant_date, "%Y-%m-%d")
    move_date = dt.strptime(args.relocate_date, "%Y-%m-%d")

    days_in_Russia = (move_date - beg_date).days
    print(days_in_Russia)
    out = list()
    total = dict(
        date="Total",
        stocks_amount=0.0,
        rub_for_Russia=0.0,
        russian_tax=0.0,
    )
    for rec in args.vestings:
        date, s_amount = rec.split(":")
        amount = float(s_amount)
        delta = (dt.strptime(date, "%Y-%m-%d") - beg_date).days
        rus_amount = amount*days_in_Russia/delta
        rus_price  = rus_amount*stock_prices[date]
        rub_price  = rus_price*usd_rates[date]
        russian_tax = rub_price*args.tax_rate/100
        out_rec = dict(
            date=date,
            stocks_amount=amount,
            stocks_price=amount*stock_prices[date],
            part_for_Russia=rus_amount,
            usd_for_Russia=rus_price,
            rub_for_Russia=rub_price,
            russian_tax=russian_tax,
        )
        total['stocks_amount'] += amount
        total['rub_for_Russia'] += rub_price
        total['russian_tax'] += russian_tax
        out.append(out_rec)
    out.append(total)
    return out


def main():
    args = parse_args()

    stock_prices = read_stock_prices()
    usd_rates = read_usd_rates()
    result = make_calc(args, stock_prices, usd_rates)

    try:
        import tabulate
        print("Tabulate")
        print(tabulate.tabulate(result, headers="keys", floatfmt="7.2f"))
    except ModuleNotFoundError:
        print(result)


if __name__ == "__main__":
    main()
