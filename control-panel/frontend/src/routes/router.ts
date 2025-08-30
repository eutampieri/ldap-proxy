import { createRouter, createWebHistory } from 'vue-router';
import { useUserStore } from '@/store/user';
import Login from '@/pages/Login.vue';
import Home from '@/pages/Home.vue';
import CreateServerPage from '@/pages/CreateServerPage.vue';
import ServerListPage from '@/pages/ServerListPage.vue';
import CreateClientPage from '@/pages/CreateClientPage.vue';
import ClientListPage from '@/pages/ClientListPage.vue';
import CreateAdminPage from '@/pages/CreateAdminPage.vue';
import AdminListPage from '@/pages/AdminListPage.vue';


const routes = [
    { path: '/login', name: "Login", component: Login },
    { path: '/', name: "adminPage", component: Home },
    { path: '/servers/new', name: "createServer", component: CreateServerPage },
    { path: '/servers/:id', name: "updateServer", component: CreateServerPage, props: true },
    { path: '/servers/', name: "listServers", component: ServerListPage },
    { path: '/clients/new', name: "createClient", component: CreateClientPage },
    { path: '/clients/:id', name: "updateClient", component: CreateClientPage, props: true },
    { path: '/clients/', name: "listClients", component: ClientListPage },
    { path: '/admins/new', name: "createAdmin", component: CreateAdminPage },
    { path: '/admins/:id', name: "updateAdmin", component: CreateAdminPage, props: true },
    { path: '/admins/', name: "listAdmins", component: AdminListPage },
];

const router = createRouter({
    history: createWebHistory(),
    routes
});
router.beforeEach(async (to, from) => {
    const store = useUserStore()
    if (
        !store.client.isLoggedIn &&
        to.name !== 'Login'
    ) {
        return { name: 'Login' }
    }
});

export default router;
