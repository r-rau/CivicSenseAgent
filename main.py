import os
import time
import requests
from newsapi import NewsApiClient
from google import genai

# Config
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def send_to_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "Markdown"}
    try:
        requests.post(url, data=payload).raise_for_status()
    except Exception as e:
        print(f"Telegram Error: {e}")

def run_agent():
    newsapi = NewsApiClient(api_key=NEWS_API_KEY)
    client = genai.Client(api_key=GEMINI_API_KEY)

    # Search for Nagpur/India Civic News
    query = '(civic sense OR "public etiquette") AND (Nagpur OR India)'
    articles = newsapi.get_everything(q=query, language='en', sort_by='relevancy', page_size=2)

    if not articles.get('articles'):
        print("No news found.")
        return

    for art in articles['articles']:
        try:
            prompt = f"Summarize this civic event for a Nagpur audience: {art['title']}. Add a lesson on public etiquette."
            
            # Using Gemini 2.5 (Free Tier)
            response = client.models.generate_content(
                model="gemini-2.5-flash", 
                contents=prompt
            )
            
            send_to_telegram(f"📢 *Civic Sense Nagpur*\n\n{response.text}")
            
            # Wait 10 seconds to stay within Free Tier limits (15 RPM)
            time.sleep(10)
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    run_agent()
