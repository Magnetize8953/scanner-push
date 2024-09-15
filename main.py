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

if __name__ == "__main__":
    # woodward is 10, cone is 9
    space_id = 10
    scanner.download_scanner_data(space_id, 60)

    file_name = ""
    if space_id == 10:
        file_name = "Woodward 120 Fall Term 2024_sign_in_export.csv"
    elif space_id == 9:
        file_name = "Cone 175 Fall Term 2024_sign_in_export.csv"

    # canvas.push_attendance_to_canvas(-1, -1, file_name)
