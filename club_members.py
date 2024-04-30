import requests
import time
import argparse

BASE_URL = "https://api.chess.com/pub"
CLUB_URL = BASE_URL + "/club"
CLUB_ID = "https://api.chess.com/pub/club/platense"
DAY_IN_SEC = 60 * 60 * 24



def send_request(url):
    headers = {'User-Agent': 'username: elmorejames, email: norberto.rosemberg@crowe.com.ar'}
    response = requests.get(url, headers=headers)
    return response.json()

def current_time():
    return int(round(time.time()))

now = current_time()

def now_formatted():
    return time_formatted(int(round(time.time())))


def time_formatted(timestamp):
    return time.strftime("%Y-%m-%d_%H-%M-%S", time.gmtime(timestamp))


def get_club_members(club_id):
    url = CLUB_URL + f"/{club_id}/members"
    members = send_request(url)
    keys = ["weekly", "monthly", "all_time"]
    all_members = []
    for key in keys:
        all_members += [member['username'] for member in members[key]]
    return all_members


def get_member_stats(username):
    url = BASE_URL + f"/player/{username}/stats"
    return send_request(url)


def get_member_profile(username):
    url = BASE_URL + f"/player/{username}"
    profile = send_request(url)
    return profile


def get_active_members_in_last_days(members, days):
    last_active_members = {}
    for username in members:
        profile = get_member_profile(username)
        if profile["last_online"] + (DAY_IN_SEC * days) > now:
            last_active_members[username] = profile
    return last_active_members
    #
    # return [profile for profile in members if get_member_last_active(username) + (DAY_IN_SEC * days) > now]


def filter_member(stats, type, elo):
    stats_by_type = stats.get(type)
    if not stats_by_type:
        return False
    last_elo = stats_by_type["last"]["rating"]
    return last_elo >= elo



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Club members")
    parser.add_argument("-d", "--days", type=int, default=7, help="Active in the past days")
    parser.add_argument("-elo", "--elo", type=int, default=1500, help="Minimum ELO")
    parser.add_argument("-t", "--type", type=str, default='chess_daily', help="Chess Type for minimum ELO")

    args = parser.parse_args()

    print(f"Returning members active in the last {args.days} days, that their {args.type} rating is above {args.elo}.")
    if not args.elo or not args.type:
        print("Minimum ELO or chess type weren't provided, returning all members")

    members = get_club_members("platense")
    active_members = get_active_members_in_last_days(members, args.days)
    members_stats = {}
    for username in active_members:
        print(f"Getting {username} stats...")
        member_stats = get_member_stats(username)
        if filter_member(member_stats, args.type, args.elo):
            members_stats[username] = member_stats

    headers_row = "Username, Name, User URL, Last Online, Last ELO\n"
    file_name = f"./Last-Active_Members-For-{args.type}-With-ELO-{args.elo}-{now_formatted()}.csv"
    with open(file_name, 'w') as file:
        file.write(headers_row)
        for username, stats in members_stats.items():
            profile = active_members[username]
            name = profile.get("name")
            url = profile.get("url")
            last_online = profile.get("last_online")
            elo = 0
            stats_by_type = stats.get(args.type)
            if stats_by_type:
                elo = stats[args.type]["last"]["rating"]
            row = f"{username}, {name}, {url}, {time_formatted(last_online)}, {elo}\n"
            file.write(row)
