from datetime import datetime
import os
import pandas as pd

log_file = 'dolphins_chiefs_section_log.csv'

# Current live price points from Hard Rock Stadium ticketing data
# (You can also write a live scraper here later, but this logs your tracked metrics hourly)
current_data = {
    'date': datetime.now().strftime('%Y-%m-%d %H:00'),  # Logs hour-by-hour
    'upper_deck_min': 91.0,  # Section 330
    'upper_deck_mid': 146.0,  # Section 306
    'mid_level': 203.0,  # Section 106
    'lower_bowl': 275.0,  # Section 121
}

# Load existing log or create a new one
if os.path.exists(log_file):
  df = pd.read_csv(log_file)
  # Append new hourly row
  df = pd.concat([df, pd.DataFrame([current_data])], ignore_index=True)
else:
  df = pd.DataFrame([current_data])

# Save back to CSV
df.to_csv(log_file, index=False)
print(f'Successfully logged hourly entry for {current_data["date"]}')
