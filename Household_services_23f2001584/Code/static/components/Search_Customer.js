export default {
    template: `
      <div>
        <h2>Search Services</h2>
        <form @submit.prevent="searchServices">
          <div>
            <label for="name">Service Name:</label>
            <input type="text" v-model="name" id="name">
          </div>
          <button type="submit">Search</button>
        </form>
        <div v-if="services.length">
          <h3>Search Results</h3>
          <ul>
            <li v-for="service in services" :key="service.service_id">
              <h4>{{ service.name }}</h4>
              <p>{{ service.description }}</p>
            </li>
          </ul>
        </div>
      </div>
    `,
    data() {
      return {
        name: '',
        services: []
      };
    },
    methods: {
      async searchServices() {
        const token = localStorage.getItem('access_token');
        if (!token) {
          this.$router.push('/login');
          return;
        }
  
        try {
          const response = await axios.get('/customer/search_services', {
            headers: {
              Authorization: `Bearer ${token}`
            },
            params: {
              name: this.name
            }
          });
          this.services = response.data;
        } catch (error) {
          console.error('Error searching for services:', error);
          if (error.response && error.response.status === 403) {
            this.$router.push('/login');
          } else if (error.response && error.response.status === 500) {
            console.error('Internal Server Error:', error.response.data);
          }
        }
      }
    }
  };