export default {
    template: `
      <div>
        <h1>Professional Dashboard</h1>
        <nav>
          <ul>
            <li><router-link to="/professional/view_services">View Services</router-link></li>
            <li><router-link to="/professional/service_requests">Service Requests</router-link></li>
            <li><router-link to="/professional/service_requests/update_status">Update Service Requests </router-link></li>
          </ul>
        </nav>
        <router-view></router-view>
      </div>
    `
  };