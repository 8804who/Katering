from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
import uvicorn
from fastapi import FastAPI, Depends, HTTPException, Form, Request, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import firebase_admin
from firebase_admin import credentials, db
from secret import SERVICEACCOUNTKEY, DBURL
from typing import List
from collections import Counter
from random import sample, choice
from utils import create_articles_list, create_keyword_articles_list

templates = Jinja2Templates(directory="templates")
app = FastAPI()

app.mount('/static', StaticFiles(directory='./static'), name="static")

cred = credentials.Certificate(SERVICEACCOUNTKEY)
firebase_admin.initialize_app(cred, {
    'databaseURL': DBURL
})

user_ID=''
user_topic=''
user_survey = False

ARTICLES_LOG_NUM = 5
RECOMMNED_NUM = 6

class Keyword(BaseModel):
    article_keyword: str

@app.get('/')
def first(request: Request):
    return templates.TemplateResponse('login.html', context={'request':request})

@app.post('/main')
def main(request: Request):
    # db 읽어오면 끝
    global user_ID
    best_keyword = db.reference(f'users/{user_ID}/best_keyword').get()
    articles = db.reference(f'users/{user_ID}/articles').get()  # survey만 되어 있고 로그 안 쌓여 있으면 6개, 로그 쌓이면 5개
    articles_list = create_articles_list(articles)

    if best_keyword:
        recommend_item = db.reference(f'users/{user_ID}/item').get()
        item_name = recommend_item.pop('name')
        item_url = recommend_item.pop('url')
        item_info = [[item_name] + [i + ': ' + j for i, j in recommend_item.items()] + [item_url, recommend_item['keyword'], '상품']]
        articles_list.extend(item_info) 
    return templates.TemplateResponse('main.html', context={'request': request, 'articles':articles_list, 'user_ID':user_ID, 'page':'recommend'})

@app.post('/login')
def login(ID: str = Form(...)):
    global user_ID
    global user_survey
    user_ID = ID
    if not user_survey:
        return RedirectResponse('/survey')
    else:
        return RedirectResponse('/main')

@app.post('/survey')
def survey(request: Request):
    return templates.TemplateResponse('survey.html', context={'request':request, 'user_ID':user_ID, 'page':'survey'})

@app.post('/get_survey_result')
def get_survey_result(request: Request, select_items: list = Form(...)):
    global user_ID
    global user_survey
    user_survey = True
    select_items.pop()
    survey_articles_ref = db.reference(f'users/{user_ID}')
    num_per_article = RECOMMNED_NUM // len(select_items)  # 한 기사 당 추천할 개수
    rest_article = RECOMMNED_NUM % len(select_items)   # 나머지 추천해야 할 기사 개수
    recommend_articles = []  # 사용자한테 추천할 기사들 리스트

    for survey_item in select_items:
        article_ref = db.reference(f'articles/{survey_item}')
        keyword_articles = sample(
            article_ref.get(), num_per_article)  # 무작위로 기사 추출
        recommend_articles.extend(keyword_articles)

    # 나머지 추천해야 할 기사를 무작위로 키워드 추출
    random_keywords = sample(select_items, rest_article)
    for random_keyword in random_keywords:
        article_ref = db.reference(f'articles/{random_keyword}')

        while True:
            rest_recommend_article = choice(
                article_ref.get())  # 무작위로 기사 한 개 추출
            if rest_recommend_article not in recommend_articles:  # 중복 기사가 걸리면 다시 추출
                break
        recommend_articles.append(rest_recommend_article)

    survey_articles_ref.update({'articles': recommend_articles})
    return RedirectResponse('/main')

@app.post('/deposit')
def deposit(request: Request):
    global user_topic
    user_topic='예금'
    articles = create_keyword_articles_list(db=db, keyword=user_topic)
    return templates.TemplateResponse('category.html', context={'request': request, 'articles':articles, 'user_ID':user_ID, 'page':'deposit'})

@app.post('/saving')
def saving(request: Request):
    global user_topic
    user_topic='적금'
    articles = create_keyword_articles_list(db=db, keyword=user_topic)
    return templates.TemplateResponse('category.html', context={'request': request, 'articles':articles, 'user_ID':user_ID, 'page':'saving'})

@app.post('/insurance')
def insurance(request: Request):
    global user_topic
    user_topic='보험공제'
    articles = create_keyword_articles_list(db=db, keyword=user_topic)
    return templates.TemplateResponse('category.html', context={'request': request, 'articles':articles, 'user_ID':user_ID, 'page':'insurance'})

@app.post('/trust')
def trust(request: Request):
    global user_topic
    user_topic='신탁'
    articles = create_keyword_articles_list(db=db, keyword=user_topic)
    return templates.TemplateResponse('category.html', context={'request': request, 'articles':articles, 'user_ID':user_ID, 'page':'trust'})

@app.post('/foreign_deposit')
def foreign_deposit(request: Request):
    global user_topic
    user_topic='외화예금'
    articles = create_keyword_articles_list(db=db, keyword=user_topic)
    return templates.TemplateResponse('category.html', context={'request': request, 'articles':articles, 'user_ID':user_ID, 'page':'foreign_deposit'})

@app.post('/fund')
def fund(request: Request):
    global user_topic
    user_topic='펀드'
    articles = create_keyword_articles_list(db=db, keyword=user_topic)
    return templates.TemplateResponse('category.html', context={'request': request, 'articles':articles, 'user_ID':user_ID, 'page':'fund'})

@app.post('/ISA')
def ISA(request: Request):
    global user_topic
    user_topic='ISA'
    articles = create_keyword_articles_list(db=db, keyword=user_topic)
    return templates.TemplateResponse('category.html', context={'request': request, 'articles':articles, 'user_ID':user_ID, 'page':'ISA'})

@app.post('/subscription')
def subscription(request: Request):
    global user_topic
    user_topic='주택청약'
    articles = create_keyword_articles_list(db=db, keyword=user_topic)
    return templates.TemplateResponse('category.html', context={'request': request, 'articles':articles, 'user_ID':user_ID, 'page':'subscription'})

@app.post('/gold')
def gold(request: Request):
    global user_topic
    user_topic='골드'
    articles = create_keyword_articles_list(db=db, keyword=user_topic)
    return templates.TemplateResponse('category.html', context={'request': request, 'articles':articles, 'user_ID':user_ID, 'page':'gold'})

@app.post('/loan')
def loan(request: Request):
    global user_topic
    user_topic='대출'
    articles = create_keyword_articles_list(db=db, keyword=user_topic)
    return templates.TemplateResponse('category.html', context={'request': request, 'articles':articles, 'user_ID':user_ID, 'page':'loan'})

@app.post('/click_article')
def click_article(request: Request):
    global user_ID
    global user_topic
    def update_best_keyword_item(items: List):
        counter = Counter(items)
        keyword_counts = list(counter.values())  # 키워드 등장 횟수
        max_count = max(keyword_counts)  # 가장 많이 등장한 키워드의 등장 횟수

        best_keywords = [key for key, value in counter.items() if value == max_count]  # best keywords에 최빈 키워드(들) 저장
        best_keyword = choice(best_keywords)  # 최빈 키워드가 여러 개면 한 개 무작위로 추출
        user_ref.update({"best_keyword": best_keyword})  # 최적 키워드 update
        
        items_ref = db.reference(f'items/{best_keyword}')  # items에서 상품 추출
        best_item = items_ref.get()[0]
        user_ref.update({'item': best_item})  # 최적 상품 추천

    def avoid_duplicate_article(current_articles: List, keyword: str = user_topic):  # 중복 기사 방지
        while True:
            new_article = choice(db.reference(f'articles/{keyword}').get())  # 새로운 키워드에 대한 새로운 기사 추천
            if new_article not in current_articles:  # 현재 추천 기사들에 포함이 안 되어 있을 때 return
                return new_article
            
    def create_articles(new_keywords: List):  # 로그에 남은 키워드에 맞게 추천 기사 생성
        new_articles = []
        
        for i in range(len(new_keywords)):
            new_keyword = new_keywords[i]
            if i == 0:  # 맨 첫 키워드면 일단 new_articles에 append
                initial_article = choice(db.reference(f'articles/{new_keyword}').get())
                new_articles.append(initial_article)
                
            else:  # 두 번째 기사부턴 중복을 방지하며 append
                new_article = avoid_duplicate_article(new_articles, new_keyword)
                new_articles.append(new_article)
    
    def update_articles(current_articles: List, new_keyword: str):  # 새로 포함된 키워드에 맞게 기사 update
        remain_articles = current_articles[1:]  # 가장 먼저 들어온 기사 삭제
        new_article = avoid_duplicate_article(remain_articles, new_keyword)
        new_articles = remain_articles + [new_article]
        user_ref.update({'articles': new_articles})  # 새로운 기사들로 update
        

    user_ref = db.reference(f'users/{user_ID}')
    user_log_ref = db.reference(f'users/{user_ID}/article_log')
    user_articles_ref = db.reference(f'users/{user_ID}/articles')
    current_keywords = user_log_ref.get()  # 사용자가 현재까지 읽은 기사 키워드 리스트
    current_recommend_articles = user_articles_ref.get()  # 사용자에게 현재 추천되는 기사들, 로그가 5개 쌓였을 때 사용

    if not current_keywords or len(current_keywords) < ARTICLES_LOG_NUM - 1:  # 기준치-1 미만이면 item log에 마지막 번호로 keyword 추가
        if not current_keywords:
            user_log_ref.update({0: user_topic})
        else:
            user_log_ref.update({len(current_keywords): user_topic})

    elif len(current_keywords) == ARTICLES_LOG_NUM - 1:  # 로그가 (기준치-1)만큼 쌓였으면 마지막에 keyword 추가하고, 가장 많이 나온 키워드 추출
        user_log_ref.update({len(current_keywords): user_topic})
        updated_keywords = db.reference(f'users/{user_ID}/article_log').get()
        update_best_keyword_item(updated_keywords)
        create_articles(updated_keywords)

    else:  # 로그가 기준치만큼 쌓여있는데 새로운 keyword가 들어온다면, 선입선출로 keyword 변경
        current_keywords = current_keywords[1:] + [user_topic]  # 가장 먼저 들어온 keyword 없애고 새로운 keyword 추가
        new_keywords = dict((i, j) for i, j in enumerate(current_keywords))  # 0~4 인덱싱 update
        user_log_ref.update(new_keywords)
        update_best_keyword_item(current_keywords)
        update_articles(current_recommend_articles, user_topic)