export default {
  template: `
    <div class="container mt-4">
      <h2 class="mb-4">View Professionals</h2>
      <div v-if="isLoading" class="text-center">
        <div class="spinner-border" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
      </div>
      <div v-else>
        <table class="table table-striped">
          <thead>
            <tr>
              <th>Professional ID</th>
              <th>Approved</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="professional in professionals" :key="professional.professional_id">
              <td>{{ professional.professional_id }}</td>
              <td>{{ professional.approved ? 'Yes' : 'No' }}</td>
            </tr>
            <tr v-if="professionals.length === 0">
              <td colspan="2" class="text-center">No professionals found</td>
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
      professionals: [],
      errorMessage: null,
      successMessage: null,
      isLoading: false,
    };
  },

  created() {
    this.fetchProfessionals();
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

    async fetchProfessionals() {
      const token = localStorage.getItem('access_token');
      if (!token) {
        this.setMessage('Unauthorized! Please log in.', 'error');
        return;
      }

      this.isLoading = true;
      try {
        const response = await axios.get('/customer/view_professionals', {
          headers: { Authorization: `Bearer ${token}` }
        });
        this.professionals = response.data;
        this.setMessage('Professionals fetched successfully.', 'success');
      } catch (error) {
        console.error('Error fetching professionals:', error);
        const message = error.response?.status === 401 
          ? 'Unauthorized! Please log in.'
          : 'Failed to fetch professionals.';
        this.setMessage(message, 'error');
      } finally {
        this.isLoading = false;
      }
    },
  },

  name: 'ViewProfessionals',
};