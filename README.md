# Legal disclaimer

This project was developed and tested exclusively on systems for which the author had explicit administrator-level access.

All data accessed by this tool was available through the system’s standard, authenticated web interface, and no authentication mechanisms, access controls, or security features were bypassed.

The automation replicates actions that an authorized administrator could perform manually in a web browser, such as navigating pages and downloading files already exposed to permitted users.

This project is intended for educational and personal automation purposes, demonstrating browser automation, structured data extraction, and file handling techniques. It is not intended for use on systems without proper authorization.

This repository is provided for educational purposes. Users are responsible for ensuring that their use of this code complies with applicable terms of service and local laws.

# Description

This is a set of Python-based tools that are used to scrape a mysterious webpage that contains courses and course content. The webpage in question did not offer the means to retrieve media content effectively, only manually going though all the media one by one, thus the need for this tool.

The set of tools are designed to programmatically retrieve metadata and downloadable resources from a web-based content platform using authorized administrator access.

The tool automates the process of:

* Enumerating available resources (documents, media files, etc.)

* Extracting file metadata such as names, formats, and sizes

* Downloading media assets in a controlled manner

* Logging skipped, expired, or inaccessible resources for auditing

The tool navigates around the elements of the webpage retrieving the links that contain the required media content, storing them in a structured way using primary keys. The page is structured in a page of courses that lead to a page that contains modules. These modules are dropdown menus that show the lessons when displayed. The content of these lessons is the content to be retrieved. The tool downloads these media files into a folder structure. This folder structure is determined by the primary key assigned to each lesson's content, which is composed of the course name and the lesson name (separated with a separator). The course name determines the folder where it will be saved and the lesson name determines the subfolder. The tool iterates through the links downloading the content into the according folder.

# Usage

As I had to change the code to disclose the identity of my client and the webpage to be scraped, the code requires some tweaking to run effectively. If required, the credentials should be set up in the config.json, as well as the source page. Then, in the code, all the CSS selectors should be replaced to tailor the webpage that you may want to scrape.

Note that this tool was tailored to a specific website's structure so it may not work properly and effectively in other websites unless tailored to those.