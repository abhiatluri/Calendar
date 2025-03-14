from flask import Flask, render_template
import requests
from ics import Calendar
from datetime import datetime, timedelta, timezone

app = Flask(__name__)

@app.route('/')
def index():
    # Fetch and parse ICS feed
    url = "https://purdue.brightspace.com/d2l/le/calendar/feed/user/feed.ics?token=aojgh5e9xenysnf045ca8"
    response = requests.get(url)
    if response.status_code == 200:
        calendar = Calendar(response.text)
        upcoming_events = []
        now = datetime.now(timezone.utc)
        for event in calendar.events:
            if event.begin and event.begin - now <= timedelta(days=7):
                upcoming_events.append({
                    'event': event.name if event.name else "No Title",
                    'start_time': event.begin.strftime('%Y-%m-%d %H:%M:%S'),
                    'description': event.description if event.description else "No Description"
                })
        return render_template('index.html', events=upcoming_events)
    else:
        return "Error fetching calendar."

if __name__ == '__main__':
    app.run(debug=True)