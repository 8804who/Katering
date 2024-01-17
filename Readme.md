## Katering: 금융이 어렵다면? Katering 하세요!

### 🤷🏻‍♂️ Katering이 뭔가요?
- 사용자 맞춤 정보를 골라 보여주는 금융 기사 및 상품 추천 서비스입니다.

<br>

### 🤷🏻‍♀️ Katering은 무엇을 하나요?
- 개인이 선호하는 키워드에 맞춘 금융 기사를 추천해줍니다.
- 그 외에도 여러 기사들과 그 요약을 한 눈에 찾아볼 수 있습니다.
- 내가 관심있는 기사를 바탕으로 관련 상품을 추천해줍니다. 

<br>
<br>

## 프로젝트 실행
### 요구사항
```
python 3.10
```

### 세팅
```
$ pip install -r requirements.txt
$ cd backend
$ uvicorn main:app
```

※ 작동을 위해선 firebase 및 chatGPT API key가 필요합니다.

<br>
<br>

## 각 코드 폴더 기능
#### article_crawling
- 네이버 기사 크롤링 및 데이터베이스 데이터 업로드 자동화 코드 폴더

#### modeling
- 데이터 전처리, 증강 및 학습 코드 폴더

#### backend
- 프론트 및 백엔드 코드 포함 및 웹 실행 폴더
