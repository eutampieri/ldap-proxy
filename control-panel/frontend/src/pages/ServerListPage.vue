<script setup lang="ts">
import ListView from '@/components/ListView.vue';
import router from '@/routes/router';
import { useModalsStore } from '@/store/modals';
import { useNotificationsStore } from '@/store/notifications';
import { useUserStore } from '@/store/user';
import { ListData, RowData } from '@/utils/lists';
import { Server } from '@ldap-proxy-config/models/src/generated/server';
import { User } from '@ldap-proxy-config/models/src/generated/user.js';
import { computed, ref } from 'vue';

const client = useUserStore().client;
const confirm = useModalsStore().confirm;
const notification = useNotificationsStore();
const servers = ref<Server[]>([]);
client.listServers().then(x => servers.value = x);

const data = computed<ListData>((): ListData => {
    return {
        actions: [
            { action: edit, colour: "primary", label: "Edit" },
            { action: del, colour: "danger", label: "Delete" },
        ],
        data: servers.value.map(x => {
            return {
                ip: x.ip,
                port: x.port.toString(),
                baseDN: x.base_dn,
                tls: x.tls ? "Yes" : "No",
            }
        }),
        headers: [
            { key: "ip", name: "IP/hostname" },
            { key: "port", name: "Port" },
            { key: "tls", name: "TLS" },
            { key: "baseDN", name: "Base DN" },
        ]
    };
});
const edit = (d: Server) => router.push({ path: '/servers/' + d._id })
const del = async (d: Server) => {
    if (await confirm(`Are you sure you want to delete server ${d.ip}?`)) {
        client.deleteServer(d._id as string).then(r => {
            if (r) {
                servers.value = servers.value.filter(a => a._id != d._id)
                notification.fire({
                    title: 'Success',
                    body: 'Server deleted successfully!',
                    background: 'success',
                    when: new Date(),
                });
            } else {
                notification.fire({
                    title: 'Error',
                    body: 'Error while deleting the server',
                    background: 'danger',
                    when: new Date(),
                });
            }
        });
    }
}

const mobileHeader = (d: User | RowData) =>
    `${d.ip}`;

const filter = (d: User | RowData, s: string) =>
    (d.ip as string).toLocaleLowerCase().indexOf(s.toLowerCase()) >= 0;

</script>
<template>
    <h2>All servers</h2>
    <ListView :data="data" :mobile-header="mobileHeader" :filter-function="filter"></ListView>
</template>