import os
import sys
from spacy import load
from spacy.matcher import Matcher
from pathlib import Path

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from tabulate import tabulate


class GoogleDriveAPI:
    def __init__(self) -> None:
        self._base_dir = Path(__file__).resolve().parent.parent
        self._credentials = os.path.join(self._base_dir, os.getenv("CREDENTIAL_FILENAME"))
        self._scopes = os.getenv("SCOPES").split(',')
        self.list_fields = "nextPageToken, files(id, name, mimeType, size, parents, modifiedTime)"
        self.page_size = 100

    def get_session(self):
        creds = None
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file(
                "token.json", self._scopes
            )
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self._credentials, self._scopes
                )
                creds = flow.run_local_server(port=0)
            with open("token.json", "w") as token:
                token.write(creds.to_json())
        return build("drive", "v3", credentials=creds)

    def get_size_format(self, b, factor=1024, suffix="B"):
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

    def list_files(self, items):
        """given items returned by Google Drive API, prints them in a tabular way"""
        if items:
            rows = []
            headers = ["ID", "Name", "Parents", "Size", "Type", "Modified Time"]
            for item in items:
                id = item["id"]
                name = item["name"]
                parents = item.get('parents', "N/A")
                if item.get("size"):
                    size = self.get_size_format(int(item["size"]))
                else:
                    size = "N/A"
                mime_type = item["mimeType"]
                modified_time = item["modifiedTime"]
                rows.append((id, name, parents, size, mime_type, modified_time))
            print("Files:")
            table = tabulate(rows, headers)
            print(table)
        else:
            print("No files found.")

    def show_itens(self):
        """Shows basic usage of the Drive v3 API.
        Prints the names and ids of the first 5 files the user has access to.
        """
        service = self.get_session()
        results = service.files().list(
            pageSize=self.page_size, fields=self.list_fields).execute()
        items = results.get("files", [])
        self.list_files(items)


class MetaEngine:
    def __init__(self) -> None:
        self._nlp = load("en_core_web_md")

    def _extract_texts(self, items):
        rows = []
        if items:
            for item in items:
                name = item.get("name")
                rows.append(name)
        rows = self._nlp.pipe(rows)
        return rows

    def _data_processing(self, documents, keywords):
        pattern = []
        matcher = Matcher(self._nlp.vocab)
        for word in keywords:
            pattern.append({"text": word})
        for doc in documents:
            field_name_reference = "_".join(keywords)
            matcher.add(field_name_reference, [pattern])
            found = matcher(doc)
            print("Matches:", [doc[start:end].text for match_id, start, end in found])

    def output(self, itens, keywords):
        text = self._extract_texts(itens)
        self._data_processing(documents=text, keywords=keywords)


class DocumentSearcher:
    def __init__(self) -> None:
        self._google_api = GoogleDriveAPI()
        self._meta_emgine = MetaEngine()

    def main(self, *args, **kwargs):
        """Shows basic usage of the Drive v3 API."""
        size = self._google_api.page_size
        fieldlist = self._google_api.list_fields
        session = self._google_api.get_session()
        results = session.files().list(pageSize=size, fields=fieldlist).execute()
        items = results.get("files", [])
        if len(args[0]) < 2:
            self._google_api.show_itens()
        else:
            args[0].pop(0)
            self._meta_emgine.output(items, args[0])


if __name__ == "__main__":
    engine = DocumentSearcher()
    engine.main(sys.argv)
