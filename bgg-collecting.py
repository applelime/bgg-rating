import pandas as pd
import requests
import xml.etree.ElementTree as ET
import time
from tqdm import tqdm
from datetime import date

# --- 설정 ---
INPUT_CSV_PATH = 'boardgames_ranks.csv'
# 오늘 날짜를 포함한 출력 파일 경로 설정
OUTPUT_CSV_PATH = f'bgg_data_{date.today().strftime("%Y-%m-%d")}.csv'
TOP_N_GAMES = 5000
BGG_API_ENDPOINT = 'https://www.boardgamegeek.com/xmlapi2/thing'
BATCH_SIZE = 20

# --- 1. CSV 파일에서 상위 N개 게임 ID 추출 ---
print(f"1. '{INPUT_CSV_PATH}'에서 상위 {TOP_N_GAMES}개 게임 불러오는 중...")
try:
    df_ranks = pd.read_csv(INPUT_CSV_PATH)
    df_ranks = df_ranks[df_ranks['rank'] > 0]
    top_games_df = df_ranks.sort_values('rank').head(TOP_N_GAMES)
    game_ids = top_games_df['id'].tolist()
    print(f"   성공적으로 {len(game_ids)}개 게임 ID를 불러왔습니다.")
except FileNotFoundError:
    print(f"   오류: '{INPUT_CSV_PATH}' 파일을 찾을 수 없습니다. 파일이 올바른 디렉토리에 있는지 확인해주세요.")
    exit()

# --- 2. BGG API를 통해 게임 상세 정보(weight, average) 가져오기 ---
print(f"\n2. BoardGameGeek API에서 {len(game_ids)}개 게임의 상세 정보를 가져오는 중...")
print("   이 작업은 시간이 걸릴 수 있습니다. 진행 상황은 아래에 표시됩니다.")

all_game_data = []

for i in tqdm(range(0, len(game_ids), BATCH_SIZE), desc="배치 처리 중"):
    batch_ids = game_ids[i:i + BATCH_SIZE]
    ids_str = ','.join(map(str, batch_ids))
    url = f"{BGG_API_ENDPOINT}?id={ids_str}&stats=1"
    try:
        response = requests.get(url)
        response.raise_for_status()
        root = ET.fromstring(response.content)
        for item in root.findall('item'):
            game_id = int(item.get('id'))
            # 일부 게임은 이름이 여러 개일 수 있으므로 primary 이름을 가져옵니다.
            name_element = item.find("name[@type='primary']")
            name = name_element.get('value') if name_element is not None else "N/A"
            
            stats = item.find('statistics/ratings')
            average = float(stats.find('average').get('value'))
            weight = float(stats.find('averageweight').get('value'))
            usersrated = float(stats.find('usersrated').get('value'))
            
            all_game_data.append({
                'id': game_id,
                'name': name,
                'average': average,
                'weight': weight,
                'usersrated': usersrated
            })
    except requests.exceptions.RequestException as e:
        print(f"   API 요청 중 오류가 발생했습니다: {e}")
        pass
    time.sleep(2)

print(f"   성공적으로 {len(all_game_data)}개 게임의 데이터를 가져왔습니다.")

# --- 3. 수집한 데이터를 파일로 저장 ---
if all_game_data:
    print(f"\n3. 수집된 데이터를 '{OUTPUT_CSV_PATH}' 파일로 저장하는 중...")
    df_bgg = pd.DataFrame(all_game_data)
    # 원본 순위 정보도 추가합니다.
    df_bgg_with_rank = df_bgg.merge(top_games_df[['id', 'rank']], on='id', how='left')
    df_bgg_with_rank.to_csv(OUTPUT_CSV_PATH, index=False, encoding='utf-8-sig')
    print(f"   데이터를 성공적으로 저장했습니다.")
else:
    print("\n데이터를 수집하지 못해 파일을 저장하지 않습니다.")

print("\n수집 작업이 완료되었습니다!")
