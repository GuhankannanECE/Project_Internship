export default {
  template: `
    <div class="container mt-4">
      <h2 class="mb-4">Manage Service Requests</h2>
      <div v-if="isLoading" class="text-center">
        <div class="spinner-border" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
      </div>
      <div v-else>
        <table class="table table-striped">
          <thead>
            <tr>
              <th>Service</th>
              <th>Professional</th>
              <th>Request Date</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="request in serviceRequests" :key="request.request_id">
              <td>
                <span v-if="editingRequestId !== request.servicerequest_id">{{ request.service_name || request.service_id }}</span>
                <input v-else type="text" v-model="editRequest.service_name" class="form-control">
              </td>
              <td>
                <span v-if="editingRequestId !== request.servicerequest_id">{{ request.professional_name || request.professional_id }}</span>
                <input v-else type="text" v-model="editRequest.professional_name" class="form-control">
              </td>
              <td>
                <span v-if="editingRequestId !== request.servicerequest_id">{{ formatDate(request.request_date) }}</span>
                <input v-else type="date" class="form-control" v-model="editRequest.request_date">
              </td>
              <td>
                <span v-if="editingRequestId !== request.servicerequest_id">{{ request.status }}</span>
                <select v-else v-model="editRequest.status" class="form-select">
                  <option value="Pending">Pending</option>
                  <option value="In Progress">In Progress</option>
                  <option value="Completed">Completed</option>
                  <option value="Cancelled">Cancelled</option>
                </select>
              </td>
              <td>
                <div v-if="editingRequestId !== request.servicerequest_id">
                  <button class="btn btn-primary btn-sm me-2" @click="startEditing(request)">
                    <i class="bi bi-pencil"></i> Edit
                  </button>
                  <button class="btn btn-danger btn-sm" @click="deleteServiceRequest(request)">
                    <i class="bi bi-trash"></i> Delete
                  </button>
                </div>
                <div v-else>
                  <button class="btn btn-success btn-sm me-2" @click="saveEdit()">
                    <i class="bi bi-check"></i> Save
                  </button>
                  <button class="btn btn-secondary btn-sm" @click="cancelEdit()">
                    <i class="bi bi-x"></i> Cancel
                  </button>
                </div>
              </td>
            </tr>
            <tr v-if="serviceRequests.length === 0">
              <td colspan="5" class="text-center">No service requests found</td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <div v-if="errorMessage" class="alert alert-danger alert-dismissible fade show mt-3" role="alert">
        {{ errorMessage }}
        <button type="button" class="btn-close" @click="errorMessage = null"></button>
      </div>
      
      <div v-if="successMessage" class="alert alert-success alert-dismissible fade show mt-3" role="alert">
        {{ successMessage }}
        <button type="button" class="btn-close" @click="successMessage = null"></button>
      </div>
    </div>
  `,
  
  data() {
    return {
      serviceRequests: [],
      errorMessage: null,
      successMessage: null,
      isLoading: false,
      editingRequestId: null,
      editRequest: {
        servicerequest_id: null,
        service_name: null,
        professional_name: null,
        request_date: null,
        status: null
      }
    };
  },

  created() {
    this.fetchServiceRequests();
  },

  methods: {
    formatDate(dateString) {
      const date = new Date(dateString);
      return date.toLocaleDateString();
    },
    
    formatDateForInput(dateString) {
      const date = new Date(dateString);
      return date.toISOString().split('T')[0]; // Format as YYYY-MM-DD for input type="date"
    },

    setMessage(message, type) {
      if (type === 'success') {
        this.successMessage = message;
        setTimeout(() => this.successMessage = null, 3000);
      } else {
        this.errorMessage = message;
        setTimeout(() => this.errorMessage = null, 3000);
      }
    },

    async fetchServiceRequests() {
      const token = localStorage.getItem('access_token');
      if (!token) {
        this.setMessage('Unauthorized! Please log in.', 'error');
        return;
      }

      this.isLoading = true;
      try {
        const response = await axios.get('/customer/manage_service_requests', {
          headers: { Authorization: `Bearer ${token}` }
        });
        this.serviceRequests = response.data;
      } catch (error) {
        console.error('Error fetching service requests:', error);
        const message = error.response?.status === 401 
          ? 'Unauthorized! Please log in.'
          : 'Failed to fetch service requests.';
        this.setMessage(message, 'error');
      } finally {
        this.isLoading = false;
      }
    },
    
    startEditing(request) {
      this.editingRequestId = request.servicerequest_id;
      this.editRequest = { 
        servicerequest_id: request.servicerequest_id,
        service_name: request.service_name || request.service_id,
        professional_name: request.professional_name || request.professional_id,
        request_date: this.formatDateForInput(request.request_date),
        status: request.status
      };
    },
    
    cancelEdit() {
      this.editingRequestId = null;
      this.editRequest = {
        servicerequest_id: null,
        service_name: null,
        professional_name: null,
        request_date: null,
        status: null
      };
    },
    
    async saveEdit() {
      const token = localStorage.getItem('access_token');
      if (!token) {
        this.setMessage('Unauthorized! Please log in.', 'error');
        return;
      }

      try {
        const response = await axios.put(
          '/customer/manage_service_requests',
          this.editRequest,
          {
            headers: {
              Authorization: `Bearer ${token}`,
              'Content-Type': 'application/json',
            },
          }
        );
        this.setMessage('Service request updated successfully!', 'success');
        this.editingRequestId = null;
        await this.fetchServiceRequests();
      } catch (error) {
        console.error('Error updating service request:', error.response?.data || error.message);
        const message =
          error.response?.status === 401
            ? 'Unauthorized! Please log in.'
            : 'Failed to update service request. ' + (error.response?.data?.msg || 'An unexpected error occurred.');
        this.setMessage(message, 'error');
      }
    },
    
    async deleteServiceRequest(request) {
      // Confirm with the user before proceeding with the deletion
      if (!confirm('Are you sure you want to delete this service request?')) {
        return;
      }
      if (!request || !request.servicerequest_id) {
        console.error('Invalid request object:', request);
        this.setMessage('Invalid request object.', 'error');
        return;
      }
    
      // Retrieve the access token from local storage
      const token = localStorage.getItem('access_token');
      if (!token) {
        // If no token is found, set an unauthorized error message and return
        this.setMessage('Unauthorized! Please log in.', 'error');
        return;
      }
    
      try {
        await axios.delete('/customer/manage_service_requests', {
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
          data: { servicerequest_id: request.servicerequest_id },
        });
        
        // Set a success message indicating the deletion was successful
        this.setMessage('Service request deleted successfully!', 'success');
        // Refresh the list after deletion
        await this.fetchServiceRequests();
      } catch (error) {
        // Log the error to the console for debugging purposes
        console.error('Error deleting service request:', error);
    
        // Set an error message indicating the deletion failed
        const message = error.response?.status === 401
          ? 'Unauthorized! Please log in.'
          : 'Failed to delete service request. ' + (error.response?.data?.msg || 'An unexpected error occurred.');
        this.setMessage(message, 'error');
      }
    }      
  },

  name: 'ManageServiceRequests'
};