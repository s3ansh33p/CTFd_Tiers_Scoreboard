from flask import render_template
import os

from CTFd.models import Users, Challenges
from sqlalchemy.sql import and_
from CTFd.utils.scores import get_standings
from CTFd.utils.plugins import override_template
from CTFd.utils import get_config
from CTFd.utils.modes import TEAMS_MODE
from CTFd.utils import config
# teams
from CTFd.models import Teams

def get_team_affiliation(team_id):
    team = Teams.query.filter_by(id=team_id).first_or_404()
    return team.affiliation

def get_user_solves(user_id):
    user = Users.query.filter_by(id=user_id).first_or_404()
    solves = user.get_solves(admin=True)
    if get_config("user_mode") == TEAMS_MODE:
        if user.team:
            all_solves = user.team.get_solves(admin=True)
        else:
            all_solves = user.get_solves(admin=True)
    else:
        all_solves = user.get_solves(admin=True)
    return all_solves

def get_all_affiliations():
    # teams = Teams.query.all()
    # affiliations_list = []
    # for team in teams:
    #     if not team.affiliation in affiliations_list:
    #         affiliations_list.append(team.affiliation)
    # return affiliations_list
    return ['Tier 1', 'Tier 2'] # hardcoded for our needs

def load(app):
    def view_tiers():
        # override templates
        dir_path = os.path.dirname(os.path.realpath(__file__))
        template_path = os.path.join(dir_path, 'assets')
        template_path = os.path.join(template_path, 'scoreboard.html')
        override_template("scoreboard.html", open(template_path).read())

        # get affiliations
        affiliations = get_all_affiliations()

        # load scores
        standings = get_standings()

        ranks = []
        # rank[0] account_id
        # rank[1] name
        # rank[2] oauth_id
        # rank[3] score

        # ranks[ [TIER 1], [TIER 2] ]

        for index, affiliation in enumerate(affiliations):
            ranks.append([])
            for standing in standings:
                if get_team_affiliation(standing[0]) == affiliation:
                    account_id = standing.account_id
                    name = standing.name
                    oauth_id = standing.oauth_id
                    score = standing.score
                    ranks[index].append([account_id, name, oauth_id, score])

        return render_template("scoreboard.html", tiers=affiliations, enumerate=enumerate, ranks=ranks, standings=standings, score_frozen=config.is_scoreboard_frozen())

    app.view_functions['scoreboard.listing'] = view_tiers