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
        rosters = get_rosters(league_id)
        return render_template('home_page.html', id=league_id, rosters=rosters)
    return render_template('home_page.html')


# get all rosters from a league given a league id using the sleeper API
def get_rosters(league_id):
    rosters = []
    # get all rosters from a league
    url = "https://api.sleeper.app/v1/league/" + league_id + "/rosters"
    response = requests.get(url)
    data = response.json()
    # load json data from sleeper_players.json into an object
    players = json.load(open('sleeper_players.json'))

    if data is not None:
        for roster in data:
            r = {}
            r['owner_id'] = roster['owner_id']
            r['qbs'] = [players[p]['full_name'] for p in roster['players'] if players[p]['position'] == 'QB']
            r['rbs'] = [players[p]['full_name'] for p in roster['players'] if players[p]['position'] == 'RB']
            r['wrs'] = [players[p]['full_name'] for p in roster['players'] if players[p]['position'] == 'WR']
            r['tes'] = [players[p]['full_name'] for p in roster['players'] if players[p]['position'] == 'TE']
            r['ks'] = [players[p]['full_name'] for p in roster['players'] if players[p]['position'] == 'K']                
            r['players'] = roster['players']
            r['starters'] = roster['starters']
            r['reserve'] = roster['reserve']
            rosters.append(r)
    return rosters