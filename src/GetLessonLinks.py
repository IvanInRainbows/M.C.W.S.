import selenium, time, requests, os, json
import selenium.common.exceptions as exceptions
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service
from pathlib import Path

path = Path(os.path.abspath(os.path.dirname(__file__)))
cfg = json.load(open(path / ".." / "config.json"))

# Setup Selenium
options = webdriver.FirefoxOptions()
#options.add_argument("-headless") # Uncomment this line to setup headless. Normal headless option setting wasn't working for me for some reason
service = Service("/opt/geckodriver/geckodriver") # NOTE: Path to geckodriver
options.binary_location = "/usr/bin/firefox" # NOTE: Path to Firefox binary
driver = webdriver.Firefox(service=service, options=options)

# Get the source/login url, change in the config.json
driver.get(cfg["source_url"])

# Automated login. Find username/password fields and submit in the config.json
wait = WebDriverWait(driver, 10)
wait.until(EC.presence_of_element_located((By.ID, "password")))
driver.find_element(By.ID, "username").send_keys(cfg["credentials"]["username"])
driver.find_element(By.ID, "password").send_keys(cfg["credentials"]["password"])
driver.find_element(By.CSS_SELECTOR, "Login/button/CSS_selector").click() # TODO: Change the Login CSS_Selector

# Wait for courses page to load. Waiting 45 second just in case you want to login manually.
course_css_selector = "h1.course-CSS-selector" # TODO: Replace with your course's CSS selector, the one that has the hyperlinks (href attribute)
wait = WebDriverWait(driver, 45)
wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, course_css_selector.replace(" ", "."))))

# --- Iterate courses ---
courses = []
for i in driver.find_elements(By.CSS_SELECTOR, course_css_selector.replace(" ", ".")):
    courses.append(i.get_attribute("href"))
video_links = {}
for course in courses:
    driver.get(course)

    module_csspath = "h2.module-CSS-selector".replace(" ", ".") # TODO: Replace with the dropdown menu's button, as these will be clicked to open all of them.
    coursename_css_selector = "" # TODO: Replace with the CSS selector of the label that contains the course's name (this will be used as part of a composite primary key)

    # Wait for modules to load
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "section.whatever"))) # Here I wait until the sections are loaded, replace with your sections.
    coursename = driver.find_element(By.CSS_SELECTOR, coursename_css_selector).text
    print(coursename)
    while True: # Open all dropdown menus, done like this because things change in the page once you press a dropdown menu, so they have to be updated constantly
        modules = driver.find_elements(By.CSS_SELECTOR, module_csspath) # opened dropdown menus no longer have the down button so they should no loner have the module_csspath element
        if len(modules) > 0: # If there are no buttons there are no menus to open anymore
            try:
                modules[0].click()
                time.sleep(1)  # wait for dropdown to appear
            except exceptions.ElementNotInteractableException:
                pass
        else: break

    # Module entries (videos, PDFs)
    # Modules are composed of entries/lessons (displayed after the dropdown is activated)
    entry_css_selector = "section.whatever" # TODO: Replace with your entries' css_selector
    entries = driver.find_elements(By.CSS_SELECTOR, entry_css_selector)
    for entry in entries:
        try:
            # Check if the entry has a video icon, as here is the media we want to retrieve
            video_icon = entry.find_element(By.CSS_SELECTOR, "div.icon-video") # TODO: Replace with your video icon's CSS selector
            # If it does not exist it should not carry on and should throw an exception instead
            
            # Now we set up the primary key for the dictionary, which is composed of the course name, a separator and a lesson name
            pkey = coursename + "<separator>" + entry.find_element(By.CSS_SELECTOR, "span.lesson-name").text # TODO: replace with the CSS selector of the label that contains the lesson name.
            link_element = entry.find_element(By.CSS_SELECTOR, "h1.item-title a") # TODO: Replace with the element that contains the hyperlink to the lesson page
            link = link_element.get_attribute("href")
            # Print for debug
            print(pkey)
            print(link)
            # Add to the dictionary
            video_links[pkey] = link
        except:
            # No video icon -> skip
            continue

open(path / ".." / "logs" / "links.json", "w").write(json.dumps(video_links))
driver.quit()
