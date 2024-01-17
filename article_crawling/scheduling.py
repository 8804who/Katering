from crawler import crawling
import schedule
import time
from summarize import summarize

import firebase_admin
from firebase_admin import credentials, db
from ..backend.secret import DBURL, SERVICEACCOUNTKEY

from ..modeling.inference import inference

def send_datas_to_database(summary, keyword, article_info):
    cred = credentials.Certificate(SERVICEACCOUNTKEY)
    firebase_admin.initialize_app(cred,{
        'databaseURL': DBURL
    })
    
    ref = db.reference(f'articles/{keyword}')
    num = len(ref.get())
    article_info.pop('content')
    article_info['summary'] = summary
    article_info['keyword'] = keyword
    ref.update({num: article_info})
    

def job():
    '''
    crawling: 네이버 뉴스에서 금융 기사 수집
    summarize: chatGPT를 이용해 수집 기사 요약
    inference: 요약된 기사를 albert 모델을 이용해 키워드 분류
    send_datas_to_database: 기사 요약 및 다른 정보들을 database로 이동
    article_info: 기사 원문, url, 제목 정보
    '''
    articles = crawling()
    for article_info in articles:
        summary = summarize(article_info['content'])  # 기사 요약문
        keyword = inference(summary)
        send_datas_to_database(summary, keyword, article_info)


schedule.every().day.at("09:00").do(job_func=job)
while True:
    schedule.run_pending()
    time.sleep(1)
