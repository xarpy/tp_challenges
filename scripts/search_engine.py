import os
import sys
import re
from spacy import load
from spacy.tokens import Doc
from spacy.matcher import Matcher
from pathlib import Path
from typing import Tuple, Any, List, Iterator

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

    def get_session(self) -> Any:
        """Function created to connect to google drive via the google API
        Returns:
            Any: Returns a session object from the connection
        """
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

    def get_size_format(
            self, byte:int, factor: int = 1024, suffix: str ="B") -> str:
        """ Scale bytes to its proper byte format
        Args:
            byte (int): Integer passed relative to size
            factor (int, optional): Size factor for calculation, in bits_.Defaults to 1024.
            suffix (str, optional): Suffix, relating to type,. Defaults to "B".

        Returns:
            str: Returns a string with the size definition.
        """
        for unit in ["", "K", "M", "G", "T", "P", "E", "Z"]:
            if byte < factor:
                return f"{byte:.2f}{unit}{suffix}"
            byte /= factor
        return f"{byte:.2f}Y{suffix}"

    def list_files(self, items: List) -> str:
        """Function created to list the fields and columns of the files to be displayed.
        Args:
            items (List): Dictionary list, containing file references.
        Returns:
            str: Returns a tabulated and formatted string, to be displayed correctly
            showing all the files in the connected Google Drive.
        """
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

    def show_itens(self) -> str:
        """Function created to show all items in google drive
        Returns:
            str: Returns a formatted string with most of the items in google drive.
            The number of items depends on the page_size variable.
        """
        service = self.get_session()
        results = service.files().list(
            pageSize=self.page_size, fields=self.list_fields).execute()
        items = results.get("files", [])
        self.list_files(items)


class MetaEngine:
    def __init__(self) -> None:
        self._nlp = load("en_core_web_sm")

    def _extract_texts(self, items: List) -> List[Iterator[Doc]]:
        """Function created to extract file names and convert them into
        Doc type for being processed.
        Args:
            items (List): List of file names
        Returns:
            List[Iterator[Doc]]: Returns a Doc object
        """
        rows = []
        if items:
            for item in items:
                name = item.get("name")
                rows.append(self.handle_phrase(name))
        rows = self._nlp.pipe(rows)
        return rows

    def handle_phrase(self, phrase: str) -> str:
        """Function created to treat phrases and remove characters,
        making the search process easier.
        Args:
            phrase (str): Entry sentence
        Returns:
            str: Sentence processed
        """
        output = re.findall('[A-Z]?[a-z]+',phrase)
        new_phrase = ' '.join([word for word in output])
        return new_phrase

    def _data_processing(
            self, documents: List[Iterator[Doc]], keywords:Tuple[Any, Any]) -> str:
        """Function created to process the data and find the correct file
        based on the word given.
        Args:
            documents (List[Iterator[Doc]]): Doc object with all sentences
            keywords (Tuple[Any, Any]): Keyword given

        Returns:
            str: Returns the name of the file found.
        """
        pattern = []
        matcher = Matcher(self._nlp.vocab)
        for word in keywords:
            pattern.append({"TEXT": word})
        for doc in documents:
            matcher.add("matching", [pattern])
            found = matcher(doc)
            if found:
                print("Matches: " + str(doc))

    def output(self, itens: List, keywords: Tuple):
        text = self._extract_texts(itens)
        self._data_processing(documents=text, keywords=keywords)


class DocumentSearcher:
    def __init__(self) -> None:
        self._google_api = GoogleDriveAPI()
        self._meta_emgine = MetaEngine()

    def main(self, *args: Tuple[Tuple[Any, Any]]) -> str:
        """Function that initialized the script
        Returns:
            str: Returns the result
        """
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
    """Context for running the main"""
    engine = DocumentSearcher()
    engine.main(sys.argv)
