export default {
  template: `
    <div>
      <h2>Manage Users</h2>
      <table class="table">
        <thead>
          <tr>
            <th>Name</th>
            <th>Username</th> 
            <th>Email</th>
            <th>Role</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in users" :key="user.user_id">
            <td>{{ user.name }}</td>
            <td>{{ user.user_name }}</td>
            <td>{{ user.email_id }}</td>
            <td>{{ user.role }}</td>
            <td>
              <button class="btn btn-danger" v-if="!user.is_blocked" @click="blockUser(user.user_id)">Block</button>
              <span v-else>Blocked</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  `,
  data() {
    return {
      users: [],
    };
  },
  computed: {
    filteredUsers() {
      return this.users.filter(user => !user.is_blocked && user.role !== 'admin');
    }
  },
  created() {
    this.fetchUsers();
  },
  methods: {
    fetchUsers() {
      const token = localStorage.getItem('access_token');
      if (!token) {
        this.errorMessage = 'Unauthorized! Please log in.';
        return;
      }

      axios
        .get('/admin/users', {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        })
        .then((response) => {
          this.users = response.data;
          console.log(this.users);
        })
        .catch((error) => {
          console.error('There was an error fetching the users!', error);
          if (error.response && error.response.status === 401) {
            this.errorMessage = 'Unauthorized! Please log in.';
          } else {
            this.errorMessage = 'An error occurred while fetching users.';
          }
        });
    },
    blockUser(userId) {
      const token = localStorage.getItem('access_token');
      if (!token) {
        this.errorMessage = 'Unauthorized! Please log in.';
        return;
      }

      axios
        .post(
          '/admin/block_users',
          { user_id: userId },
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        )
        .then(() => {
          this.users = this.users.map((user) =>
            user.user_id === userId ? { ...user, is_blocked: true } : user
          );
        })
        .catch((error) => {
          console.error('There was an error blocking the user!', error);
          this.errorMessage = 'An error occurred while blocking the user.';
        });
    },
  },
  name: 'ManageUsers',
};