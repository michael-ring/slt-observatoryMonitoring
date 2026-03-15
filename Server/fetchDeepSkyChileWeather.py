#!/usr/bin/env python3
import requests
import sqlite3
import json
from datetime import datetime, timezone
from pathlib import Path
import sys

# Add paths for Common
script_dir = Path(__file__).parent
sys.path.append(str(script_dir.parent))
sys.path.append(str(script_dir.parent / 'Common'))

from Common.config import logger

def fetch_weather_data():
    url = "http://api.deepskychile.com/weather"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.RequestException as e:
        logger.error(f"Failed to fetch weather data: {e}")
        return None

def store_weather_data(data):
    db_path = script_dir.parent / 'weather-deepskychile.sqlite'
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Create tables if they don't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cloudwatcher (
            timestamp TEXT,
            clouds REAL,
            temp REAL,
            wind REAL,
            gust REAL,
            rain REAL,
            light REAL,
            switch INTEGER,
            safe INTEGER,
            hum REAL,
            dewp REAL,
            cloudsState TEXT,
            rainState TEXT,
            lightState TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ninox (
            timestamp TEXT,
            UTC TEXT,
            NSBNow REAL,
            SunAltitude REAL,
            MoonAltitude REAL,
            MoonPhase REAL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS seeing (
            timestamp TEXT,
            UTC TEXT,
            SeeingValue REAL,
            status TEXT
        )
    ''')
    
    # Get timestamp
    timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
    
    weather = data.get('weather', {})
    
    # Insert cloudwatcher
    cw = weather.get('cloudwatcher', {})
    cursor.execute('''
        INSERT INTO cloudwatcher (
            timestamp, clouds, temp, wind, gust, rain, light, switch, safe, hum, dewp,
            cloudsState, rainState, lightState
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        timestamp,
        cw.get('clouds'),
        cw.get('temp'),
        cw.get('wind'),
        cw.get('gust'),
        cw.get('rain'),
        cw.get('light'),
        cw.get('switch'),
        cw.get('safe'),
        cw.get('hum'),
        cw.get('dewp'),
        cw.get('cloudsState'),
        cw.get('rainState'),
        cw.get('lightState')
    ))
    
    # Insert ninox
    nx = weather.get('ninox', {})
    cursor.execute('''
        INSERT INTO ninox (
            timestamp, UTC, NSBNow, SunAltitude, MoonAltitude, MoonPhase
            
        ) VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        timestamp,
        nx.get('UTC'),
        nx.get('NSBNow'),
        nx.get('SunAltitude'),
        nx.get('MoonAltitude'),
        nx.get('MoonPhase')
    ))
    
    # Insert seeing
    se = weather.get('seeing', {})
    cursor.execute('''
        INSERT INTO seeing (
            timestamp, UTC, SeeingValue, status
        ) VALUES (?, ?, ?, ?)
    ''', (
        timestamp,
        se.get('UTC'),
        se.get('SeeingValue'),
        se.get('status')
    ))
    
    conn.commit()
    conn.close()
    logger.info("Weather data stored successfully")

if __name__ == "__main__":
    data = fetch_weather_data()
    if data:
        store_weather_data(data)
    else:
        sys.exit(1)
