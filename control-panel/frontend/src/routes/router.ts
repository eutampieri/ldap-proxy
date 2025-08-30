import { createRouter, createWebHistory } from 'vue-router';
import { useUserStore } from '@/store/user';
import Login from '@/pages/Login.vue';
import Home from '@/pages/Home.vue';
import ProfilePage from '@/pages/ProfilePage.vue';
import UserListPage from '@/pages/UserListPage.vue';
import CreateAdminPage from '@/pages/CreateServerPage.vue';
import AdminListPage from '@/pages/ServerListPage.vue';
import CreateServerPage from '@/pages/CreateServerPage.vue';
import ServerListPage from '@/pages/ServerListPage.vue';


const routes = [
    { path: '/login', name: "Login", component: Login },
    { path: '/', name: "adminPage", component: Home },
    { path: '/servers/new', name: "createServer", component: CreateServerPage },
    { path: '/servers/:id', name: "updateServer", component: CreateServerPage, props: true },
    { path: '/servers/', name: "listServers", component: ServerListPage },
    { path: '/admin/listCustomers', name: "listCustomers", component: UserListPage },
    { path: '/admin/createAdmin', name: "createAdmin", component: CreateAdminPage },
    { path: '/admin/updateAdmin/:id', name: "updateAdmin", component: CreateAdminPage, props: true },
    { path: '/admin/listAdmins', name: "listAdmins", component: AdminListPage },
    { path: '/:role/profile/:id', name: "userProfile", component: ProfilePage, props: true },
];

const router = createRouter({
    history: createWebHistory(),
    routes
});
router.beforeEach(async (to, from) => {
    /*const store = useUserStore()
    if (
        !store.client.isLoggedIn &&
        to.name !== 'Login'
    ) {
        return { name: 'Login' }
    }*/
});

export default router;
