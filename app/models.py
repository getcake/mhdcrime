#!/usr/bin/env python3.9

from datetime import timezone
from app.database import db


class Report(db.Model):  # NOTE was db.Model
    """
    Report Model

    Generate Report from scraper data

    """

    __tablename__ = "report"
    __searchable__ = [
        "date",
        "reason",
        "action_taken",
        "location",
        "primary_id",
        "vehicle",
        "criminal_name",
        "criminal_age",
        "criminal_address",
        "criminal_charges",
        "call",
        "units",
    ]

    id = db.Column(db.Integer, primary_key=True)
    call_number = db.Column(db.String(20), unique=True, nullable=False)
    call = db.Column(db.String)
    time = db.Column(db.Integer, nullable=False)
    reason = db.Column(db.String, nullable=False)
    date = db.Column(db.String)
    link = db.Column(db.String)
    units = db.Column(db.Text)
    dispatcher = db.Column(db.Text)
    action_taken = db.Column(db.String)
    location = db.Column(db.String)
    cords = db.Column(db.Float)
    lat = db.Column(db.Float)
    lon = db.Column(db.Float)
    jurisdiction = db.Column(db.String)
    primary_id = db.Column(db.String)
    vicinity_of = db.Column(db.String)
    vehicle = db.Column(db.Text)
    vehicle_towed = db.Column(db.String)
    related_incident = db.Column(db.String)
    criminal_name = db.Column(db.String)
    criminal_age = db.Column(db.String)
    criminal_address = db.Column(db.String)
    criminal_charges = db.Column(db.String)

    def __repr__(self):
        return f"""Report:\n 
        'id: {self.id}\n', 
        call number: '{self.call_number}'\n, 
        time: '{self.time}'\n, 
        reason: '{self.reason}'\n,
        date: '{self.date}'\n,
        link: '{self.link}'\n,
        call method: {self.call}\n',
        action taken: {self.action_taken}\n', 
        location {self.location}\n,
        coordinates {self.cords}\n,
        lattitude {self.lat}\n,
        longitude {self.lon}\n,
        responding officer: {self.primary_id}\n', 
        vicinity of: {self.vicinity_of}\n', 
        jurisdiction: {self.jurisdiction}\n', 
        units: {self.units}\n', 
        dispatcher: {self.dispatcher}\n,
        vehicle: {self.vehicle}\n', 
        towed: {self.vehicle_towed}\n',
        related incident: {self.related_incident}\n', 
        criminal name: {self.criminal_name}\n'),
        criminal age: {self.criminal_age}\n'),
        criminal address: {self.criminal_address}\n'),
        criminal charges: {self.criminal_charges}\n')
        
        
        """


class Marker(db.Model):  # NOTE was db.Model
    """
    Marker Model

    Data necessary to create, update, and delete markers on the live map

    """

    __tablename__ = "marker"

    id = db.Column(db.Integer, primary_key=True)
    date_time = db.Column(db.String)
    reason = db.Column(db.String)
    action_taken = db.Column(db.String)
    resp_officer = db.Column(db.String)
    comment = db.Column(db.String)
    location = db.Column(db.String)
    lat = db.Column(db.Float, nullable=False)
    lon = db.Column(db.Float, nullable=False)
    marker_color = db.Column(db.String, nullable=False)


db.create_all()
