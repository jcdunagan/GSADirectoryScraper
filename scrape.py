#!/usr/bin/env python3
"""scrape.py: Scrapes contacts from GSA Search Directory. Writes JSON to file."""
__author__= "John Dunagan"
__email__= "jcdunagan@wustl.edu"

import json
import sys
from string import ascii_uppercase

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

from parse import parse_html

# Where to write output
OUTPUT_FILE = 'data.json'

# Preferred Selenium browser. Should work with Chrome or Firefox
BROWSER = webdriver.Chrome

# Webpage-specific information
TARGET_URL = 'https://gsa.gov/portal/staffDirectory/searchStaffDirectory'
MAX_RESULTS = 250
SEARCH_FIELD_ID = 'lastName'
SEARCH_BUTTON_CLASS = 'gsa-primary-btn'

# Extended to include O'Brien and Day-Lewis, etc
EXTENDED_ALPHABET = ascii_uppercase + '\'-'

def name_crawler(search_function, output, first=True, stem=''):
    """Iterates through alphabet, feeding into search_function.
    If search_function returns more than MAX_RESULTS for a letter,
    search depth is increased for that letter ("D"--> "DA"-"DZ")"""

    # NOTE: assumes last names always BEGIN with a letter,
    # but apostrophes, and hyphens may appear later
    charset = ascii_uppercase if first else EXTENDED_ALPHABET

    total = 0
    for c in charset:
        tag = stem + c
        results = search_function(tag)
        size = len(results)

        if size >= MAX_RESULTS:
            print('%s: maxed out...' % tag)
            total += name_crawler(search_function, output, False, tag)
        else:
            print('%s: %d entries' % (tag, size))
            output.write(json.dumps(results, indent=4))
            total += size

    return total

def command_click(driver, button):
    """Command-click action chain for opening in new window"""
    chain = ActionChains(driver)
    chain.key_down(Keys.SHIFT)
    chain.click(button)
    chain.key_up(Keys.SHIFT)
    chain.perform()

if __name__ == '__main__':
    # Load browser
    driver = BROWSER()
    driver.implicitly_wait(15)

    # Load search page, locate elements
    driver.get(TARGET_URL)
    root_handle = driver.current_window_handle

    search_field = driver.find_element_by_id(SEARCH_FIELD_ID)
    search_button = driver.find_element_by_class_name(SEARCH_BUTTON_CLASS)

    with open(OUTPUT_FILE, 'w') as target_file:

        # Create routine to be run by name_crawler
        def search_for(key):
            search_field.clear()
            search_field.send_keys(key)
            command_click(driver, search_button)

            # NOTE little hack-ish, but can't find anything better in the API
            # (the search results open in a window with the same title)
            for handle in driver.window_handles:
                if handle != root_handle:
                    # any handle that isn't the root_handle
                    new_window = handle

            # extract results from new window
            driver.switch_to_window(new_window)
            results = parse_html(driver.page_source)

            # Close window, switch back to search page
            driver.close()
            driver.switch_to_window(root_handle)

            return results

        # Begin crawling
        total = name_crawler(search_for, target_file)

    # Close search window, report
    driver.close()
    print('Completed. Wrote %d entries to \'%s\'' % (total, OUTPUT_FILE))
