const parent = new Vue({
  el: '#app',
  data: {
        start: '',
        end: '',
        department: '',
        category: '',
        observations: [],
        flashMessage: '',
        flashMessageType: '',
        loading:false,
        all_departments: ["ACVS","BF","CED","CO&CC","CR(E)","CR(M)","CRM","CRM-3","DNW","EL&TC","EMD","ERS","ETL","FORGE SHOP",
          "GM(E)","GM(M)","GU","HM(E)","HM(M)","HRCF","HSM","I&A","ICF","IMF","M/C SHOP","OG&CBRS","PEB","PFRS","PROJECTS","R&R",
          "RCL","RED","RGBS","RMHP","RMP","SF & PS","SGP", "SMS-1","SMS-2&CCS","SP","MRD","STORES","STRL SHOP","TBS","TRAFFIC","WMD"],
        all_categories: ["DLSIC","SAC","SAW", "Contractor Safety Committee"]
  },
  methods: {
    async getAllData(){
      const res = await fetch('/api/meeting-records')
      const observations_ = await res.json()
      this.observations = observations_
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
        if (!this.category){
          this.category="all";
        }
        if (!this.department){
          this.department="all";
        }
        const res = await fetch('/api/meeting-records/' + this.start + '/' + this.end + '/' + this.category + '/' + this.department)
        if (this.department=="all"){
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
        async createSummary(){
      arr = []
      unique_obs = []
      let i=1
      this.observations.forEach(observation => {
        if (observation.meeting_category!="SAW" && !arr.includes(observation.date+observation.meeting_category+observation.department)){
          arr.push(observation.date+observation.meeting_category+observation.department)
          unique_obs.push({sl_no: i,
                            date: observation.date,
                            category: observation.meeting_category,
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
      ws['C1'].v='Meeting Category'
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
  mounted() {
    this.getAllData()
  },
  delimiters : ['[[', ']]']
})