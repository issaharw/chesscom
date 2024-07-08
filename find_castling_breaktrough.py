import requests
import time
import re

BASE_URL = "https://api.chess.com/pub"

DRAW_RESULTS = ["agreed", "repetition", "stalemate", "insufficient", "50move", "timevsinsufficient"]

tournament_names = []

def send_request(url):
    headers = {'User-Agent': 'username: issaharw, email: issahar.wss@gmail.com'}
    response = requests.get(url, headers=headers)
    return response.json()


def now_formatted():
    return time_formatted(int(round(time.time())))


def time_formatted(timestamp):
    return time.strftime("%Y-%m-%d_%H-%M-%S", time.gmtime(timestamp))


def get_games_archives():
    archives = send_request(f"{BASE_URL}/player/issaharw/games/archives")
    return sorted(archives["archives"], reverse=True)


def get_games(url):
    games = send_request(url)
    games = games['games']
    games.sort(key=lambda game: game['end_time'], reverse=True)
    return games


def get_game_color_and_result(game):
    if game['white']['username'].lower() == 'issaharw':
        return 'w', game['white']['result']
    elif game['black']['username'].lower() == 'issaharw':
        return 'b', game['black']['result']
    else:
        raise AttributeError("There was a problem with the username")


def is_breakthrough_on_castling(pgn, color):
    if color == 'w':
        short_castle_pattern = r'(\d+)\. O-O'
        short_castle_pawn_moves = [r'(\d+)\.\.\. g4', r'(\d+)\.\.\. h4']

        if find_breakthrough(pgn, short_castle_pattern, short_castle_pawn_moves):
            return True

        long_castle_pattern = r'(\d+)\. O-O-O'
        long_castle_pawn_moves = [r'(\d+)\.\.\. a4', r'(\d+)\.\.\. b4']

        if find_breakthrough(pgn, long_castle_pattern, long_castle_pawn_moves):
            return True
    else:
        short_castle_pattern = r'(\d+)\.\.\. O-O'
        short_castle_pawn_moves = [r'(\d+)\. h5', r'(\d+)\. g5']

        if find_breakthrough(pgn, short_castle_pattern, short_castle_pawn_moves):
            return True

        long_castle_pattern = r'(\d+)\.\.\. O-O-O'
        long_castle_pawn_moves = [r'(\d+)\. a5', r'(\d+)\. b5']

        if find_breakthrough(pgn, long_castle_pattern, long_castle_pawn_moves):
            return True


def find_breakthrough(pgn, castling_pattern, pawn_moves_patterns):
    matches = re.finditer(castling_pattern, pgn)
    castling_move_number = -1
    for match in matches:
        castling_move_number = int(match.group(1))

    if castling_move_number < 0:
        return False

    for pawn_pattern in pawn_moves_patterns:
        matches = re.finditer(pawn_pattern, pgn)
        for match in matches:
            pawn_move_number = match.group(1)
            if int(pawn_move_number) > castling_move_number:
                return True

    return False


def find_games():
    archives = get_games_archives()
    headers_row = "URL, Color, Score, Result, Time\n"
    file_name = f"./Castling-Breakthrough-{now_formatted()}.csv"
    with open(file_name, 'w') as file:
        file.write(headers_row)
        for archive in archives:
            games = get_games(archive)
            print(f"Archive: {archive} has {len(games)} games...")
            for game in games:
                color, result = get_game_color_and_result(game)
                score = 0
                if result == 'win':
                    score = 1
                elif result in DRAW_RESULTS:
                    score = 0.5
                if is_breakthrough_on_castling(game['pgn'], color):
                    row = f"{game['url']}, {color}, {score}, {result}, {time_formatted(game['end_time'])}\n"
                    file.write(row)


if __name__ == '__main__':
    find_games()