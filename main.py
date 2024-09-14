"""
This is a bit of a mess. It's a quick and dirty solution to automating grabbing CCI Events scanner
data.
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from dotenv import load_dotenv
from datetime import date
import datetime
import os

# TODO: set up dotenv
load_dotenv()

# set up selenium
options = webdriver.FirefoxOptions()
# options.addArguments("-headless")
driver = webdriver.Firefox(options=options)
wait = WebDriverWait(driver, timeout=60)

def main():

    # open cci-events
    driver.get("https://cci-events.charlotte.edu/")
    print("opening cci-events page...")

    # get to ninernet login
    try:
        wait.until(lambda d: driver.find_element(By.CLASS_NAME, "block"))
    except TimeoutError:
        print("cci-events timed out")
        driver.quit()
        return

    # load page
    driver.find_element(By.CLASS_NAME, "block").click()
    wait.until(lambda d: driver.title != "Events")
    print("opening ninernet login page...")

    # load ninernet page information
    try:
        wait.until(lambda d: driver.find_element(By.ID, "username"))
    except TimeoutError:
        print("ninernet timed out")
        driver.quit()
        return
    username = driver.find_element(By.ID, "username")
    password = driver.find_element(By.ID, "password")
    submit_button = driver.find_element(By.ID, "shibboleth-login-button")

    # enter login info
    username.send_keys(str(os.getenv("NINERNET_USER")))
    password.send_keys(str(os.getenv("NINERNET_PASS")))
    submit_button.click()

    # wait for duo to load
    try:
        print("logging in...")
        wait.until(lambda d: driver.title == "")
    except TimeoutError:
        print("ninernet timed out")
        driver.quit()
        return
    # wait for duo auth
    try:
        print("waiting for duo 2fa...")
        wait.until(lambda d: driver.find_element(By.ID, "dont-trust-browser-button"))
    except TimeoutError:
        print("duo timed out")
        driver.quit()
        return
    driver.find_element(By.ID, "dont-trust-browser-button").click()
    print("duo 2fa authenticated")

    # TODO: open appropriate section

    # wait for spaces list to load
    try:
        print("waiting for spaces page...")
        wait.until(lambda d: driver.find_element(By.XPATH, "//*[text()='Woodward 120  Fall Term 2024']"))
    except TimeoutError:
        print("events spaces page timed out")
        driver.quit()
        return

    # open woodward section
    # cone:     9
    # woodward: 10
    space_id = 10

    # download daily report
    # time in eastern time
    # time format: YYYY/MM/DD+HH:MM
    today = date.strftime(date.today(), "%Y/%m/%d")
    minutes_ago = 5
    start_time = date.strftime(datetime.datetime.now() - datetime.timedelta(minutes=minutes_ago), '%H:%M')
    end_time = date.strftime(datetime.datetime.now(), '%H:%M')
    download_link = f"https://cci-events.charlotte.edu/spaces/{space_id}/report/daily-sign-ins/download?start_time={today}+{start_time}&end_time={today}+{end_time}"
    print("downloading file...")
    driver.execute_script(f"window.location.href='{download_link}'")
    print(download_link)


    # exit selenium
    print("quitting selenium...")
    driver.quit()

if __name__ == "__main__":
    main()
else:
    print("this really shouldn't be run as an import")
