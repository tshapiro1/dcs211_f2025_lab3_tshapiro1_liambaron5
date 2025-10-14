#!/usr/bin/env python3
# dcs211_lab3.py 
#
# How to run (examples):
#   python dcs211_lab3.py --help
#   python dcs211_lab3.py false
#   python dcs211_lab3.py true dcs_minor_roster.html

import sys
import os
import csv
from bs4 import BeautifulSoup
from prettytable import PrettyTable

def usage() -> None:
    print(f"Usage: python {sys.argv[0]} [--help | true filename | false]")
    print("  --help          : print this help message and exit")
    print("  true filename   : parse the given HTML file and print a table of DCS minors")
    print("  false          : run built-in tests (no file needed)")
    print()
    print("Notes:")
    print("  - Requires: pip install beautifulsoup4 prettytable")
    print("  - The filename should be a local HTML file in the USGS format")
    print("  - If 'false' is given, no filename is needed or used")