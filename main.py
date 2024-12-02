import logging as log
import os
from datetime import datetime, timezone

from data.farside import get_eth_etf_table
from data.ultrasound_money import (
    ultraasound_get_average_eth_price,
    ultrasound_get_curr_supply_and_supply_differential_since_merge,
    ultrasound_get_eth_price,
)


# Generate the markdown text for the comment
def generate_comment() -> str:
    # wrap the commands in a try block to catch any exceptions

    try:
        # get ultrasound stats
        log.info("Getting the Ethereum price from ultrasound.money")
        eth_price, timestamp, eth_price = ultrasound_get_eth_price()

        log.info("Getting the average Ethereum price from ultrasound.money")
        eth_avg_1d, eth_avg_7d, eth_avg_30d = ultraasound_get_average_eth_price()

        log.info(
            "Getting the current supply and supply differential since merge from ultrasound.money"
        )
        eth_supply_at_merge, eth_curr_supply, eth_supply_diff = (
            ultrasound_get_curr_supply_and_supply_differential_since_merge()
        )

        # get etf tables
        log.info("Getting the ETF table from farside.co.uk")
        tbl_legend, tbl_data = get_eth_etf_table()
        total_flow = round(tbl_legend["Flow"].sum(), 2)
        total_flow_3d = round(tbl_data["Total"].iloc[-3:].sum(), 2)
        total_flow_last_recorded_day = round(tbl_data.iloc[:, 3].sum(), 2)
        tbl_legend = tbl_legend.to_markdown(index=False)
        tbl_data = tbl_data.to_markdown(index=False)
    except Exception as e:
        log.error(f"An error occurred: {e}")
        return None

    return f"""
# ETH stats

- UTC Timestamp: {timestamp}

## Price and supply

Source: https://ultrasound.money

- Current ETH price: {eth_price} USD
- Average ETH price over 1 day: {eth_avg_1d} USD
- Average ETH price over 7 days: {eth_avg_7d} USD
- Average ETH price over 30 days: {eth_avg_30d} USD

- Supply at merge: {eth_supply_at_merge} ETH
- Current supply: {eth_curr_supply} ETH
- Supply differential since merge: {eth_supply_diff} ETH
- Total inflation (%) since merge: {round(eth_supply_diff / eth_supply_at_merge * 100,3)}%

## ETF Flow (in millions of USD)

- Total ETF Flow: {total_flow} million USD
- Total ETF Flow over the last 3 days: {total_flow_3d} million USD
- Total ETF Flow on the last recorded day: {total_flow_last_recorded_day} million USD

Source: https://farside.co.uk/eth

Full historical table: https://farside.co.uk/ethereum-etf-flow-all-data/

### Basic ETF info

{tbl_legend}

### ETF Flow (last 3 days)

{tbl_data}
    """


if __name__ == "__main__":
    # save the comment to a markdown file with its timestamp in UTC
    with open(
        os.path.join(
            "generated", f"eth_stats-{datetime.now(timezone.utc).isoformat()}.md"
        ),
        "w",
    ) as f:
        # generate the information
        log.info("Generating information")
        comment = generate_comment()

        # if the comment is None, exit the program
        if comment is None:
            log.error("Error: Exiting program")
            exit(1)

        # write the information to the file
        f.write(comment)
        log.info("Markdown file generated successfully")
