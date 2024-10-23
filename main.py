import requests
from telegram import Bot
from telegram.error import TelegramError
import asyncio
import schedule
import time
from dotenv import load_dotenv
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

load_dotenv()

# Configuration
WEBSITE_URL = os.getenv("WEBSITE_URL")
SEARCH_STRING = os.getenv("SEARCH_STRING")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")

# Global variable to store the status message ID
status_message_id = None

def get_page_content():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    try:
        driver.get(WEBSITE_URL)
        time.sleep(5)  # Wait for JavaScript to load
        return driver.page_source
    finally:
        driver.quit()

async def check_website_and_notify():
    global status_message_id
    try:
        # Get current timestamp
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Fetch the website content using Selenium
        page_content = get_page_content()
        
        # Check if the search string is in the content
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        if SEARCH_STRING not in page_content:
            # If the string is not found, send a new alert message to Telegram
            message = await bot.send_message(
                chat_id=TELEGRAM_CHANNEL_ID,
                text=f"🚨 Alert: The string '{SEARCH_STRING}' was not found on {WEBSITE_URL}\n\nCheck performed at: {current_time}"
            )
            status_message_id = None  # Reset the status message ID
            print(f"Alert sent to Telegram: String not found")
        else:
            # If the string is found, update or send a status message
            status_text = f"✅ Status Update: The string '{SEARCH_STRING}' was found.\n\nLast check: {current_time}"
            if status_message_id:
                try:
                    # Try to edit the existing message
                    await bot.edit_message_text(
                        chat_id=TELEGRAM_CHANNEL_ID,
                        message_id=status_message_id,
                        text=status_text
                    )
                except TelegramError:
                    # If editing fails (e.g., message is too old), send a new message
                    message = await bot.send_message(
                        chat_id=TELEGRAM_CHANNEL_ID,
                        text=status_text
                    )
                    status_message_id = message.message_id
            else:
                # If there's no existing status message, send a new one
                message = await bot.send_message(
                    chat_id=TELEGRAM_CHANNEL_ID,
                    text=status_text
                )
                status_message_id = message.message_id
            print(f"Status update sent to Telegram: String found")
    
    except Exception as e:
        print(f"An error occurred: {e}")
        # Send error message to Telegram
        await bot.send_message(
            chat_id=TELEGRAM_CHANNEL_ID,
            text=f"❌ Error: An unexpected error occurred while checking {WEBSITE_URL}\n\nError details: {str(e)}\n\nCheck attempted at: {current_time}"
        )
        status_message_id = None  # Reset the status message ID

def run_check():
    asyncio.run(check_website_and_notify())

def test_check_website():
    """
    Test function to check the website without sending Telegram messages.
    """
    try:
        # Get current timestamp
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Fetch the website content using Selenium
        page_content = get_page_content()
        
        # Check if the search string is in the content
        if SEARCH_STRING not in page_content:
            print(f"🚨 Alert: The string '{SEARCH_STRING}' was not found.")
        else:
            print(f"✅ Status Update: The string '{SEARCH_STRING}' was found.")
        
        print(f"Check performed at: {current_time}")
    
    except Exception as e:
        print(f"❌ Error: An unexpected error occurred while checking {WEBSITE_URL}")
        print(f"Error details: {str(e)}")

# Schedule the check to run every 5 minutes
schedule.every(5).minutes.do(run_check)

# Run the scheduled tasks
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_check_website()
    else:
        print("Website monitoring script started")
        run_check()  # Run the first check immediately
        while True:
            schedule.run_pending()
            time.sleep(1)
