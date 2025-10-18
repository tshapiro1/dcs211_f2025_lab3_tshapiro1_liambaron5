#!/usr/bin/env python3  
 
# How to run (examples):
#   python dcs211_lab3.py --help
#   python dcs211_lab3.py false
#   python dcs211_lab3.py true dcs_minor_roster.html

import sys
import os
import csv
from bs4 import BeautifulSoup
from prettytable import PrettyTable
from Student import Student

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

def parseHTML(filename: str) -> list[Student]:
    ''' 
    Parse an HTML file and extract student information into Student objects.
    Parameters:
        filename: (str) path to the HTML file to parse
    Returns:
        list[Student]: a list of Student objects extracted from the HTML
    ''' 

    # Open and read the HTML file
    file = open(filename, 'r')
    html_content = file.read()
    file.close()
    
    # Create a BeautifulSoup object to parse the HTML
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find the table with student data (it has id="studentList")
    table = soup.find('table', id='studentList')
    
    # Find where the actual student rows are
    tbody = table.find('tbody') # type: ignore
    
    # Find all the rows (each row is a student)
    rows = tbody.find_all('tr')  # type: ignore
    
    # Create an empty list to store Student objects
    students = []
    
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
        # The advisor name is in plain text after a hidden span
        advisor = advisor_cell.text.strip()
        
        # Create a Student object with all the extracted information
        student = Student(name, email, year, majors, minors, gecs, advisor)
        
        # Add the student to our list
        students.append(student)
    
    # Return the list of students
    return students

def main() -> None:
    '''
    Main function that handles command-line arguments and runs the program.
    '''
    # Check if user wants help
    if len(sys.argv) == 2 and sys.argv[1] == "--help":
        usage()
        return
    
    # Check if we have the right number of arguments
    if len(sys.argv) < 2:
        print("Error: Not enough arguments")
        usage()
        return
    
    # Get the first argument (write CSV? true/false)
    write_csv = sys.argv[1].lower()
    
    # Check if it's "false" (just test/display mode)
    if write_csv == "false":
        print("Running in test mode (no CSV output)")
        print("\nTesting with 'two_minors_only.html'...")
        
        # Parse the test file
        students = parseHTML('two_minors_only.html')
        
        # Print how many students we found
        print(f"\nFound {len(students)} students:")
        print("-" * 80)
        
        # Print each student
        for student in students:
            print(student)
        
        print("-" * 80)
        return
    
    # Check if it's "true" (CSV output mode)
    elif write_csv == "true":
        # Make sure we have a filename
        if len(sys.argv) < 3:
            print("Error: You must provide an HTML filename when using 'true'")
            usage()
            return
        
        # Get the filename
        filename = sys.argv[2]
        
        # Check if file exists
        if not os.path.exists(filename):
            print(f"Error: File '{filename}' not found")
            return
        
        print(f"Parsing '{filename}'...")
        
        # Parse the HTML file
        students = parseHTML(filename)
        
        # Print how many students we found
        print(f"Found {len(students)} students")
        
        # Display the students in a table
        print("\nStudent roster:")
        print("-" * 80)
        for student in students:
            print(student)
        print("-" * 80)
        
        # Write to CSV file
        csv_filename = "dcs_minors.csv"
        writeCSV(students, csv_filename)
    
    else:
        print(f"Error: First argument must be 'true' or 'false', got '{write_csv}'")
        usage()
        return

if __name__ == "__main__":
    main()





