from collections.abc import Callable
from typing import TypeVar, Generic
from re import Pattern
import re

import pandas as pd
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

ParserFunc = Callable[[str], pd.DataFrame]

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


class ParserFinder:
    def __init__(self):
        self.__parsers = []

    def register(self, url_pattern: str, parser: ParserFunc) -> None:
        """
        URLパターンとパーサー関数を登録する。
        """
        compiled_pattern = re.compile(url_pattern)
        self.__parsers.append((compiled_pattern, parser))

    def find(self, url: str) -> ParserFunc | None:
        for pattern, parser in self.__parsers:
            if pattern.search(url):
                return parser
        return None
