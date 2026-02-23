import os
import requests
from newsapi import NewsApiClient
import google.genai as genai

# Load Secrets from GitHub Environment
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def send_to_telegram(text, image_url=None):
    base_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/"
    if image_url:
        requests.post(base_url + "sendPhoto", data={"chat_id": TELEGRAM_CHAT_ID, "caption": text, "photo": image_url, "parse_mode": "Markdown"})
    else:
        requests.post(base_url + "sendMessage", data={"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "Markdown"})

def run_agent():
    newsapi = NewsApiClient(api_key=NEWS_API_KEY)
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')

    # 1. Search for Civic News
    query = '(civic sense OR "public etiquette") AND (failure OR learning)'
    articles = newsapi.get_everything(q=query, language='en', sort_by='relevancy', page_size=1)

    if articles['articles']:
        art = articles['articles'][0]
        
        # 2. Logic & Summarization
        prompt = f"Analyze this civic event: {art['title']}. Provide: 1. Summary of Failure vs Learning 2. SEO Tags. 3. A DALL-E style image prompt."
        response = model.generate_content(prompt)
        
        # 3. Output
        report = f"*Daily Civic Report*\n\n{response.text}"
        send_to_telegram(report) # Add image logic if you have an OpenAI/Imagen key!

if __name__ == "__main__":
    run_agent()
