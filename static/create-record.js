const parent = new Vue({
      el: '#app',
      data: {
        newInspectionRecord: {
          date: '',
          inspection_category: '',
          department: '',
          location: '',
          observation: '',
          compliance_status: '',
          discussed_with: '',
          target_date: '',
          photos: []
        },
        newMeetingRecord: {
          date: '',
          meeting_category: '',
          department: '',
          no_participants: '',
          chaired_by: '',
          photos: []
        },
        newTrainingRecord: {
          date: '',
          training_category: '',
          department: '',
          no_participants: '',
          participation_level: '',
          photos: [],
          other_category: ''
        },
        all_departments: ["ACVS","BF","CED","CO&CC","CR(E)","CR(M)","CRM","CRM-3","DNW","EL&TC","EMD","ERS","ETL","FORGE SHOP",
            "GM(E)","GM(M)","GU","HM(E)","HM(M)","HRCF","HSM","I&A","ICF","IMF","M/C SHOP","OG&CBRS","PEB","PFRS","PROJECTS","R&R",
            "RCL","RED","RGBS","RMHP","RMP","SF & PS","SGP", "SMS-1","SMS-2&CCS","SP","MRD","STORES","STRL SHOP","TBS","TRAFFIC","WMD"],
        inspection_categories : ["General","Safety Monitoring","Audio-Visual System", "Central Cable Gallery", "Conveyor Gallery", "EOT Crane", "Illumination", "Locomotive", "Rail-Road Level Crossing","Safety Walk"],
        meeting_categories: ["DLSIC","SAC","SAW", "Contractor Safety Committee"],
        training_categories: ["One Day Safety Awareness Training for Non-Exec","Two Day Safety Awareness Training for Exec","Half Day Electrical Safety Training","Others"],
        active_tab: 1,    //1 for training, 2 for meeting, 3 for training
        flashMessage: '',
        flashMessageType: '',
        uploading: false
      },
      methods: {
        async submitInspectionData() {
          // Handle form submission, e.g., send data to the server
          this.uploading=true;
          this.showUploadingFlashMessage('Uploading...', 'info');
          const formData = new FormData();
          for (let key in this.newInspectionRecord) {
            console.log(key);
            console.log(this.newInspectionRecord[key]);
            if (key!="photos"){
              formData.append(key, this.newInspectionRecord[key]);
            }
          }
          if (this.newInspectionRecord.photos.length != 0){
            this.newInspectionRecord.photos.forEach((file, index) => {
              formData.append(`file${index}`, file); // Append each file to the form data
            });
          }
          try{
            const response = await fetch('/api/create-inspection-record', {
              method: 'POST',
              body: formData
            })

            if (!response.ok){
              throw new Error('Failed to upload data');
            }
            const result = await response.json();
            this.newInspectionRecord.observation='';
            this.newInspectionRecord.compliance_status='';
            this.newInspectionRecord.target_date='';
            this.newInspectionRecord.photos=[];
            this.uploading=false;
            this.showUploadingFlashMessage('', '');
            this.showFlashMessage("Upload Successful","success")
          }catch(error){
            console.log("Error Updating: ", error);
            this.uploading=false;
            this.showUploadingFlashMessage('', '');
            this.showFlashMessage('Upload Failed','error');
          }
        },
        handleInspectionPhotoUpload(event) {
          this.newInspectionRecord.photos = Array.from(event.target.files);
        },
        async submitMeetingData() {
          // Handle form submission, e.g., send data to the server
          this.uploading=true;
          this.showUploadingFlashMessage('Uploading...', 'info');
          const formData = new FormData();
          for (let key in this.newMeetingRecord) {
            if (key!="photos"){
              formData.append(key, this.newMeetingRecord[key]);
            }
          }
          if (this.newMeetingRecord.photos.length != 0){
            this.newMeetingRecord.photos.forEach((file, index) => {
              formData.append(`file${index}`, file); // Append each file to the form data
            });
          }
          try{
            const response = await fetch('/api/create-meeting-record', {
              method: 'POST',
              body: formData
            })

            if (!response.ok){
              throw new Error('Failed to upload data');
            }
            const result = await response.json();
            this.newMeetingRecord.meeting_category='';
            this.newMeetingRecord.department='';
            this.newMeetingRecord.no_participants='';
            this.newMeetingRecord.chaired_by='';
            this.newMeetingRecord.photos=[];
            this.uploading=false;
            this.showUploadingFlashMessage('', '');
            this.showFlashMessage("Upload Successful","success")
          }catch(error){
            console.log("Error Updating: ", error);
            this.uploading=false;
            this.showUploadingFlashMessage('', '');
            this.showFlashMessage('Upload Failed','error');
          }
        },
        handleMeetingPhotoUpload(event) {
          this.newMeetingRecord.photos = Array.from(event.target.files);
        },
        async submitTrainingData() {
          // Handle form submission, e.g., send data to the server
          this.uploading=true;
          this.showUploadingFlashMessage('Uploading...', 'info');
          const formData = new FormData();
          for (let key in this.newTrainingRecord) {
            if (key!="photos"){
              formData.append(key, this.newTrainingRecord[key]);
            }
          }
          if (this.newTrainingRecord.photos.length != 0){
            this.newTrainingRecord.photos.forEach((file, index) => {
              formData.append(`file${index}`, file); // Append each file to the form data
            });
          }
          try{
            const response = await fetch('/api/create-training-record', {
              method: 'POST',
              body: formData
            })

            if (!response.ok){
              throw new Error('Failed to upload data');
            }
            const result = await response.json();
            this.newTrainingRecord.training_category='';
            this.newTrainingRecord.other_category='';
            this.newTrainingRecord.department='';
            this.newTrainingRecord.no_participants='';
            this.newTrainingRecord.participation_level='';
            this.newTrainingRecord.photos=[];
            this.uploading=false;
            this.showUploadingFlashMessage('', '');
            this.showFlashMessage("Upload Successful","success")
          }catch(error){
            console.log("Error Updating: ", error);
            this.uploading=false;
            this.showUploadingFlashMessage('', '');
            this.showFlashMessage('Upload Failed','error');
          }
        },
        handleTrainingPhotoUpload(event) {
          this.newTrainingRecord.photos = Array.from(event.target.files);
        },
        changeActiveTab(tab_no){
          console.log(this.active_tab);
          this.active_tab = tab_no;
          console.log(this.active_tab);
          const tabLinks = document.querySelectorAll('.nav-link');

          tabLinks.forEach((tabLink, index) => {
              if (index === this.active_tab - 1) {
                  tabLink.classList.add('active');
                  tabLink.setAttribute('aria-selected', 'true');
              } else {
                  tabLink.classList.remove('active');
                  tabLink.setAttribute('aria-selected', 'false');
              }
          });
        },
        showFlashMessage(message, type) {
          this.flashMessage = message;
          this.flashMessageType = type;

          // Hide the flash message after 3 seconds
          setTimeout(() => {
            this.flashMessage = '';
            this.flashMessageType = '';
          }, 3000);
        },
        showUploadingFlashMessage(message, type) {
          if (this.uploading==true){
            this.flashMessage = message;
            this.flashMessageType = type;
          }else{
            this.flashMessage = '';
            this.flashMessageType = '';
          }
        }
      },
      delimiters : ['[[', ']]']
    });