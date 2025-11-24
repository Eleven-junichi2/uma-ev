import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from umaev.scraping import ParserFinder
from parser import netkeiba

parser_finder = ParserFinder()
parser_finder.register(r"race\.netkeiba\.com/odds/index\.html\?race_id=(\d+)", netkeiba.odds)
parser_finder.register(r"race\.netkeiba\.com/race/shutuba\.html\?race_id=(\d+)", netkeiba.racecard)
