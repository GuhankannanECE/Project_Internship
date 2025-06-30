export default {
  template: `
    <div>
      <h2>Register</h2>
      <label for="name">Name:</label>
      <input type="text" id="name" v-model="name" required>
      <br><br>
      <label for="username">Username:</label>
      <input type="text" id="username" v-model="username" required>
      <br><br>
      <label for="email">Email:</label>
      <input type="email" id="email" v-model="email" required>
      <br><br>
      <label for="password">Password:</label>
      <input type="password" id="password" v-model="password" required>
      <br><br>
      <label for="role">Role:</label>
      <select id="role" v-model="role" required>
        <option value="customer">Customer</option>
        <option value="professional">Professional</option>
      </select>
      <br><br>
      <button @click="register">Register</button>
      <p v-if="errorMessage" style="color: red;">{{ errorMessage }}</p>
      <p v-if="successMessage" style="color: green;">{{ successMessage }}</p>
    </div>
  `,
  data() {
    return {
      name: '',
      username: '',
      email: '',
      password: '',
      role: 'customer', // Default role
      errorMessage: null,
      successMessage: null,
    };
  },
  methods: {
    async register() {
        this.errorMessage = null;
        this.successMessage = null;
    
        const registrationData = {
            user_name: this.username,
            password: this.password,
            email_id: this.email,
            name: this.name,
            role: this.role,
        };
    
        try {
            const response = await fetch('http://127.0.0.1:5000/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(registrationData),
            });
    
            if (response.ok) {
                const data = await response.json();
                this.successMessage = data.msg || "Registration successful!";
            } else {
                const errorData = await response.json();
                this.errorMessage = errorData.msg || "Registration failed!";
            }
        } catch (error) {
            console.error('Error during registration:', error);
    
            // Check if it's a network error or other unhandled issues
            if (error.name === 'TypeError' && error.message.includes('Failed to fetch')) {
                this.errorMessage = 'Cannot connect to the server. Please try again later.';
            } else {
                this.errorMessage = 'An unexpected error occurred while registering.';
            }
        }
    }
    
  },
};
