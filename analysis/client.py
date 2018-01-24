import requests
import urllib
import urllib.parse


class Client:

    API_BASE_URL = "https://api.utopian.io/api/"

    def _generate_url(self, action, query_params=None):

        if query_params:
            if not isinstance(query_params, dict):
                raise TypeError(
                    "query_string variable should be a dictionary.")

        if query_params:
            action = "{}/?{}".format(
                action, urllib.parse.urlencode(query_params))

        abs_url = urllib.parse.urljoin(self.API_BASE_URL, action)

        return abs_url

    @property
    def moderators(self):
        """
        Returns JSON containing all Utopian.io moderators.
        """
        return requests.get(self._generate_url("moderators")).json()

    @property
    def sponsors(self):
        """
        Returns JSON containing all Utopian.io sponsors.
        """
        return requests.get(self._generate_url("sponsors")).json()

    def is_moderator(self, account):
        """
        Returns true if account is a Utopian.io moderator.

        :param string account: A Steemit username
        """
        return account in [m["account"] for m in self.moderators["results"]]

    def is_sponsor(self, account):
        """
        Returns true if account is a Utopian.io sponsor.

        :param string account: A Steemit username
        """
        return account in [m["account"] for m in self.sponsors["results"]]

    def posts(self, query_params=None):
        """
        Returns JSON containing all posts that satisfy the given `query_params`.

        :param dict query_params: Query parameters
        """
        if not query_params:
            query_params = {}

        return requests.get(
            self._generate_url("posts", query_params=query_params)).json()

    def post(self, account, permlink):
        """
        Returns JSON containing information about a post.

        :param string account: A Steemit username
        :param string permlink: A permlink of a post
        """
        return requests.get(
            self._generate_url("posts/%s/%s" % (account, permlink))).json()

    @property
    def stats(self):
        """
        Returns JSON containing statistics about Utopian.io.
        """
        return requests.get(self._generate_url("stats")).json()["stats"]

    @property
    def bot_is_voting(self):
        """
        Returns true if the Utopian.io bot is currently voting.
        """
        return self.stats["bot_is_voting"]

    def count(self, query_params=None):
        """
        Returns the count of posts that satisfy the given `query_params`.

        :param dict query_params: Query parameters
        """
        if not query_params:
            query_params = {"limit": 1}
        else:
            query_params.update({"limit": 1})

        return self.posts(query_params)["total"]