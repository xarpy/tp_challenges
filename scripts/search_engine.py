import pickle
import os
from dotenv import find_dotenv, load_dotenv
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from tabulate import tabulate

load_dotenv(find_dotenv())

# If modifying these scopes, delete the file token.pickle.
# CREDENTIAL_PATH = os.path.abspath(os.getenv("CREDENTIAL_FILENAME"))


def get_gdrive_service():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", os.getenv("SCOPES")
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)
    # return Google Drive API service
    return build("drive", "v3", credentials=creds)


def search(service, query):
    # search for the file
    result = []
    page_token = None
    while True:
        response = (
            service.files()
            .list(
                q=query,
                spaces="drive",
                fields="nextPageToken, files(id, name, mimeType)",
                pageToken=page_token,
            )
            .execute()
        )
        # iterate over filtered files
        for file in response.get("files", []):
            result.append((file["id"], file["name"], file["mimeType"]))
        page_token = response.get("nextPageToken", None)
        if not page_token:
            # no more files
            break
    return result


def get_size_format(b, factor=1024, suffix="B"):
    """
    Scale bytes to its proper byte format
    e.g:
        1253656 => '1.20MB'
        1253656678 => '1.17GB'
    """
    for unit in ["", "K", "M", "G", "T", "P", "E", "Z"]:
        if b < factor:
            return f"{b:.2f}{unit}{suffix}"
        b /= factor
    return f"{b:.2f}Y{suffix}"


def list_files(items):
    """given items returned by Google Drive API, prints them in a tabular way"""
    if not items:
        # empty drive
        print("No files found.")
    else:
        rows = []
        for item in items:
            # get the File ID
            id = item["id"]
            # get the name of file
            name = item["name"]
            try:
                # parent directory ID
                parents = item["parents"]
            except:
                # has no parrents
                parents = "N/A"
            try:
                # get the size in nice bytes format (KB, MB, etc.)
                size = get_size_format(int(item["size"]))
            except:
                # not a file, may be a folder
                size = "N/A"
            # get the Google Drive type of file
            mime_type = item["mimeType"]
            # get last modified date time
            modified_time = item["modifiedTime"]
            # append everything to the list
            rows.append((id, name, parents, size, mime_type, modified_time))
        print("Files:")
        # convert to a human readable table
        table = tabulate(
            rows,
            headers=["ID", "Name", "Parents", "Size", "Type", "Modified Time"],
        )
        # print the table
        print(table)


# def main():
#     # filter to text files
#     filetype = "text/plain"
#     # authenticate Google Drive API
#     service = get_gdrive_service()
#     # search for files that has type of text/plain
#     search_result = search(service, query=f"mimeType='{filetype}'")
#     # convert to table to print well
#     table = tabulate(search_result, headers=["ID", "Name", "Type"])
#     print(table)


def main():
    """Shows basic usage of the Drive v3 API.
    Prints the names and ids of the first 5 files the user has access to.
    """
    service = get_gdrive_service()
    # Call the Drive v3 API
    results = (
        service.files()
        .list(
            pageSize=5,
            fields="nextPageToken, files(id, name, mimeType, size, parents, modifiedTime)",
        )
        .execute()
    )
    # get the results
    items = results.get("files", [])
    # list all 20 files & folders
    list_files(items)


if __name__ == "__main__":
    main()
