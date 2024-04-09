import requests
import time

BASE_URL = "https://api.chess.com/pub"
CLUB_URL = BASE_URL + "/club"
CLUB_ID = "https://api.chess.com/pub/club/platense"


def send_request(url):
    headers = {'User-Agent': 'username: elmorejames, email: norberto.rosemberg@crowe.com.ar'}
    response = requests.get(url, headers=headers)
    return response.json()


def now_formatted():
    return time_formatted(int(round(time.time())))


def time_formatted(timestamp):
    return time.strftime("%Y-%m-%d_%H-%M-%S", time.gmtime(timestamp))


def get_club_finished_matches(club_id):
    url = CLUB_URL + f"/{club_id}/matches"
    matches = send_request(url)
    return matches["finished"]


def get_match(match_url):
    match = send_request(match_url)
    match_url = match["url"]
    match_name = match["name"]
    match_start = time_formatted(match["start_time"])
    match_end = time_formatted(match["end_time"])
    match_rules = match["settings"]["rules"]
    match_time_class = match["settings"]["time_class"]
    match_time_control = match["settings"]["time_control"]
    for key, value in match["teams"].items():
        if value["@id"] == CLUB_ID:
            return [match_url, match_name, match_start, match_end, match_rules, match_time_class, match_time_control, value["players"]]
    return [None, None, None, None, None, None, None, None]


def get_timed_out_boards(boards):
    timed_out_board = []
    for board in boards:
        white_result = board.get("played_as_white")
        black_result = board.get("played_as_black")
        if white_result == "timeout" or black_result == "timeout":
            timed_out_board.append(board)
    return timed_out_board

def get_timed_out_game_in_board_for_user(username, board_url):
    games = []
    board_games = send_request(board_url)
    first_games = board_games["games"][0]
    second_games = board_games["games"][1]
    if lost_on_timeout(username, first_games["white"]) or lost_on_timeout(username, first_games["black"]):
        games.append(first_games)
    if lost_on_timeout(username, second_games["white"]) or lost_on_timeout(username, second_games["black"]):
        games.append(second_games)
    return games


def lost_on_timeout(username, side):
    return side["username"].lower() == username and side["result"] == "timeout"


def get_game_details_for_user(username, game):
    url = game["url"]
    start_time = time_formatted(game["start_time"])
    end_time = time_formatted(game["end_time"])
    if lost_on_timeout(username, game["white"]):
        color = "white"
    elif lost_on_timeout(username, game["black"]):
        color = "black"
    else:
        color = None
    return url, start_time, end_time, color

if __name__ == '__main__':
    matches = get_club_finished_matches("platense")
    matches.sort(key=lambda match: match['start_time'], reverse=True)
    headers_row = "Match URL, Match Name, Match Start, Match End, Match Rules, Match Time Class, Match Time Control, Username, Color, Game URL, Game Start Time, Game End Time\n"
    file_name = f"./Timed-Out-Games-{now_formatted()}.csv"
    with open(file_name, 'w') as file:
        file.write(headers_row)
        for match in matches:
            match_url, match_name, match_start, match_end, match_rules, match_time_class, match_time_control, boards = get_match(match["@id"])
            timed_out_boards = get_timed_out_boards(boards)
            if len(timed_out_boards) > 0:
                print(f"Match: {match_name} ({match_url}), Started: {match_start}.    Has {len(timed_out_boards)} timeout(s): ")
                for timed_out_board in timed_out_boards:
                    username = timed_out_board["username"].lower()
                    timed_out_games = get_timed_out_game_in_board_for_user(username, timed_out_board["board"])
                    for game in timed_out_games:
                        game_url, game_start_time, game_end_time, color = get_game_details_for_user(username, game)
                        row = f"{match_url}, {match_name}, {match_start}, {match_end}, {match_rules}, {match_time_class}, {match_time_control}, {username}, {color}, {game_url}, {game_start_time}, {game_end_time}\n"
                        file.write(row)
