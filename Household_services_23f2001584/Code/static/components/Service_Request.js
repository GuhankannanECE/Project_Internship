export default {
    template: `
      <div class="service-requests">
        <h2>Service Requests</h2>
        <table v-if="serviceRequests.length > 0">
          <thead>
            <tr>
              <th>Service Request ID</th>
              <th>Service Name</th>
              <th>Customer Name</th>
              <th>Request Date</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="request in serviceRequests" :key="request.servicerequest_id">
              <td>{{ request.servicerequest_id }}</td>
              <td>{{ request.service_name }}</td>
              <td>{{ request.customer_name }}</td>
              <td>{{ request.request_date }}</td>
              <td>{{ request.status }}</td>
            </tr>
          </tbody>
        </table>
        <p v-else>No service requests found.</p>
      </div>
    `,
    
    data() {
      return {
        serviceRequests: []
      };
    },
  
    created() {
      this.fetchServiceRequests();
    },
  
    methods: {
      async fetchServiceRequests() {
        const token = localStorage.getItem('access_token');
        
        if (!token) {
          this.$router.push('/login');
          return;
        }
  
        try {
          const response = await axios.get('/professional/service_requests', {
            headers: {
              Authorization: `Bearer ${token}`
            }
          });
          
          this.serviceRequests = response.data;
        } catch (error) {
          console.error('Error fetching service requests:', error);
          if (error.response?.status === 401) {
            this.$router.push('/login');
          }
        }
      }
    }
  };