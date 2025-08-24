# BoardGameGeek 복잡도 편향 보정

BoardGameGeek(BGG)의 게임 랭킹은 게임의 복잡도(weight)가 높을수록 평점도 높아지는 경향이 있습니다.  
이로 인해 비교적 쉬운 게임들이 랭킹에서 저평가되는 현상이 발생할 수 있습니다.  
이 프로젝트는 이러한 weight 편향을 보정하여 보다 공정한 새로운 게임 랭킹을 생성하는 것을 목표로 합니다.

## 📃 작업 개요

1. **BGG API를 통한 데이터 수집**  
BGG API를 활용하여 게임의 상세 정보(평점, 복잡도, 평가자 수 등)를 수집합니다.  

2. **복잡도 편향 분석**  
선형 회귀(Linear Regression) 모델을 사용하여 게임의 복잡도에 따른 기대 평점을 계산합니다.  

3. **보정된 평점 (`new_rating`) 계산**  
실제 평점과 기대 평점의 차이(`rating_difference`)에 전체 게임의 평균 평점을 더하여 복잡도 편향이 보정된 새로운 평점을 산출합니다.  

4. **베이지안 보정 평점 (`bayes_new_rating`) 계산**  
보정된 평점에 실제 평가 수를 반영하고, 중간 평점(5.5)의 2000개의 평가를 추가하여 최종 베이지안 보정 평점을 산출합니다.  

5. **새로운 랭킹 생성**  
보정된 평점을 기준으로 게임의 새로운 순위를 매깁니다.


## 🛠️ 설치 및 준비

### 📋 필수 요구사항

-   `Python 3.x`
-   `pandas`
-   `requests`
-   `scikit-learn`
-   `tqdm`

다음 명령어를 사용하여 필요한 라이브러리를 설치할 수 있습니다:

```bash
pip install pandas requests scikit-learn tqdm
```

### 📁 데이터 준비

**`boardgames_ranks.csv` 파일 다운로드**  
BGG에서 제공하는 전체 랭킹 정보를 CSV 파일로 다운로드하여 프로젝트 루트 디렉토리에 저장해야 합니다.
- 다운로드 링크: [https://boardgamegeek.com/data_dumps/bg_ranks/](https://boardgamegeek.com/data_dumps/bg_ranks/)
- **참고**: 다운로드를 위해서는 BoardGameGeek 로그인이 필요할 수 있습니다.

## 🚀 사용법

이 프로젝트는 두 단계로 나뉘어 진행됩니다.

### 1단계: 데이터 수집 (`bgg-collecting.py`)

이 스크립트는 `boardgames_ranks.csv` 파일에서 상위 5000개 게임의 ID를 추출하고,  
BGG API를 통해 각 게임의 상세 정보(평점, 복잡도, 평가자 수 등)를 수집합니다.  
수집된 데이터는 오늘 날짜가 포함된 CSV 파일(`bgg_data_YYYY-MM-DD.csv`)로 저장됩니다.

- **실행 방법:**
    ```bash
    python bgg-collecting.py
    ```

- **출력 파일:** `bgg_data_YYYY-MM-DD.csv` (예: `bgg_data_2025-08-16.csv`)
    - 이 파일에는 `id`, `name`, `average`, `weight`, `usersrated` 등의 정보가 포함됩니다.

### 2단계: 랭킹 계산 (`bgg-rating.py`)

이 스크립트는 1단계에서 수집된 오늘 날짜의 데이터 파일(`bgg_data_YYYY-MM-DD.csv`)을 읽어와 복잡도 편향을 보정한 새로운 평점(`bayes_new_rating`)을 계산하고, 이를 기반으로 게임의 순위를 다시 매깁니다.  
최종 결과는 `boardgames_re_ranked_YYYY-MM-DD.csv` 파일로 저장됩니다.

- **실행 방법:**
    ```bash
    python bgg-rating.py
    ```
- **입력 파일:** `bgg_data_YYYY-MM-DD.csv` (1단계에서 생성된 파일)
- **출력 파일:** `boardgames_re_ranked_YYYY-MM-DD.csv`

## 📚 참고 자료

-   [https://dvatvani.com/blog/bgg-analysis-part-2](https://dvatvani.com/blog/bgg-analysis-part-2)

## 📅 최종 업데이트 (BGG 데이터 기준)

2025년 08월 15일
