const parent = new Vue({
  el: '#app',
  data: {
        start: '',
        end: '',
        department: '',
        compliance_status: '',
        observations: [],
        to_upload_photos: [],
        flashMessage: '',
        flashMessageType: '',
        loading:false,
        active_observationID: '',
        all_departments: ["ACVS","BF","CED","CO&CC","CR(E)","CR(M)","CRM","CRM-3","DNW","EL&TC","EMD","ERS","ETL","FORGE SHOP",
          "GM(E)","GM(M)","GU","HM(E)","HM(M)","HRCF","HSM","I&A","ICF","IMF","M/C SHOP","OG&CBRS","PEB","PFRS","PROJECTS","R&R",
          "RCL","RED","RGBS","RMHP","RMP","SF & PS","SGP", "SMS-1","SMS-2&CCS","SP","MRD","STORES","STRL SHOP","TBS","TRAFFIC","WMD"]
  },
  methods: {
    async getAllData(){
      const res = await fetch('/api/inspection-records')
      const observations_ = await res.json()
      this.observations = observations_
      /*
      payload = {"date":"a",
        "inspection_category": "b",
        "department": "c",
        "location": "d",
        "observation": "e",
        "compliance_status": "f",
        "photo": "f",
        "discussed_with": "g",
        "target_date": "h"}
      fetch('/api/inspection-records', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
      })    */
    },
    async getData() {
      this.loading=true;
      this.showLoadingFlashMessage('Searching...', 'info');
      try{
        if (!this.start){
          this.start="all";
        }
        if (!this.end){
          this.end="all";
        }
        if (!this.department){
          this.department="all";
        }
        if (!this.compliance_status){
          this.compliance_status="all";
        }
        const res = await fetch('/api/inspection-records/' + this.start + '/' + this.end + '/' + this.department + '/' + this.compliance_status)
        if (this.department=="all"){
          this.department='';
        }
        if (this.compliance_status=="all"){
          this.department='';
        }
        if (!res.ok){
          const errorData = await res.json();
          throw new Error(errorData.message);
        }
        const observations_ = await res.json()
        this.observations = observations_
        this.loading=false;
        this.showLoadingFlashMessage('', '');
        this.showFlashMessage('Search Succesful','success');
      }catch(error){
        this.showFlashMessage(error,'error');
      }
    },
    async updateData(id, compliance_status){
      if (this.active_observationID!=id && this.to_upload_photos.length != 0){
        this.showFlashMessage('Photos uploaded and Save Button clicked for different Observations','error');
        return;
      }
      this.showFlashMessage('Updating Record..','info');
      const formData = new FormData();
      formData.append("id",id);
      formData.append("compliance_status",compliance_status);
      if (this.to_upload_photos.length != 0){
        this.to_upload_photos.forEach((file, index) => {
          formData.append(`file${index}`, file); // Append each file to the form data
        });
      }
      try{
          const response = await fetch('/api/update/inspection-records', {
            method: 'PUT',
            body: formData
          })

          if (!response.ok){
            throw new Error('Failed to upload files');
          }
          const result = await response.json();
          console.log('Update Successful: ', result);
          this.to_upload_photos = [];
          this.showFlashMessage('Update Successful. Hit Refresh.','success');
      }catch(error){
          console.log("Error Updating: ", error);
          this.to_upload_photos = [];
          this.showFlashMessage('Update Failed','error');
      }
    },
    selectImage(observationID){
      this.to_upload_photos = [];
      this.active_observationID = observationID; //to make sure that button for photo upload and button for Save are clicked for the same observation
      const input = document.createElement('input');
      input.type = 'file';
      input.accept = 'image/*';
      input.multiple = true;
      input.onchange = event => {
        const selectedFiles = Array.from(event.target.files);
        if (selectedFiles.length > 2) {
          this.showFlashMessage('You can upload a maximum of 2 files.', 'error'); // Show error message
          return; // Prevent further action if more than 2 files are selected
        }
        this.showFlashMessage('Uploading photos...', 'info'); // Show upload message
        this.to_upload_photos = selectedFiles; // Convert file list to an array
      };
      input.click();
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
    showLoadingFlashMessage(message, type) {
      if (this.loading==true){
        this.flashMessage = message;
        this.flashMessageType = type;
      }else{
        this.flashMessage = '';
        this.flashMessageType = '';
      }
    },
    async createReport(){
      if (this.observations.length<=0){
        this.showFlashMessage('No observations found', 'error');
      }
      if (this.loading==true){
        this.showFlashMessage('Please Wait, a download is already in progress', 'error');
        return;
      }
      this.loading=true;
      this.showLoadingFlashMessage('Please wait, your report download should start in a few seconds', 'info');
      try{
        const response = await fetch('/api/create-word-report', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(this.observations),
        })
        if (!response.ok) {
          throw new Error('Network response was not ok ' + response.statusText);
        }
        // Get the blob from the response
        const blob = await response.blob();

        // Create a link element, set the href to the blob URL, and click it to start the download
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'report.docx'; // Name of the file
        document.body.appendChild(a);
        a.click();

        // Clean up by removing the link element and revoking the object URL
        a.remove();
        window.URL.revokeObjectURL(url);
        this.loading=false;
        this.showLoadingFlashMessage('', '');
        this.showFlashMessage('Report downloaded successfully', 'success');
      }catch (error){
        this.showFlashMessage(`Error sending data: ${error.message}`, 'error');
      }
    },
    async createPresentation(){
      if (this.observations.length<=0){
        this.showFlashMessage('No observations found', 'error');
      }
      if (this.loading==true){
        this.showFlashMessage('Please Wait, a download is already in progress', 'error');
        return;
      }
      this.loading=true;
      this.showLoadingFlashMessage('Please wait, your presetnation download should start in a few seconds', 'info');
      try{
        const response = await fetch('/api/create-ppt-report', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(this.observations),
        })
        if (!response.ok) {
          throw new Error('Network response was not ok ' + response.statusText);
        }
        // Get the blob from the response
        const blob = await response.blob();

        // Create a link element, set the href to the blob URL, and click it to start the download
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'Presentation.pptx'; // Name of the file
        document.body.appendChild(a);
        a.click();

        // Clean up by removing the link element and revoking the object URL
        a.remove();
        window.URL.revokeObjectURL(url);
        this.loading=false;
        this.showLoadingFlashMessage('', '');
        this.showFlashMessage('Presentation downloaded successfully', 'success');
      }catch (error){
        this.showFlashMessage(`Error sending data: ${error.message}`, 'error');
      }
    },
    async createSummary(){
      arr = []
      unique_obs = []
      let i=1
      this.observations.forEach(observation => {
        if (observation.inspection_category!="General" && observation.inspection_category!="Safety Monitoring" && !arr.includes(observation.date+observation.inspection_category+observation.department)){
          arr.push(observation.date+observation.inspection_category+observation.department)
          unique_obs.push({sl_no: i,
                            date: observation.date,
                            category: observation.inspection_category,
                            department: observation.department
                          })
          i+=1;
        }
      })
      filename='Summary '+this.start+' to '+this.end+'.xlsx';
      var ws = XLSX.utils.json_to_sheet(unique_obs);
      var wb = XLSX.utils.book_new();
      ws['A1'].v='Sl. No.'
      ws['B1'].v='Date'
      ws['C1'].v='Inspection Category'
      ws['D1'].v='Department'
      var wscols = [
        {wch:8},
        {wch:14},
        {wch:28},
        {wch:16}
      ];
      ws['!cols'] = wscols;
      XLSX.utils.book_append_sheet(wb, ws, "Summary");
      XLSX.writeFile(wb,filename);
      arr = []
      unique_obs = []
    }
  },
  computed: {
    no_of_violators: function(){
    }
  },
  mounted() {
    this.getAllData()
  },
  delimiters : ['[[', ']]']
})