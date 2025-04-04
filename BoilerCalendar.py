from flask import Flask, render_template
import requests
from ics import Calendar
from datetime import datetime, timedelta, timezone
import pytz

app = Flask(__name__)

def escapejs(value):
    """Custom filter to escape strings for JavaScript"""
    if not value: return ''
    return (str(value)
            .replace('\\', '\\\\')
            .replace("'", "\\'")
            .replace('"', '\\"')
            .replace('\n', '\\n')
            .replace('\r', '\\r')
            .replace('\t', '\\t'))

app.jinja_env.filters['escapejs'] = escapejs

def format_event_time(event_dt):
    """Convert UTC time to Eastern Time and format"""
    utc_dt = event_dt.astimezone(timezone.utc)
    et = pytz.timezone('US/Eastern')
    local_dt = utc_dt.astimezone(et)
    return {
        'date': local_dt.strftime('%b %d, %Y'),
        'time': local_dt.strftime('%I:%M %p').lstrip('0'),
        'weekday': local_dt.strftime('%A'),
        'iso_date': local_dt.strftime('%Y-%m-%d')
    }

@app.route('/')
def index():
    url = "https://purdue.brightspace.com/d2l/le/calendar/feed/user/feed.ics?token=aojgh5e9xenysnf045ca8"
    response = requests.get(url)
    
    if response.status_code == 200:
        calendar = Calendar(response.text)
        now = datetime.now(timezone.utc)
        events_by_date = {}

        for event in calendar.events:
            if event.begin:
                event_time_utc = event.begin.datetime.astimezone(timezone.utc)
                if now <= event_time_utc <= now + timedelta(days=14):
                    formatted = format_event_time(event_time_utc)
                    key = formatted['iso_date']
                    
                    if key not in events_by_date:
                        events_by_date[key] = []
                    
                    events_by_date[key].append({
                        'title': event.name or "No Title",
                        'time': formatted['time'],
                        'date': formatted['date'],
                        'weekday': formatted['weekday'],
                        'description': event.description or "No Description"
                    })

        return render_template(
            'calendar.html',
            events=events_by_date,
            now=now,
            timedelta=timedelta
        )
    return "Error fetching calendar"

if __name__ == '__main__':
    app.run(debug=True)