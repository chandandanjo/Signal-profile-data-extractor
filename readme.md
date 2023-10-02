# Signal Profile Extractor

This Python script is designed to extract information about investors from the [Signal](https://signal.nfx.com/) website. It performs the following tasks:

1. Extracts category links from the Signal website.
2. Extracts person IDs for each category.
3. Extracts detailed information about each person using their IDs.

## Prerequisites

Before running the script, make sure you have the following Python libraries installed:

- requests
- BeautifulSoup (bs4)
- lxml

You can install these libraries using pip:

```bash
pip install requests beautifulsoup4 lxml
```

## Usage

1. Clone this repository to your local machine or download the script.
2. Make sure you have the required libraries installed.
3. Run the script using the following command:

```bash
python signal_extractor.py
```

## Output

The script will generate two JSON files:

1. `ids.json`: Contains a list of person IDs extracted from the website.
2. `output.json`: Contains detailed information about each investor, including their name, Signal profile link, firm name, title, location, social media links, firm website, investment preferences, and more.

## Note

- The script uses multithreading to improve efficiency. You can adjust the number of threads by modifying the `max_workers` parameter in the `ThreadPoolExecutor` instances.
- The `output.json` file will contain information for all investors extracted from the website.

Please be respectful of website terms of use and API usage policies when using this script for data extraction.
