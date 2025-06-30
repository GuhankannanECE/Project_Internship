export default {
    template: `
      <div>
        <h1>Admin Dashboard</h1>
        <p v-if="errorMessage" style="color: red;">{{ errorMessage }}</p>
        <table v-if="users.length">
          <thead>
            <tr>
              <th>User ID</th>
              <th>Username</th>
              <th>Role</th>
              <th>Blocked</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="user in users" :key="user.user_id">
              <td>{{ user.user_id }}</td>
              <td>{{ user.user_name }}</td>
              <td>{{ user.role }}</td>
              <td>{{ user.is_blocked ? 'Yes' : 'No' }}</td>
            </tr>
          </tbody>
        </table>
        <p v-else>No users found.</p>
      </div>
    `,
    data() {
      return {
        users: [],
        errorMessage: null,
      };
    },
    created() {
      this.fetchUsers();
    },
    methods: {
      async fetchUsers() {
        try {
          const token = localStorage.getItem('access_token');
          const response = await fetch('/admin/view_users', {
            method: 'GET',
            headers: {
              'Authorization': `Bearer ${token}`
            },
          });
  
          if (response.ok) {
            const data = await response.json();
            this.users = data;
            console.log("hi");
          } else {
            const errorData = await response.json();
            this.errorMessage = errorData.msg || 'Failed to fetch users!';
          }
        } catch (error) {
          console.error('Error during fetching users:', error);
          this.errorMessage = 'An error occurred while fetching the users.';
        }
      },
    },
  };