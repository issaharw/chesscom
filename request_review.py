import requests
import time
import argparse

BASE_URL = "https://api.chess.com/pub"
ARCHIVES_URL = "/player/issaharw/games/archives"
USERNAME = "issaharw"
PASSWORD = "jalingR4"


from enum import Enum
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains


def send_request(url):
    headers = {'User-Agent': 'username: issaharw, email: issahar.wss@gmail.com'}
    response = requests.get(url, headers=headers)
    return response.json()


def now_formatted():
    return time_formatted(int(round(time.time())))


def time_formatted(timestamp):
    return time.strftime("%Y-%m-%d_%H-%M-%S", time.gmtime(timestamp))


def get_archives():
    archives_json = send_request(BASE_URL + ARCHIVES_URL)
    return sorted(archives_json["archives"], reverse=True)


def get_games_urls_by_month(archive_url):
    games_json = send_request(archive_url)
    print(f"Got {len(games_json['games'])} games in this month: {archive_url}")
    sorted_games = sorted(games_json['games'], key=lambda x: x["end_time"], reverse=True)
    return [x["url"] for x in sorted_games if x.get("accuracies") is None]


def request_review_for_game(game_url):
    print(f"Requesting review for game url: {game_url}")
    driver = webdriver.Chrome()
    driver.maximize_window()
    actions = ActionChains(driver)
    try:
        driver.get("http://chess.com/login")
        # play_online_button = WebDriverWait(driver, 10).until(
        #     EC.element_to_be_clickable((By.CLASS_NAME, 'index-guest-button'))
        # )
        # play_online_button.click()
        #
        # open_log_in_button = WebDriverWait(driver, 10).until(
        #     EC.element_to_be_clickable((By.CLASS_NAME, 'cc-button-secondary'))
        # )
        # open_log_in_button.click()
        #
        email_field = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@type="email"]'))
        )
        password_field = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@type="password"]'))
        )

        email_field.send_keys(USERNAME)
        password_field.send_keys(PASSWORD)

        login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, 'login'))
        )
        login_button.click()

        driver.get(game_url)
        review_button = WebDriverWait(driver, 20).until(
            # EC.element_to_be_clickable((By.CLASS_NAME, 'game-over-review-button-component'))
            EC.element_to_be_clickable((By.XPATH, '//button[@aria-label="Game Review"]'))
        )
        review_button.click()

        # start_review_button = WebDriverWait(driver, 10).until(
        #     EC.element_to_be_clickable((By.XPATH, '//span[text()="Start Review"]'))
        # )

    except:
        print(Exception)
        driver.quit()
        raise
    finally:
        driver.quit()

if __name__ == '__main__':
    archives = get_archives()
    for archive in archives:
        urls = get_games_urls_by_month(archive)
        print(f"Got {len(urls)} games without accuracies in this month: {archive}")
        for game_url in urls:
            request_review_for_game(game_url)
