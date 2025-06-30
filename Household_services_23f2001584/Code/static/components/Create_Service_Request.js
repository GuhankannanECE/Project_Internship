export default {
    template: `
      <div>
        <h2>Create Service Request</h2>
        <label for="service">Service ID:</label>
        <input type="text" v-model="service_id" required>
        <br><br>
        <label for="professional">Professional ID:</label>
        <input type="text" v-model="professional_id" required>
        <br><br>
        <label for="request_date">Request Date:</label>
        <input type="date" v-model="request_date" required>
        <br><br>
        <button @click="createServiceRequest">Submit</button>
        <p v-if="errorMessage" style="color: red;">{{ errorMessage }}</p>
        <p v-if="successMessage" style="color: green;">{{ successMessage }}</p>
      </div>
    `,
    data() {
      return {
        service_id: '',
        professional_id: '',
        request_date: '',
        errorMessage: null,
        successMessage: null,
      };
    },
    methods: {
      async createServiceRequest() {
        const token = localStorage.getItem('access_token');
        const requestData = {
          service_id: this.service_id,
          professional_id: this.professional_id,
          request_date: this.request_date,
        };
        try {
          const response = await fetch('/customer/create_service_request', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(requestData),
          });
          if (response.ok) {
            const data = await response.json();
            this.successMessage = data.msg || 'Service request created successfully!';
            this.service_id = '';
            this.professional_id = '';
            this.request_date = '';
          } else {
            const errorData = await response.json();
            this.errorMessage = errorData.msg || 'Failed to create service request. Server responded with an error.';
          }
        } catch (error) {
          console.error('Error creating service request:', error);
          this.errorMessage = 'An error occurred while creating the service request.';
        }
      },
    },
  };