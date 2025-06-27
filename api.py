from flask_restful import Resource
from flask_restful import fields, marshal_with
from validation import *
from flask_restful import reqparse
from sqlalchemy import exc, func
from sqlalchemy import or_,and_
from datetime import datetime
import pandas as pd
from flask import request, jsonify, make_response, send_file
from model import *
import logging
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError
import gspread
import os

from create_word_report import *
from create_ppt_report import *

class RecordNotFoundException(Exception):
    pass

# Configure logging level and file
logging.basicConfig(filename='app.log', level=logging.DEBUG)

# Create a logger object
logger = logging.getLogger()



############################ Google Sheets ##########################################
import gspread

# Define the scope and credentials for Google Sheets API
scope = ['https://spreadsheets.google.com/feeds',
   'https://www.googleapis.com/auth/drive']

# Authorize the client with credentials
creds = ServiceAccountCredentials.from_json_keyfile_name('/home/sailbslsafety/mysite/credentials.json', scope)
client = gspread.authorize(creds)

#######################################################################################


##############################    Google Drive  ################################################
drive_service = build('drive', 'v3', credentials=creds, cache_discovery=False)
###############################################################################################

UPLOADS_DIR = '/home/sailbslsafety/mysite/uploads'

inspection_records={
     "id":fields.Integer,
    "date":fields.String,
    "inspection_category":fields.String,
    "department":fields.String,
    "location":fields.String,
    "observation":fields.String,
    "compliance_status":fields.String,
    "photo":fields.String,
    "discussed_with":fields.String,
    "target_date":fields.String,
    "images":fields.List(fields.String),
    "complied_photo":fields.String,
    "complied_images":fields.List(fields.String),
    "updated_on":fields.String
}

meeting_records={
    "id":fields.Integer,
    "date":fields.String,
    "meeting_category":fields.String,
    "department":fields.String,
    "no_participants":fields.String,
    "chaired_by":fields.String,
    "images":fields.List(fields.String)
}

class MeetingRecordsAPI (Resource):
      def get(self, start_date, end_date, category, department):
            # Start building the base query
            query = db.session.query(MeetingRecords)
            # Construct the filters based on conditions
            if start_date != 'all':
                  query = query.filter(MeetingRecords.date >= start_date)
            if end_date != 'all':
                  query = query.filter(MeetingRecords.date <= end_date)
            if category != 'all':
                  query = query.filter(MeetingRecords.meeting_category == category)
            if department != 'all':
                  query = query.filter(MeetingRecords.department == department)

            records = query.all()
            if records:
                  for record in records:
                        if record.photo:
                              record.images = record.photo.split(",")
                        else:
                              record.images = []

                  return self.marshal_records(records)
            else:
                  logger.error(str(datetime.now()) + " : " + "No records found for this combination of department & date")
                  return make_response(jsonify({'message': "No records found for this combination of department & date"}), 404)

      @marshal_with(meeting_records)
      def marshal_records(self, records):
            return records

class InspectionRecordsAPI (Resource):
      def get(self, start_date, end_date, department, compliance_status):
            # Start building the base query
            query = db.session.query(InspectionRecords)
            # Construct the filters based on conditions

            # Construct the filters based on conditions
            if compliance_status != 'all':
                  query = query.filter(InspectionRecords.compliance_status == compliance_status)
            if department != 'all':
                  query = query.filter(InspectionRecords.department == department)
            if start_date != 'all':
                  query_on_inspection_date = query.filter(InspectionRecords.date >= start_date)
                  query_on_compliance_date = query.filter(InspectionRecords.updated_on >= start_date)
            if end_date != 'all':
                  query_on_inspection_date = query_on_inspection_date.filter(InspectionRecords.date <= end_date)
                  query_on_compliance_date = query_on_compliance_date.filter(InspectionRecords.updated_on <= end_date)

            combined_query = query_on_inspection_date.union(query_on_compliance_date)

            # Remove duplicates based on a specific column
            distinct_query = combined_query.distinct('id')

            records = distinct_query.all()
            if records:
                  for record in records:
                        if record.photo:
                              record.images = record.photo.split(",")
                        else:
                              record.images = []

                        if record.complied_photo:
                              record.complied_images = record.complied_photo.split(",")
                        else:
                              record.complied_images = []
                  return self.marshal_records(records)
            else:
                  logger.error(str(datetime.now()) + " : " + "No records found for this combination of department, date & compliance status")
                  return make_response(jsonify({'message': "No records found for this combination of department, date & compliance status"}), 404)

      @marshal_with(inspection_records)
      def marshal_records(self, records):
            return records


class AllInspectionRecordsAPI (Resource):
    @marshal_with(inspection_records)
    def get(self):
          records = db.session.query(InspectionRecords).order_by(InspectionRecords.id.desc()).limit(100).all()
          if records:
            for record in records:
                  if record.photo:
                        record.images = record.photo.split(",")
                  else:
                        record.images = []
                  if record.complied_photo:
                       record.complied_images = record.complied_photo.split(",")
                  else:
                       record.complied_images = []
            return records
          else:
            raise NotFoundError(status_code=404)
    #to add a new record to inspection database
    #Note that this as of now, ONLY adds record incoming from the telegram bot/google sheet to the database and NOT the other way around
    def post(self):
      try:
            form = request.get_json()
            new_record = InspectionRecords(date=datetime.strptime(form.get('date'),'%Y-%m-%d').date(),
                                          inspection_category=form.get('inspection_category'),
                                          department=form.get('department'),
                                          location=form.get('location'),
                                          observation=form.get('observation'),
                                          compliance_status=form.get('compliance_status'),
                                          photo=form.get('photo'),
                                          discussed_with=form.get('discussed_with'),
                                          target_date=form.get('target_date'),
                                          complied_photo = form.get('complied_photo'),
                                          updated_on = form.get('date'))
            db.session.add(new_record)
            db.session.commit()
            success_message = "Record added in database"
            logger.info(str(datetime.now()) + " : " + success_message)
            return make_response(jsonify({'message': success_message}), 200)
      except Exception as e:
            # Handle other unexpected errors
            error_message = f"Failed to update record in Database: {str(e)}"
            logger.error(str(datetime.now()) + " : " + error_message)
            return make_response(jsonify({'message': error_message}), 500)

class AllMeetingRecordsAPI (Resource):
    @marshal_with(meeting_records)
    def get(self):
          records = db.session.query(MeetingRecords).all()
          if records:
            for record in records:
                  if record.photo:
                        record.images = record.photo.split(",")
                  else:
                        record.images = []
            return records
          else:
            raise NotFoundError(status_code=404)
    #to add a new record to meeting database
    #Note that this as of now, ONLY adds record incoming from the telegram bot to the database
    def post(self):
      try:
            form = request.get_json()
            new_record = MeetingRecords(date=datetime.strptime(form.get('date'),'%Y-%m-%d').date(),
                                          meeting_category=form.get('meeting_category'),
                                          department=form.get('department'),
                                          no_participants=form.get('no_participants'),
                                          chaired_by=form.get('chaired_by'),
                                          photo=form.get('photo'))
            db.session.add(new_record)
            db.session.commit()
            success_message = "Record added in database"
            logger.info(str(datetime.now()) + " : " + success_message)
            return make_response(jsonify({'message': success_message}), 200)
      except Exception as e:
            # Handle other unexpected errors
            error_message = f"Failed to update record in Database: {str(e)}"
            logger.error(str(datetime.now()) + " : " + error_message)
            return make_response(jsonify({'message': error_message}), 500)

#to add a new record
#Note that this API is used to add record from the web app database (Not the telegram bot) to the google sheet AND to the database
class CreateInspectionRecordAPI (Resource):
    @marshal_with(inspection_records)
    def post(self):
      files = request.files
      if (files):
            photo_list = []
            for key in files:
                  file_list = request.files.getlist(key)
                  for file in file_list:
                        filename = file.filename
                        image_path = os.path.join(UPLOADS_DIR, filename)
                        file.save(image_path)
                        photo_list.append(upload_photo_to_google_drive(filename,image_path))
                        os.remove(image_path)
            photo_links = ','.join(photo_list)
      else:
            photo_links=''

      try:
            # Open the Google Spreadsheet by its name
            spreadsheet_name = 'Safety-Records'
            inspection_sheet = client.open(spreadsheet_name).worksheet('Inspection')
            # Retrieve all rows from the sheet
            all_rows = inspection_sheet.get_all_values()

            # Determine the next serial number
            if len(all_rows) > 1:  # Assuming the first row is the header
                  last_serial_number = int(all_rows[-1][0])
                  next_serial_number = last_serial_number + 1
            else:
                  next_serial_number = 1
            inspection_sheet.append_rows([[next_serial_number,\
                  str(datetime.strptime(str(request.form.get('date')), "%Y-%m-%d").strftime("%d-%m-%Y")),\
                  request.form.get('inspection_category'),\
                  request.form.get('department'),\
                  request.form.get('location'),\
                  request.form.get('observation'),\
                  request.form.get('compliance_status'),\
                  photo_links,\
                  request.form.get('discussed_with'),\
                  request.form.get('target_date')]])
            success_message = "Record added in Google Spreadsheet"
            logger.info(str(datetime.now()) + " : " + success_message)
            new_record = InspectionRecords(date=datetime.strptime(request.form.get('date'),'%Y-%m-%d').date(),
                                          inspection_category=request.form.get('inspection_category'),
                                          department=request.form.get('department'),
                                          location=request.form.get('location'),
                                          observation=request.form.get('observation'),
                                          compliance_status=request.form.get('compliance_status'),
                                          photo=photo_links,
                                          discussed_with=request.form.get('discussed_with'),
                                          target_date=request.form.get('target_date'),
                                          complied_photo = "",
                                          updated_on = "")
            db.session.add(new_record)
            db.session.commit()
            success_message = "Inspection Record added in database"
            logger.info(str(datetime.now()) + " : " + success_message)
            return make_response(jsonify({'message': "Inspection record successfully added"}), 200)
      except Exception as e:
            error_message = f"Failed to create Inspection record in database or/and spreadsheet: {str(e)}"
            logger.error(str(datetime.now()) + " : " + error_message)
            return make_response(jsonify({'message': error_message}), 500)

class CreateMeetingRecordsAPI (Resource):
    def post(self):
      files = request.files
      if (files):
            photo_list = []
            for key in files:
                  file_list = request.files.getlist(key)
                  for file in file_list:
                        filename = file.filename
                        image_path = os.path.join(UPLOADS_DIR, filename)
                        file.save(image_path)
                        photo_list.append(upload_photo_to_google_drive(filename,image_path))
                        os.remove(image_path)
            photo_links = ','.join(photo_list)
      else:
            photo_links=''

      try:
            # Open the Google Spreadsheet by its name
            spreadsheet_name = 'Safety-Records'
            meeting_sheet = client.open(spreadsheet_name).worksheet('Meeting')

            meeting_sheet.append_rows([[str(datetime.strptime(str(request.form.get('date')), "%Y-%m-%d").strftime("%d-%m-%Y")),\
                  request.form.get('meeting_category'),\
                  request.form.get('department'),\
                  request.form.get('no_participants'),\
                  request.form.get('chaired_by'),\
                  photo_links]])
            success_message = "Meeting Record added in Spreadsheet"
            logger.info(str(datetime.now()) + " : " + success_message)
            new_record = MeetingRecords(date=datetime.strptime(request.form.get('date'),'%Y-%m-%d').date(),
                                          meeting_category=request.form.get('meeting_category'),
                                          department=request.form.get('department'),
                                          no_participants=request.form.get('no_participants'),
                                          chaired_by=request.form.get('chaired_by'),
                                          photo=photo_links)
            db.session.add(new_record)
            db.session.commit()
            success_message = "Meeting Record added in database"
            logger.info(str(datetime.now()) + " : " + success_message)
            return make_response(jsonify({'message': "Meeting record successfully added"}), 200)
      except Exception as e:
            error_message = f"Failed to create Meeting record  in database or/and spreadsheet: {str(e)}"
            logger.error(str(datetime.now()) + " : " + error_message)
            return make_response(jsonify({'message': error_message}), 500)

class CreateTrainingRecordsAPI (Resource):
    def post(self):
      files = request.files
      if (files):
            photo_list = []
            for key in files:
                  file_list = request.files.getlist(key)
                  for file in file_list:
                        filename = file.filename
                        image_path = os.path.join(UPLOADS_DIR, filename)
                        file.save(image_path)
                        photo_list.append(upload_photo_to_google_drive(filename,image_path))
                        os.remove(image_path)
            photo_links = ','.join(photo_list)
      else:
            photo_links=''

      try:
            # Open the Google Spreadsheet by its name
            spreadsheet_name = 'Safety-Records'
            meeting_sheet = client.open(spreadsheet_name).worksheet('Training')

            meeting_sheet.append_rows([[str(datetime.strptime(str(request.form.get('date')), "%Y-%m-%d").strftime("%d-%m-%Y")),\
                  request.form.get('training_category'),\
                  request.form.get('other_category'),\
                  request.form.get('department'),\
                  request.form.get('no_participants'),\
                  request.form.get('participation_level'),\
                  photo_links]])
            success_message = "Training Record added in Spreadsheet"
            logger.info(str(datetime.now()) + " : " + success_message)
            new_record = TrainingRecords(date=datetime.strptime(request.form.get('date'),'%Y-%m-%d').date(),
                                          training_category=request.form.get('training_category'),
                                          other_category= request.form.get('other_category'),
                                          department=request.form.get('department'),
                                          no_participants=request.form.get('no_participants'),
                                          participation_level=request.form.get('participation_level'),
                                          photo=photo_links)
            db.session.add(new_record)
            db.session.commit()
            success_message = "Training Record added in database"
            logger.info(str(datetime.now()) + " : " + success_message)
            return make_response(jsonify({'message': "Training record successfully added"}), 200)

      except Exception as e:
            error_message = f"Failed to create Training record in database or/and spreadsheet: {str(e)}"
            logger.error(str(datetime.now()) + " : " + error_message)
            return make_response(jsonify({'message': error_message}), 500)

class UpdateInspectionRecordsAPI (Resource):
      def put(self):
            id = request.form.get("id")
            compliance_status = request.form.get("compliance_status")
            files = request.files
            if (files):
                  photo_links = []
                  for key in files:
                        file_list = request.files.getlist(key)
                        for file in file_list:
                              filename = file.filename
                              image_path = os.path.join(UPLOADS_DIR, filename)
                              file.save(image_path)
                              photo_links.append(upload_photo_to_google_drive(filename,image_path))
                              os.remove(image_path)
                  old_photo_links = str(db.session.query(InspectionRecords).filter(InspectionRecords.id==int(id)).first().complied_photo)
                  if old_photo_links == "":
                        new_photo_links = ','.join(photo_links)
                  else:
                        new_photo_links = old_photo_links + ',' + ','.join(photo_links)
            else:
                 new_photo_links=''
            updated_on = datetime.now().strftime('%Y-%m-%d')      #datetime object in YYYY-MM-DD format for database
            updated_on_str = str(datetime.strptime(str(updated_on), "%Y-%m-%d").strftime("%d-%m-%Y")) #string in DD-MM-YYYY for google spreadsheet


            try:
                  # Spreadsheet ID and sheet name
                  spreadsheet_name = 'Safety-Records'
                  inspection_sheet = client.open(spreadsheet_name).worksheet('Inspection')

                  # Value to search for and new value to set
                  SEARCH_VALUE = id
                  NEW_VALUE_1 = compliance_status
                  NEW_VALUE_2 = new_photo_links
                  NEW_VALUE_3 = updated_on_str
                  SEARCH_COLUMN_INDEX = 1  # Column to search for the value (1 for column A, i.e SN.)
                  UPDATE_COLUMN_INDEX_1 = 7  # Column to update (7 for column F, i.e, compliance status)
                  UPDATE_COLUMN_INDEX_2 = 11  # Column to update (11 for column K, i.e, complied photos)
                  UPDATE_COLUMN_INDEX_3 = 12  # Column to update (12 for column L, i.e, Updated On)


                  # Get all values from the search column
                  column_values = inspection_sheet.col_values(SEARCH_COLUMN_INDEX)

                  # Find the row with the matching value
                  row_to_update = None
                  for idx, value in enumerate(column_values):
                        if value == SEARCH_VALUE:
                              row_to_update = idx + 1  # Google Sheets is 1-indexed
                              break

                  if row_to_update:
                        # Update the cell in the specified column and row
                        inspection_sheet.update_cell(row_to_update, UPDATE_COLUMN_INDEX_1, NEW_VALUE_1)
                        inspection_sheet.update_cell(row_to_update, UPDATE_COLUMN_INDEX_2, NEW_VALUE_2)
                        inspection_sheet.update_cell(row_to_update, UPDATE_COLUMN_INDEX_3, NEW_VALUE_3)
                        success_message_spreadsheet = f"Updated row {row_to_update} in column {UPDATE_COLUMN_INDEX_1}, {UPDATE_COLUMN_INDEX_2} and {UPDATE_COLUMN_INDEX_3} with new value {NEW_VALUE_1}, {NEW_VALUE_2} and {NEW_VALUE_3} respectively in Google Spreadsheet."
                        logger.info(success_message_spreadsheet + " at " + str(datetime.now()))

                        #Updating the sqlite database only after the spreadhsheet is sucessfully updated
                        db.session.query(InspectionRecords).filter(InspectionRecords.id==int(id)).update({'compliance_status':compliance_status,'complied_photo':new_photo_links,'updated_on':updated_on})
                        db.session.commit()
                        success_message_databse = "Updated Record in Database in observation ID " + id
                        logger.info(str(datetime.now()) + " : " + success_message_databse)

                        return make_response(jsonify({'message': 'Record updated successfully'}), 200)
                  else:
                        raise RecordNotFoundException(f"Value '{SEARCH_VALUE}' not found in column {SEARCH_COLUMN_INDEX}.")
            except HttpError as e:
                  # Handle specific HTTP errors from Google API
                  error_message = f"Failed to update record in Google Spreadsheet: {e.response.status} - {e.response.reason}"
                  logger.error(error_message + " at time " + str(datetime.now()))
                  return make_response(jsonify({'message': error_message}), e.response.status)
            except RecordNotFoundException as e:
                  # Handle the custom exception for record not found
                  logger.error(str(datetime.now()) + " : " + str(e))
                  return make_response(jsonify({'message': str(e)}), 404)
            except Exception as e:
                  # Handle other unexpected errors
                  error_message = f"Failed to update record in Google Spreadsheet: {str(e)}"
                  logger.error(str(datetime.now()) + " : " + error_message)
                  return make_response(jsonify({'message': error_message}), 500)

class CreateWordReportAPI(Resource):
    def post(self):
        try:
            observations = request.json  # Parse the JSON data
            observations_df = pd.DataFrame(observations)
            file_path = create_report(observations_df)
            return send_file(file_path, download_name='report.docx', as_attachment=True)
        except Exception as e:
            return make_response(jsonify({'message': f'Failed to process data: {str(e)}'}), 500)

class CreatePPTReportAPI(Resource):
    def post(self):
        try:
            observations = request.json  # Parse the JSON data
            observations_df = pd.DataFrame(observations)
            file_path = createPPT(observations_df)
            print (file_path)
            return send_file(file_path, download_name='presentation.pptx', as_attachment=True)
        except Exception as e:
            return make_response(jsonify({'message': f'Failed to process data: {str(e)}'}), 500)

def upload_photo_to_google_drive(file_id, image_path):
  file_metadata = {
    'name': f'{file_id}.jpg',
    'parents': ["1Pw3zmGy0M3p-fwAYarevmM0DnqSZbWIv"]  #ID of the folder where you want to upload the image
  }
  media = MediaFileUpload(image_path, mimetype='image/jpeg')
  uploaded_file = drive_service.files().create(body=file_metadata, media_body=media, fields='webViewLink').execute()
  photo_link = uploaded_file.get('webViewLink')
  return photo_link