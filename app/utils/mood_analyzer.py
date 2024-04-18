from random import randint
from math import fabs

from nltk.sentiment.vader import SentimentIntensityAnalyzer
from deep_translator import GoogleTranslator

from app.models import Sentiment


def analyze_sentiment(text):
    translated_text = GoogleTranslator(source='auto', target='en').translate(text)
    sid = SentimentIntensityAnalyzer()
    return sid.polarity_scores(translated_text)['compound']


def get_sentiment(text: str, session):
    mood_value = fabs(analyze_sentiment(text))

    category = randint(0, 4)
    
    sentiment = Sentiment(
        category=category,
        value=mood_value,
        advice="Это небольшой совет по заметке. Он будет персональным для каждой записи."
    )
    
    session.add(sentiment)
    session.commit()
    session.refresh(sentiment)
    
    return sentiment
