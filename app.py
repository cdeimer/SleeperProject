from collections import defaultdict
import json
from flask import Flask, render_template, request
import requests
app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        # do something
        league_id = request.form['id']
        league_name = get_league_info(league_id)['name']
        rosters = get_rosters(league_id)
        players = json.load(open('sleeper_players.json'))
        print(rosters)
        return render_template('home_page.html', id=league_id, rosters=rosters, league_name=league_name, players=players)
    return render_template('home_page.html')


# get all rosters from a league given a league id using the sleeper API
def get_rosters(league_id):
    rosters = []
    url = "https://api.sleeper.app/v1/league/" + league_id + "/rosters"
    response = requests.get(url)
    data = response.json()
    # load json data from sleeper_players.json into an object
    players = json.load(open('sleeper_players.json'))
    users = get_users(league_id)
    print(users)

    if data is not None:
        for roster in data:
            r = {}
            r['owner_id'] = users[roster['owner_id']]['display_name'] if roster['owner_id'] in users else roster['owner_id']
            r['qbs'] = [p for p in roster['players'] if players[p]['position'] == 'QB']
            r['rbs'] = [p for p in roster['players'] if players[p]['position'] == 'RB']
            r['wrs'] = [p for p in roster['players'] if players[p]['position'] == 'WR']
            r['tes'] = [p for p in roster['players'] if players[p]['position'] == 'TE']
            r['ks'] = [p for p in roster['players'] if players[p]['position'] == 'K']
            r['defs'] = [players[p]['player_id'] for p in roster['players'] if players[p]['position'] == 'DEF']
            r['players'] = roster['players']
            r['starters'] = roster['starters']
            r['reserve'] = roster['reserve']
            rosters.append(r)
    return rosters

# get all users from a league given a league id
def get_users(league_id):
    users = {}
    url = "https://api.sleeper.app/v1/league/" + league_id + "/users"
    response = requests.get(url)
    data = response.json()
    if data is not None:
        for user in data:
            u = {}
            u['display_name'] = user['display_name']
            # not all users have a team name
            if "team_name" in user['metadata']:
                u['team_name'] = user['metadata']['team_name']
            else:
                u['team_name'] = 'Team ' + user['display_name']

            users[user['user_id']] = u

    return users

# get league info given a league id
def get_league_info(league_id):
    url = "https://api.sleeper.app/v1/league/" + league_id
    response = requests.get(url)
    data = response.json()
    return data