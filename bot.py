import os
import time
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, 
    CommandHandler, 
    MessageHandler, 
    ContextTypes, 
    filters
)

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


# --------------------------
#  Create Selenium Driver
# --------------------------
def get_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--remote-debugging-port=9222")

    # Heroku Chrome binary
    chrome_options.binary_location = "/app/.apt/usr/bin/google-chrome"

    driver = webdriver.Chrome(
        executable_path="/app/.chromedriver/bin/chromedriver",
        options=chrome_options
    )
    return driver


driver = get_driver()
user_state = {}


# --------------------------
#    /start Command
# --------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome! Send your email to continue.")
    user_state[update.effective_chat.id] = "ASK_EMAIL"


# --------------------------
#    Handle Messages
# --------------------------
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    text = update.message.text

    if user_state.get(chat_id) == "ASK_EMAIL":
        context.user_data["email"] = text
        user_state[chat_id] = "ASK_OTP"
        await update.message.reply_text("Email received. Now enter your OTP.")

    elif user_state.get(chat_id) == "ASK_OTP":
        email = context.user_data["email"]
        otp = text

        await update.message.reply_text("Logging in, please wait...")

        try:
            udemy_login(email, otp)
            await update.message.reply_text("Login Success!")
        except Exception as e:
            await update.message.reply_text(f"Error: {str(e)}")


# --------------------------
#    Selenium Udemy Login
# --------------------------
def udemy_login(email, otp):
    driver.get("https://www.udemy.com/join/login-popup/")
    time.sleep(3)

    driver.find_element(By.XPATH, "//input[@placeholder='Email']").send_keys(email)
    driver.find_element(By.XPATH, "//button[contains(., 'Continue')]").click()
    time.sleep(2)

    driver.find_element(By.XPATH, "//input[@placeholder='6-digit code']").send_keys(otp)
    driver.find_element(By.XPATH, "//button[contains(., 'Log in')]").click()
    time.sleep(3)


# --------------------------
#    BOT START
# --------------------------
async def main():
    BOT_TOKEN = os.getenv("BOT_TOKEN")

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    await app.run_polling()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
