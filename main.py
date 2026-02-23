import os
import requests
from newsapi import NewsApiClient
from google import genai  # THE NEW STYLE IMPORT

# Load Secrets
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def run_agent():
    # 1. NEW STYLE SETUP: Create the Client
    # It automatically looks for 'GEMINI_API_KEY' in your environment!
    client = genai.Client(api_key=GEMINI_API_KEY)
    newsapi = NewsApiClient(api_key=NEWS_API_KEY)

    # 2. Get News
    query = '(civic sense OR "public etiquette") AND (failure OR learning)'
    articles = newsapi.get_everything(q=query, language='en', sort_by='relevancy', page_size=1)

    if articles.get('articles'):
        art = articles['articles'][0]
        prompt = f"Analyze this civic event: {art['title']}. Provide: 1. Summary 2. SEO Tags. 3. Image Prompt."
        
        # 3. NEW STYLE GENERATION
        # Use 'client.models.generate_content'
        response = client.models.generate_content(
            model="gemini-2.0-flash", 
            contents=prompt
        )
        
        # 4. Output
        report = f"*Daily Civic Report*\n\n{response.text}"
        base_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(base_url, data={"chat_id": TELEGRAM_CHAT_ID, "text": report, "parse_mode": "Markdown"})
    else:
        print("No news found.")

if __name__ == "__main__":
    run_agent()
    
