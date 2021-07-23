from selenium import webdriver
import time
import requests
import sys
import json
import env
driver = webdriver.Firefox()


def site_login(url, email, password):
    driver.get(url)
    driver.find_element_by_name("email").send_keys(email)
    driver.find_element_by_name("password").send_keys(password)
    driver.find_element_by_class_name("button--primary").click()
    actual_session = requests.session()
    g = actual_session.get(url)
    no_login_1 = "Please enter a valid email address"
    no_login_2 = "Hmm... That doesn't look like the right email or password."
    no_login_3 = "Failed to sign in. Please try again."
    if no_login_1 not in g.text and no_login_2 not in g.text and no_login_3 not in g.text:
        print("ATTENZIONE! LOGIN NON EFFETTUATO!")
        # sys.exit()


def change_language():
    driver.find_element_by_class_name("language-selector__button").click()
    driver.find_element_by_css_selector('button[data-qa="set-language-it_IT"]').click()


def go_to_streak(url):
    if not url.startswith("https://www.geoguessr.com/"):
        print("Url non valido")
        sys.exit()
    actual_session = requests.session()
    g = actual_session.get(url)
    if "Pagina non trovata" in g.text:
        print("Partita non trovata")
        sys.exit()
    driver.get(url)


def main():
    # TODO: Autoplay
    args = sys.argv[1:]
    url = "https://www.geoguessr.com/signin"
    email = env.USERNAME
    password = env.PASSWORD
    url_streak = env.URL
    if len(args) > 1:
        if "-url" in args and args[args.index("-url") + 1]:
            url_streak = args[args.index("-url") + 1]
        if "-l" in args and args[args.index("-l") + 1] and args[args.index("-l") + 2]:
            email = args[args.index("-l") + 1]
            password = args[args.index("-l") + 2]
    # site_login(url, email, password)
    # change_language()
    go_to_streak(url_streak)
    # Message wait 10 seconds, than click return the game
    time.sleep(11)
    driver.find_element_by_class_name("button--primary").click()

    # click next round
    driver.find_element_by_class_name("button--primary").click()

    while True:
        # load js script
        js = open("files/fetch_coord", "r").read()
        geo = driver.execute_script(js)
        actual_session = requests.session()
        get_geo = actual_session.get(geo)
        text = get_geo.text.split(",")

        # Fetch coord using Google, elements google +4 and +5
        google_index = text.index('[[[["© 2021 Google"]]]]')
        c1 = text[google_index + 4]
        c2 = text[google_index + 5][:-1]
        maps_url = f"https://api.tomtom.com/search/2/reverseGeocode/{c1},{c2}.JSON?key={env.KEY}"
        # Get Request to fetch Nation
        g = actual_session.get(maps_url)
        print(maps_url)
        res_code = json.loads(g.text)["addresses"][0]["address"]["countryCode"]
        print(json.loads(g.text)["addresses"][0]["address"]["country"])
        # read file with nation name
        nats = open("files/nat_it.txt", "r", encoding="utf8")
        for nat in nats:
            if res_code in nat:
                res = nat[:-5]
                break
        print(res)
        input("Continuare?\n")
        go_to_streak(url_streak)  # refresh
        time.sleep(10)


if __name__ == "__main__":
    main()
