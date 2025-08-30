<script setup lang="ts">
import ListView from '@/components/ListView.vue';
import router from '@/routes/router';
import { useModalsStore } from '@/store/modals';
import { useNotificationsStore } from '@/store/notifications';
import { useUserStore } from '@/store/user';
import { ListData, RowData } from '@/utils/lists';
import { Client } from '@ldap-proxy-config/models/src/generated/client';
import { computed, ref } from 'vue';

const client = useUserStore().client;
const confirm = useModalsStore().confirm;
const notification = useNotificationsStore();
const clients = ref<Client[]>([]);
client.listClients().then(x => clients.value = x);

const data = computed<ListData>((): ListData => {
    return {
        actions: [
            { action: edit, colour: "primary", label: "Edit" },
            { action: del, colour: "danger", label: "Delete" },
        ],
        data: clients.value.map(x => {
            return {
                dn: x.dn,
            }
        }),
        headers: [
            { key: "dn", name: "Bind DN" },
        ]
    };
});
const edit = (d: Client) => router.push({ path: '/clients/' + d._id })
const del = async (d: Client) => {
    if (await confirm(`Are you sure you want to delete client ${d.dn}?`)) {
        client.deleteClient(d._id as string).then(r => {
            if (r) {
                clients.value = clients.value.filter(a => a._id != d._id)
                notification.fire({
                    title: 'Success',
                    body: 'Client deleted successfully!',
                    background: 'success',
                    when: new Date(),
                });
            } else {
                notification.fire({
                    title: 'Error',
                    body: 'Error while deleting the client',
                    background: 'danger',
                    when: new Date(),
                });
            }
        });
    }
}

const mobileHeader = (d: Client | RowData) =>
    `${d.dn}`;

const filter = (d: Client | RowData, s: string) =>
    (d.dn as string).toLocaleLowerCase().indexOf(s.toLowerCase()) >= 0;

</script>
<template>
    <h2>All servers</h2>
    <ListView :data="data" :mobile-header="mobileHeader" :filter-function="filter"></ListView>
</template>