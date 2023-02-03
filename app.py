from collections import defaultdict
import json
from flask import Flask, render_template, request
import requests
import statistics
app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        # do something
        if request.form['id']:
            league_id = request.form['id']
            league_info = get_league_info(league_id)
            if league_info:
                league_name = get_league_info(league_id)['name']
                rosters = get_rosters(league_id)
                players = json.load(open('sleeper_players.json'))
                print(get_avg_and_stdev(rosters))
                return render_template('home_page.html', id=league_id, rosters=rosters, league_name=league_name, players=players, stats=get_avg_and_stdev(rosters))
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

    if data is not None:
        for roster in data:
            r = {}
            r['owner_id'] = users[roster['owner_id']]['display_name'] if roster['owner_id'] in users else roster['owner_id']
            r['defs'] = [players[p]['player_id'] for p in roster['players'] if players[p]['position'] == 'DEF']
            r['players'] = roster['players']
            r['starters'] = roster['starters']
            r['reserve'] = roster['reserve']

            player_object_list = []
            for player in roster['players']:
                # checking for a full_name prevents us from adding Defenses to the player list
                if 'full_name' in players[player]:
                    player_object = {
                        'player_id': players[player]['player_id'],
                        'position': players[player]['position'],
                        'full_name': players[player]['full_name'],
                        'rank': players[player]['search_rank']
                    }
                    player_object_list.append(player_object)
            
            player_object_list.sort(key=lambda x: x['rank'])
            r['player_objects'] = player_object_list

            # get the average search rank for the whole team and each positional group
            r['avg_team_rank'] = get_avg_rank(player_object_list)
            r['avg_qb_rank'] = get_avg_rank(player_object_list, 'QB')
            r['avg_rb_rank'] = get_avg_rank(player_object_list, 'RB')
            r['avg_wr_rank'] = get_avg_rank(player_object_list, 'WR')
            r['avg_te_rank'] = get_avg_rank(player_object_list, 'TE')

            print(r['owner_id'], r['avg_team_rank'], r['avg_qb_rank'], r['avg_rb_rank'], r['avg_wr_rank'], r['avg_te_rank'])
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

# calculate the average search rank for a list of players
def get_avg_rank(players, position=None):
    if position is not None:
        players = [p for p in players if p['position'] == position]
    else:
        # for a full roster, drop the last 3 players by search rank to not punish teams with speculative depth/meme players
        players = players[:-3]

    # if RB or WR, only take the top 4 players at that position
    if position == 'RB' or position == 'WR':
        players = players[:4]
    
    # if QB or TE, only take the top 1 player at that position
    if position == 'QB' or position == 'TE':
        players = players[:1]

    # if a player has a rank over 1000, give them a rank of 300
    # this is because the sleeper API has some fantasy relevant players with a rank of 9999999
    return sum([p['rank'] if p['rank'] < 1000 else 300 for p in players]) / len(players)

# return a tuple of the avg and stdev of the ranks of each roster
def get_avg_and_stdev(rosters):
    positions = ['qb', 'rb', 'wr', 'te', 'team']
    stats = {}
    for position in positions:
        ranks = []
        for roster in rosters:
            ranks.append(roster['avg_' + position + '_rank'])
        print(position, ranks)
        stats[position] = (statistics.mean(ranks), statistics.stdev(ranks))
    return stats