import logging as log
import re
from io import StringIO

import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options


def get_eth_etf_table() -> tuple[pd.DataFrame, pd.DataFrame]:
    # Set up Firefox WebDriver with headless mode
    options = Options()
    options.headless = True

    # Initialize WebDriver
    driver = webdriver.Firefox(options=options)

    try:
        # Open the target website
        driver.get("https://farside.co.uk/eth/")

        # Wait for the table to load (if necessary)
        driver.implicitly_wait(10)

        # Find the table element by class name
        table_element = driver.find_element(By.CLASS_NAME, "etf")

        # Get the table's HTML
        table_html = table_element.get_attribute("outerHTML")

        # Convert the HTML table to a pandas DataFrame
        df = pd.read_html(StringIO(table_html))[0]
        tbl_legend, tbl_data = process_dataframes(df)

        return tbl_legend, tbl_data
    finally:
        # Ensure the browser quits in all cases
        driver.quit()


def process_dataframes(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    # modify the columns so that col1 is properly named
    cols = df.columns
    new_cols = [x for x in cols]
    new_cols[0] = ("Entity", "Ticker", "Fee")
    new_cols[-1] = ("Total", "", "")
    df.columns = pd.MultiIndex.from_tuples(new_cols)

    # create a 'legend' dataframe with the name of the ETFs, tickers and seed
    tbl_legend = pd.DataFrame(
        {
            "Entity": [x[0] for x in df.columns],
            "Ticker": [x[1] for x in df.columns],
            "Fee": [x[2] for x in df.columns],
            "Seed": df.iloc[0],
        }
    ).iloc[1:-1]
    tbl_legend.index = range(1, len(tbl_legend) + 1)

    # create a table with the data
    tbl_data = df.iloc[2:]
    tbl_data.columns = ["Date"] + list(tbl_legend["Ticker"].values.tolist()) + ["Total"]
    tbl_data.index = range(1, len(tbl_data) + 1)

    # Add total flow to the legend table
    tbl_data[tbl_data["Date"] == "Total"]
    tbl_legend["Flow"] = [
        tbl_data.loc[tbl_data["Date"] == "Total", x].values[0]
        for x in tbl_legend["Ticker"].unique()
    ]
    tbl_legend["Flow"] = tbl_legend["Flow"].apply(
        lambda x: float(convert_accounting_str_format_to_float(x))
    )

    # Remove rows with zero flow
    tbl_data = tbl_data.loc[tbl_data["Total"] != "0.0"]

    # parse dates
    tbl_data["Date"] = pd.to_datetime(
        tbl_data["Date"], format="%d %b %Y", errors="coerce"
    )

    # remove last col (contains total flow, which is already present in the legend table)
    tbl_data = tbl_data.iloc[:-1]

    # format dates, e.g. Nov 5
    tbl_data["Date"] = tbl_data["Date"].dt.strftime("%Y-%m-%d")

    # sort by date
    tbl_data_sorted = tbl_data.sort_values("Date")

    # get the last 3 dates
    last_3_dates = tbl_data["Date"].tail(3)
    df_last3 = tbl_data_sorted[tbl_data["Date"].isin(last_3_dates)]

    # melt the data
    df_melted = df_last3.melt(id_vars="Date", var_name="Ticker", value_name="Value")
    df_melted = df_melted[df_melted["Ticker"] != "Total"]

    # pivot the table in a more readable format
    df_pivoted = {
        "Ticker": df_melted["Ticker"].unique(),
    }

    # add values to the pivoted table
    # totals = {"Ticker":"All (Total)"}
    for date in df_melted["Date"].unique():
        df_pivoted[date] = df_melted[df_melted["Date"] == date]["Value"].values
        df_pivoted[date] = [
            float(convert_accounting_str_format_to_float(x)) for x in df_pivoted[date]
        ]

        # gather per-column totals
        # totals = totals | {date: sum(df_pivoted[date])}

    # add the total sum of totals to totals
    # totals = totals | {"Total": sum([x for x in totals.values() if x != "All (Total)"])}

    # create a dataframe
    df_pivoted = pd.DataFrame(df_pivoted)
    df_pivoted["Total"] = df_pivoted[
        [x for x in df_pivoted.columns if x != "Ticker"]
    ].sum(axis=1)

    # drop rows with fully zero flow
    tbl_data = df_pivoted.loc[df_pivoted["Total"] != 0]

    # replace back the ticker names with the entity names in the data table
    tbl_data["Ticker"] = tbl_data["Ticker"].apply(
        lambda x: tbl_legend.loc[tbl_legend["Ticker"] == x, "Entity"].values[0]
    )

    # add the totals - I'm not sure if this is necessary, but I'll keep it in the code in case I use it
    # the lines relevant to it are commented out above too
    # tbl_data = pd.concat([tbl_data, pd.DataFrame(totals, index=[max(tbl_data.index) + 1])])

    # rename the ticker column to entity
    tbl_data = tbl_data.rename(columns={"Ticker": "Entity"})

    return tbl_legend, tbl_data


def convert_accounting_str_format_to_float(value: str) -> float:
    return re.sub(r"\((.*?)\)", r"-\1", value.replace("-", "0.0").replace(",", ""))


def return_consolidated_etf_tables() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    # get etf tables
    log.info("Getting the ETF table from farside.co.uk")
    tbl_legend, tbl_data = get_eth_etf_table()
    total_flow = round(tbl_legend["Flow"].sum(), 2)
    total_flow_3d = round(tbl_data["Total"].sum(), 2)
    total_flow_last_recorded_day = round(tbl_data.iloc[:, 3].sum(), 2)

    # summary table
    summary_table = pd.DataFrame(
        {
            "Metric": [
                "Total ETF Flow",
                "Total ETF Flow over the last 3 days",
                "Total ETF Flow on the last recorded day",
            ],
            "Value": [
                total_flow,
                total_flow_3d,
                total_flow_last_recorded_day,
            ],
        }
    )

    # return the tables
    return tbl_legend, tbl_data, summary_table
