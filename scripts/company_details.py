import os
import sys
from typing import Any, Dict, List

from pandas import read_csv
from playwright.sync_api import Browser, Locator, Page, sync_playwright
from tabulate import tabulate  # type: ignore

from . import get_filepath, logger


class DataHandle:
    """DataHandle class"""

    def __init__(self) -> None:
        self._filename = os.environ["G2_FILENAME"]
        self._sourcefile = get_filepath(self._filename)
        self._dataframe = read_csv(self._sourcefile)

    def get_companies_urls(self) -> List[str]:
        """Function created to retrieve company urls
        Returns:
            List[str]: Return list companies url
        """
        result = self._dataframe["Url"].to_list()
        return result

    def _processing_details(self, items: List[Any]) -> Dict[Any, Any]:
        """Function created to process the scraped datelines and format
        them in a table to display them on the terminal.
        Args:
            items (List[Any]): Receives a list of details, in dictionaries
        Returns:
            Dict[Any, Any]: Returns a dictionary containing 2 keys, message
            and date, the title and the information to be displayed.
        """
        results = {}
        rows = []
        headers = [
            "Name",
            "Visit website",
            "Year Founded",
            "Total Revenue (USD mm)",
            "HQ Location",
            "Ownership",
            "Phone",
        ]
        for item in items:
            website = item.get("Visit website", "N/A")
            name = item.get("Name", "N/A")
            total = item.get("Total Revenue (USD mm)", "N/A")
            founded = item.get("Year Founded", "N/A")
            location = item.get("HQ Location", "N/A")
            ownership = item.get("Ownership", "N/A")
            phone = item.get("Phone", "N/A")
            rows.append(
                (name, website, founded, total, location, ownership, phone)
            )
        results["message"] = "Companies Details:"
        results["data"] = tabulate(rows, headers)
        return results

    def show_details(self, details: List[Any]) -> None:
        """Function responsible for displaying tabulated data.
        Args:
            details (List[Any]): Receives the list of details
        """
        data = self._processing_details(details)
        logger.info(data.get("message"))
        logger.info(data.get("data"))


class Scrapper:
    """Scrapper class"""

    def __init__(self) -> None:
        self._headless = bool(int(os.environ["HEADLESS_MODE"]))

    def _get_browser(self) -> Browser:
        """Function created to instantiate the browser.
        Returns:
            Browser: Returns the browser.
        """
        player = sync_playwright().start()
        browser = player.firefox.launch(headless=self._headless)
        return browser

    def _avoid_security_question(self, page: Page) -> None:
        """Function responsible for validating the cloudfare captcha and
        requesting human intervention to continue the process.
        Args:
            page (Page): Receive a page instance
        """
        not_safe = True
        while not_safe:
            if (
                page.locator("#challenge-running").all_inner_texts()
                and self._headless
            ):
                logger.warning("Captcha page! Human intervention is needed!")
                logger.error("Try again with headless mode active")
                sys.exit(1)
            if not page.locator("#challenge-running").all_inner_texts():
                logger.info(
                    "Captcha solved. Continuing with the rest of the process."
                )
                not_safe = False
                page.wait_for_timeout(2000)
                break
            page.wait_for_timeout(5000)

    def _processing_data(self, detail_page: Locator) -> Dict[Any, Any]:
        """Function created to scrape the details from the page of the
        indicated company.
        Args:
            detail_page (Locator): Located page, with the details
            already selected.
        Returns:
            Dict[Any, Any]: Returns the data scraped from the delivered page.
        """
        detail = {}
        items = detail_page.locator(".detail-block__text")
        for item in items.all():
            if item.locator("p.fw-semibold > a").count() > 0:
                link = item.locator("p.fw-semibold > a")
                text = link.all_inner_texts()[0]
                detail[text] = link.get_attribute("href")

            elif item.locator("span").count() > 0:
                text = item.locator("p.fw-semibold").all_inner_texts()[0]
                detail[text] = item.locator("span").first.all_inner_texts()[0]
            else:
                text = item.locator("p").first.all_inner_texts()[0]
                detail[text] = item.locator("p").last.all_inner_texts()[0]
        return detail

    def get_companies_details(self, companies_urls: List[str]) -> List[Any]:
        """Main function, being responsible for building the scraping process,
        and building the list of scraped data.
        Args:
            companies_urls (List[str]): Receives the list of company urls.

        Returns:
            List: Returns the list of scraped company data.
        """
        result = []
        browser = self._get_browser()
        page = browser.new_page()
        for url in companies_urls:
            page.goto(url)
            self._avoid_security_question(page)
            company_name = (
                page.locator("div.rated-item__info")
                .locator("h2")
                .all_inner_texts()[0]
            )
            detail_page = page.locator("div.show-for-xlarge").locator(".paper")
            data = self._processing_data(detail_page)
            data.update({"Name": company_name})
            result.append(data)
        return result


class BuildManager:
    """BuildManager class"""

    def __init__(self) -> None:
        self._scrapper = Scrapper()
        self._handle_data = DataHandle()

    def main(self) -> None:
        """Main function to build the script"""
        companies_url = self._handle_data.get_companies_urls()
        details = self._scrapper.get_companies_details(companies_url)
        self._handle_data.show_details(details)


if __name__ == "__main__":
    """Context for running the main"""
    app = BuildManager()
    app.main()
