"""Scrapers package initialization"""
from .nyc_tlc import NYCTLCScraper
from .chicago_tnp import ChicagoTNPScraper
from .seattle_tnc import SeattleTNCScraper
from .boston_massdot import BostonMassDOTScraper
from .california_cpuc import CaliforniaCPUCScraper
from .airport_reports import AirportReportsScraper

__all__ = [
    'NYCTLCScraper',
    'ChicagoTNPScraper',
    'SeattleTNCScraper',
    'BostonMassDOTScraper',
    'CaliforniaCPUCScraper',
    'AirportReportsScraper'
]
