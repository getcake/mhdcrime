#!/usr/bin/env python3.9

from bs4 import BeautifulSoup

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# from flask_debugtoolbar import DebugToolbarExtension
from flask import render_template, url_for, flash, redirect, request

# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy import create_engine, Column, Integer, String, Text

from tika import parser
from io import BytesIO
from datetime import datetime as dt

from geopy.geocoders import MapQuest, GoogleV3, Nominatim, ArcGIS, OpenMapQuest
from functools import cached_property, cache, partial

from termcolor import cprint, colored
from tqdm import tqdm

from time import sleep

import requests
import re
import os
import functools

from app.database import db
from app.models import Report

# from app.get_reports import download_reports

from pathlib import Path


def make_report():

    directory = "/path/to/reports/folder"
    mv_dir = "/path/to/reports/folder/"

    def mark_read(d):
        fn = d.replace(".pdf", "")
        if "read" not in d:
            os.system(f"mv {mv_dir}/{d} {mv_dir}/{fn}-read.pdf")
        else:
            print(f'{d} already has "read" ')

    def sort(data):
        convert = lambda text: int(text) if text.isdigit() else text.lower()
        alphanum_key = lambda key: [convert(c) for c in re.split("([0-9]+)", key)]
        return sorted(data, key=alphanum_key)

    dirl = sort(os.listdir(directory))

    for d in dirl:

        if "read" not in d and ".DS_Store" not in d:

            pdf = parser.from_file(f"/path/to/reports/folder")
            # print(pdf['content'])
            data = str(pdf["content"]).strip()
            # data = str(data)
            # data.strip()
            # data = pdf['content']
            # data = str(data)
            call_number_regex = r"\d{2}(-)\d{1,6}[^-\w{2}]"  # ignores AR calls to avoid splitting of criminal informatoin
            call_number_regex2 = r"(?=\d{2}(-)\d{1,6}[^-\w{2}])"  # ignores AR calls to avoid splitting of criminal informatoin
            pg = re.split(call_number_regex2, data)

            def get_vehicle_information(x):

                vehicle_match = re.findall(r"Vehicle:(.*)", x)
                towed_match = re.findall(r"Towed:(.*)", x)

                if vehicle_match and not towed_match:

                    return "\n".join(vehicle_match)

                elif towed_match and vehicle_match:

                    return "\n".join(vehicle_match).join(towed_match)

            def get_jurisdiction(x):

                jurisdiction_match = re.search(r"Jurisdiction:(.*)", x)

                if jurisdiction_match is not None:

                    jurisdiction = jurisdiction_match.group()

                    if len(jurisdiction) > 4:

                        jurisdiction = jurisdiction.replace("Jurisdiction:", "").strip()

                        return jurisdiction

                else:

                    cprint("JURISDICTION NOT FOUND", "green")
                    print(jurisdiction_match)

            def get_action_taken(x):

                action_slice = x[20:80]

                action_regex = r"False Alarm|Services Rendered|No Action Required|Citation|Verbal Warning|Peace Restored|Could Not Locate|Transported to Hospital|Report Taken|Investigated|Taken/Referred to Other Agency|Vehicle Towed|Extinguished|Arrest|Unfounded|Founded"

                action_match = re.search(action_regex, action_slice, re.IGNORECASE)

                if action_match:
                    action = action_match.group()
                    if action is not None:
                        return action

            def get_primary_id(x):

                primary_id_match = re.findall(r"(Primary Id)(.*)", x)

                if primary_id_match:
                    match = primary_id_match[0]

                    prim = (
                        str(match)
                        .replace("Primary Id", "")
                        .replace("Police _", "")
                        .replace("('', ':", "")
                        .replace(")", "")
                        .replace("'", "")
                        .strip()
                    )

                    return prim

            def get_time(x):
                time_slice = x[5:20]
                time_match = re.search(r"\d{4}", time_slice)

                if time_match:
                    utime = time_match.group()
                    utime = utime[:2] + ":" + utime[2:]
                    time = dt.strptime(utime, "%H:%M")
                    time = time.strftime("%I:%M %p")

                    if time is not None:
                        return time

            def get_date(x):

                date_match = re.search(
                    r"(Dispatch|From:|Log|(?:\d{2}/){2}\d{4})(.*)", data
                )

                if date_match:
                    date = date_match.group()
                    date = re.split(r"From:|Thru:", date)[1]
                    if date is not None:
                        return date

            def get_call_type(x):

                call_type_slice = x[10:30]  # NOTE Can use similar slice for Time / date
                call_type_match = re.search(
                    r"Initiated|Cellular|Walk\-In|Alarm|Phone|911|Radio|Other",
                    call_type_slice,
                )
                if call_type_match:
                    # print(call_type_match.group())
                    call_type = call_type_match.group()
                    return call_type
                    # sleep(2)

            def get_unit_information(x):

                unit_matches = re.findall(r"(Unit:|EMS Unit:|Fire Unit:)(.*)", x)

                unit_matches_iter = re.finditer(r"(Unit:|EMS Unit:|Fire Unit:)(.*)", x)

                if unit_matches:

                    number_of_units = len(unit_matches)

                    unit_info = []

                    info_string = ""

                    disp_string = ""

                    arvd_string = ""

                    clrd_string = ""

                    for match in unit_matches_iter:

                        match_location_slice = x[match.start() : len(x)]

                        unit_match = re.search(
                            r"(Unit:|EMS Unit:|Fire Unit:)(.*)", str(match)
                        )

                        unit_match_disp = re.search(
                            r"Disp\-\d\d:\d\d:\d\d", match_location_slice
                        )

                        unit_match_arvd = re.search(
                            r"Arvd\-\d\d:\d\d:\d\d", match_location_slice
                        )

                        unit_match_arvd_all = re.findall(
                            r"Arvd\-\d\d:\d\d:\d\d", match_location_slice
                        )

                        unit_match_clrd = re.search(
                            r"Clrd\-\d\d:\d\d:\d\d", match_location_slice
                        )

                        unit_match = str(unit_match[0]).replace("'>", "")

                        unit_info.append(unit_match)

                        info_string += unit_match

                        if unit_match is not None:

                            if unit_match_disp is not None:

                                unit_info.append(
                                    unit_match_disp[0]
                                )  # NOTE Can we do something like this but with dictionaries?

                                disp_string += "  " + unit_match_disp[0]

                            if unit_match_arvd is not None:

                                unit_info.append(unit_match_arvd[0])

                                arvd_string += "  " + unit_match_arvd[0]

                            if unit_match_clrd is not None:

                                unit_info.append(unit_match_clrd[0])

                                clrd_string += "  " + unit_match_clrd[0]

                    return (
                        "\n"
                        + info_string
                        + "\n"
                        + disp_string
                        + "\n"
                        + arvd_string
                        + "\n"
                        + clrd_string
                    )

            def get_vicinity_of(x):

                vicinity_match = re.search(r"Vicinity of(.*)", x)

                if vicinity_match is not None:
                    vicinity = vicinity_match.group()
                    vicinity = (
                        vicinity.replace("Vicinity of:", "").replace(":", "").strip()
                    )
                    vicinity = re.sub(r"\[MAR \d{1,5}]", "", vicinity)

                    dup_match = re.search(r".+?(?= (\@|\+|\#) )", vicinity)

                    if dup_match:
                        vic = dup_match.group()
                        return vic

                    elif not dup_match and not None:

                        return vicinity

                else:
                    return None

            @cache
            def get_location_information(x):

                location_match = re.search(r"Location/Address(.*)", x)
                jurisdiction = get_jurisdiction(x)

                if location_match is not None:
                    location = location_match.group()
                    location = (
                        location.replace("Location/Address", "")
                        .replace(":", "")
                        .strip()
                    )
                    location = re.sub(r"\[MAR \d{1,5}]", "", location)

                    remove_match = re.search(
                        r"@(.*) | \+(.*)", location
                    )  # NOTE This works!
                    rm = re.compile(r"@(.*) | \+(.*)")
                    rmm = re.search(rm, location)
                    dup_match = re.search(r".+?(?=@ | \+ | Apt.)", location)

                    if dup_match:

                        loc = dup_match.group()
                        loc += " " + jurisdiction + " MA"
                        return loc

                    else:

                        return location + " " + jurisdiction + " MA"

                elif location_match is None:

                    vicinity = get_vicinity_of(x)
                    if vicinity is not None and jurisdiction is not None:
                        return vicinity + " " + jurisdiction + " MA"

                    else:
                        return None

            @cache
            def get_cords(x):

                location = get_location_information(x)
                gl = Nominatim(user_agent="mhdcrime", timeout=5)

                address = str(location)

                try:

                    location = gl.geocode(address)

                    if location is not None:
                        coordinates = location.latitude, location.longitude

                        if coordinates is not None:
                            return coordinates

                except Exception:
                    pass

            @cache
            def get_loc_lat(x):

                cords = get_cords(x)

                if cords is not None:
                    lat = cords[0]
                    return lat

            @cache
            def get_loc_lon(x):

                cords = get_cords(x)

                if cords is not None:
                    lon = cords[1]
                    return lon

            def get_call_reason(x):

                reason_match = re.search(r"- (.*)", x)
                reason_slice = x[:80]
                action_regex = r"False Alarm|Services Rendered|No Action Required|Citation|Verbal Warning|Peace Restored|Could Not Locate|Transported to Hospital|Report Taken|Investigated|Taken/Referred to Other Agency|Vehicle Towed|Extinguished|Arrest|Unfounded|Founded"

                if "Date" not in reason_slice:

                    if reason_match:
                        reason_match = str(reason_match.group()).replace(">", "")

                        if "Printed" not in reason_match:
                            reason_match = re.sub(action_regex, "", reason_match)
                            reason_match = reason_match.replace("-", " ")
                            return reason_match

            def get_call_number(x):

                cnum_slice = x[:10]
                cnum_match = re.search(r"\d{2}(-)\d{1,6}", cnum_slice)
                if cnum_match:
                    call_number = cnum_match.group()
                    return call_number

            def get_criminal_name(x):
                crim_match = re.search(r"Arrest:(.*)", x)
                if crim_match:
                    criminal_slice = x[crim_match.start() : len(x)]
                    crim_name_slice = criminal_slice[20 : len(x)]
                    crim_name_match = re.search(r"Arrest:(.*)", crim_name_slice)

                    if crim_name_match is not None:
                        criminal_name = crim_name_match.group()
                        criminal_name = criminal_name.replace("Arrest:", "").strip()
                        if criminal_name is not None:
                            return criminal_name

            def get_criminal_age(x):
                crim_match = re.search(r"Arrest:(.*)", x)
                if crim_match:
                    criminal_slice = x[crim_match.start() : len(x)]
                    crim_age_slice = criminal_slice[20 : len(x)]
                    crim_age_match = re.search(r"Age:(.*)", crim_age_slice)

                    if crim_age_match is not None:
                        criminal_age = crim_age_match.group()
                        criminal_age = criminal_age.replace("Age:", "").strip()
                        return criminal_age

            def get_criminal_address(x):
                crim_match = re.search(r"Arrest:(.*)", x)
                if crim_match:
                    criminal_slice = x[crim_match.start() : len(x)]
                    crim_address_slice = criminal_slice[20 : len(x)]
                    crim_address_match = re.search(r"Address:(.*)", crim_address_slice)

                    if crim_address_match is not None:
                        criminal_address = crim_address_match.group()
                        criminal_address = criminal_address.replace(
                            "Address:", ""
                        ).strip()
                        return criminal_address

            def get_criminal_charges(x):
                crim_match = re.search(r"Arrest:(.*)", x)
                if crim_match:
                    criminal_slice = x[crim_match.start() : len(x)]
                    crim_charges_slice = criminal_slice[20 : len(x)]
                    crim_charges_match = re.search(r"Charges:(.*)", crim_charges_slice)

                    if crim_charges_match is not None:
                        criminal_charges = crim_charges_match.group()
                        criminal_charges = criminal_charges.replace(
                            "Charges:", ""
                        ).strip()
                        return criminal_charges

            for x in pg:

                if len(x) > 5:

                    if get_call_type(x) is not None:

                        report = Report()

                        report.call_number = get_call_number(x)

                        report.call = get_call_type(x)
                        report.time = get_time(x)
                        # report.link = get_link(x)
                        report.reason = get_call_reason(x)
                        report.action_taken = get_action_taken(x)
                        report.location = get_location_information(x)
                        # report.cords = get(x)
                        report.lat = get_loc_lat(x)
                        report.lon = get_loc_lon(x)
                        report.primary_id = get_primary_id(x)
                        report.vicinity_of = get_vicinity_of(x)
                        report.jurisdiction = get_jurisdiction(x)
                        report.units = get_unit_information(x)
                        # report.dispatcher #TODO
                        report.vehicle = get_vehicle_information(x)
                        # report.related_incident #TODO
                        report.date = get_date(x)
                        # report.call_number = get_call_number(x) #TODO

                        report.criminal_name = get_criminal_name(x)
                        report.criminal_age = get_criminal_age(x)
                        report.criminal_address = get_criminal_address(x)
                        report.criminal_charges = get_criminal_charges(x)

                        # report.criminal_info = get_criminal_information(x)

                        exists = Report.query.filter_by(
                            call_number=report.call_number
                        ).first()

                        if not exists and "read" not in d:

                            db.session.add(report)
                            db.session.commit()

                            cprint(report, "green")
                            mark_read(d)

                        else:

                            cprint(
                                f" report {report.call_number} already exists", "red"
                            )

        else:

            print(f"file {d} already read")
