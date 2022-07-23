#!/usr/bin/python

import glob
import json
from datetime import datetime

import bs4
import pandas as pd

def main():
    """
    Reads the QuoteBack export to my Downloads folder,
    and parses it using panda's to_html returning an index.html file.
    """

    # Definitely a better way of doing this, but for now it works
    export_directory = "/home/justin/Downloads/"
    qb_file = glob.glob(f"{export_directory}/*-quoteback.json")[-1]
    print(qb_file)

    with open(
        qb_file,
    ) as f:

        quotes = []

        data = json.load(f)
        for k, v in data.items():
            quote_title = v.get("title")
            quote_url = v.get("url")
            for q in v["quotes"]:
                quote_date = (
                    datetime.fromtimestamp(q.get("date") / 1000)
                    .replace(microsecond=0)
                    .isoformat()
                )
                quote_comment = q.get("comment")
                quote_text = q.get("text")

                quote = [quote_date, quote_title, quote_text, quote_comment, quote_url]
                quotes.append(quote)

    table = pd.DataFrame(
        quotes, columns=["DateTime", "Link", "Text", "Comments", "URL"]
    )
    table["DateTime"] = pd.to_datetime(table["DateTime"], infer_datetime_format=True)

    table["Date"] = table["DateTime"].dt.date
    table["Time"] = table["DateTime"].dt.time

    table["Text"] = table["Text"].apply(
        lambda x: bs4.BeautifulSoup(x, "lxml").get_text().replace("\n", " ")
    )
    table["Link"] = "<a href=" + table["URL"] + "><div>" + table["Link"] + "</div></a>"
    table = (table.drop(["URL", "DateTime", "Comments"], axis=1))
    table = table.set_index(["Date", "Link", "Time"]).sort_index(ascending=False)

    html_string = """
    <html>
    <head>
        <title>quotes.justin.vc</title>
        <link rel="shortcut icon" type="image/x-icon" href="favicon.ico">
    </head>
    <link rel="stylesheet" type="text/css" href="bootstrap.css"/>
    <body>
        {table}
    </body>
    </html>.
    """

    formatted_string = html_string.format(
        table=table.to_html(
            classes=[
                "table-bordered",
                "table-striped",
                "table-hover",
                "th",
            ],
            table_id="myTable",
            escape=False,
            col_space=100,
            index=True,
        )
    )

    with open("index.html", "w") as file:
        file.write(formatted_string)

if __name__ == "__main__":
    main()
