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
    # Removed Markdown parsing to strictly match the plain-text style of your screenshot
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text}
    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
    except Exception as e:
        print(f"Telegram Error: {e}")

def run_agent():
    newsapi = NewsApiClient(api_key=NEWS_API_KEY)
    client = genai.Client(api_key=GEMINI_API_KEY)

    # Search for Indian Civic News
    query = '(civic sense OR "public etiquette" OR "civic apathy") AND (India OR Nagpur OR Maharashtra OR Mumbai)'
    
    # FETCH EXACTLY 5 ARTICLES
    articles = newsapi.get_everything(q=query, language='en', sort_by='relevancy', page_size=5)

    if not articles.get('articles'):
        print("No news found.")
        return

    for art in articles['articles']:
        try:
            # THE 300 IQ PROMPT: Locked-in formatting
            prompt = f"""
            Act as the strict copywriter for the 'civiciq_' page.
            Analyze this news event:
            Title: {art['title']}
            Description: {art.get('description', 'N/A')}
            Date Published: {art.get('publishedAt', 'Today')}

            Output ONLY the final post. Do not include any greetings, intro text, or markdown bolding (**). Use EXACTLY this structure and emojis:

            [Write a 4-7 word catchy title]
            📅 Date: [Format Date Published as MMM DD, YYYY]
            📰 The News: [Write a 3-4 sentence factual summary of the incident]
            ❌ Civic Failure: [Write 1-2 sentences explaining the exact failure in public etiquette, safety, or civic duty]
            ✅ The Civic Standard: [Write 1-2 sentences explaining the ideal citizen behavior or responsibility]

            #[City/State]News #CivicSense #India #[RelevantTag1] #[RelevantTag2]
            """
            
            # Execution
            response = client.models.generate_content(
                model="gemini-2.5-flash", 
                contents=prompt
            )
            
            # Send to Telegram
            send_to_telegram(response.text.strip())
            
            # 15 Second delay to ensure safe rate-limiting across 5 posts
            time.sleep(15)
            
        except Exception as e:
            print(f"Error processing article: {e}")

if __name__ == "__main__":
    run_agent()
