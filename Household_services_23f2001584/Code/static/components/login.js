export default {
  template: `
    <div>
      <label for="user_name">Username:</label>
      <input type="text" id="user_name" v-model="user_name" name="user_name" required>
      <br><br>
      <label for="password">Password:</label>
      <input type="password" id="password" v-model="password" name="password" required>
      <br><br>
      <button @click="login">Login</button>
      <p v-if="errorMessage" style="color: red;">{{ errorMessage }}</p>
    </div>
  `,
  data() {
    return {
      user_name: '',
      password: '',
      errorMessage: null,
    };
  },
  methods: {
    async login() {
      this.errorMessage = null; // Clear previous error messages

      const credentials = {
        user_name: this.user_name,
        password: this.password,
      };

      try {
        const response = await fetch('/login', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(credentials),
        });

        if (response.ok) {
          const data = await response.json();
          localStorage.setItem('access_token', data.access_token);
          console.log(localStorage.getItem('access_token'));
          alert('Login successful!');

          // Decode JWT to get user role
          const token = data.access_token;
          const payload = JSON.parse(atob(token.split('.')[1]));
          const role = payload.sub.role;

          // Debug log for role verification
          console.log(payload);
          console.log("User role:", role);

          // Redirect based on user role
          if (role === 'admin') {
            this.$router.push('/admin/dashboard');
          } else if (role === 'customer') {
            this.$router.push('/customer/dashboard');
          } else if (role === 'professional') {
            this.$router.push('/professional/dashboard');
          } else {
            this.errorMessage = 'Unknown user role!';
          }
        } else {
          const errorData = await response.json();
          this.errorMessage = errorData.msg || 'Login failed! Please try again.';
        }
      } catch (error) {
        console.error('Error during login:', error);
        this.errorMessage = 'An error occurred while logging in.';
      }
    },
  },
};