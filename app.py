from flask import Flask
from flask_restful import Resource, Api
from api import *
import os
from model import db

app = Flask(__name__)
#app.config['UPLOAD_FOLDER'] = './uploads'
#CORS(app)

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
current_dir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + os.path.join(current_dir, "database.sqlite3")


db.init_app(app)
api = Api(app)

app.app_context().push()

with app.app_context():
	db.create_all()

from controllers import *
from api import *

api.add_resource(InspectionRecordsAPI, "/api/inspection-records/<string:start_date>/<string:end_date>/<string:department>/<string:compliance_status>")
api.add_resource(MeetingRecordsAPI, "/api/meeting-records/<string:start_date>/<string:end_date>/<string:category>/<string:department>")
api.add_resource(AllInspectionRecordsAPI, "/api/inspection-records")
api.add_resource(AllMeetingRecordsAPI, "/api/meeting-records")
api.add_resource(UpdateInspectionRecordsAPI, "/api/update/inspection-records")
api.add_resource(CreateWordReportAPI, "/api/create-word-report")
api.add_resource(CreatePPTReportAPI,"/api/create-ppt-report")
api.add_resource(CreateInspectionRecordAPI,"/api/create-inspection-record")
api.add_resource(CreateMeetingRecordsAPI,"/api/create-meeting-record")
api.add_resource(CreateTrainingRecordsAPI,"/api/create-training-record")

# Custom 404 error handler
@app.errorhandler(404)
def page_not_found(error):
    return render_template('404_handler.html'), 404

if __name__ == '__main__':
	app.run()