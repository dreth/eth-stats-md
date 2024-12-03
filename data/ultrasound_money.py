import logging as log

import pandas as pd
import requests


def ultrasound_get_eth_price() -> tuple[str, str, float]:
    # get the eth-price-stats
    stats = requests.get("https://ultrasound.money/api/v2/fees/eth-price-stats")
    stats = stats.json()

    # get the hourly change, timestamp and eth price
    return (
        round(stats["h24Change"] * 100, 3),
        stats["timestamp"],
        round(stats["usd"]),
    )


def ultrasound_get_average_eth_price() -> tuple[float, float, float]:
    # get the eth-price-stats
    stats = requests.get("https://ultrasound.money/api/v2/fees/average-eth-price")
    stats = stats.json()

    # get the eth price
    return tuple([round(stats[x]) for x in ["d1", "d7", "d30"]])


def ultrasound_get_curr_supply_and_supply_differential_since_merge() -> (
    tuple[float, float, float]
):
    # get the eth-price-stats
    stats = requests.get("https://ultrasound.money/api/v2/fees/supply-over-time")
    stats = stats.json()

    # get supply at merge
    supply_at_merge = stats["since_merge"][0]["supply"]

    # get current supply
    curr_supply = stats["since_merge"][-1]["supply"]

    # supply differential
    supply_diff = curr_supply - supply_at_merge

    # get the eth price
    return (
        stats["since_merge"][0]["supply"],
        stats["since_merge"][-1]["supply"],
        supply_diff,
    )


def generate_ultrasound_df() -> tuple[pd.DataFrame, str]:
    # get ultrasound stats
    log.info("Getting the Ethereum price from ultrasound.money")
    eth_price_diff_24h, timestamp, eth_price = ultrasound_get_eth_price()

    log.info("Getting the average Ethereum price from ultrasound.money")
    eth_avg_1d, eth_avg_7d, eth_avg_30d = ultrasound_get_average_eth_price()

    log.info(
        "Getting the current supply and supply differential since merge from ultrasound.money"
    )
    eth_supply_at_merge, eth_curr_supply, eth_supply_diff = (
        ultrasound_get_curr_supply_and_supply_differential_since_merge()
    )

    # create the dataframe
    tbl = pd.DataFrame(
        {
            "Metric": [
                "Current ETH price",
                "24h change (%)",
                "Average ETH price over 1 day",
                "Average ETH price over 7 days",
                "Average ETH price over 30 days",
                "Supply at merge",
                "Current supply",
                "Supply differential since merge",
                "Total inflation since merge (%)",
            ],
            "Value": [
                eth_price,
                eth_price_diff_24h,
                eth_avg_1d,
                eth_avg_7d,
                eth_avg_30d,
                int(round(eth_supply_at_merge)),
                int(round(eth_curr_supply)),
                int(round(eth_supply_diff)),
                round(eth_supply_diff / eth_supply_at_merge * 100, 3),
            ],
        }
    )
    
    tbl["Value"] = tbl["Value"].astype(int)

    # return the dataframe
    return tbl, timestamp
