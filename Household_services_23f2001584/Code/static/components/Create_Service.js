export default {
    template: `
      <div>
        <h2>Create New Service</h2>
        <label for="name">Name:</label>
        <input type="text" id="name" v-model="name" required>
        <br><br>
        <label for="price">Base Price:</label>
        <input type="number" id="price" v-model="price" required>
        <br><br>
        <label for="location">Location:</label>
        <input type="text" id="location" v-model="location" required>
        <br><br>
        <label for="description">Description:</label>
        <textarea id="description" v-model="description" required></textarea>
        <br><br>
        <button @click="createService">Create Service</button>
        <p v-if="errorMessage" style="color: red;">{{ errorMessage }}</p>
        <p v-if="successMessage" style="color: green;">{{ successMessage }}</p>
      </div>
    `,
    data() {
      return {
        name: '',
        price: 0,
        location: '',
        description: '',
        errorMessage: null,
        successMessage: null,
      };
    },
    methods: {
      async createService() {
        this.errorMessage = null;
        this.successMessage = null;
  
        const serviceData = {
          name: this.name,
          price: this.price,
          location: this.location,
          description: this.description,
        };
  
        try {
          const response = await fetch('http://127.0.0.1:5000/admin/create_service', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
            },
            body: JSON.stringify(serviceData),
          });
  
          if (response.ok) {
            const data = await response.json();
            this.successMessage = data.msg || "Service created successfully!";
            this.name = '';
            this.price = 0;
            this.location = '';
            this.description = '';
          } else {
            const errorData = await response.json();
            this.errorMessage = errorData.msg || "Service creation failed!";
          }
        } catch (error) {
          console.error('Error creating service:', error);
  
          // Check if it's a network error or other unhandled issues
          if (error.name === 'TypeError' && error.message.includes('Failed to fetch')) {
            this.errorMessage = 'Cannot connect to the server. Please try again later.';
          } else {
            this.errorMessage = 'An unexpected error occurred while creating the service.';
          }
        }
      }
    }
  };