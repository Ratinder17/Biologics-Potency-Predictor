# persistence/mongo.py
from config import db
investigations = db["investigations"]
temperature_readings = db["temperature_readings"]
calculations = db["calculations"]
reports = db["reports"]
