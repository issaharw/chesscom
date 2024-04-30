import requests
import time
import argparse

BASE_URL = "https://api.chess.com/pub"
CLUB_URL = BASE_URL + "/club"
CLUB_ID = "https://api.chess.com/pub/club/platense"

DRAW_RESULTS = ["agreed", "repetition", "stalemate", "insufficient", "50move", "timevsinsufficient"]

tournament_names = []

def send_request(url):
    headers = {'User-Agent': 'username: elmorejames, email: norberto.rosemberg@crowe.com.ar'}
    response = requests.get(url, headers=headers)
    return response.json()


def now_formatted():
    return time_formatted(int(round(time.time())))


def time_formatted(timestamp):
    return time.strftime("%Y-%m-%d_%H-%M-%S", time.gmtime(timestamp))

def fill_tournament_names():
    global tournament_names
    with open('tournament_names.txt', 'r') as file:
        tournament_names = [line.strip() for line in file]


def get_club_finished_matches(club_id):
    url = CLUB_URL + f"/{club_id}/matches"
    matches = send_request(url)
    return matches["finished"]


def filter_matches(matches, type, tournament, minelo, maxelo):
    filtered_matches = []
    for match_id in matches:
        match = send_request(match_id["@id"])
        match_name = match["name"]
        match_rules = match["settings"]["rules"]
        match_min_rating = match["settings"].get("min_rating")
        match_max_rating = match["settings"].get("max_rating")

        passed_tournament = True
        if tournament is not None:
            passed_tournament = (match_name in tournament_names) == tournament

        passed_type = True
        if type:
            passed_type = match_rules == type

        if not minelo and not maxelo:
            passed_restrictions = not match_min_rating and not match_max_rating
        elif not minelo:
            if match_max_rating:
                passed_restrictions = match_max_rating <= maxelo
            else:
                passed_restrictions = True
        elif not maxelo:
            if match_min_rating:
                passed_restrictions = match_min_rating >= minelo
            else:
                passed_restrictions = True
        else:
            if not match_min_rating or not match_max_rating:
                passed_restrictions = False
            else:
                passed_restrictions = match_min_rating >= minelo and match_max_rating <= maxelo

        if passed_tournament and passed_type and passed_restrictions:
            filtered_matches.append(match)

        print(f"Match {match['name']}. Passed: {passed_tournament and passed_type and passed_restrictions}")

    return filtered_matches


def build_leaderboard(matches):
    leaderboard = {}
    for match in matches:
        players = get_match_players(match)
        for player in players:
            username = player["username"]
            result = get_player_result_in_match(player)
            if leaderboard.get(username):
                leaderboard[username] = leaderboard.get(username) + result
            else:
                leaderboard[username] = result

    return leaderboard


def get_match_players(match):
    players = []
    for key, value in match["teams"].items():
        if value["@id"] == CLUB_ID:
            players = value["players"]
    return players


def get_player_result_in_match(player):
    result = 0
    white_res = player.get("played_as_white")
    black_res = player.get("played_as_black")
    if white_res == "win":
        result += 1
    elif white_res in DRAW_RESULTS:
        result += 0.5
    if black_res == "win":
        result += 1
    elif black_res in DRAW_RESULTS:
        result += 0.5
    return result


def get_user_profiles(users):
    return [send_request(f"{BASE_URL}/player/{username}") for username in users]

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Club members")
    parser.add_argument("-t", "--type", type=str, help="Chess Type")
    parser.add_argument("-minelo", "--minelo", type=int, help="Minimum ELO")
    parser.add_argument("-maxelo", "--maxelo", type=int, help="Maximum ELO")
    parser.add_argument("-tour", "--tournament", type=bool, help="Tournament of Friendly")
    args = parser.parse_args()
    print(f"Returning leaderboards for match type {args.type}, with min elo {args.minelo} and max elo {args.maxelo}.")

    if args.tournament:
        fill_tournament_names()

    matches = get_club_finished_matches("platense")
    matches = filter_matches(matches, args.type, args.tournament, args.minelo, args.maxelo)
    leaderboard = build_leaderboard(matches)
    users_profiles = get_user_profiles(leaderboard.keys())
    for user in users_profiles:
        username = user["username"]
        user["result_for_club"] = leaderboard[username]
    users_profiles.sort(key=lambda user: user['result_for_club'], reverse=True)

    headers_row = "Username, Name, URL, Result\n"
    file_name = f"./Leaderboard-for-{args.type}-{now_formatted()}.csv"
    with open(file_name, 'w') as file:
        file.write(headers_row)
        for user_profile in users_profiles:
            username = user_profile.get("username")
            name = user_profile.get("name")
            url = user_profile.get("url")
            result = user_profile.get("result_for_club")
            row = f"{username}, {name}, {url}, {result}\n"
            file.write(row)
