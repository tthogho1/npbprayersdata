import requests
import os
import io
import time
import pandas as pd
from bs4 import BeautifulSoup

domain = "https://npb.jp/"
request_wait_seconds = 10 # waitなしでHTTPリクエストをだしていると途中で応答が返らなくなる。

def request_get(url):
    try:
        response = requests.get(url)
        time.sleep(request_wait_seconds)
        return response
    except requests.exceptions.RequestException as e:
        print(f"Error downloading page: {e}")
        print(f"URL: {url}")
        raise

def scrape_player_image(player_url,player_name,output_dir):
    response = request_get(player_url)
    soup = BeautifulSoup(response.content, 'html.parser', from_encoding='utf-8')
    div = soup.find('div', id='pc_v_photo')
    img = div.find('img')  
    if img:
        # 画像を保存
        img_url = img['src']
        img_path = f"{output_dir}/{player_name}.jpg"
        try:
            img_response = request_get(img_url)
            # 画像が存在する場合処理を抜ける
            if os.path.exists(img_path):
                return
            
            with open(img_path, 'wb') as f:
                f.write(img_response.content)
        except requests.exceptions.RequestException as e:
            print(f"Error downloading image: {e}")
            print(f"player_name: {player_name}")
            print(f"output_dir: {output_dir}")
            return
    else:
        print("No image found")

def scrape_team(team_url,output_dir):
    response = request_get(team_url)
    soup = BeautifulSoup(response.content, 'html.parser', from_encoding='utf-8')
    tables = soup.select('table')  # or use more specific selectors
    if tables:
        with io.StringIO(str(tables[1])) as f:            
            # get hrefs from table[1]
            players = tables[1].find_all('a', href=True)
            for player in players:
                player_name = player.text.strip()
                if (player_name == ""):
                    continue
                player_url = f"{domain}{player['href']}"  # player['href']
                #print(player_name)
                scrape_player_image(player_url,player_name,output_dir)                        
    else:
        print("No table found")


url = f"{domain}bis/teams/"
response = request_get(url)
soup = BeautifulSoup(response.content, 'html.parser')

leagues = soup.find_all('section', id='team_list')
for league in leagues:
    teams = league.find_all('a')
    for team in teams:
        team_name = team.text.strip()
        team_url = f"{url}{team['href']}"  # team['href']
        # ここで各球団のページを処理
        print(team_name)        
        #フォルダが存在していたら次のチームへ移る
        if os.path.exists(team_name):
            continue
        # チーム用のフォルダ作成
        os.makedirs(team_name, exist_ok=True)
        scrape_team(team_url,team_name)





