import time
import random
import sqlite3
import requests
import telebot

BOT_TOKEN = '7632190595:AAGVhetz8f2PJniACVnMhZPrfRNHw_jdDT0'
ADMIN_USER_ID = '6604452400'
CHANNEL_ID = '@Eon_Scrap'

API_KEY = 'AIzaSyDCXLl4Ef_lBqRXwG9YcDBVnjoWl_L5ZdY'
CX = '12e429663ae7a4ccb'

PROXIES = [
    {"http": "http://3.212.148.199:3128"},
    {"http": "http://3.126.147.182:80"}
]

GATEWAYS = {
    'stripe': 'Stripe',
    'braintree': 'Braintree',
    'shopify': 'Shopify',
    'paypal': 'PayPal',
    'skrill': 'Skrill',
    'payoneer': 'Payoneer',
    'nab': 'NAB',
    'omise': 'Omise',
    'epay': 'ePay',
    'mastercard': 'Mastercard',
    'visa': 'Visa',
    'discover': 'Discover',
    'american express': 'American Express',
    'adyen': 'Adyen',
    'square': 'Square',
    'authorize.net': 'Authorize.Net',
    '2checkout': '2Checkout',
    'worldpay': 'Worldpay',
    'alipay': 'Alipay',
    'wechat pay': 'WeChat Pay',
    'unionpay': 'UnionPay',
    'apple pay': 'Apple Pay',
    'google pay': 'Google Pay',
    'amazon pay': 'Amazon Pay'
}

# Initialize bot
bot = telebot.TeleBot(BOT_TOKEN)

def init_db():
    conn = sqlite3.connect('visited_sites.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS visited_sites (url TEXT PRIMARY KEY)''')
    c.execute('''CREATE TABLE IF NOT EXISTS blocklist (url TEXT PRIMARY KEY)''')
    conn.commit()
    return conn, c

def check_visited(conn, c, url):
    c.execute("SELECT * FROM visited_sites WHERE url=?", (url,))
    return c.fetchone() is not None

def mark_visited(conn, c, url):
    c.execute("INSERT INTO visited_sites (url) VALUES (?)", (url,))
    conn.commit()

def check_blocklist(conn, c, url):
    c.execute("SELECT * FROM blocklist WHERE url=?", (url,))
    return c.fetchone() is not None

def block_site(conn, c, url):
    c.execute("INSERT INTO blocklist (url) VALUES (?)", (url,))
    conn.commit()

def send_site_to_channel(bot, channel_id, site_data):
    message = f"""
    𝙽𝚎𝚠 𝚂𝚒𝚝𝚎 𝚂𝚌𝚛𝚊𝚙𝚎𝚍 ☑
    ━━━━━━━━━━━━━━
    ➔ Website ⋙ {site_data["url"]}
    ➔ Gateways ⋙ {site_data["gateway"]}
    ➔ Captcha ⋙ {site_data["captcha"]}
    ➔ Cloudflare ⋙ {site_data["cloudflare"]}
    ➔ Status code ⋙ {site_data["status_code"]}
    ➔ Platform ⋙ {site_data["platform"]}

    𝚂𝚒𝚝𝚎 𝙷𝚞𝚗𝚝𝚎𝚛 𝙱𝚢 - @itsyo3
    """
    bot.send_message(channel_id, message)

def google_search(query):
    url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={API_KEY}&cx={CX}"
    response = requests.get(url)
    if response.status_code == 200:
        results = response.json()
        search_results = []
        for item in results.get('items', []):
            search_results.append(item['link'])
        return search_results
    else:
        return []

def check_payment_gateway(url):
    response = requests.get(url, proxies=random.choice(PROXIES))
    for keyword, gateway_name in GATEWAYS.items():
        if keyword in response.text.lower():
            return gateway_name
    return None

def detect_captcha(response):
    captcha_keywords = ['recaptcha', 'captcha', 'g-recaptcha']
    return any(keyword in response.text.lower() for keyword in captcha_keywords)

def detect_cloudflare(response):
    return 'cf-ray' in response.headers or 'cf-cache-status' in response.headers

def scrape_site(url):
    try:
        response = requests.get(url, proxies=random.choice(PROXIES))
    except requests.RequestException as e:
        return None

    captcha_status = "True" if detect_captcha(response) else "False🪿"
    cloudflare_status = "True" if detect_cloudflare(response) else "False🪿"
    status_code = response.status_code
    platform = "woocommerce" if "woocommerce" in response.text.lower() else "Unknown"
    gateway = check_payment_gateway(url)
    return {
        "url": url,
        "captcha": captcha_status,
        "cloudflare": cloudflare_status,
        "status_code": status_code,
        "platform": platform,
        "gateway": gateway if gateway else "None"
    }

# Self-generating random keywords function
def generate_dynamic_keywords():
    base_keywords = [
        'inurl:/checkout intext:"pay now"',
        'inurl:/donate-now intext:"donation"',
        'inurl:/purchase intext:"cart"',
        'inurl:/order-now intext:"checkout"',
        'inurl:/pay intext:"payment page"',
        'inurl:/cart intext:"buy now"',
        'inurl:/payment intext:"stripe"',
        'inurl:/donate intext:"paypal"',
        'inurl:/product-page intext:"shop now"',
        'inurl:/checkout-form intext:"credit card"',
        'inurl:/shopping-cart intext:"order online"',
        'inurl:/payment-page intext:"secure checkout"',
        'inurl:/buy-now intext:"secure payment"',
        'inurl:/subscribe intext:"paypal payment"',
        'inurl:/fundraiser intext:"stripe donate"'
    ]
    random.shuffle(base_keywords)
    return base_keywords

def auto_process(bot):
    conn, c = init_db()

    while True:
        uploaded_keywords = generate_dynamic_keywords()  # Generate random keywords

        for keyword in uploaded_keywords:
            search_results = google_search(keyword)

            if not search_results:
                continue

            for url in search_results:
                if check_visited(conn, c, url) or check_blocklist(conn, c, url):
                    continue

                site_data = scrape_site(url)

                if site_data:
                    if site_data["gateway"] != "None" and site_data["status_code"] == 200:
                        send_site_to_channel(bot, CHANNEL_ID, site_data)
                        mark_visited(conn, c, url)

                time.sleep(2)

        # Sleep for a random time interval between keyword generation
        time.sleep(random.randint(3600, 7200))  # Sleep for 1 to 2 hours

# Update the bot handler to process the auto command
@bot.message_handler(commands=['auto'])
def handle_auto(message):
    user_id = message.from_user.id
    if user_id != int(ADMIN_USER_ID):
        bot.send_message(message.chat.id, "You are not authorized to use this command.")
        return

    bot.send_message(message.chat.id, "Bot will now start generating and processing random keywords automatically.")

    # Start auto process without sending completion message
    auto_process(bot)

@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.from_user.id
    if user_id != int(ADMIN_USER_ID):
        bot.send_message(message.chat.id, "You are not authorized to use this bot.")
        return

    bot.send_message(message.chat.id, "Bot is ready. Use /auto to start automatic scraping.")

# Handle Blocklist command
@bot.message_handler(commands=['bl'])
def handle_blocklist(message):
    user_id = message.from_user.id
    if user_id != int(ADMIN_USER_ID):
        bot.send_message(message.chat.id, "You are not authorized to use this command.")
        return

    # Extract URL from message
    blocked_url = message.text.strip().split(' ', 1)
    if len(blocked_url) < 2:
        bot.send_message(message.chat.id, "Please provide a valid URL to block.")
        return

    url = blocked_url[1]
    conn, c = init_db()

    if check_blocklist(conn, c, url):
        bot.send_message(message.chat.id, "This site is already blocklisted.")
    else:
        block_site(conn, c, url)
        bot.send_message(message.chat.id, f"The site {url} has been blocklisted.")

# Continuous bot polling
def main():
    bot.polling()

if __name__ == '__main__':
    main()
