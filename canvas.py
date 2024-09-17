from dotenv import load_dotenv
from canvasapi import Canvas
from typing import Dict, List
import os

# set up dotenv
load_dotenv()
if os.getenv("CANVAS_API_KEY") is None or os.getenv("CANVAS_API_KEY") == "":
    raise NameError("CANVAS_API_KEY not set")
if os.getenv("CANVAS_COURSE_ID") is None or os.getenv("CANVAS_COURSE_ID") == "":
    raise NameError("CANVAS_COURSE_ID not set")

# set up canvas
canvas = Canvas("https://uncc.instructure.com", os.getenv("CANVAS_API_KEY"))
course = canvas.get_course(int(str(os.getenv("CANVAS_COURSE_ID"))))

"""
get course sections from canvas

returns a dictionary with section numbers as keys and section ids as values
"""
def get_canvas_sections() -> Dict[int, int]:

    # loop through sections and add the section's number and id to a dict
    sections = {}
    for section in course.get_sections():
        section = str(section)
        section_num = int(section[10:13])
        section_id = int(section[-7:-1])
        sections[section_num] = section_id

    return sections


"""
get students from a canvas course section

returns a dictionary with student login_ids as keys and user_ids as values

section_num - number of section to get students from
"""
def get_section_students(section_num: int) -> Dict[str, int]:

    # get section data
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


"""
read in the scanner data csv and get the login_ids of students

returns a list of student login_ids

file_name - name of the scanner data file
"""
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


"""
filter scanner data for students actually in the section

returns a list of student user_ids

section_num - number of section to get students from
file_name - name of the scanner data file
"""
def get_valid_attendance(section_num: int, file_name: str) -> List[int]:

    # get data
    scanner_data = read_scanner_data_file(file_name)
    section_students = get_section_students(section_num)

    # remove duplicates from scanner data
    scanner_data = list(set(scanner_data))

    # loop through scanner data entries and add students actually in the section to a list
    valid_students_ids = []
    for entry in scanner_data:
        if entry in section_students:
            valid_students_ids.append(section_students[entry])

    return valid_students_ids


"""
push grades to canvas

assignment_id - id of assignment to be graded
section_num - number of section to get students from
file_name - name of the scanner data file
"""
def push_attendance_to_canvas(assignment_id: int, section_num: int, file_name: str) -> None:

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

