import requests
import os
import io
import time
import pandas as pd
from bs4 import BeautifulSoup

domain = "https://npb.jp/"
request_wait_seconds = 5 # waitなしでHTTPリクエストをだしていると途中で応答が返らなくなる。

def request_get(url):
    response = requests.get(url)
    time.sleep(request_wait_seconds)
    return response

def scrape_player(player_url,player_name,output_dir):
    response = request_get(player_url)
    soup = BeautifulSoup(response.content, 'html.parser', from_encoding='utf-8')
    section = soup.find('section', id='pc_bio')
    table = section.find('table')  # or use more specific selectors
    if table:
        # テーブルから余分な改行を削除
        with io.StringIO(str(table)) as f:
            df = pd.read_html(f)[0]
            csv_string = df.to_csv(index=False,lineterminator='\n')
            # csv_string の最初の改行までを削除　先頭に0,1\n　が含まれてしまうので削除する
            csv_string = csv_string.split('\n', 1)[1]
            
            output_path = f"{output_dir}/{player_name}.csv"
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(csv_string)
    else:
        print("No table found")


def scrape_team(team_url,output_dir):
    response = request_get(team_url)
    #soup = BeautifulSoup(response.text, 'html.parser')
    soup = BeautifulSoup(response.content, 'html.parser', from_encoding='utf-8')
    tables = soup.select('table')  # or use more specific selectors
    if tables:
        with io.StringIO(str(tables[1])) as f:
            df = pd.read_html(f)[0]
            # Convert DataFrame to CSV string
            csv_string = df.to_csv(index=False,lineterminator='\n')            
            #print(csv_string)
            output_path = f"{output_dir}/players.csv"
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(csv_string)
            
            # get hrefs from table[1]
            players = tables[1].find_all('a', href=True)
            for player in players:
                player_name = player.text.strip()
                if (player_name == ""):
                    continue
                player_url = f"{domain}{player['href']}"  # player['href']
                #print(player_name)
                scrape_player(player_url,player_name,output_dir)
                # ここで各選手のページを処理                        
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
        # チーム用のフォルダ作成
        os.makedirs(team_name, exist_ok=True)
        scrape_team(team_url,team_name)





