export default {
    template: `
      <div>
        <h2>Service Requests</h2>
        <div v-if="error" class="error-message">
          {{ error }}
        </div>
        <table>
          <thead>
            <tr>
              <th>Service Request ID</th>
              <th>Service Name</th>
              <th>Customer Name</th>
              <th>Request Date</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="request in serviceRequests" :key="request.servicerequest_id">
              <td>{{ request.servicerequest_id }}</td>
              <td>{{ request.service_name }}</td>
              <td>{{ request.customer_name }}</td>
              <td>{{ request.request_date }}</td>
              <td>{{ request.status }}</td>
              <td>
                <button 
                  @click="updateRequestStatus(request.servicerequest_id, 'accept')"
                  :disabled="request.status !== 'Pending' || isLoading"
                >
                  {{ isLoading ? 'Processing...' : 'Accept' }}
                </button>
                <button 
                  @click="updateRequestStatus(request.servicerequest_id, 'reject')"
                  :disabled="request.status !== 'Pending' || isLoading"
                >
                  {{ isLoading ? 'Processing...' : 'Reject' }}
                </button>
                <button 
                  @click="updateRequestStatus(request.servicerequest_id, 'close')"
                  :disabled="request.status === 'Closed' || isLoading"
                >
                  {{ isLoading ? 'Processing...' : 'Close' }}
                </button>
              </td>
            </tr>
          </tbody>
        </table>
        <p v-if="serviceRequests.length === 0">No service requests found.</p>
      </div>
    `,
  
    data() {
      return {
        serviceRequests: [],
        error: null,
        isLoading: false
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
          console.log(this.serviceRequests);
          this.error = null;
        } catch (error) {
          console.error('Error fetching service requests:', error);
          this.handleError(error, 'Failed to load service requests.');
        }
      },
  
      async updateRequestStatus(servicerequest_id, action) {
        console.log(`Button clicked for ${action}ing request ID: ${servicerequest_id}`); // Log button click
        this.isLoading = true;
        this.error = null;
        const token = localStorage.getItem('access_token');
        console.log('Access token:', token); // Log access token
  
        axios.post('/professional/service_requests/update_status', {
          servicerequest_id,
          action
        }, {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        })
        .then(response => {
          console.log('Response:', response.data); // Log the response
  
          // Show success message
          this.error = `Successfully ${action}ed the request.`;
          setTimeout(() => {
            this.error = null;
          }, 3000);
  
          // Refresh the list
          return this.fetchServiceRequests();
        })
        .catch(error => {
          console.error(`Error ${action}ing service request:`, error);
          if (error.response) {
            console.log('Error response data:', error.response.data); // Log error response data
            console.log('Error response status:', error.response.status); // Log error response status
            console.log('Error response headers:', error.response.headers); // Log error response headers
          }
          this.handleError(error, `Failed to ${action} request.`);
        })
        .finally(() => {
          this.isLoading = false;
        });
      },
  
      handleError(error, defaultMessage) {
        if (error.response) {
          // Server responded with an error
          console.log('Error response data:', error.response.data); // Log error response data
          if (error.response.status === 401) {
            this.$router.push('/login');
          } else if (error.response.data && error.response.data.msg) {
            this.error = error.response.data.msg;
          } else {
            this.error = defaultMessage;
          }
        } else if (error.request) {
          // Request was made but no response received
          this.error = 'No response from server. Please try again.';
        } else {
          // Something else went wrong
          this.error = defaultMessage;
        }
      }
    }
  };
  