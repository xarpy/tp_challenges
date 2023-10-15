import os
import sys
from typing import Any, Dict, List

from pandas import read_csv
from playwright.sync_api import Browser, sync_playwright

from . import get_filepath, logger


class DocumentReader:
    """DocumentReader class"""

    def __init__(self) -> None:
        self._filename = os.environ["COMPANY_FILENAME"]
        self._sourcefile = get_filepath(self._filename)
        self._dataframe = read_csv(self._sourcefile)

    def get_companies(self) -> List[str]:
        """Responsible for collecting the list of company names.
        Returns:
            List[str]: Return a list of string company names
        """
        company_names = self._dataframe["Companies"].to_list()
        return company_names

    def update_data(self, data: Dict[Any, Any]) -> None:
        """Function responsible for updating the dataframe and then
        building the new csv.
        Args:
            data (Dict[Any, Any]):Recieve a data with information to url
            and employees.
        """
        self._dataframe.insert(2, "Employees", "")
        self._dataframe.astype(str)
        for name in self.get_companies():
            employees = data[name].get("employees")[0]
            employees = employees.split()
            idx = self._dataframe.index[
                self._dataframe["Companies"] == name
            ].tolist()[0]
            self._dataframe.at[idx, "Url"] = data[name].get("url")
            self._dataframe.at[idx, "Employees"] = employees[0]
        self._build_file()

    def _build_file(self) -> None:
        """Function create to build a new CSV"""
        self._dataframe.to_csv(self._filename, index=False)


class Scrapper:
    """Scrapper class"""

    def __init__(self) -> None:
        self._headless = True
        self._url = "https://www.linkedin.com/home"
        self._login = os.getenv("ACCOUNT_NAME")
        self._password = os.getenv("ACCOUNT_PASSWORD")

    def _get_browser(self) -> Browser:
        """Function created to instantiate the browser.
        Returns:
            Browser: Returns the browser.
        """
        player = sync_playwright().start()
        browser = player.chromium.launch(headless=self._headless)
        return browser

    def _linkedin_login(self, page: Any) -> None:
        """Function created to enter linkedin
        Args:
            page (Any): Receive a page instance
        """
        page.goto(self._url)
        page.locator("input#session_key").fill(self._login)
        page.locator("input#session_password").fill(self._password)
        page.get_by_role("button", name="Sign in").click()
        if "checkpoint/challenge" in page.url:
            logger.warning("Captcha page! Human intervention is needed!")
            while True:
                if "checkpoint/challenge" not in page.url:
                    logger.info(
                        "Captcha solved. Continuing with the rest of the process."
                    )
                    break
                page.wait_for_timeout(2000)
            page.wait_for_timeout(5000)
        elif "checkpoint/challenge" not in page.url:
            logger.info(
                "Sometimes the captcha appears, not this time, just keep going!"
            )
        else:
            logger.error("Captcha page! Aborting due to headless mode...")
            sys.exit(1)

    def get_information(self, companies: List[str]) -> Dict[Any, Any]:
        """Function created to get data from linkedin.
        Args:
            companies (List[str]): Receive a list of company names
        Returns:
            Dict[Any, Any]: Returns a dictionary containing the url and
            number of employees for each company.
        """
        data = {item: {"url": "", "employees": []} for item in companies}
        browser = self._get_browser()
        page = browser.new_page(locale="en-US")
        self._linkedin_login(page)
        for name in companies:
            searchbar = page.locator(".search-global-typeahead__input")
            searchbar.click()
            searchbar.fill(name)
            page.keyboard.press("Enter")
            link = page.get_by_role("link", name=name, exact=True)
            data[name]["url"] = link.get_attribute("href")
            link.click()
            page.locator(".org-page-navigation__item-anchor").filter(
                has_text="People"
            ).click()
            page.wait_for_timeout(2000)
            page.wait_for_selector(".org-people__header-spacing-carousel")
            employee_card = page.locator(
                ".org-people__header-spacing-carousel"
            )
            data[name]["employees"] = employee_card.locator(
                "h2"
            ).all_inner_texts()
        browser.close()
        return data


class BuildManager:
    """BuildManager class"""

    def __init__(self) -> None:
        self._scrapper = Scrapper()
        self._document_reader = DocumentReader()

    def main(self) -> None:
        """Main function to build the script"""
        companies = self._document_reader.get_companies()
        information = self._scrapper.get_information(companies)
        self._document_reader.update_data(information)
        message = f"All information are collected, please check on your {self._document_reader._filename}!"
        logger.info(message)


if __name__ == "__main__":
    """Context for running the main"""
    app = BuildManager()
    app.main()
