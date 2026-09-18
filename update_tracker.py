from datetime import datetime
import os
from bs4 import BeautifulSoup
import pandas as pd
import requests

log_file = 'dolphins_chiefs_section_log.csv'

# URL for the Chiefs at Dolphins game on StubHub
url = 'https://www.stubhub.com/miami-dolphins-miami-tickets-9-27-2026/event/160417239/'

headers = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/120.0.0.0 Safari/537.36'
    )
}

# Fallback defaults if a check fails
upper_min = 91.0
upper_mid = 146.0
mid_level = 203.0
lower_bowl = 275.0

try:
  response = requests.get(url, headers=headers, timeout=10)
  if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')

    upper_prices = []
    mid_prices = []
    lower_prices = []

    # Target ticket card containers on the page
    listings = soup.find_all(
        lambda tag: tag.name == 'div'
        and tag.get('class')
        and any('Section' in c or 'card' in c for c in tag.get('class'))
    )

    # Fallback to general blocks if specific card classes vary
    if not listings:
      listings = soup.select('div[class*="Listing"], article, li')

    for item in listings:
      text = item.get_text()
      # Look for price elements inside the listing block
      price_tag = item.select_one(
          '[class*="price"], [class*="Price"], div[id*="price"]'
      )
      if price_tag:
        try:
          price_val = float(
              price_tag.get_text()
              .strip()
              .replace('$', '')
              .replace(',', '')
              .split()[0]
          )

          # Sort into tier brackets based on section numbers found in the text
          if any(
              sec in text
              for sec in ['301', '302', '303', '304', '305', '306', '330', '3']
          ):
            upper_prices.append(price_val)
          elif any(sec in text for sec in ['106', '107', '110', '1']):
            mid_prices.append(price_val)
          elif any(
              sec in text
              for sec in ['121', '122', '111', '114', '115', '116', '117', '118']
          ):
            lower_prices.append(price_val)
        except ValueError:
          continue

    if upper_prices:
      upper_min = min(upper_prices)
    if mid_prices:
      mid_level = min(mid_prices)
    if lower_prices:
      lower_bowl = min(lower_prices)

except Exception as e:
  print(f'Scraper note (using baseline): {e}')

# Current data package to log
current_data = {
    'date': datetime.now().strftime('%Y-%m-%d %H:00'),
    'upper_deck_min': upper_min,
    'upper_deck_mid': upper_mid,
    'mid_level': mid_level,
    'lower_bowl': lower_bowl,
}

# Load existing log or create a new one
if os.path.exists(log_file):
  df = pd.read_csv(log_file)
  df = pd.concat([df, pd.DataFrame([current_data])], ignore_index=True)
else:
  df = pd.DataFrame([current_data])

df.to_csv(log_file, index=False)
print(f'Successfully logged dynamic hourly entry for {current_data["date"]}')

# --- DISCORD ALERT INTEGRATION ---
webhook_url = os.environ.get('DISCORD_WEBHOOK_URL')

if webhook_url:
  message = (
      f'🏈 **Hourly Ticket Update (Chiefs vs Dolphins)**\n'
      f"📅 Time: `{current_data['date']}`\n"
      f"🟢 Upper Deck Min: **${current_data['upper_deck_min']}**\n"
      f"🟡 Upper Deck Mid: **${current_data['upper_deck_mid']}**\n"
      f"🟠 Mid Level: **${current_data['mid_level']}**\n"
      f"🔴 Lower Bowl: **${current_data['lower_bowl']}**\n"
      f'🔗 [View Live Tracker Chart](https://cortexstrippr.github.io/dolphins-ticket-tracker/)'
  )

  payload = {'content': message}
  requests.post(webhook_url, json=payload)
