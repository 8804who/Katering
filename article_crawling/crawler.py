from bs4 import BeautifulSoup
import pandas as pd
import requests
import time
from typing import List
import warnings
import re
warnings.filterwarnings('ignore')


keywords = ["금융"] 
max_article_num = 1000


def makePgNum(num):
    if num == 1:
        return num
    elif num == 0:
        return num+1
    else:
        return num+9*(num-1)

    
def makeNaverUrl(num: int, keyword: str):
    page_num = makePgNum(num)
    return f"https://search.naver.com/search.naver?where=news&ie=utf8&sm=nws_hty&query={keyword}&start={page_num}"


def waitRequest(url: str):
    isEscapeLoop = False
    while True:
        try:
            headers = { "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/98.0.4758.102" }
            req = requests.get(url, verify=False, headers=headers)
            soup = BeautifulSoup(req.text, 'html.parser')
            if isEscapeLoop:
                print('Successfully connect in page {}'.format(url))
            return soup
        
        except Exception as e:
            print('"{}" error occurred in page {}, reconnect ... '.format(e, url))
            time.sleep(3)
            isEscapeLoop = True
            

def getNewsUrl(naver_url: str):
    soup = waitRequest(naver_url)
    url_tags = soup.find_all('a', {'class': 'info'})
    newsUrls = [i.attrs['href'] for i in url_tags if 'n.news.naver.com/mnews/article' in str(i)]
    return newsUrls


def getNewsInfo(news_url: str):
    soup = waitRequest(news_url)
    title = soup.select_one("#ct > div.media_end_head.go_trans > div.media_end_head_title > h2")
    if not title:
        title = soup.select_one("#content > div.end_ct > div > h2")
    
    content = soup.select("article#dic_area")
    if not content:
        content = soup.select('#articeBody')
    
    if content:
        content = re.sub(pattern='<[^>]*>', repl='', string=str(content[0]))
        pattern = """[\n\n\n\n\n// flash 오류를 우회하기 위한 함수 추가\nfunction _flash_removeCallback() {}"""
        content = content.replace(pattern, '').replace('\n', '').replace('\t', '')
        content = ' '.join([i.strip() + '.' for i in content.split('.')])
        
    
    if title and content: return title.text.replace('\n', '').replace('\t', ''), content
    if not title and content: return '', content
    if title and not content: return title.text.replace('\n', '').replace('\t', ''), ''


def saveCSV(keyword: str, data: List):
    df = pd.DataFrame(data)
    df.to_csv(f'./data_plus/{keyword}.csv', encoding = 'utf-8', index=False)


def crawling():
    for keyword in keywords:
        print(f'----------------------------------{keyword} 수집 시작----------------------------------')
        start_page = 200
        data = []
        while len(data) <= max_article_num:
            naver_url = makeNaverUrl(start_page, keyword)
            for news_url in getNewsUrl(naver_url):
                try:
                    title, content = getNewsInfo(news_url)                  
                except TypeError:
                    continue
                
                data.append({
                    'title': title,
                    'content': content,
                    'keyword': keyword,
                    'url': news_url
                })
                
                if len(data) % 100 == 0:
                    print(f'----------------------------------{keyword} 기사 {len(data)}개 수집----------------------------------')
                    
            start_page += 1
            
        saveCSV(keyword, data)
    return data
    

if __name__ == '__main__':
    crawling()
