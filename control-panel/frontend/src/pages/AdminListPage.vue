<script setup lang="ts">
import ListView from '@/components/ListView.vue';
import router from '@/routes/router';
import { useModalsStore } from '@/store/modals';
import { useNotificationsStore } from '@/store/notifications';
import { useUserStore } from '@/store/user';
import { ListData, RowData } from '@/utils/lists';
import { User } from '@ldap-proxy-config/models/src/generated/user';
import { computed, ref } from 'vue';

const client = useUserStore().client;
const confirm = useModalsStore().confirm;
const notification = useNotificationsStore();
const admins = ref<User[]>([]);
client.listUsers().then(x => admins.value = x);

const data = computed<ListData>((): ListData => {
    return {
        actions: [
            { action: edit, colour: "primary", label: "Edit" },
            { action: del, colour: "danger", label: "Delete" },
        ],
        data: admins.value.map(x => {
            return {
                user: x.user,
                isAdmin: x.is_admin ? "Yes" : "No",
            }
        }),
        headers: [
            { key: "user", name: "Username" },
            { key: "isAdmin", name: "Full privileges?" },
        ]
    };
});
const edit = (d: User) => router.push({ path: '/admins/' + d._id })
const del = async (d: User) => {
    if (await confirm(`Are you sure you want to delete admin ${d.user}?`)) {
        client.deleteUser(d._id as string).then(r => {
            if (r) {
                admins.value = admins.value.filter(a => a._id != d._id)
                notification.fire({
                    title: 'Success',
                    body: 'Admin deleted successfully!',
                    background: 'success',
                    when: new Date(),
                });
            } else {
                notification.fire({
                    title: 'Error',
                    body: 'Error while deleting the admin',
                    background: 'danger',
                    when: new Date(),
                });
            }
        });
    }
}

const mobileHeader = (d: User | RowData) =>
    `${d.user}`;

const filter = (d: User | RowData, s: string) =>
    (d.user as string).toLocaleLowerCase().indexOf(s.toLowerCase()) >= 0;

</script>
<template>
    <h2>All admins</h2>
    <ListView :data="data" :mobile-header="mobileHeader" :filter-function="filter"></ListView>
</template>