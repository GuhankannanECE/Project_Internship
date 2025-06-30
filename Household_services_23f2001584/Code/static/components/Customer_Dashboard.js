export default {
    template: `
      <div>
        <h1>Customer Dashboard</h1>
        <nav>
          <ul>
            <li><router-link to="/customer/view_services">View Services</router-link></li>
            <li><router-link to="/customer/view_professionals">View professionals</router-link></li>
            <li><router-link to="/customer/create_service_request">Create Service Request</router-link></li>
            <li><router-link to="/customer/manage_service_request">Manage Service Requests</router-link></li>
            <li><router-link to="/customer/search_services">Search Services</router-link></li>
          </ul>
        </nav>
        <router-view></router-view>
      </div>
    `
  };