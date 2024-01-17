import nltk

def split_sentences(text: str) -> list:
    nltk.download('punkt')
    tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
    return tokenizer.tokenize(text)


def create_articles_list(articles) -> list :
    articles_list = []
    for article in articles:
        summary_sentences = split_sentences(article['summary'])
        uni_article = [article['title']] + summary_sentences + [article['url'], article['keyword'], '금융기사']
        articles_list.append(uni_article)
        
    return articles_list


def create_keyword_articles_list(db, keyword) -> list:
    keyword_articles = db.reference(f'articles/{keyword}').get()
    articles_list = create_articles_list(keyword_articles)
    return articles_list
    