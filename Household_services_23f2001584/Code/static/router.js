import Home from "./components/Home.js"
import Login from "./components/login.js"
import Register from "./components/Register.js"
import Dashboard from './components/Admin_Dashboard.js'
import Customer_Dashboard from './components/Customer_Dashboard.js'
import ManageUsers from './components/Manage_Users.js'
import ApproveProfessionals from './components/Approve_Professionals.js'
import CreateService from "./components/Create_Service.js"
import CreateServiceRequest from "./components/Create_Service_Request.js"
import ManageService from "./components/Manage_Service.js"
import ManageServiceRequest from "./components/Manage_Service_Request.js"
import ProfDashboard from "./components/Professional_Dashboard.js"
import serviceRequest from "./components/Service_Request.js"
import UpdateserviceRequest from "./components/Update_Service_Request.js"
import SearchserviceCustomer from "./components/Search_Customer.js"
import SearchAdmin from "./components/Search_Admin.js"
import DownloadCsv from "./components/Download_csv.js"
import GetCsv from "./components/Download_csv.js"
import ViewService from "./components/View_Service.js"
import ViewProf from "./components/View_professionals.js"
import viewuser from "./components/View_Users.js"
import viewServiceProf from "./components/view_service_professional.js"

const routes=[
    {path:'/', component: Home},
    {path:'/login', component: Login},
    {path:'/register', component: Register},
    { path: '/admin/dashboard', component: Dashboard },
    { path: '/admin/users', component: ManageUsers },
    { path: '/admin/approve-professionals', component: ApproveProfessionals },
    { path: '/admin/create_service', component: CreateService },
    { path: '/admin/manage_services', component: ManageService },
    { path: '/customer/dashboard', component: Customer_Dashboard },
    { path: '/customer/create_service_request', component: CreateServiceRequest },
    { path: '/customer/manage_service_request', component: ManageServiceRequest },
    { path: '/professional/dashboard', component:  ProfDashboard},
    { path: '/professional/service_requests', component:  serviceRequest},
    { path: '/professional/service_requests/update_status', component:  UpdateserviceRequest},
    { path: '/customer/search_services', component:  SearchserviceCustomer},
    { path: '/admin/search_professionals', component:  SearchAdmin},
    { path: '/download-csv', component: DownloadCsv },
    { path: '/get-csv/:task_id', component: GetCsv },
    { path: '/customer/view_services', component: ViewService },
    { path: '/customer/view_professionals', component: ViewProf },
    { path: '/admin/view_users', component: viewuser },
    { path: '/professional/view_services', component: viewServiceProf }


    
];

export default new VueRouter({
    mode: 'history',
    routes,
})