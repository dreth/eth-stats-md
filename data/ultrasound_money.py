import requests


def ultrasound_get_eth_price() -> tuple[str, str, float]:
    # get the eth-price-stats
    stats = requests.get("https://ultrasound.money/api/v2/fees/eth-price-stats")
    stats = stats.json()

    # get the hourly change, timestamp and eth price
    return (
        f"{round(stats['h24Change'], 4)*100} %",
        stats["timestamp"],
        round(stats["usd"], 2),
    )


def ultraasound_get_average_eth_price() -> tuple[float, float, float]:
    # get the eth-price-stats
    stats = requests.get("https://ultrasound.money/api/v2/fees/average-eth-price")
    stats = stats.json()

    # get the eth price
    return tuple([round(stats[x], 2) for x in ["d1", "d7", "d30"]])


def ultrasound_get_curr_supply_and_supply_differential_since_merge() -> (
    tuple[float, float, float]
):
    # get the eth-price-stats
    stats = requests.get("https://ultrasound.money/api/v2/fees/supply-over-time")
    stats = stats.json()

    # get supply at merge
    supply_at_merge = round(stats["since_merge"][0]["supply"],2)

    # get current supply
    curr_supply = round(stats["since_merge"][-1]["supply"],2)

    # get the eth price
    return supply_at_merge, curr_supply, curr_supply - supply_at_merge
