from flask import render_template, url_for,redirect, flash, send_file
from flask import request
from flask import current_app as app
from model import db
from model import *
from datetime import datetime

import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import plotly.express as px

# Define the scope and credentials for Google Sheets API
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

# Authorize the client with credentials
creds = ServiceAccountCredentials.from_json_keyfile_name('/home/sailbslsafety/mysite/credentials.json', scope)
client = gspread.authorize(creds)

# Open the Google Spreadsheet
spreadsheet_name = 'Safety-Records'
inspection_sheet = client.open(spreadsheet_name).worksheet('Inspection')
meeting_sheet = client.open(spreadsheet_name).worksheet('Meeting')
training_sheet = client.open(spreadsheet_name).worksheet('Training')

# Get all records in the Google Spreadsheet
inspection_data = inspection_sheet.get_all_records()
meeting_data = meeting_sheet.get_all_records()
training_data = training_sheet.get_all_records()

# Load data into a Pandas DataFrame
inspection_df = pd.DataFrame(inspection_data)
meeting_df = pd.DataFrame(meeting_data)
training_df = pd.DataFrame(training_data)

def create_bar_chart(categories, values):
    fig = px.bar(x=categories, y=values, text=values, title='Bar Chart',
                 labels={'x': 'Categories', 'y': 'Values'},
                 color_discrete_sequence=px.colors.qualitative.T10,
                 width=600, height=400)
    fig.update_layout(plot_bgcolor='#000000', paper_bgcolor='#000000', font_color='white')
    fig.update_traces(marker_line_width=1, marker_line_color='white', opacity=0.8)
    return fig.to_html(full_html=False)

def create_pie_chart(categories, values):
    fig = px.pie(names=categories, values=values, title='Pie Chart',
                 color_discrete_sequence=px.colors.qualitative.T10,
                 width=600, height=400)
    fig.update_traces(textinfo='percent+label', textfont_size=12, marker=dict(line=dict(color='white', width=2)))
    fig.update_layout(plot_bgcolor='#000000', paper_bgcolor='#000000', font_color='white')
    return fig.to_html(full_html=False)

@app.route('/', methods=["GET", "POST"])
def index():
    if request.method == "GET":
        '''
        for index, observation in inspection_df.iterrows():
            #print(f"A: {row['A']}, B: {row['B']}, C: {row['C']}")
            new_record = InspectionRecords(date=datetime.strptime(observation['Inspection Date'],'%d-%m-%Y').date(),
                                        inspection_category=observation['Inspection Category'],
                                        department=observation['Department'],
                                        location=observation['Location'],
                                        observation=observation['Observation'],
                                        compliance_status=observation['Compliance Status'],
                                        photo=observation['Photo'],
                                        discussed_with=observation['Discussed with'],
                                        target_date=observation['Compliance Target'],
                                        complied_photo=observation['Complied Photo'],
                                        updated_on=observation['Updated on'])
            db.session.add(new_record)
            db.session.commit()
        '''
        return render_template("homepage.html")

@app.route('/inspection-records', methods=["GET", "POST"])
def inspection_records():
    if request.method == "GET":
        return render_template("inspection-records.html")

@app.route('/meeting-records', methods=["GET", "POST"])
def meeting_records():
    if request.method == "GET":
        return render_template("meeting-records.html")

@app.route('/create-record', methods=["GET", "POST"])
def create_records():
    if request.method == "GET":
        return render_template("create-record.html")
