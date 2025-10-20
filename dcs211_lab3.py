#!/usr/bin/env python3  
 
# How to run (examples):
#   python dcs211_lab3.py --help
#   python dcs211_lab3.py false 
#   python dcs211_lab3.py true two_minors_only.html 
#   python dcs211_lab3.py true five_minors_only.html
#   python dcs211_lab3.py true dcs_minor_roster.html

import sys
import os
import csv
from bs4 import BeautifulSoup
from prettytable import PrettyTable
from Student import Student

def usage() -> None:
    '''Print usage message for the program.'''
    print(f"Usage: python {sys.argv[0]} <write CSV? False/True> <optional: HTML filename>")
    print()
    print("Notes:")
    print("  - Requires: pip install beautifulsoup4 prettytable")
    print("  - The filename should be a local HTML file in the USGS format")
    print("  - If 'false' is given, no filename is needed or used") 

### Write CSV Function:  

def writeCSV(students: list[Student], filename: str) -> None:
    '''
    Write a list of Student objects to a CSV file.
    
    Parameters:
        students: list of Student objects to write
        filename: name of the CSV file to create
    '''
    # Open a new CSV file for writing
    file = open(filename, 'w', newline='')
    
    # Create a CSV writer object
    writer = csv.writer(file)
    
    # Write the header row
    writer.writerow(['Last Name', 'First Name', 'Email', 'Year', 'Majors', 'Minors', 'GECs', 'Advisor'])
    
    # Write each student as a row
    for student in students:
        # Get the student data as a list
        student_data = student.getCSVList()
        # Write this row to the CSV
        writer.writerow(student_data)
    
    # Close the file
    file.close()
    
    print(f"CSV file '{filename}' created successfully!")


### Main Code:   

def parseMinors(soup: BeautifulSoup) -> tuple[dict[str, list[Student]], dict[str, list[Student]]]:
    ''' 
    Parse a BeautifulSoup object and extract student information into two dictionaries.
    Parameters:
        soup: (BeautifulSoup) the parsed HTML object
    Returns:
        tuple containing:
            - dict[str, list[Student]]: dictionary with year as key, list of Students as value
            - dict[str, list[Student]]: dictionary with advisor as key, list of Students as value
    '''
    
    # Find the table with student data (it has id="studentList")
    table = soup.find('table', id='studentList')
    
    # Find where the actual student rows are
    tbody = table.find('tbody') # type: ignore
    
    # Find all the rows (each row is a student)
    rows = tbody.find_all('tr')  # type: ignore
    
    # Create dictionaries to store students by year and by advisor
    by_year = {}
    by_advisor = {}
    
    # Loop through each row and extract student information
    for row in rows:
        # Find all the cells (td tags) in this row
        cells = row.find_all('td')
        # Extract the student name (it's in the 2nd cell, index 1)
        name = cells[1].text.strip()
        # Extract the class year (it's in the 4th cell, index 3)
        year = cells[3].text.strip()
        # Extract the email (it's in the 6th cell, index 5, inside an 'a' tag)
        email_link = cells[5].find('a')
        if email_link is not None:
            email = email_link.text.strip()
        else:
            email = ""
        
        # Extract majors (7th cell, index 6, has abbr tags)
        majors_cell = cells[6]
        major_tags = majors_cell.find_all('abbr')
        majors = []
        for major_tag in major_tags:
            major_name = major_tag.get('title')
            majors.append(major_name)
        
        # Extract minors (8th cell, index 7, has abbr tags)
        minors_cell = cells[7]
        minor_tags = minors_cell.find_all('abbr')
        minors = []
        for minor_tag in minor_tags:
            minor_name = minor_tag.get('title')
            minors.append(minor_name)
        
        # Extract GECs (9th cell, index 8, has abbr tags)
        gecs_cell = cells[8]
        gec_tags = gecs_cell.find_all('abbr')
        gecs = []
        for gec_tag in gec_tags:
            gec_name = gec_tag.get('title')
            gecs.append(gec_name)
        
        # Extract advisor name (10th cell, index 9)
        advisor_cell = cells[9]
        # Get the hidden span which has the advisor name (fix as it was previously printing duplicate advisor names)
        advisor_span = advisor_cell.find('span')
        advisor = advisor_span.text.strip() # type: ignore
        
        # Create a Student object with all the extracted information
        student = Student(name, email, year, majors, minors, gecs, advisor)
        
        # Add the student to the by_year dictionary
        if year in by_year:
            by_year[year].append(student)
        else:
            by_year[year] = [student]
        
        # Add the student to the by_advisor dictionary
        if advisor in by_advisor:
            by_advisor[advisor].append(student)
        else:
            by_advisor[advisor] = [student]
    
    # Return the two dictionaries as a tuple
    return (by_year, by_advisor)


def printOutput(by_year: dict[str, list[Student]], by_advisor: dict[str, list[Student]], write_csv: bool) -> None:
    '''
    Print output based on the parsed data - either CSV files or tables to screen.
    
    Parameters:
        by_year: dictionary with year as key, list of Students as value
        by_advisor: dictionary with advisor as key, list of Students as value
        write_csv: if True, write CSV files; if False, print tables to screen
    '''
    if write_csv:
        # Write one CSV file per graduation year
        for year in sorted(by_year.keys()):
            filename = f"dcs_minors_{year}.csv"
            print(f"Writing {filename}...")
            writeCSV(by_year[year], filename)
    else:
        # Print three tables to the screen
        
        # Table 1: All students sorted by year, then by name
        student_table = PrettyTable()
        student_table.field_names = ["Student", "Email", "Year", "Major(s)", "Minor(s)", "Advisor"]
        student_table.align["Student"] = 'l'  # left-align
        student_table.align["Email"] = 'l'
        student_table.align["Major(s)"] = 'l'
        student_table.align["Minor(s)"] = 'l'
        student_table.align["Advisor"] = 'l'
        
        for year in sorted(by_year.keys()):
            # Sort students by name within each year
            sorted_students = sorted(by_year[year], key=lambda s: s._name)
            for student in sorted_students:
                student_table.add_row([
                    student._name,
                    student._email,
                    student._year,
                    ','.join(student._majors),
                    ','.join(student._minors),
                    student._advisor
                ])
        print(student_table)
        
        # Table 2: Number of DCS minors per year
        year_table = PrettyTable()
        year_table.field_names = ["Year", "# DCS Minors"]
        for year in sorted(by_year.keys()):
            year_table.add_row([year, len(by_year[year])])
        print(year_table)
        
        # Table 3: Number of DCS minors per advisor (sorted by last name)
        advisor_table = PrettyTable()
        advisor_table.field_names = ["Advisor", "# DCS Minors"]
        # Sort advisors by last name (split on comma and use first part)
        sorted_advisors = sorted(by_advisor.keys(), key=lambda name: name.split(',')[0])
        for advisor in sorted_advisors:
            advisor_table.add_row([advisor, len(by_advisor[advisor])])
        print(advisor_table)


def main() -> None:
    '''
    Main function that handles command-line arguments and runs the program.
    '''
    # Check if user wants help
    if len(sys.argv) >= 2 and sys.argv[1] == "--help":
        usage()
        sys.exit(0)
    
    # Check if we have at least one argument
    if len(sys.argv) < 2:
        print("Error: Not enough arguments")
        usage()
        sys.exit(1)
    
    # Get the first argument (write CSV? true/false) and handle case-insensitivity
    write_csv_str = sys.argv[1].title()  # Converts to "True" or "False"
    try:
        write_csv = bool(eval(write_csv_str))
    except:
        print(f"Error: First argument must be 'true' or 'false', got '{sys.argv[1]}'")
        usage()
        sys.exit(1)
    
    # Determine the HTML filename to use
    html_filename = ""
    
    if len(sys.argv) >= 3:
        # User provided a filename
        html_filename = sys.argv[2]
    else:
        # No filename provided - find HTML files and let user choose
        all_files = os.listdir()
        html_files = sorted([f for f in all_files if f.endswith('.html')])
        
        if len(html_files) == 0:
            print("Error: No HTML files found in current directory")
            sys.exit(1)
        
        print("HTML files found:")
        for html_file in html_files:
            print(f"  {html_file}")
        
        # Prompt user for choice (use first file as default)
        default_file = html_files[0]
        user_input = input(f"Enter name of HTML source (return for default '{default_file}'): ")
        
        if user_input.strip() == "":
            html_filename = default_file
        else:
            html_filename = user_input.strip()
    
    # Try to open and read the HTML file
    try:
        file = open(html_filename, 'r')
        html_content = file.read()
        file.close()
    except FileNotFoundError:
        print(f"Error: File '{html_filename}' cannot be read or does not exist")
        sys.exit(1)
    except Exception as e:
        print(f"Error: Cannot read file '{html_filename}': {e}")
        sys.exit(1)
    
    # Create a BeautifulSoup object
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Parse the HTML and get the two dictionaries
    by_year, by_advisor = parseMinors(soup)
    
    # Call printOutput to handle all output
    printOutput(by_year, by_advisor, write_csv)

if __name__ == "__main__":
    main()





