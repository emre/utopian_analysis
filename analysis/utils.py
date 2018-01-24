from pymongo import MongoClient

from .settings import MONGO_URI
from .analyzer import Analyzer

_mongo_connection = None
_analyzer = None


def get_mongo_conn():
    global _mongo_connection
    if not _mongo_connection:
        _mongo_connection = MongoClient(MONGO_URI)
    return _mongo_connection


def get_analyzer():
    global _analyzer
    if not _analyzer:
        _analyzer = Analyzer(get_mongo_conn())
    return _analyzer
