
import logging

import pygal

from .client import Client

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logging.basicConfig()


def get_percent(dictionary, s):
    percent = dictionary[s] * 1.0 / sum(dictionary.values()) * 100
    return round(percent, 2)


class Analyzer(object):

    def __init__(self, mongo_conn):
        self.client = Client()
        self.mongo_conn = mongo_conn
        self.database = self.mongo_conn["utopian_analysis"]
        self.posts = self.database["posts"]
        self.categories = self.database["categories"]
        self.moderators = self.database["moderators"]

    def fetch_recursive(self, limit=1000, skip=0, post_list=None, hidden=False):
        if post_list is None:
            post_list = []

        query = {
            "skip": skip,
            "limit": limit,
        }

        if hidden:
            query["status"] = "flagged"

        approved_posts = self.client.posts(query)
        for post in approved_posts["results"]:
            self.posts.update(
                {"_id": post["_id"]}, post, upsert=True)

        if skip + limit < approved_posts["total"]:
            logger.info(
                "New iteration. skip:%s, limit:%s",
                skip,
                limit
            )
            return self.fetch_recursive(
                limit=limit,
                skip=skip+limit,
                post_list=post_list,
                hidden=hidden)

    def fetch_approved_posts(self):
        self.fetch_recursive()

    def fetch_hidden_posts(self):
        self.fetch_recursive(hidden=True)

    def get_moderator_leaderboard(self, category, status, group_by):
        return self.get_moderator_data(category, status, group_by=group_by)

    def get_moderator_data(self, category, status,
                           moderator=None, group_by="moderator", author=None):

        if category == "all":
            category = None

        if status == "all":
            status = None

        pipeline = [
            {
                "$group": {
                    "_id": "$%s" % group_by,
                    "count": {"$sum": 1}
                }
            },
            {
                "$sort": {"count": -1}
            },
        ]
        match_query = None
        if category or status or moderator or author:
            match_query = {}

        if category:
            match_query.update({
                "json_metadata.type": category
            })
        if status:
            if status == "hidden":
                match_query.update({
                    "flagged": True,
                })
            elif status == "approved":
                match_query.update({
                    "reviewed": True,
                })
        if moderator:
            match_query.update({
                "moderator": moderator,
            })
        if author:
            match_query.update({
                "author": author,
            })

        if match_query:
            pipeline.insert(
                0,
                {"$match": match_query}
            )
        moderators = self.posts.aggregate(pipeline)
        return moderators

    def get_moderator_overview(self, category, moderator=None, author=None):

        try:
            if moderator:
                total = list(
                    self.get_moderator_data(
                        category, None, moderator=moderator))[0]["count"]
            elif author:
                total = list(
                    self.get_moderator_data(
                        category, None, author=author, group_by="author")
                )[0]["count"]
        except IndexError:
            total = 0

        try:
            if moderator:
                approved = list(
                self.get_moderator_data(
                    category, "approved", moderator=moderator))[0]["count"]
            elif author:
                approved = list(
                self.get_moderator_data(
                    category, "approved", author=author, group_by="author"
                ))[0]["count"]
        except IndexError:
            approved = 0

        try:
            if moderator:
                hidden = list(
                    self.get_moderator_data(
                        category, "hidden", moderator=moderator))[0]["count"]
            elif author:
                hidden = list(
                    self.get_moderator_data(
                        category, "hidden", author=author, group_by="author"
                    ))[0]["count"]
        except IndexError:
            hidden = 0
        return total, approved, hidden

    def fetch_categories(self):
        categories = set()
        for post in self.posts.find({}):
            category = post.get("json_metadata").get("type", {})
            if category:
                categories.add(category)

        for category in categories:
            self.categories.update(
                {"name": category}, {"name": category},
                upsert=True)

        logger.info(categories)

    def fetch_moderators(self):
        for moderator in self.client.moderators["results"]:
            self.moderators.update(
                {"account": moderator["account"]}, moderator, upsert=True)

    def plot_leaderboard(self, category, status, group_by):
        line_chart = pygal.Bar()
        actors = "moderators"
        if group_by == "author":
            actors = "authors"
        line_chart.title = 'Top %s ' \
                           '(Category: %s, Status: %s)' \
                           % (actors, category, status)
        moderators = self.get_moderator_leaderboard(category, status, group_by)

        for mod in list(moderators)[0:25]:
            line_chart.add(mod["_id"], mod["count"])

        return line_chart

    def plot_overview(self, moderator, category, group_by):

        actor = "Moderator"
        if group_by == "author":
            actor = "Author"

        line_chart = pygal.Pie()
        line_chart.title = '%s Overview (%s - %s)' % (
            actor, moderator or "all", category or "all")
        if moderator:
            if group_by == "author":
                _, approved, hidden = self.get_moderator_overview(
                    category, author=moderator)
            else:
                _, approved, hidden = self.get_moderator_overview(
                    category, moderator=moderator)

        else:
            approved_query = {
                "reviewed": True,
            }
            hidden_query = {
                "flagged": True
            }
            if category:
                approved_query["json_metadata.type"] = category
                hidden_query["json_metadata.type"] = category

            approved = self.posts.find(approved_query).count()
            hidden = self.posts.find(hidden_query).count()

        stats = {
            "approved": approved,
            "hidden": hidden,
        }

        if approved > 0:
            line_chart.add(
                "Approved (%%%s)" % get_percent(stats, "approved"), approved)
        if hidden > 0:
            line_chart.add(
                "Rejected (%%%s)" % get_percent(stats, "hidden"), hidden)

        return line_chart

    def get_categories(self):
        return list(self.categories.find({}).sort("name", 1))

    def get_moderators(self):
        return list(self.moderators.find({}).sort("account", 1))

    def get_statuses(self):
        return ["hidden", "approved"]

    def run(self):
        self.fetch_approved_posts()
        self.fetch_hidden_posts()
