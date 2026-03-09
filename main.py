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

    # 1. Pan-India Civic Query
    # Captures major metros to ensure we get city-level civic news from across the country
    query = (
        '("civic sense" OR "traffic rule" OR "waste management" OR "civic issue" '
        'OR "garbage dump" OR "pothole" OR "illegal parking" OR "public nuisance" OR "public etiquette") '
        'AND (India OR Delhi OR Bengaluru OR Mumbai OR Chennai OR Kolkata OR Hyderabad OR Pune) '
        '-election -politics -murder -rape -bollywood -cricket -stock -share -market -movie'
    )

    # 2. National Indian News Domains
    indian_news_domains = 'timesofindia.indiatimes.com,indianexpress.com,hindustantimes.com,ndtv.com,thehindu.com,news18.com'

    # 3. Fetch up to 10 articles
    articles = newsapi.get_everything(
        q=query, 
        domains=indian_news_domains,
        language='en', 
        sort_by='relevancy', 
        page_size=10
    )

    if not articles.get('articles'):
        print("No news found.")
        return

    for art in articles['articles']:
        try:
            # 4. The 300 IQ Bouncer Prompt
            prompt = f"""
            Act as the strict copywriter for the 'civiciq_' page.
            Analyze this news event:
            Title: {art['title']}
            Description: {art.get('description', 'N/A')}
            Date Published: {art.get('publishedAt', 'Today')}

            CRITICAL INSTRUCTION: If this article is NOT about public etiquette, traffic violations, civic infrastructure, or citizen behavior, reply with ONLY the exact word: SKIP
            Do not explain why. Just output SKIP.

            If it IS a valid civic issue, output ONLY the final post using EXACTLY this structure and emojis:

            [Write a 4-7 word catchy title]
            📅 Date: [Format Date Published as MMM DD, YYYY]
            📰 The News: [Write a 3-4 sentence factual summary of the incident]
            ❌ Civic Failure: [Write 1-2 sentences explaining the exact failure in public etiquette, safety, or civic duty]
            ✅ The Civic Standard: [Write 1-2 sentences explaining the ideal citizen behavior or responsibility]

            #[City/State]News #CivicSense #India #CivicDuty #PublicEtiquette
            """
            
            response = client.models.generate_content(
                model="gemini-2.5-flash", 
                contents=prompt
            )
            
            output = response.text.strip()
            
            # 5. The Bouncer Logic
            if output == "SKIP":
                print(f"Skipped irrelevant article: {art['title']}")
                continue # Instantly moves to the next article without sending to Telegram

            # Send valid reports to Telegram
            send_to_telegram(output)
            
            # Rate limit buffer
            time.sleep(15)
            
        except Exception as e:
            print(f"Error processing article: {e}")

if __name__ == "__main__":
    run_agent()
