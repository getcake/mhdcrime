from importlib import reload
from operator import truediv
from re import U
from typing import Text
from flask.templating import render_template_string
from geopy.geocoders import MapQuest, GoogleV3, Nominatim, ArcGIS, OpenMapQuest

from flask import (
    render_template,
    request,
    jsonify,
    Blueprint,
    send_from_directory,
    flash,
)
from flask import request
from jinja2 import TemplateNotFound, Template

from flask_googlemaps import GoogleMaps
from flask_googlemaps import Map

from flask_paginate import Pagination, get_page_parameter

from flask_wtf import FlaskForm
from requests.models import RequestEncodingMixin
from requests.sessions import default_headers
from sqlalchemy.orm import relation
from wtforms import (
    StringField,
    BooleanField,
    widgets,
    SelectMultipleField,
    SubmitField,
    RadioField,
    SelectField,
    IntegerField,
    FormField,
    HiddenField,
)

from datetime import datetime
from time import ctime

from wtforms.fields.html5 import DateTimeField, DateField, DateTimeLocalField


# from wtforms.validators import DataRequired
from wtforms.validators import (
    DataRequired,
    InputRequired,
    ValidationError,
    Length,
    Optional,
)
from flask_msearch import Search
from markupsafe import Markup

from termcolor import cprint

import json
import random


from werkzeug.utils import redirect
from app.models import Report, Marker
from app.database import server, db  


import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go


# external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

# dash_app = dash.Dash(
#     __name__,
#     server=server,
#     url_base_pathname="/visualization/",
#     external_stylesheets=external_stylesheets,
# )


search = Search()
search.init_app(server)

GoogleMaps(server, key="ENTER_KEY")
gl = Nominatim(user_agent="mhdcrime", timeout=5)


@server.route("/", defaults={"path": "index.html"})
@server.route("/<path>")
def index(path):

    try:

        segment = get_segment(request)

        return render_template(path, segment=segment)

    except TemplateNotFound:
        return render_template("page-404.html")


def get_segment(request):

    try:

        segment = request.path.split("/")[-1]

        if segment == "":
            segment = "index"

        return segment

    except:
        return None


@server.route("/robots.txt")
def robots():
    return send_from_directory("static/assets", "robots.txt")


@server.route("/reports/search", methods=["POST", "GET"])
def search(page=1):

    searchword = request.args.get("q")  # might remove '' ?
    page = request.args.get("page", 1, type=int)
    search_reports = Report.query.msearch(
        searchword,
        fields=[
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
        ],
    ).paginate(page=page, per_page=10)

    # s = request.args.get('')

    return render_template(
        "result.html", search_reports=search_reports, searchword=searchword
    )


@server.route("/reports")
# @server.route('/reports/<int:page>',methods=['GET'])


def reports(page=1):

    page = request.args.get("page", 1, type=int)

    reports = Report.query.order_by(Report.id).paginate(page=page, per_page=10)
    # reports = Report.query(Report.id).paginate(page=page, per_page=10)

    return render_template("reports.html", reports=reports)


# class SimpleForm(FlaskForm):
#     years = RadioField('Years', choices=[('2019','year 2019'),('2020','year 2020'),('2021','year 2021'),('20','All years')])
class SimpleForm(FlaskForm):
    years = SelectField(
        "Years",
        choices=[("2021", "2021"), ("2020", "2020"), ("2019", "2019"), ("20", "All")],
        validators=[DataRequired()],
    )


@server.route("/", methods=["GET", "POST"])
def mapview():

    # form = MarkerFilterForm()
    form = SimpleForm()

    with open("app/dark_mode.json") as d, open("app/default.json") as default:
        dark_data = json.load(d)
        default_data = json.load(default)

    # cords = db_session.query(Report)
    if request.method == "POST" and form.is_submitted():

        year = str(form.data["years"])

        print(year)

        cords = Report.query.filter(Report.date.contains(year))
        mks = []
        for c in cords:

            danger_keys = [
                "transported to hospital",
                "arrest",
                # "Vehicle Towed",
                # "Citation",
                # "Could Not Locate",
                "unfounded",
            ]
            warning_keys = [
                "verbal warning",
                "founded",
                "citation",
                "vehicle towed",
            ]
            isDanger = any(i in str(c.action_taken).lower() for i in danger_keys)
            isWarning = any(i in str(c.action_taken).lower() for i in warning_keys)

            if c.lat is not None and c.lon is not None:
                c.lat += random.uniform(
                    0.0001, 0.0019
                )  # NOTE This is the best one so far
                c.lon += random.uniform(0.0001, 0.0019)  # // 25000

            if c.lat is not None and c.lon is not None and isDanger:

                details = {
                    "icon": "http://maps.google.com/mapfiles/ms/icons/red-dot.png",
                    "category": "red",
                    # "call_number": c.call_number,
                    # "reason":c.reason,
                    # "action_taken":c.action_taken,
                    "criminal_name": c.criminal_name,
                    # "criminal_charges": c.criminal_charges,
                    # "primary_id":c.primary_id,
                    "lt": c.lat,
                    "ln": c.lon,
                    "location": c.location,
                    "lat": c.lat,
                    "lng": c.lon,
                    "infobox": f"""<b>Report # :</b> <h>{str(c.id)}</h> 


                                    <br></br>

                                    <b>Date</b>: <h>{str(c.date)}</h>

                                    <br></br>

                                    <b>Time</b>: <h>{str(c.time)}</h>

                                    <br></br>
                    
                                    <b>Reason:</b> <h>{str(c.reason)}</h> 

                                    <br></br>

                                    <b>Action Taken:</b> <h>{str(c.action_taken)}</h> 

                                    <br></br> 

                                    <b>Unit(s):</b> <h>{str(c.units)}</h> 

                                    <br></br>


                                    <b>Responding Officer:</b> <h>{str(c.primary_id)}</h> 

                                    <br></br>

                                    <b>Criminal Name:</b> <h>{str(c.criminal_name)}</h> 

                                    <br></br>

                                    <b>Criminal Age:</b> <h>{str(c.criminal_age)}</h> 

                                    <br></br>

                                    <b>Criminal Charges:</b> <h>{str(c.criminal_charges)}</h> 

                                    <br></br>

                                    <b>Criminal's Address:</b> <h>{str(c.criminal_address)}</h> 

                                    <br></br>
                                """,
                }

                mks.append(details)

            elif c.lat is not None and c.lon is not None and isWarning:
                details = {
                    "icon": "http://maps.google.com/mapfiles/ms/icons/orange-dot.png",
                    "category": "orange",
                    # "call_number": c.call_number,
                    # "reason":c.reason,
                    # "action_taken":c.action_taken,
                    "criminal_name": c.criminal_name,
                    # "criminal_charges": c.criminal_charges,
                    # "primary_id":c.primary_id,
                    "lt": c.lat,
                    "ln": c.lon,
                    "location": c.location,
                    "lat": c.lat,
                    "lng": c.lon,
                    "infobox": f"""<b>Report # :</b> <h>{str(c.id)}</h> 

                                        <br></br>
                            
                                        <b>Date</b>: <h>{str(c.date)}</h>
                                        
                                        <br></br>

                                        <b>Time</b>: <h>{str(c.time)}</h>

                                        <br></br>
                        
                                        <b>Reason:</b> <h>{str(c.reason)}</h> 

                                        <br></br>

                                        <b>Action Taken:</b> <h>{str(c.action_taken)}</h> 

                                        <br></br> 

                                        <b>Unit(s):</b> <h>{str(c.units)}</h> 

                                        <br></br>


                                        <b>Responding Officer:</b> <h>{str(c.primary_id)}</h> 

                                        <br></br>


                                        <b>Criminal Name:</b> <h>{str(c.criminal_name)}</h> 

                                        <br></br>

                                        <b>Criminal Age:</b> <h>{str(c.criminal_age)}</h> 

                                        <br></br>

                                        <b>Criminal Charges:</b> <h>{str(c.criminal_charges)}</h> 

                                        <br></br>

                                        <b>Criminal's Address:</b> <h>{str(c.criminal_address)}</h> 

                                        <br></br>
                                        """,
                }

                mks.append(details)

            elif c.lat is not None and c.lon is not None:
        
                details = {
                    "icon": "http://maps.google.com/mapfiles/ms/icons/green-dot.png",
                    "category": "green",
                    # "call_number": c.call_number,
                    # "reason":c.reason,
                    # "action_taken":c.action_taken,
                    "criminal_name": c.criminal_name,
                    # "criminal_charges": c.criminal_charges,
                    # "primary_id":c.primary_id,
                    "lt": c.lat,
                    "ln": c.lon,
                    "location": c.location,
                    "lat": c.lat,
                    "lng": c.lon,
                    "infobox": f"""<b>Report # :</b> <h>{str(c.id)}</h> 

                                                <br></br>
                                    
                                                <b>Date</b>: <h>{str(c.date)}</h>

                                                <br></br>

                                                <b>Time</b>: <h>{str(c.time)}</h>

                                                <br></br>
                        
                                                <b>Reason:</b> <h>{str(c.reason)}</h> 

                                                <br></br>

                                                <b>Action Taken:</b> <h>{str(c.action_taken)}</h> 

                                                <br></br> 

                                                <b>Unit(s):</b> <h>{str(c.units)}</h> 

                                                <br></br>

                                                <b>Responding Officer:</b> <h>{str(c.primary_id)}</h> 

                                                <br></br>

                                                <b>Criminal Name:</b> <h>{str(c.criminal_name)}</h> 

                                                <br></br>

                                                <b>Criminal Age:</b> <h>{str(c.criminal_age)}</h> 

                                                <br></br>

                                                <b>Criminal Charges:</b> <h>{str(c.criminal_charges)}</h> 

                                                <br></br>

                                                <b>Criminal's Address:</b> <h>{str(c.criminal_address)}</h> 

                                                <br></br>
                                    
                                                """,
                }

                mks.append(details)

        crime_map = Map(
            identifier="crime_map",
            varname="crime_map",
            lat=42.504349000000005,
            lng=-70.8469596707424,
            markers=[(m) for m in mks],
            styles=dark_data,
            cluster=True,
            fullscreen_control=False,
            # maxZoom = 20,
            scale_control=False,
            zoom_control=False
            # disableDefaultUI = True
            # rotate_control=True
            # cluster_gridsize=2
            # collapsible=True
        )

        return render_template("index.html", crime_map=crime_map, form=form)

    else:
        cprint("ELSE", "red")
        # cords = Report.query
        cords = Report.query.filter(Report.date.contains("2021"))
        cprint(form.data, "red")

    mks = []
    for c in cords:
        danger_keys = [
            "transported to hospital",
            "arrest",
            # "Vehicle Towed",
            # "Citation",
            # "Could Not Locate",
            "unfounded",
        ]
        warning_keys = [
            "verbal warning",
            "founded",
            "citation",
            "vehicle towed",
        ]
        isDanger = any(i in str(c.action_taken).lower() for i in danger_keys)
        isWarning = any(i in str(c.action_taken).lower() for i in warning_keys)

        if c.lat is not None and c.lon is not None:
            c.lat += random.uniform(0.0001, 0.0019)  # NOTE This is the best one so far
            c.lon += random.uniform(0.0001, 0.0019)  # // 25000

            if isDanger:

                details = {
                    "icon": "http://maps.google.com/mapfiles/ms/icons/red-dot.png",
                    "category": "red",
                    # "call_number": c.call_number,
                    # "reason":c.reason,
                    # "action_taken":c.action_taken,
                    "criminal_name": c.criminal_name,
                    # "criminal_charges": c.criminal_charges,
                    # "primary_id":c.primary_id,
                    "lt": c.lat,
                    "ln": c.lon,
                    "location": c.location,
                    "lat": c.lat,
                    "lng": c.lon,
                    "infobox": f"""<b>Report # :</b> <h>{str(c.id)}</h> 


                                    <br></br>

                                    <b>Date</b>: <h>{str(c.date)}</h>

                                    <br></br>

                                    <b>Time</b>: <h>{str(c.time)}</h>

                                    <br></br>
                    
                                    <b>Reason:</b> <h>{str(c.reason)}</h> 

                                    <br></br>

                                    <b>Action Taken:</b> <h>{str(c.action_taken)}</h> 

                                    <br></br> 

                                    <b>Unit(s):</b> <h>{str(c.units)}</h> 

                                    <br></br>


                                    <b>Responding Officer:</b> <h>{str(c.primary_id)}</h> 

                                    <br></br>

                                    <b>Criminal Name:</b> <h>{str(c.criminal_name)}</h> 

                                    <br></br>

                                    <b>Criminal Age:</b> <h>{str(c.criminal_age)}</h> 

                                    <br></br>

                                    <b>Criminal Charges:</b> <h>{str(c.criminal_charges)}</h> 

                                    <br></br>

                                    <b>Criminal's Address:</b> <h>{str(c.criminal_address)}</h> 

                                    <br></br>
                                """,
                }

                mks.append(details)

            elif isWarning:
        
                details = {
                    "icon": "http://maps.google.com/mapfiles/ms/icons/orange-dot.png",
                    "category": "orange",
                    # "call_number": c.call_number,
                    # "reason":c.reason,
                    # "action_taken":c.action_taken,
                    "criminal_name": c.criminal_name,
                    # "criminal_charges": c.criminal_charges,
                    # "primary_id":c.primary_id,
                    "lt": c.lat,
                    "ln": c.lon,
                    "location": c.location,
                    "lat": c.lat,
                    "lng": c.lon,
                    "infobox": f"""<b>Report # :</b> <h>{str(c.id)}</h> 

                                        <br></br>
                            
                                        <b>Date</b>: <h>{str(c.date)}</h>
                                        
                                        <br></br>

                                        <b>Time</b>: <h>{str(c.time)}</h>

                                        <br></br>
                        
                                        <b>Reason:</b> <h>{str(c.reason)}</h> 

                                        <br></br>

                                        <b>Action Taken:</b> <h>{str(c.action_taken)}</h> 

                                        <br></br> 

                                        <b>Unit(s):</b> <h>{str(c.units)}</h> 

                                        <br></br>


                                        <b>Responding Officer:</b> <h>{str(c.primary_id)}</h> 

                                        <br></br>


                                        <b>Criminal Name:</b> <h>{str(c.criminal_name)}</h> 

                                        <br></br>

                                        <b>Criminal Age:</b> <h>{str(c.criminal_age)}</h> 

                                        <br></br>

                                        <b>Criminal Charges:</b> <h>{str(c.criminal_charges)}</h> 

                                        <br></br>

                                        <b>Criminal's Address:</b> <h>{str(c.criminal_address)}</h> 

                                        <br></br>
                                        """,
                }

                mks.append(details)

            else:
        
                details = {
                    "icon": "http://maps.google.com/mapfiles/ms/icons/green-dot.png",
                    "category": "green",
                    # "call_number": c.call_number,
                    # "reason":c.reason,
                    # "action_taken":c.action_taken,
                    "criminal_name": c.criminal_name,
                    # "criminal_charges": c.criminal_charges,
                    # "primary_id":c.primary_id,
                    "lt": c.lat,
                    "ln": c.lon,
                    "location": c.location,
                    "lat": c.lat,
                    "lng": c.lon,
                    "infobox": f"""<b>Report # :</b> <h>{str(c.id)}</h> 

                                                <br></br>
                                    
                                                <b>Date</b>: <h>{str(c.date)}</h>

                                                <br></br>

                                                <b>Time</b>: <h>{str(c.time)}</h>

                                                <br></br>
                        
                                                <b>Reason:</b> <h>{str(c.reason)}</h> 

                                                <br></br>

                                                <b>Action Taken:</b> <h>{str(c.action_taken)}</h> 

                                                <br></br> 

                                                <b>Unit(s):</b> <h>{str(c.units)}</h> 

                                                <br></br>

                                                <b>Responding Officer:</b> <h>{str(c.primary_id)}</h> 

                                                <br></br>

                                                <b>Criminal Name:</b> <h>{str(c.criminal_name)}</h> 

                                                <br></br>

                                                <b>Criminal Age:</b> <h>{str(c.criminal_age)}</h> 

                                                <br></br>

                                                <b>Criminal Charges:</b> <h>{str(c.criminal_charges)}</h> 

                                                <br></br>

                                                <b>Criminal's Address:</b> <h>{str(c.criminal_address)}</h> 

                                                <br></br>
                                    
                                                """,
                }

                mks.append(details)

    crime_map = Map(
        identifier="crime_map",
        varname="crime_map",
        lat=42.504349000000005,
        lng=-70.8469596707424,
        markers=[(m) for m in mks],
        styles=dark_data,
        cluster=True,
        fullscreen_control=False,
        scale_control=False,
        zoom_control=False,
        maptype_control=True,
    )

    return render_template("index.html", crime_map=crime_map, form=form)


def validate_location(form, field):

    if len(field.data) > 4:

        if "marblehead" in field.data.lower():

            try:
                cor = gl.geocode(field.data, country_codes="us")
                cprint(cor, "green")
                if cor is None:
                    raise ValidationError("Please Enter a Valid Town Address ")

            except Exception:
                raise ValidationError("Please Enter a Valid Town Address ")

        else:
            try:
                if "marblehead" not in field.data.lower():

                    field.data += " Marblehead, MA 01945"
                cor = gl.geocode(field.data, country_codes="us")
                cprint(cor, "green")
                if cor is None:
                    raise ValidationError("Please Enter a Valid Town Address ")

            except Exception:
                raise ValidationError("Please Enter a Valid Town Address ")

    else:
        raise ValidationError("Please Enter a Valid Town Address ")


class CreateMarkerForm(FlaskForm):
    icon_desc = Markup("Marker Color")

    # years = SelectField('Years', choices=[('2021','2021'),('2020','2020'),('2019','2019'),('20','All')], validators=[DataRequired()])
    reason = StringField(
        "Crime/Reason for call",
        render_kw={"placeholder": "Reason"},
        validators=[DataRequired()],
    )

    action_taken = StringField(
        "What action was taken?",
        render_kw={"placeholder": "Action taken (optional)"},
        validators=[Optional()],
    )

    officer = StringField(
        "Who was the responding officer?",
        render_kw={"placeholder": "Responding officer (optional)"},
        validators=[Optional()],
    )

    location = StringField(
        "Location (marblehead)",
        render_kw={"placeholder": "Location"},
        validators=[DataRequired(), validate_location],
    )

    additional_comments = StringField(
        "Add any additional comments",
        render_kw={"placeholder": "(optional)"},
        validators=[Optional()],
    )

    c_id = HiddenField()

    # date = DateField('Date/Time', format='%Y-%m-%d', validators=[DataRequired()])
    date_time = DateTimeLocalField(
        "Date/Time",
        # 2021-08-12T01:32
        # format='%Y-%m-%d %H:%M',
        format="%Y-%m-%dT%H:%M",
        default=datetime.now()
        # validators=[DataRequired()]
    )

    icon = SelectField(
        icon_desc,
        choices=[
            ("http://maps.google.com/mapfiles/ms/icons/green-dot.png", "Green"),
            ("http://maps.google.com/mapfiles/ms/icons/orange-dot.png", "Orange"),
            ("http://maps.google.com/mapfiles/ms/icons/red-dot.png", "Red"),
        ],
        validators=[DataRequired()],
    )


class CreateEditMarkerForm(FlaskForm):
    normal = Markup(
        '<btn class="badge filter bg-gradient-success" data-color="success">Normal</span> '
    )
    abnormal = Markup(
        '<btn class="badge filter bg-gradient-warning" data-color="warning">Abnormal </span>'
    )
    serious = Markup(
        '<btn class="badge filter bg-gradient-danger" data-color="danger">Serious</span>'
    )
    icon_desc = Markup("Marker Color")

    e_reason = StringField(
        "Crime/Reason for call",
        render_kw={"placeholder": "reason"},
        validators=[DataRequired()],  # Length(min=4, max=20)
    )

    e_action_taken = StringField(
        "What action was taken?",
        render_kw={"placeholder": "Action taken (optional)"},
        validators=[Optional()],
    )

    e_officer = StringField(
        "Who was the responding officer?",
        render_kw={"placeholder": "Responding officer (optional)"},
        validators=[Optional()],
    )

    e_location = StringField(
        "Location (Marblehead)",
        render_kw={"placeholder": "location"},
        validators=[DataRequired(), validate_location],
    )

    e_additional_comments = StringField(
        "Add any additional comments",
        render_kw={"placeholder": "(optional)"},
        validators=[Optional()],
    )

    e_date_time = DateTimeLocalField(
        "Date/Time",
        format="%Y-%m-%dT%H:%M",
        default=datetime.now()
        # validators=[DataRequired()]
    )

    e_id = HiddenField()

    e_icon = SelectField(
        icon_desc,
        choices=[
            ("http://maps.google.com/mapfiles/ms/icons/green-dot.png", "Green"),
            ("http://maps.google.com/mapfiles/ms/icons/orange-dot.png", "Orange"),
            ("http://maps.google.com/mapfiles/ms/icons/red-dot.png", "Red"),
        ],
        validators=[DataRequired()],
    )


class MarkerForm(FlaskForm):
    main = FormField(CreateMarkerForm)


class EditMarkerForm(FlaskForm):
    edit = FormField(CreateEditMarkerForm)


@server.route("/live", methods=["GET", "POST"])
# @cache.cached(timeout=50)
def live():

    marker = Marker()

    create_form = MarkerForm()

    edit_form = EditMarkerForm()

    temp_markers = []

    marker_data = Marker.query
    marker_cords = Marker.query

    marker_query = Marker.query

    error = None

    with open("app/dark_mode.json") as d, open("app/default.json") as default:
        dark_data = json.load(d)
        default_data = json.load(default)

    # update marker
    if request.method == "POST" and edit_form.validate_on_submit():

        # cprint(edit_form.edit.e_icon.data, 'yellow')

        reason = str(edit_form.data["edit"]["e_reason"])
        action_taken = str(edit_form.data["edit"]["e_action_taken"])
        resp_officer = str(edit_form.data["edit"]["e_officer"])
        add_comment = str(edit_form.data["edit"]["e_additional_comments"])
        date_time = str(edit_form.data["edit"]["e_date_time"])
        location = str(edit_form.data["edit"]["e_location"])
        marker_color = str(edit_form.data["edit"]["e_icon"])
        coords = gl.geocode(location, country_codes="us")
        lat = coords.latitude
        lon = coords.longitude

        date_time_obj = datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")
        date_time_obj = date_time_obj.ctime()

        # # cprint(date_time.datetime.strftime("'%Y-%m-%dT%H:%M'"), 'blue')
        # cprint(date_time.ctime(), 'blue')

        # cprint(edit_form.edit.name, 'blue')
        marker_id = edit_form.edit.e_id.data

        updated_marker = Marker.query.filter_by(id=marker_id).first()

        if action_taken:
            updated_marker.action_taken = action_taken
        if resp_officer:
            updated_marker.resp_officer = resp_officer
        if add_comment:
            updated_marker.comment = add_comment

        updated_marker.reason = reason

        updated_marker.date_time = date_time_obj
        updated_marker.location = location
        updated_marker.lat = lat
        updated_marker.lon = lon
        updated_marker.marker_color = marker_color
        db.session.add(updated_marker)
        db.session.commit()

        return redirect("/live")

    # create marker
    if (
        request.method == "POST"
        and create_form.is_submitted()
        # and request.form.main
        and not request.json
        and create_form.validate_on_submit()
        and len(create_form.data["main"]["location"]) > 0
    ):

        reason = str(create_form.data["main"]["reason"])
        action_taken = str(create_form.data["main"]["action_taken"])
        resp_officer = str(create_form.data["main"]["officer"])
        add_comment = str(create_form.data["main"]["additional_comments"])
        date_time = str(create_form.data["main"]["date_time"])
        location = str(create_form.data["main"]["location"])
        marker_color = str(create_form.data["main"]["icon"])
        cprint(f"SUBMITTED POST: {create_form.data}", "red")

        if "marblehead" in location.lower():

            # cprint(date_time, 'blue')
            # cprint(date_time.datetime.strftime("'%Y-%m-%dT%H:%M'"), 'blue')
            date_time_obj = datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")
            date_time_obj = date_time_obj.ctime()

            # try:

            coords = gl.geocode(location, country_codes="us")
            lat = coords.latitude
            lon = coords.longitude

            if action_taken:
                marker.action_taken = action_taken
            if resp_officer:
                marker.resp_officer = resp_officer
            if add_comment:
                marker.comment = add_comment

            marker.lat = lat
            marker.lon = lon
            marker.reason = reason
            marker.date_time = date_time_obj
            marker.location = location
            marker.marker_color = marker_color

            db.session.add(marker)
            db.session.commit()
            cprint(f"SUBMITTED {coords}", "red")

            return redirect("/live")

        elif len(location) > 2 and "marblehead" not in location.lower():

            cprint(date_time, "blue")

            location += " marblehead ma"

            date_time_obj = datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")
            date_time_obj = date_time_obj.ctime()

            # try:

            if action_taken:
                marker.action_taken = action_taken
            if resp_officer:
                marker.resp_officer = resp_officer
            if add_comment:
                marker.comment = add_comment

            coords = gl.geocode(location, country_codes="us")
            lat = coords.latitude
            lon = coords.longitude

            marker.lat = lat
            marker.lon = lon
            marker.reason = reason
            marker.date_time = date_time_obj
            marker.location = location
            marker.marker_color = marker_color

            db.session.add(marker)
            db.session.commit()
            cprint(f"SUBMITTED {coords}", "red")

            # cprint(location, 'green')
            return redirect("/live")

        else:
            cprint("ELSE ELSE ", "red")

    for m in marker_data:

        if m.lat is not None and m.lon is not None:

            details = {
                "icon": m.marker_color,
                "category": "green",
                # "call_number": c.call_number,
                # "reason":c.reason,
                # "action_taken":c.action_taken,
                # "criminal_name": c.criminal_name,
                # "criminal_charges": c.criminal_charges,
                # "primary_id":c.primary_id,
                "marker_id": m.id,
                "lt": m.lat,
                "ln": m.lon,
                # "location": c.location,
                "lat": m.lat,
                "lng": m.lon,
                "infobox": f"""


                                <div id="marker_div">

                                    <button  type="submit" id="delete_marker" style="background: none; display: block; border: 0px; margin: 0px; padding: 0px; text-transform: none; appearance: none; position: absolute; cursor: pointer; user-select: none; top: -5px; right: 50px; width: 30px; height: 30px;" value={m.id} marker_id={m.id}>
                                        <i class="far fa-trash-alt"></i>
                                    </button>

                                    <button class="button gm-ui-hover-effect" style="background: none; display: block; border: 0px; margin: 0px; padding: 0px; text-transform: none; appearance: none; position: absolute; cursor: pointer; user-select: none; top: -5px; right: 20px; width: 30px; height: 30px;" id="edit_marker" data-modal="modalTwo" value={m.id} marker_id={m.id}>
                                        <i class="fas fa-edit" value={m.id} marker_id={m.id}></i>
                                    </button>

                                    <br>

                                    <span id="submission_number"><b>Submission # :</span> {m.id}</b>

                                    <br></br>
                                                    
                                    <b>Reason</b>: <span id="reason_span">{m.reason}</span>

                                    <br></br>

                                    <b>Action taken</b>: <span id="action_taken">{m.action_taken}</span>

                                    <br></br>

                                    <b>Comments</b>: <span id="marker_comment">{m.comment}</span>

                                    <br></br>

                                    <b>Date/Time</b>: <h id="marker_date">{m.date_time}</h>

                                    <br></br>

                                    <b>Location:</b> <h id="marker_loc">{m.location}</h> 





                                    

                                </div>


                                                """,
            }

            temp_markers.append(details)

    # delete marker
    if (
        request.method == "POST"
        and request.json
        and not edit_form.validate_on_submit()
        and not create_form.validate_on_submit()
    ):
        data = request.args.get("data")
        data = request.json

        # cprint(data, 'blue')

        if data.get("marker_id_delete"):
            cprint(f"GOT DELETE {data} {request} ", "green")
            data = request.json
            marker_id = int(data.get("marker_id_delete"))

            cprint("SUBMITTED DELETE", "red")
            Marker.query.filter_by(id=marker_id).delete()
            db.session.commit()
            return redirect("/live")

    live_map = Map(
        identifier="live_map",
        varname="live_map",
        lat=42.504349000000005,
        lng=-70.8469596707424,
        markers=[(m) for m in temp_markers],
        styles=dark_data,
        cluster=False,
        fullscreen_control=False,
        scale_control=False,
        zoom_control=False,
        maptype_control=True,
    )

    return render_template(
        "live.html",
        live_map=live_map,
        create_form=create_form,
        edit_form=edit_form,
        marker_query=marker_query,
    )


# @server.route("/graphs")
# # @cache.cached(timeout=60)
# def graphs():

#     return render_template("graphs.html")


# pd.set_option("display.max_columns", None)
# pd.set_option("display.max_rows", None)
# MAPBOX_ACCESS_TOKEN = "pk.eyJ1Ijoiam1jZ2lubmkwNCIsImEiOiJja29yZncxZDEweWdqMndwcG9oeDRsdjAwIn0.gTgxm7umJpptmbuMIs0YVw"

# a = Report.query.filter(Report.action_taken.contains("arrest"))

# o = Report.query.filter(
#     Report.criminal_charges.contains("OUI"),
# )


# df = pd.DataFrame([(d.primary_id) for d in a], columns=["officer"])
# df["Frequency"] = df.groupby("officer")["officer"].transform("count")
# df.sort_values("Frequency", inplace=True, ascending=False, ignore_index=True)
# df.drop_duplicates(inplace=True)
# df2 = pd.DataFrame(
#     [
#         (
#             d.criminal_name,
#             d.date,
#             d.criminal_charges,
#             d.criminal_age,
#             d.criminal_address,
#             d.lat,
#             d.lon,
#         )
#         for d in o
#     ],
#     columns=["criminal", "date", "charges", "age", "address", "lat", "lon"],
# )

# X = df["officer"]
# Y = df["Frequency"]

# # X1 = df2['criminal']
# # Y1 = df2['date']

# fig = go.Figure(data=[go.Bar(x=X, y=Y)])
# # fig2 = go.Figure(data=[go.Histogram(x=X1, y=Y1)])
# # fig2 = go.Figure()
# fig.update_layout(
#     # <a href="/home">home</a>
#     title_text="<b> Arrests by Officer (2019-2021) </b> <br> ",
#     xaxis_title="Arresting Officer <br>",
#     yaxis_title="Arrests Made <br>",
#     # plot_bgcolor='#000000',
#     font=dict(
#         # family="Courier New, monospace",
#         color="#000000"
#     ),
# )

# date = df2["date"]
# data = go.Scattermapbox(
#     lon=[df2["lon"][i] for i in range(len(df2))],
#     lat=[df2["lat"][i] for i in range(len(df2))],
#     mode="markers+text",
#     marker=dict(size=25, color="red", allowoverlap=True),
#     textposition="top right",
#     textfont=dict(size=12, color="white"),
#     hovertemplate="longitude: %{lon}<br>" + "latitude: %{lat}<br>" + "<extra></extra>",
#     text=df2["date"]
#     + "<br>"
#     + df2["criminal"]
#     + "<br>"
#     + df2["charges"]
#     + "<br>"
#     + "Age: "
#     + df2["age"],
# )

# fig2 = go.Figure(data=data)

# fig2.update_layout(
#     # title_text="<b> Arrests by Officer (2019-2021) </b> <br> ",
#     # title="<br> <b> Reported OUI's (2019-2021) ", #(2019-2021)</b><br>(hold right-click & move mouse to change pitch )
#     title_text="<b> Arrests by Officer (2019-2021) </b> <br> ",
#     autosize=True,
#     hovermode="closest",
#     showlegend=False,
#     margin=dict(l=25, t=0, r=25, b=0, pad=0),
#     font=dict(
#         # family="Courier New, monospace",
#         color="red",
#         size=13,
#     ),
#     mapbox=dict(
#         accesstoken=MAPBOX_ACCESS_TOKEN,
#         bearing=0,
#         center=dict(lat=42.4817822, lon=-70.8844412),
#         pitch=120,
#         zoom=14,
#         style="dark",
#     ),
# )


# dash_app.layout = html.Div(
#     [
#         html.H1("More maps/graphs will be added here"),
#         # html.Label([html.A('Home', href='/', style={'color': 'blue', 'fontSize': 28})]),
#         dcc.Graph(
#             id="graph",
#             figure=fig,
#             animate=True,
#             style={
#                 "backgroundColor": "##000000",
#                 "color": "white",
#                 "margin-bottom": "50px",
#             },
#         ),
#         html.H5(
#             "More maps/graphs will be added here",
#             style={"margin-left": "100px", "margin-top": "50px"},
#         ),
#         dcc.Graph(
#             id="graph2",
#             figure=fig2,
#             animate=True,
#             style={
#                 "backgroundColor": "#FFFFFF",
#                 "color": "white",
#                 "margin-top": "50px",
#             },
#         ),
#     ]
# )


# @dash_app.callback(Output("graph", "data"))
# # [Input('interval-component', 'n_intervals')])
# def update_graph():
#     return get_value()
