"""
This is a bit of a mess. It's a quick and dirty solution to automating grabbing CCI Events scanner data.
The goal is to download the csv, parse it for student information, and use that to mark attendance.

Before running, ensure you have environment variables set for NINERNET_USER, NINERNET_PASS, 
CANVAS_API_KEY, and CANVAS_COURSE_ID.
Make sure that your NinerNet account has Manager role for the CCI Events spaces you're planning on
downloading from.
The Canvas account also needs to have permissions to grade and view SIS data (e.g. the professor).

Set these at the OS level or in a `.env` file next to this one.
"""

import scanner
import canvas
import time
import os
import argparse

parser = argparse.ArgumentParser(prog='Scanner Push', description="a quick and dirty solution to automating grabbing CCI Events scanner data")
parser.add_argument('location', choices=['cone', 'woodward'], help='the building location of the section')
parser.add_argument('assignment_id', type=int, help='the canvas id for the attendance assignment being graded')
parser.add_argument('section_num', type=int, help='the number for the course section being checked')
parser.add_argument('-t', '--time_modifier', default=1, type=float, help='modifier to the amount of time the scanner looks back')
args = parser.parse_args()

if __name__ == "__main__":
    # woodward is 10, cone is 9
    if args.location == 'woodward':
        space_id = 10
        file_name = "Woodward 120 Fall Term 2024_sign_in_export.csv"
    else:
        space_id = 9
        file_name = "Cone 175 Fall Term 2024_sign_in_export.csv"

    scanner.download_scanner_data(space_id, 60*args.time_modifier)

    # wait for file to download
    while file_name not in os.listdir():
        time.sleep(5)
        print('\twaiting for download...')

    canvas.push_attendance_to_canvas(args.assignment_id, args.section_num, file_name)
