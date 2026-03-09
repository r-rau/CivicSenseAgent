import os
import time
import requests
from newsapi import NewsApiClient
from google import genai

# Configuration from Environment
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def send_to_telegram(text):
    """Sends a formatted message to the Telegram bot."""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
    except Exception as e:
        print(f"Telegram Error: {e}")

def run_agent():
    # Initialize Clients
    newsapi = NewsApiClient(api_key=NEWS_API_KEY)
    client = genai.Client(api_key=GEMINI_API_KEY)

    # 1. Fetch News (Filtered for high relevancy)
    query = '(civic sense OR "public etiquette") AND (India OR Mumbai OR Delhi OR Nagpur)'
    articles = newsapi.get_everything(q=query, language='en', sort_by='relevancy', page_size=2)

    if not articles.get('articles'):
        print("No relevant civic news found today.")
        return

    for art in articles['articles']:
        try:
            # 2. Optimized Prompt for Gemini 3 Flash
            prompt = (
                f"Topic: {art['title']}\n"
                f"Source Info: {art.get('description', 'N/A')}\n\n"
                "As a Civic Sense expert, create a report including:\n"
                "1. Summary: A 2-sentence punchy breakdown.\n"
                "2. The Lesson: What should citizens learn from this?\n"
                "3. Tags: #CivicSense #India + 3 relevant tags.\n"
                "4. Image Idea: A prompt for an AI image generator to visualize this."
            )
            
            # 3. Execution using Gemini 3 Flash (Free Tier)
            # gemini-3-flash is the 2026 standard for free high-speed tasks.
            response = client.models.generate_content(
                model="gemini-3-flash", 
                contents=prompt
            )
            
            # 4. Final Formatting
            report = f"🚨 *Civic Sense Update*\n\n{response.text}"
            send_to_telegram(report)
            
            # 5. Rate Limit Buffer (Free Tier: 15 RPM)
            time.sleep(10) 

        except Exception as e:
            if "429" in str(e):
                print("Quota hit. Cooling down for 60 seconds...")
                time.sleep(60)
            else:
                print(f"Skipping article due to error: {e}")

if __name__ == "__main__":
    run_agent()
