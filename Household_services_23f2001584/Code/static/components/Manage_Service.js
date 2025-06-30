export default {
  template: `
    <div>
      <h2>Manage Services</h2>
      <table class="table">
        <thead>
          <tr>
            <th>Name</th>
            <th>Price</th>
            <th>Location</th>
            <th>Description</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="service in services" :key="service.service_id">
            <td><input v-model="service.name" /></td>
            <td><input type="number" v-model="service.price" /></td>
            <td><input v-model="service.location" /></td>
            <td><input v-model="service.description" /></td>
            <td>
              <button class="btn btn-primary" @click="updateService(service)">Update</button>
              <button class="btn btn-danger" @click="deleteService(service.service_id)">Delete</button>
            </td>
          </tr>
        </tbody>
      </table>
      <p v-if="errorMessage" style="color: red;">{{ errorMessage }}</p>
      <p v-if="successMessage" style="color: green;">{{ successMessage }}</p>
    </div>
  `,
  data() {
    return {
      services: [],
      errorMessage: null,
      successMessage: null,
    };
  },
  created() {
    this.fetchServices();
  },
  methods: {
    fetchServices() {
      const token = localStorage.getItem('access_token');
      if (!token) {
        this.errorMessage = 'Unauthorized! Please log in.';
        return;
      }

      axios
        .get('/admin/manage_services', {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        })
        .then((response) => {
          this.services = response.data;
        })
        .catch((error) => {
          console.error('There was an error fetching the services!', error);
          if (error.response && error.response.status === 401) {
            this.errorMessage = 'Unauthorized! Please log in.';
          } else {
            this.errorMessage = 'An error occurred while fetching services.';
          }
        });
    },
    updateService(service) {
      const token = localStorage.getItem('access_token');
      if (!token) {
        this.errorMessage = 'Unauthorized! Please log in.';
        return;
      }

      axios
        .put(
          '/admin/manage_services',
          {
            service_id: service.service_id,
            name: service.name,
            price: service.price,
            location: service.location,
            description: service.description,
          },
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        )
        .then(() => {
          this.successMessage = 'Service updated successfully!';
        })
        .catch((error) => {
          console.error('There was an error updating the service!', error);
          this.errorMessage = 'An error occurred while updating the service.';
        });
    },
    deleteService(serviceId) {
      const token = localStorage.getItem('access_token');
      if (!token) {
        this.errorMessage = 'Unauthorized! Please log in.';
        return;
      }

      axios
        .delete('/admin/manage_services', {
          headers: {
            Authorization: `Bearer ${token}`,
          },
          data: { service_id: serviceId },
        })
        .then(() => {
          this.services = this.services.filter(service => service.service_id !== serviceId);
          this.successMessage = 'Service deleted successfully!';
        })
        .catch((error) => {
          console.error('There was an error deleting the service!', error);
          this.errorMessage = 'An error occurred while deleting the service.';
        });
    },
  },
  name: 'ManageServices',
};