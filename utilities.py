import logging
import os

from playwright.sync_api import Page


def create_directories(path: str) -> bool:
    if path is None:
        logging.error("Could not create directories: path is None")
        return False
    if not path.endswith("/"):
        path += "/"
    try:
        os.makedirs(os.path.dirname(path))
        return True
    except:
        return False

def safe_get_inner_text(page: Page, selector: str) -> str:
    element = page.query_selector(selector)
    if element is not None:
        return element.inner_text()
    else:
        return ''
