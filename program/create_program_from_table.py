import codecs
import html
from datetime import datetime
import pandas as pd

program_table = pd.read_csv("program_table.csv")

day_names = {"monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"}


def get_value(row, *names):
    for name in names:
        if name in row and pd.notna(row[name]):
            value = str(row[name]).strip()
            if value:
                return value
    return ""


def is_day_row(row):
    values = [
        str(value).strip() for value in row.tolist() if pd.notna(value) and str(value).strip()
    ]
    return len(values) == 1 and values[0].lower() in day_names


def parse_time(value):
    value = (value or "").strip()
    if not value:
        return None
    for fmt in ("%H:%M", "%H.%M", "%I:%M %p", "%I.%M %p"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    return None


def is_long_slot(start_time, end_time, minutes=15):
    start_dt = parse_time(start_time)
    end_dt = parse_time(end_time)
    if not start_dt or not end_dt:
        return False
    return (end_dt - start_dt).total_seconds() > minutes * 60


SESSION_COLORS = {
    "Super-Eddington Accretion Physics": "#cea9bd",
    "Black hole growth and galaxy evolution": "#799de5",
    "Active Galactic Nuclei and quasars": "#f19e38",
    "X-ray binaries and ULXs": "#78a75b",
    "Gamma-ray bursts and tidal disruption events": "#f9da79",
    "Unsure": "#d4e2f1",
    "LOC": "#222255",
}

html_template = """<!-- <!doctype html>
<html>
<head>
    <meta charset="utf-8">
    <title>Conference Program</title>
    <style>
        body { line-height: 1.4; background: transparent; }
        table { width: 100%; max-width: 100%; border-collapse: collapse; margin: 0 0 2rem 0; background: transparent; color: inherit; border: 1px solid currentColor; }
        th, td { border: 1px solid transparent; padding: 0.5rem; vertical-align: top; background: transparent; color: inherit; font: inherit; }
        th { background: transparent; text-align: left; }
        h2 { margin-top: 2rem; }
        details { cursor: pointer; }
    </style>
</head>
<body>
<h1>Conference Program</h1>
-->
<br/>
(Click on the title of each talk to see the abstract)
"""

in_table = False

for _, row in program_table.iterrows():
    if is_day_row(row):
        if in_table:
            html_template += "</tbody></table>"
        day = html.escape(get_value(row, "day", "Day") or str(row.dropna().iloc[0]).strip())
        html_template += f"<br />\n<h2>{day}</h2>\n<table>\n"
        # html_template += "<thead><tr><th>Start</th><th>End</th><th>Speaker</th><th>Title</th><th>Abstract</th></tr></thead>\n"
        html_template += "<tbody>\n"
        in_table = True
        continue

    if not in_table:
        html_template += "<table>"
        # html_template += "<thead><tr><th>Start</th><th>End</th><th>Speaker</th><th>Title</th><th>Abstract</th></tr></thead>"
        html_template += "<tbody>"
        in_table = True

    start_time = html.escape(
        get_value(row, "start", "Start", "start_time", "Start time", "time_start")
    )
    end_time = html.escape(get_value(row, "end", "End", "end_time", "End time", "time_end"))
    speaker = html.escape(get_value(row, "speaker", "Speaker"))
    title = html.escape(get_value(row, "talk title", "talk_title", "title", "Title"))
    abstract = html.escape(get_value(row, "abstract", "Abstract", "description", "Description"))
    session = html.escape(get_value(row, "session", "Session"))

    if speaker.strip() == "" and title.strip() == "" and abstract.strip() == "":
        continue
    if start_time.strip() == "":
        continue

    talk = title.strip() != "" or speaker.strip() == "Discussion"
    if is_long_slot(start_time, end_time):
        speaker = f"<strong>{speaker}</strong>"

    color = SESSION_COLORS.get(session, "#333333")
    if talk:
        new_row = f"""
        <tr style="background: transparent;">
            <td style="background-color: {color};">{start_time}</td>
            <td style="min-width: 200px;">{speaker}</td>
        """
    else:
        new_row = f"""
        <tr style="background-color: #333333;">
            <td style="background-color: {color};">{start_time}</td>
            <td>{speaker}</td>
        """

    if talk:
        # new_row += f"""<td>{title}</td>
        # <td><details><summary>Show abstract</summary>{abstract}</details></td>
        # </tr>"""
        new_row += f"""<td><details><summary>{title}</summary>{abstract}</details></td>
        </tr>"""
    else:
        new_row += f"""<td></td>
        <td></td>
        </tr>"""

    html_template += new_row

if in_table:
    html_template += "</tbody></table>"

html_template += "</body></html>"

with open("../_includes/program_table.html", "w", encoding="utf-8") as f:
    f.write(html_template)

with codecs.open("../_includes/program_table.html", "r", "utf-8") as file:
    print(file.read())
