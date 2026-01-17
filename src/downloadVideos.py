import requests, json, os
from pathlib import Path
from tqdm import tqdm
from urllib.parse import urlparse, parse_qs, unquote

def get_filename(url):
    """Usually, the original name of the PDFs can be retrieved from the content. This function does that with the url.

    Args:
        url (str): The url to the pdf.

    Returns:
        str: Original name of the pdf.
    """
    parsed = urlparse(url)
    params = parse_qs(parsed.query)

    disposition = params.get("response-content-disposition", [None])[0]

    if disposition:
        disposition = unquote(disposition)
        filename = disposition.split("filename=")[-1]
    else:
        filename = None

    return filename


def get_filename_from_url(url):
    """Used for videos, because seems like the original name cannot be retrieved. This extracts the name from the url, instead of from the content.

    Args:
        url (str): URL to the video

    Returns:
        str: Name of the file
    """
    path = urlparse(url).path
    return unquote(os.path.basename(path))

# Directory where files will be saved
save_dir = Path("/media/ivan/LinuxHDD/scrapTest/") # TODO: Replace with the directory where the files will be saved
save_dir.mkdir(exist_ok=True, parents=True)
path = Path(os.path.abspath(os.path.dirname(__file__)))

# Some files may throw and error, in which case they will be skipped and saved into this dictionary (and into a json file in /logs)
skipped_files = {
    "pdfs" : [],
    "videos" : {}
}

# Files that have already been downloaded in previous executions will also be saved in a json file and the downloads will be resumed from there
try: # Load the json
    done = json.load(open(path / ".." / "logs" / "completedFiles.json", "r"))
except json.decoder.JSONDecodeError: # If it doesn't exist make a dictionary (will later be saved into a json)
    done = {
        "pdfs" : {},
        "videos" : {}
    }

is_error = False # If a file has an error this will be true (so be saved into skippedFiles.json)

log_update = 10 # Every certain number of links downloaded the skippedFiles.json and downloadedFiles.json are updated (default 10)
i=0 # To count iterations

# pdf (and others) download
links = json.load(open(path / ".." / "logs" / "pdf_links.json", "r"))
for k, v in tqdm(links.items()):
    folder = k.split("<separator>")[0]
    subfolder = k.split("<separator>")[1]
    for lk in v: # A single lesson may contain several pdf links
        if k not in done.keys(): # Check if it has been done previously
            try:
                file_name = get_filename(lk)

                if folder not in os.listdir(save_dir):
                    os.mkdir(save_dir / folder)
                if subfolder not in os.listdir(save_dir / folder):
                    os.mkdir(save_dir / folder / subfolder)

                response = requests.get(lk, stream=True)
                response.raise_for_status()  # fail if request failed
                with open(save_dir / folder / subfolder / file_name, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
            except Exception as e: # Failed download: print the error (usually 403) and add it to skipped files (these are not added to completedFiles.json)
                print(f"⚠️ Failed download: {e}")
                skipped_files["pdfs"].append([k, lk, str(e)])
                is_error = True
    if not is_error:
        done["pdfs"][k] = v
    else:
        is_error = False
    i += 1
    if i == 10: # Update json file
        json.dump(skipped_files, open(path / ".." / "logs" / "skippedFiles.json", "w"))
        json.dump(done, open(path / ".." / "logs" / "completedFiles.json", "w"))
        i = 0


# video download
links = json.load(open(path / ".." / "logs" / "video_links.json", "r"))
for k, v in tqdm(links.items()): # Each lesson should contain only one video link
    if k not in done.keys(): # Check if it has been done previously
        try:
            folder = k.split("<separator>")[0]
            subfolder = k.split("<separator>")[1]
            file_name = get_filename_from_url(v)

            if folder not in os.listdir(save_dir):
                os.mkdir(save_dir / folder)
            if subfolder not in os.listdir(save_dir / folder):
                os.mkdir(save_dir / folder / subfolder)

            response = requests.get(v, stream=True)
            response.raise_for_status()  # fail if request failed
            with open(save_dir / folder / subfolder / file_name, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            done["videos"][k] = v
        except Exception as e: # Failed download: print the error (usually 403) and add it to skipped files (these are not added to completedFiles.json)
            print(f"⚠️ Failed download: {e}")
            skipped_files["videos"][k] = {
                "url" : v,
                "Error" : str(e)
            }
        i += 1
        if i == 10:
            json.dump(skipped_files, open(path / ".." / "logs" / "skippedFiles.json", "w"))
            json.dump(done, open(path / ".." / "logs" / "completedFiles.json", "w"))
            i = 0

json.dump(skipped_files, open(path / ".." / "logs" / "skippedFiles.json", "w"))
json.dump(done, open(path / ".." / "logs" / "completedFiles.json", "w"))