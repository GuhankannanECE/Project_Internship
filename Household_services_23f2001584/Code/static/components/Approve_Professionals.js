export default {
  template: `
    <div>
      <h2>Approve Professionals</h2>
      <table class="table">
        <thead>
          <tr>
            <th>Professional ID</th>
            <th>Username</th>
            <th>Email</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="professional in professionals" :key="professional.professional_id">
            <td>{{ professional.professional_id }}</td>
            <td>{{ professional.user.user_name }}</td>
            <td>{{ professional.user.email_id }}</td>
            <td>
              <button class="btn btn-success" @click="approveProfessional(professional.professional_id)">Approve</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  `,
  data() {
    return {
      professionals: [],
      errorMessage: '',
    };
  },
  created() {
    this.fetchProfessionals();
  },
  methods: {
    fetchProfessionals() {
      const token = localStorage.getItem('access_token');
      if (!token) {
        this.errorMessage = 'Unauthorized! Please log in.';
        return;
      }

      axios
        .get('/admin/approve_professionals', {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        })
        .then((response) => {
          this.professionals = response.data;
          console.log(this.professionals); // Log the response to check structure
        })
        .catch((error) => {
          console.error('There was an error fetching the professionals!', error);
          if (error.response && error.response.status === 401) {
            this.errorMessage = 'Unauthorized! Please log in.';
          } else {
            this.errorMessage = 'An error occurred while fetching professionals.';
          }
        });
    },
    approveProfessional(professionalId) {
      const token = localStorage.getItem('access_token');
      if (!token) {
        this.errorMessage = 'Unauthorized! Please log in.';
        return;
      }

      axios
        .post(
          '/admin/approve_professionals',
          { professional_id: professionalId },
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        )
        .then(() => {
          this.professionals = this.professionals.filter(
            (pro) => pro.professional_id !== professionalId
          );
          console.log(`Professional with ID ${professionalId} approved successfully!`);
        })
        .catch((error) => {
          console.error('There was an error approving the professional!', error);
          this.errorMessage = 'An error occurred while approving the professional.';
        });
    },
  },
  name: 'ApproveProfessionals',
};