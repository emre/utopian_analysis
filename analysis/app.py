from flask import Flask, render_template, request
app = Flask(__name__)

from .utils import get_analyzer


@app.route("/moderators/leaderboard")
def moderator_leaderboard():
    analyzer = get_analyzer()

    category, status = "all", "all"
    if request.args.get("category"):
        category = request.args["category"]

    if request.args.get("review_status"):
        status = request.args["review_status"]

    chart = analyzer.plot_leaderboard(
        category, status, group_by="moderator"
    ).render_data_uri()

    return render_template(
        "moderators/leaderboard.html",
        chart=chart,
        categories=["all"] + [c["name"] for c in analyzer.get_categories()],
        statuses=["all"] + analyzer.get_statuses(),
        selected_category=category,
        selected_status=status,
    )


@app.route("/contributors/leaderboard")
def contributor_leaderboard():
    analyzer = get_analyzer()

    category, status = "all", "all"
    if request.args.get("category"):
        category = request.args["category"]

    if request.args.get("review_status"):
        status = request.args["review_status"]

    chart = analyzer.plot_leaderboard(
        category, status, group_by="author"
    ).render_data_uri()

    return render_template(
        "contributors/leaderboard.html",
        chart=chart,
        categories=["all"] + [c["name"] for c in analyzer.get_categories()],
        statuses=["all"] + analyzer.get_statuses(),
        selected_category=category,
        selected_status=status,
    )

@app.route("/moderators/overview/")
def moderator_overview():
    analyzer = get_analyzer()
    moderator = request.args.get("moderator")
    category = request.args.get("category")

    chart = analyzer.plot_overview(
        moderator, category, group_by="moderator").render_data_uri()

    return render_template(
        "moderators/overview.html",
        chart=chart,
        categories=["all"] + [c["name"] for c in analyzer.get_categories()],
        moderators=["all"] + [m["account"] for m in analyzer.get_moderators()],
        selected_category=category,
        selected_moderator=moderator,
    )


@app.route("/contributors/overview/")
def contributor_overview():
    analyzer = get_analyzer()
    contributor = request.args.get("contributor")
    if not contributor:
        return "select a contributor: example: ?contributor=ruah"
    category = request.args.get("category")

    chart = analyzer.plot_overview(
        contributor, category, "author").render_data_uri()

    return render_template(
        "contributors/overview.html",
        chart=chart,
        categories=["all"] + [c["name"] for c in analyzer.get_categories()],
        selected_category=category,
        contributors=[contributor, ],
        selected_contributor=contributor,
    )


@app.route("/")
def index():
    return render_template("index.html")