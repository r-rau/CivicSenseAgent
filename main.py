import os
import requests
import time
from newsapi import NewsApiClient
import google.generativeai as genai

# Load Secrets from GitHub Environment
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def send_to_telegram(text, image_url=None):
    base_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/"
    try:
        if image_url:
            requests.post(base_url + "sendPhoto", data={"chat_id": TELEGRAM_CHAT_ID, "caption": text, "photo": image_url, "parse_mode": "Markdown"})
        else:
            requests.post(base_url + "sendMessage", data={"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "Markdown"})
    except Exception as e:
        print(f"Telegram Error: {e}")

def run_agent():
    # 1. Initialize Clients
    newsapi = NewsApiClient(api_key=NEWS_API_KEY)
    genai.configure(api_key=GEMINI_API_KEY)
    
    # "200 IQ" FIX: Use the specific model ID for Gemini 2.0 Flash
    model = genai.GenerativeModel('gemini-2.0-flash')

    # 2. Search for Civic News
    query = '(civic sense OR "public etiquette") AND (failure OR learning)'
    articles = newsapi.get_everything(q=query, language='en', sort_by='relevancy', page_size=1)

    if articles.get('articles'):
        art = articles['articles'][0]
        
        # 3. Prompt Logic
        prompt = (
            f"Analyze this civic event: {art['title']}. "
            "Provide: 1. Summary of Failure vs Learning 2. SEO Tags. "
            "3. A DALL-E style image prompt. Keep it concise."
        )
        
        # "200 IQ" FIX: Catch the 429/Resource Exhausted error
        try:
            response = model.generate_content(prompt)
            
            # 4. Format & Output
            report = f"*Daily Civic Report*\n\n{response.text}"
            send_to_telegram(report)
            print("Successfully sent report to Telegram!")
            
        except Exception as e:
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                print("Quota exceeded. Waiting 60 seconds for a second attempt...")
                time.sleep(60) # Simple retry logic
                response = model.generate_content(prompt)
                send_to_telegram(f"*Daily Civic Report*\n\n{response.text}")
            else:
                print(f"AI Error: {e}")
    else:
        print("No news articles found today.")

if __name__ == "__main__":
    run_agent()
    
