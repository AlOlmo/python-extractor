import logging
import os
import sys

import pandas as pd
from pandas import DataFrame
from playwright.sync_api import sync_playwright, Page

from utilities import create_directories, safe_get_inner_text

USER_AGENT = "ASdasdasdsd"


def setup_browser(playwright, user_agent: str = USER_AGENT, headless: bool = True):
    chromium = playwright.firefox  # or "firefox" or "webkit".
    browser = chromium.launch(headless=headless)
    context = browser.new_context(user_agent=user_agent)
    context.set_default_timeout(10000)
    page = context.new_page()
    return page


def accept_cookies(page: Page):
    aggree_button = page.locator("#didomi-notice-agree-button")
    if aggree_button is not None:
        aggree_button.click()
        logging.info("Cookies accepted")


def navigate_to_url(page: Page, url: str, retries: int = 3):
    try:
        page.goto(url)
        logging.info(f"Navigate to url: '{url}'")
    except Exception:
        logging.warning(f"Could not go to url '{url}'. Retrying ({retries} retries left).")
        navigate_to_url(page, url, retries-1)


def load_dynamic_elements(page: Page):
    dynamic_elements = page.query_selector_all(".sui-PerfDynamicRendering-placeholder")
    for element in dynamic_elements:
        try:
            element.scroll_into_view_if_needed()
        except:
            page.mouse.down()
            page.mouse.down()
            page.mouse.down()


def process_links(page: Page) -> [str]:
    links_processed = []
    for link in page.query_selector_all(".ma-AdCardListingV2-TitleLink"):
        links_processed.append(link.get_attribute("href"))
    return links_processed

def __get_phone_number(page: Page) -> str:
    page.wait_for_selector(".ma-ContentAdDetail-contactButtons")
    phone_button = page.query_selector(".ma-AdContactCallButton-button")
    if phone_button is not None:
        phone_button.click()
        page.wait_for_selector(".ma-ModalContactCallPhoneLink-phone")
        phone = page.query_selector(".ma-ModalContactCallPhoneLink-phone").get_attribute("href")
        return phone
    else:
        logging.warning("No phone number available.")
        return ''


def visit_links_and_save_results(page: Page, links: [str], target_folder: str):
    successful_records = []
    error_records = []
    for link in links:
        try:
            page.goto("https://www.milanuncios.com" + link)
            title = safe_get_inner_text(page, ".ma-AdDetail-title")
            ref = safe_get_inner_text(page, ".ma-AdDetail-description-reference")
            user = safe_get_inner_text(page, ".ma-UserOverviewProfileName")
            location = safe_get_inner_text(page, ".ma-AdLocation-text")
            professional = page.query_selector(".ma-UserOverviewProfessionalLabel") is not None
            phone = __get_phone_number(page)
            successful_records.append({
                "title": title,
                "ref": ref,
                "user": user,
                "phone": phone,
                "location": location,
                "professional": professional

            })
            logging.debug("Element extracted: " + str(successful_records[-1]))
        except Exception as e:
            logging.debug("Error: could not find phone number: ", repr(e))
            error_records.append(link)

    # Create dataframes
    success_df = DataFrame.from_dict(successful_records)
    errors_df = DataFrame.from_dict(error_records)

    # Write CSVs
    success_df.to_csv(f"{target_folder}/successful_records.csv", mode='a', header=not os.path.exists(target_folder))
    errors_df.to_csv(f"{target_folder}/error_records.csv", mode='a', header=not os.path.exists(target_folder))


def run_scraper(url: str, target_folder: str, headless: bool = True, initial_page: int = 1):
    page_number = initial_page
    create_directories(target_folder)
    with sync_playwright() as playwright:
        page = setup_browser(playwright, headless=headless)
        navigate_to_url(page, url)
        accept_cookies(page)
        while True:
            navigate_to_url(page, f'{url}?pagina={page_number}')
            load_dynamic_elements(page)
            links = process_links(page)
            visit_links_and_save_results(page, links, target_folder)
            page_number += 1


if __name__ == '__main__':

    #Configure logger
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s %(levelname)s %(module)s - %(funcName)s: %(message)s'
    )

    endpoint = sys.argv[1]
    target_directory = sys.argv[2] if len(sys.argv) > 2 else endpoint

    if target_directory is None:
        target_directory = endpoint

    if endpoint is None:
        raise Exception("No endpoint provided")

    run_scraper(f"https://www.milanuncios.com/{endpoint}/", target_directory, headless=False)
