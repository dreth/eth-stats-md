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
        tbl_data.columns = (
            ["Date"] + list(tbl_legend["Entity"].values.tolist()) + ["Total"]
        )
        tbl_data.index = range(1, len(tbl_data) + 1)

        return tbl_legend, tbl_data
    finally:
        # Ensure the browser quits in all cases
        driver.quit()
