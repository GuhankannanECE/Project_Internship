export default {
    template: `
      <div>
        <h2>Search Professionals</h2>
        <form @submit.prevent="searchProfessionals">
          <div>
            <label for="name">Professional Name:</label>
            <input type="text" v-model="name" id="name">
          </div>
          <button type="submit">Search</button>
        </form>
        <div v-if="professionals.length">
          <h3>Search Results</h3>
          <ul>
            <li v-for="professional in professionals" :key="professional.professional_id">
              <h4>{{ professional.name }}</h4>
              <p>Status: <span :style="{color: professional.is_blocked ? 'red' : 'green'}">{{ professional.is_blocked ? 'Blocked' : 'Active' }}</span></p>
              <button @click="redirectToManageUsers">Block</button>
            </li>
          </ul>
        </div>
      </div>
    `,
    data() {
      return {
        name: '',
        professionals: []
      };
    },
    methods: {
      async searchProfessionals() {
        const token = localStorage.getItem('access_token');
        if (!token) {
          this.$router.push('/login');
          return;
        }
  
        try {
          const response = await axios.get('/admin/search_professionals', {
            headers: {
              Authorization: `Bearer ${token}`
            },
            params: {
              name: this.name
            }
          });
          this.professionals = response.data;
        } catch (error) {
          console.error('Error searching for professionals:', error);
          if (error.response && error.response.status === 403) {
            this.$router.push('/login');
          } else if (error.response && error.response.status === 500) {
            console.error('Internal Server Error:', error.response.data);
          }
        }
      },
      redirectToManageUsers() {
        this.$router.push('/admin/users');
      }
    }
  };