// static/Dashboard.js
export default {
    template: `
      <div>
        <h1>Admin Dashboard</h1>
        <nav>
          <ul>
            <li><router-link to="/admin/view_users">View Users</router-link></li>
            <li><router-link to="/admin/users">Manage Users</router-link></li>
            <li><router-link to="/admin/approve-professionals">Approve Professionals</router-link></li>
            <li><router-link to="/admin/create_service">Create Service</router-link></li>
            <li><router-link to="/admin/manage_services">Manage Service</router-link></li>
            <li><router-link to="/admin/search_professionals">Search Professionals</router-link></li>
            <li><router-link to="/download-csv">Download CSV</router-link></li>
          </ul>
        </nav>
        <router-view></router-view>
      </div>
    `
  };