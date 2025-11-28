from selenium import webdriver
from selenium.webdriver.firefox.options import Options


def fetch_html(url: str) -> str:
    driver_options = Options()
    driver_options.add_argument("--headless")
    try:
        driver = webdriver.Firefox(options=driver_options)
        driver.implicitly_wait(5)
        driver.get(url)
        html_data = driver.page_source
    finally:
        driver.quit()
    return html_data
