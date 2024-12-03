import logging as log
import os
from datetime import datetime, timezone

from data.farside import return_consolidated_etf_tables
from data.ultrasound_money import generate_ultrasound_df


# Generate the markdown text for the comment
def generate_comment() -> str:
    # wrap the commands in a try block to catch any exceptions

    try:
        # get the ultrasound stats consolidated tables
        ultrasound_summary, timestamp = generate_ultrasound_df()

        # get the ETF tables
        tbl_legend, tbl_data, summary_table = return_consolidated_etf_tables()

        # generate all the tables in markdown format
        tbl_legend = tbl_legend.to_markdown(index=False)
        tbl_data = tbl_data.to_markdown(index=False)
        summary_table = summary_table.to_markdown(index=False)
        ultrasound_summary = ultrasound_summary.to_markdown(index=False)
        
    except Exception as e:
        log.error(f"An error occurred: {e}")
        return None

    return f"""
# ETH stats

UTC Timestamp: **{timestamp}**

## Price and supply

{ultrasound_summary}

## ETF Flow (in millions of USD)

### Summary

{summary_table}

### Basic ETF info

{tbl_legend}

### ETF Flow (last 3 days)

{tbl_data}

#### Sources

- [ultrasound.money](https://ultrasound.money)
- [farside.co.uk](https://farside.co.uk/eth)
- [farside.co.uk ETH ETF full historical tables](https://farside.co.uk/ethereum-etf-flow-all-data/)

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
