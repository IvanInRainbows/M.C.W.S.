import selenium, json, csv, os
import selenium.common.exceptions as exceptions
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service
from pathlib import Path
import time
import requests

path = Path(os.path.abspath(os.path.dirname(__file__)))
cfg = json.load(open(path / ".." / "config.json"))

# Setup Selenium
options = webdriver.FirefoxOptions()
#options.add_argument("-headless") # Uncomment this line to setup headless. Normal headless option setting wasn't working for me for some reason
service = Service("/opt/geckodriver/geckodriver") # NOTE: Path to geckodriver
options.binary_location = "/usr/bin/firefox" # NOTE: Path to Firefox binary
driver = webdriver.Firefox(service=service, options=options)

# Replace with your login URL
driver.get(cfg["source_url"]) # This is just for login, as later the links will be loaded from the json file
driver.set_window_size(1920, 1080) # Comment this when running headless

# Automated login. Find username/password fields and submit in the config.json
wait = WebDriverWait(driver, 10)
wait.until(EC.presence_of_element_located((By.ID, "password")))
driver.find_element(By.ID, "username").send_keys(cfg["credentials"]["username"])
driver.find_element(By.ID, "password").send_keys(cfg["credentials"]["password"])
driver.find_element(By.CSS_SELECTOR, "button.login").click() # TODO: Change the Login CSS_Selector

# Wait for courses page to load. Waiting 45 second just in case you want to login manually.
course_css_selector = "a.link-heading-4" # TODO: Replace with your course's CSS selector, the one that has the hyperlinks (href attribute)
wait = WebDriverWait(driver, 45)
wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, course_css_selector.replace(" ", "."))))

# Load the links.json
links = json.load(open(path / ".." / "logs" / "links.json", "r"))
video_links = {}
pdf_links = {}
for k, v in links.items():
    driver.get("about:blank") # This restores the browser to free memory
    driver.get(v)
    panel = driver.find_element(By.CSS_SELECTOR, "div.panel") # TODO: Replace with the panel's css_selector
    # Pdf Downloads
    try:
        downloads = panel.find_element(By.CSS_SELECTOR,"div.downloads-list") # TODO: Replace with the CSS selector of the downloads section for the PDFs (or others) downloads
        downloads_links = []
        dlbtns = downloads.find_elements(By.CSS_SELECTOR,"a.btn-icon-download") # TODO: Replace with the CSS selector of the download button (or whatever it is that contains the hyperlink/href)
        for i in dlbtns:
            lk = i.get_attribute("href")
            print("PDF: ", lk)
            downloads_links.append(lk)
        pdf_links[k] = downloads_links
    except exceptions.NoSuchElementException:
        print("No PDFs found")
    # Video Dropdown: The download is inside this dropdown so we have to press it
    button = panel.find_element(By.CSS_SELECTOR, "button.dropdown-caret-down") # TODO: Replace with the CSS selector of the dropdown menu button
    button.click()
    ddmenu_css_selector = "ul.dropdown-menu" # TODO: Replace with the CSS selector of the dropdown menu
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ddmenu_css_selector))) # Wait until it opens
    ddmenu = driver.find_element(By.CSS_SELECTOR, ddmenu_css_selector) # get the dropdown menu
    v_link = WebDriverWait(driver, 10).until(   # Wait until the download button is loaded
                                                EC.presence_of_element_located((
                                                    By.CSS_SELECTOR,
                                                    "a.dropdown-icon-download" # TODO: replace with the css selector of the download button (which contains the href)
                                                ))
                                            ).get_attribute("href")
    print("Video:", v_link)
    video_links[k] = v_link # Add it to the links

open("video_links.json", "w").write(json.dumps(video_links))
open("pdf_links.json", "w").write(json.dumps(pdf_links))
