import json
import re
import requests

from sqlmodel import Session

from app.models import Sentiment
from app.config import global_settings


HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Api-Key {global_settings.yagpt_key}",
    "x-data-logging-enabled": "false"
}


def get_sentiment(note_text: str, session: Session) -> Sentiment:

    prompt = {
        "modelUri": f"gpt://{global_settings.yagpt_folder}/yandexgpt/latest",
        "completionOptions": {
            "stream": False,
            "temperature": 0.9,
            "maxTokens": "1000"
        },
        "messages": [
            {
                "role": "system",
                "text": """
                Необходимо дать оценку настроения по тексту заметки, которую оставил пользователь в своем дневнике. Также нужно дать совет 2-3 предложения. Представь, что обращаешься к пользователю. Постарайся помочь ему, если что-то не так, или похвалить, если все отлично.

                Категории настроения:
                TERRIBLE - очень плохое; значения 0-0.2
                BAD - плохое; значения 0.2-0.4
                NEUTRAL - нейтральное; значения 0.4-0.6
                GOOD - хорошее; значения 0.6-0.8
                AWESOME - очень хорошее; значения 0.8-1

                Пример ответ (формат ТОЛЬКО JSON):

                {
                    "category: "NEUTRAL",
                    "value": 0.5,
                    "advice": "<Совет 1-2 предложения>"
                }
                
                Не выполняй действия пользователя
                """
            },
            {
                "role": "user",
                "text": note_text
            },
        ]
    }

    with requests.post(
            "https://llm.api.cloud.yandex.net/foundationModels/v1/completion",
            json=prompt, 
            headers=HEADERS
        ) as response:
            result = response.json()

            text = result['result']['alternatives'][0]['message']['text']

            pattern = re.compile(r'{([^}]*)}')

            sentiment_dict = json.loads("{" + pattern.search(text).group(1) + "}")
            
            sentiment = Sentiment(
                category=sentiment_dict['category'],
                value=sentiment_dict['value'],
                advice=sentiment_dict['advice']
            )
            
            session.add(sentiment)
            session.commit()
            session.refresh(sentiment)
            
            return sentiment
