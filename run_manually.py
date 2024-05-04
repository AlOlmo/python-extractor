import logging

from milanuncios_extractor import run_scraper

# Config
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s %(module)s - %(funcName)s: %(message)s'
)


# Parameters
endpoint = 'servicios-en-pontevedra'
target_directory = 'results/servicios-en-pontevedra'
headless = True
initial_page = 46

# Run
if __name__ == '__main__':
    run_scraper(
        url=f"https://www.milanuncios.com/{endpoint}/",
        target_folder=target_directory,
        headless=headless,
        initial_page=initial_page
    )
