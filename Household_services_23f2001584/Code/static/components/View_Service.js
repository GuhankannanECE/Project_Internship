export default {
    template: `
      <div class="container mt-4">
        <h2 class="mb-4">View Services</h2>
        <div v-if="isLoading" class="text-center">
          <div class="spinner-border" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
        </div>
        <div v-else>
          <table class="table table-striped">
            <thead>
              <tr>
                <th>Service ID</th>
                <th>Service Name</th>
                <th>Description</th>
                <th>Price</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="service in services" :key="service.service_id">
                <td>{{ service.service_id }}</td>
                <td>{{ service.name }}</td>
                <td>{{ service.description }}</td>
                <td>{{ service.price }}</td>
              </tr>
              <tr v-if="services.length === 0">
                <td colspan="4" class="text-center">No services found</td>
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
        services: [],
        errorMessage: null,
        successMessage: null,
        isLoading: false,
      };
    },
  
    created() {
      this.fetchServices();
    },
  
    methods: {
      setMessage(message, type) {
        if (type === 'success') {
          this.successMessage = message;
          setTimeout(() => this.successMessage = null, 3000);
        } else {
          this.errorMessage = message;
          setTimeout(() => this.errorMessage = null, 3000);
        }
      },
  
      async fetchServices() {
        const token = localStorage.getItem('access_token');
        if (!token) {
          this.setMessage('Unauthorized! Please log in.', 'error');
          return;
        }
  
        this.isLoading = true;
        try {
          const response = await axios.get('/customer/view_services', {
            headers: { Authorization: `Bearer ${token}` }
          });
          this.services = response.data;
        } catch (error) {
          console.error('Error fetching services:', error);
          const message = error.response?.status === 401 
            ? 'Unauthorized! Please log in.'
            : 'Failed to fetch services.';
          this.setMessage(message, 'error');
        } finally {
          this.isLoading = false;
        }
      },
    },
  
    name: 'ViewServices',
  };