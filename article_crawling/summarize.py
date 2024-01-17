import pandas as pd
import openai
import yaml
from tqdm import tqdm

df = pd.read_csv('./종합 데이터.csv')

with open('api.yaml') as f:
    api = yaml.load(f, Loader=yaml.FullLoader)

    openai.api_key = api['openai']
    

def summarize(news: str):
    input_text = f'[{news}] 짧은 글로도 이 기사에서 설명하는 금융 소식을 쉽게 알 수 있게 3 문장으로 요약해줘'
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": input_text}
        ],
        request_timeout=6000
    )
    
    generated_words = response.choices[0].message.content.replace('\n',' ')
    
    return generated_words


def create_summarization_data():
    contents = list(df.content)
    for news in tqdm(contents[869:]):
        while True:
            try:
                input_text = f'[{news}] 짧은 글로도 이 기사에서 설명하는 금융 소식을 쉽게 알 수 있게 3 문장으로 요약해줘'
                
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "user", "content": input_text}
                    ],
                    request_timeout=6000
                )
                generated_words = response.choices[0].message.content.replace('\n',' ')
            except Exception as e:
                print('error', e)
            else:
                t1=pd.read_csv('./summ.csv')
                t2=pd.DataFrame({'summ':[generated_words]})
                t3 = pd.concat([t1, t2])
                t3.to_csv('./summ.csv', index=False)
                break
            
