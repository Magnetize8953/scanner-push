"""
This is a bit of a mess. It's a quick and dirty solution to automating grabbing CCI Events scanner data.
The goal is to download the csv, parse it for student information, and use that to mark attendance.

Before running, ensure you have environment variables set for NINERNET_USER and NINERNET_PASS and
that your account has manager permission for the CCI Events spaces you're planning on downloading from.
Set these at the OS level or in a `.env` file next to this one.
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
from canvasapi import Canvas
from typing import Dict, List
from datetime import date
import datetime
import os


"""
a function to load the cci events page and download scanner data

space_id - id number of the cci events space
scanner_delta - amount of time, in minutes, to look back in the scanner data from time of running
driver_timeout - amount of time, in seconds, to wait before timing out webpage loads
"""
def download_scanner_data(space_id: int, scanner_delta: int, driver_timeout: int):
    # set up dotenv
    load_dotenv()

    # set up selenium
    options = webdriver.FirefoxOptions()
    # options.addArguments("-headless")
    driver = webdriver.Firefox(options=options)
    wait = WebDriverWait(driver, timeout=driver_timeout)

    # open cci-events
    print("opening cci-events page...")
    driver.get("https://cci-events.charlotte.edu/")

    # get to ninernet login
    wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "block")))

    # load page
    print("opening ninernet login page...")
    driver.find_element(By.CLASS_NAME, "block").click()
    wait.until(EC.title_contains("Web Authentication"))

    # load ninernet page information
    wait.until(EC.element_to_be_clickable((By.ID, "username")))
    username = driver.find_element(By.ID, "username")
    password = driver.find_element(By.ID, "password")
    submit_button = driver.find_element(By.ID, "shibboleth-login-button")

    # enter login info
    print("logging in...")
    username.send_keys(str(os.getenv("NINERNET_USER")))
    password.send_keys(str(os.getenv("NINERNET_PASS")))
    submit_button.click()

    # wait for duo to load
    wait.until(EC.title_is(""))
    # wait for duo auth
    print("waiting for duo 2fa...")
    wait.until(EC.element_to_be_clickable((By.ID, "dont-trust-browser-button")))
    driver.find_element(By.ID, "dont-trust-browser-button").click()
    print("duo 2fa authenticated")

    # wait for spaces list to load
    print("waiting for spaces page...")
    wait.until(EC.url_matches("https://cci-events.charlotte.edu/spaces"))

    # download daily report
    # time in eastern time
    # time format: YYYY/MM/DD+HH:MM
    today = date.strftime(date.today(), "%Y/%m/%d")
    start_time = date.strftime(datetime.datetime.now() - datetime.timedelta(minutes=scanner_delta), '%H:%M')
    end_time = date.strftime(datetime.datetime.now(), '%H:%M')
    download_link = f"https://cci-events.charlotte.edu/spaces/{space_id}/report/daily-sign-ins/download?start_time={today}+{start_time}&end_time={today}+{end_time}"
    print("downloading file...")
    driver.execute_script(f"window.location.href='{download_link}'")
    print(download_link)

    # exit selenium
    print("quitting selenium...")
    driver.quit()


def get_canvas_sections() -> Dict[int, int]:
    # set up dotenv
    load_dotenv()

    # set up canvas
    canvas = Canvas("https://uncc.instructure.com", str(os.getenv("CANVAS_API_KEY")))
    course = canvas.get_course(int(str(os.getenv("CANVAS_COURSE_ID"))))

    # loop through sections and add the section's number and id to a dict
    sections = {}
    for section in course.get_sections():
        section = str(section)
        section_num = int(section[10:13])
        section_id = int(section[-7:-1])
        sections[section_num] = section_id

    return sections

def get_section_students(section_num: int) -> Dict[str, int]:
    # set up dotenv
    load_dotenv()

    # set up canvas
    canvas = Canvas("https://uncc.instructure.com", str(os.getenv("CANVAS_API_KEY")))
    sections = get_canvas_sections()
    section_enrollment = canvas.get_section(sections[section_num]).get_enrollments(role=["StudentEnrollment"])
    # information on returned objects
    # https://canvas.instructure.com/doc/api/enrollments.html#Enrollment

    # loop through enrollments for the section and add student ninernet ids and canvas ids to a dict
    students = {}
    for student in section_enrollment:
        if student is not None and student.user["name"] != "Test Student":
            # NOTE: login_id is only visible with certain permissions on the Canvas account
            students[student.user["login_id"]] = int(student.user_id)

    return students


def read_scanner_data_file(file_name: str) -> List[str]:
    # open file and remove header
    with open(file_name, "r") as file:
        entries = file.readlines()
    entries.pop(0)

    # loop through scanner data entries and add user ids (login_ids) to a list
    user_ids = []
    for entry in entries:
        user_ids.append(entry[0:entry.index("@")])

    return user_ids


def get_valid_attendance(section_num: int, file_name: str) -> List[int]:
    # get data
    scanner_data = read_scanner_data_file(file_name)
    section_students = get_section_students(section_num)

    # loop through scanner data entries and add students actually in the section to a list
    valid_students_ids = []
    for entry in scanner_data:
        if entry in section_students:
            valid_students_ids.append(section_students[entry])

    return valid_students_ids


def push_attendance_to_canvas(assignment_id: int, section_num: int, file_name: str):
    # set up dotenv
    load_dotenv()

    # set up canvas
    canvas = Canvas("https://uncc.instructure.com", str(os.getenv("CANVAS_API_KEY")))

    # get student attendance
    attendance = get_valid_attendance(section_num, file_name)

    # loop through attendance data and create dict of grades
    grades = {}
    for student in attendance:
        grades[str(student)] = {"posted_grade": "complete"}

    # push grades to canvas
    # bulk grade is needed to grade assignments without submissions
    # https://community.canvaslms.com/t5/Canvas-Developers-Group/Grading-an-assignment-without-a-submission/m-p/160140
    canvas.get_section(section_num).submissions_bulk_update(grade_data={str(assignment_id): grades})


if __name__ == "__main__":
    space_id = 10 # woodward is 10, cone is 9
    download_scanner_data(space_id, 5, 60)
else:
    print("this really shouldn't be run as an import")
