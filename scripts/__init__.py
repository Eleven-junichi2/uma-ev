import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from odds2ev.scraping import ParserFinder
from parser import netkeiba

parser_finder = ParserFinder()
parser_finder.register(r"race\.netkeiba\.com/odds/index\.html\?race_id=(\d+)", netkeiba.racecard)
