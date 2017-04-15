# GSADirectoryScraper
Small scraper for extracting JSON from [GSA Staff Directory](https://gsa.gov/portal/staffDirectory/searchStaffDirectory). Made for April 14, 2017 DataRefuge at Washington University.

## Motivation

DataRefuge marked GSA Staff Directory as vulnerable.  Contact info is only returned through search queries, with a limit of 250 results per search, obstructing extraction. 

## Requirements

- Python 3
- [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/)
- [Selenium](https://pypi.python.org/pypi/selenium)

## Details

### Files

- scrape.py: uses Selenium to procedurally query
- parse.py: uses BeautifulSoup to extract listings from returned html

### How It Works

Selenium controls a browser and begins searching alphabetically single letters in the last name field.  The directory returns all last names that begin with that letter, but truncates to the first 250 results.  If 250 results are returned for a given letter, the scraper concludes that there are likely more than 250 entries, and increases search depth for that particular letter.  For example, if 'D' returns 250 results, the scraper will begin searching 'DA' through 'DZ' and compile these results instead.  Likewise, if 'DE' returns 250 results, then 'DEA' through 'DEZ' are traversed instead.

If a query returns less than 250 names, the results are parsed using BeautifulSoup4, and written to a JSON file.

