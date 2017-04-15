#!/usr/bin/env python3
"""parse.py: Extracts contacts from HTML of GSA Directory search results"""
__author__= "John Dunagan"
__email__= "jcdunagan@wustl.edu"
# https://github.com/jcdunagan/GSADirectoryScraper

from bs4 import BeautifulSoup
import re

# Various string cleaners
clean_name = lambda x: re.sub('[\t\n ]+', ' ', x).strip()
clean_dep_code = lambda x: re.sub('[()]', '', x).strip()
clean_dep_title = lambda x: x.strip()
clean_addr = clean_name

con_string_valid = lambda x: bool(re.search('\w+', x)) and not x.endswith(';')
clean_con_key = lambda x: x.replace(':', '').strip()
clean_con_value = clean_dep_title


def parse_row(tr):
    """Extract single entry from row"""
    person = dict()

    # Extract name and department from name span
    name_span = tr.find("span", "name")
    if name_span:
        # Assumes every name string contains comma
        last, first = name_span.contents[0].split(',')
        person['firstname'] = clean_name(first)
        person['lastname'] = clean_name(last)


        # Extract department code (i.e. M1AG)
        # QUESTION: what are these codes officially called?
        if name_span.span:
            code = clean_dep_code(name_span.span.string)
            title = clean_dep_title(name_span.span['title'])
            person['department'] = {'code': code, 'title': title}

    # Extract address and position from address span
    address_span = tr.find("span", "address")
    if address_span:
        # Separate into lines and clean up excess whitespace
        address_strings = list(map(clean_addr, address_span.stripped_strings))

        lines = len(address_strings)
        if lines == 1:
            # 1 line means it's somebody's position with no address
            person['position'] = address_strings[0]
        elif lines == 2:
            # 2 lines means it's an address with no title
            person['address'] = address_strings[:]
        elif lines > 2:
            # 3 lines, we can assume first is position, next 2 are address
            person['position'], *person['address'] = address_strings
            # 4 lines is unanticipated, but information WILL be extracted

    # Extract various contact info from number span
    number_span = tr.find("span", "number")
    if number_span:
        contacts = dict()

        # Eliminate empties and 'nbsp;'
        stripped = list(filter(con_string_valid, number_span.stripped_strings))

        # Find labels of form "Phone:" or "Email:"
        keys = [(i,s) for i,s in enumerate(stripped) if s.endswith(':')]

        for i, s in keys:
            # Next entry should be value
            contacts[clean_con_key(s)] = clean_con_value(stripped[i+1])

        person['contacts'] = contacts

    return person

def parse_table(table):
    """Extract contacts from table"""
    return list(map(parse_row, table.tbody.find_all('tr')))


def parse_html(html_doc):
    """Extract contacts from page source"""
    soup = BeautifulSoup(html_doc, 'html.parser')

    if not soup.table or soup.find(class_='bg-warning'):
        return []
    else:
        return parse_table(soup.table)


if __name__ == '__main__':
    with open('sample.html','r') as f:
        html_doc = f.read()

    persons = parse_html(html_doc)
    for p in persons:
        print(p['lastname'])
