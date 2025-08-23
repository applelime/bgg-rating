import pandas as pd
from sklearn.linear_model import LinearRegression
from datetime import date
import numpy as np
import math

def truncate_float(x: float, n: int) -> float:
    factor = 10 ** n
    return math.floor(x * factor) / factor

# --- 설정 ---
# 오늘 날짜를 기준으로 데이터 파일 경로 설정
INPUT_DATA_PATH = f'bgg_data_{date.today().strftime("%Y-%m-%d")}.csv'
OUTPUT_CSV_PATH = 'boardgames_re_ranked.csv'

# --- 1. 오늘 날짜로 수집된 데이터 불러오기 ---
print(f"1. '{INPUT_DATA_PATH}' 파일에서 데이터 불러오는 중...")
try:
    df_bgg = pd.read_csv(INPUT_DATA_PATH)
    print(f"   성공적으로 {len(df_bgg)}개 게임 데이터를 불러왔습니다.")
except FileNotFoundError:
    print(f"   오류: '{INPUT_DATA_PATH}' 파일을 찾을 수 없습니다.")
    print("   먼저 bgg-collecting.py 스크립트를 실행하여 데이터를 수집해주세요.")
    exit()

# --- 2. 복잡성 편향 분석 및 보정 ---
print("\n2. 복잡도 편향 분석 및 보정 평점 계산 중...")

# 분석에 필요한 데이터가 없는 경우(weight가 0 등)는 제외합니다.
df_bgg = df_bgg[df_bgg['weight'] > 0].copy()

if df_bgg.empty:
    print("   분석할 데이터가 없습니다. 프로그램을 종료합니다.")
    exit()

# 선형 회귀 모델을 준비합니다.
X = df_bgg[['weight']]
y = df_bgg['average']

model = LinearRegression()
model.fit(X, y)

# '기대 평점' 예측 및 '보정 평점' 계산
df_bgg['predicted_average'] = model.predict(X)
df_bgg['rating_difference'] = df_bgg['average'] - df_bgg['predicted_average']

# new_rating 계산: rating_difference + 전체 데이터의 average 평균
overall_average = df_bgg['average'].mean()
df_bgg['new_rating'] = df_bgg['rating_difference'] + overall_average

# 베이지안 보정 평점 계산
m = 5.5
c = 2000
df_bgg['bayes_new_rating'] = (df_bgg['usersrated'] * df_bgg['new_rating'] + m*c) / (df_bgg['usersrated'] + c)
df_bgg['rating_change'] = df_bgg['bayes_new_rating'] - df_bgg['average']

print("   복잡도 편향 분석이 완료되었습니다.")
print(f"   - 선형 회귀 모델: average = {model.coef_[0]:.4f} * weight + {model.intercept_:.4f}")

# 데이터 저장 전 소수점 처리
df_bgg['rating_difference'] = df_bgg['rating_difference'].apply(lambda x: truncate_float(x, 2))
df_bgg['rating_change'] = df_bgg['rating_change'].apply(lambda x: truncate_float(x, 2))
df_bgg['bayes_new_rating']= df_bgg['bayes_new_rating'].apply(lambda x: truncate_float(x, 5))

# --- 3. 새로운 순위 생성 및 저장 ---
print("\n3. 새로운 순위 생성 및 결과 저장 중...")

# 보정된 평점을 기준으로 내림차순 정렬하여 새로운 순위를 매깁니다.
df_final = df_bgg.sort_values('bayes_new_rating', ascending=False).copy()
df_final['new_rank'] = range(1, len(df_final) + 1)

# 원본 순위 컬럼명을 변경합니다.
df_final.rename(columns={'rank': 'original_rank'}, inplace=True)

# 컬럼 순서를 정리합니다.
output_columns = [
    'new_rank', 'original_rank', 'id', 'name', 'yearpublished', 'recommended_players', 'weight', 'average',
    'rating_difference', 'bayes_new_rating', 'rating_change'
]
# 'original_rank'가 없는 경우를 대비하여 있는 컬럼만 선택
output_columns = [col for col in output_columns if col in df_final.columns]
df_final = df_final[output_columns]

# 결과를 CSV 파일로 저장합니다.
df_final.to_csv(OUTPUT_CSV_PATH, index=False, encoding='utf-8-sig')

print(f"   새로운 순위 데이터를 '{OUTPUT_CSV_PATH}'에 성공적으로 저장했습니다.")

# --- 4. 상위 100개 결과 출력 ---
print("\n--- Top 100 Re-ranked Board Games ---")
# 보기 좋게 출력하기 위해 to_string()을 사용하고 인덱스는 제외합니다.
print(df_final[['new_rank', 'original_rank', 'name', 'yearpublished', 'recommended_players', 'weight', 'bayes_new_rating']].head(100).to_string(index=False))

print("\n계산 작업이 완료되었습니다!")
