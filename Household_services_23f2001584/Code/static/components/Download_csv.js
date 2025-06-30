export default {
  template: `
    <div>
      <button @click="downloadResource">Download Service Request Statistics</button>
      <p v-if="errorMessage" style="color: red;">{{ errorMessage }}</p>
      <p v-if="statusMessage">{{ statusMessage }}</p>
    </div>
  `,
  data() {
    return {
      errorMessage: null,
      statusMessage: null,
      taskId: null,
      intervalId: null
    };
  },
  methods: {
    async downloadResource() {
      this.errorMessage = null;
      this.statusMessage = "Requesting CSV generation...";

      try {
        const res = await fetch('http://127.0.0.1:5000/download-csv');
        const data = await res.json();

        if (res.ok) {
          this.taskId = data['task-id'];
          console.log()
          this.statusMessage = "CSV generation initiated. Checking status...";
          this.checkCsvStatus();
        } else {
          this.errorMessage = data.msg || "Failed to initiate CSV download.";
        }
      } catch (error) {
        console.error('Error during CSV download:', error);
        this.errorMessage = 'An unexpected error occurred while downloading the CSV.';
      }
    },
    async checkCsvStatus() {
      this.intervalId = setInterval(async () => {
        const taskId = this.taskId;
        console.log(taskId);
        if (!taskId) {
          this.errorMessage = 'Task ID is missing.';
          clearInterval(this.intervalId);
          return;
        }

        try {
          const csv_res = await fetch(`http://127.0.0.1:5000/get-csv/${taskId}`);

          if (csv_res.ok) {
              clearInterval(this.intervalId);
              window.location.href = `http://127.0.0.1:5000/get-csv/${taskId}`;
              this.statusMessage = "CSV file is ready for download."; 
          } else {
            clearInterval(this.intervalId);
            this.errorMessage = "Failed to fetch CSV.";
          }
        } catch (error) {
          clearInterval(this.intervalId);
          this.errorMessage = "Error fetching CSV.";
          console.error('Error fetching CSV:', error);
        }
      }, 1000); // Check every second
    }
  },
  beforeDestroy() {
    if (this.intervalId) {
      clearInterval(this.intervalId);
    }
  }
};