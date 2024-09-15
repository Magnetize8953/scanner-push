from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
from datetime import date
import datetime
import os

# set up dotenv
load_dotenv()
if os.getenv("NINERNET_USER") is None or os.getenv("NINERNET_USER") == "":
    raise NameError("NINERNET_USER not set")
if os.getenv("NINERNET_PASS") is None or os.getenv("NINERNET_PASS") == "":
    raise NameError("NINERNET_PASS not set")

# set up selenium
options = webdriver.FirefoxOptions()
options.add_argument("-headless")
options.set_preference("browser.download.folderList", 2)
options.set_preference("browser.download.dir", os.getcwd())
driver = webdriver.Firefox(options=options)
wait = WebDriverWait(driver, timeout=60)

"""
load the cci events page and download scanner data

space_id - id number of the cci events space
scanner_delta - amount of time, in minutes, to look back in the scanner data from time of running
driver_timeout - amount of time, in seconds, to wait before timing out webpage loads
"""
def download_scanner_data(space_id: int, scanner_delta: int) -> None:

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
