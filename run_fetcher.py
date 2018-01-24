from analysis.analyzer import Analyzer
from analysis.utils import get_mongo_conn

if __name__ == '__main__':
    fetcher = Analyzer(get_mongo_conn())
    # fetcher.fetch_categories()
    # fetcher.fetch_moderators()
    fetcher.get_moderator_overview("emrebeyler", "all")