# Scanner Push

This is a bit of a mess. It's a quick and dirty solution to automating grabbing CCI Events scanner data.
The goal is to download the csv, parse it for student information, and use that to mark attendance.

## Prerequisites
Before running, ensure you have environment variables set for `NINERNET_USER`, `NINERNET_PASS`, 
`CANVAS_API_KEY`, and `CANVAS_COURSE_ID`.

Make sure that your NinerNet account has Manager role for the CCI Events spaces you're planning on
downloading from.
The Canvas account also needs to have permissions to grade and view SIS data (e.g. the professor).

Set these at the OS level or in a `.env` file in the same directory as this project.

## Running
_to be written_
