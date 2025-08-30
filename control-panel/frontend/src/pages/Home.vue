<script lang="ts" setup>
import MainButton from '@/components/MainButton.vue';
import { useUserStore } from '@/store/user';

const store = useUserStore();
const admin = store.client.userDetails;
// Verifica se admin è di tipo 'Admin' e ha la proprietà 'hasFullPrivileges'
const privilege = admin && 'hasFullPrivileges' in admin ? admin.hasFullPrivileges : false;

</script>

<template>
    <section class="d-flex flex-column mt-4">
        <h3 class="mx-auto">Upstream servers</h3>
        <MainButton path="/servers/new">Create server</MainButton>
        <MainButton path="/servers">View servers</MainButton>
    </section>
    <section class="d-flex flex-column mt-4">
        <h3 class="mx-auto">LDAP clients</h3>
        <MainButton path="/clients/new">Create client</MainButton>
        <MainButton path="/clients">View clients</MainButton>
    </section>
    <section v-if="privilege" class="d-flex flex-column mt-4">
        <h3 class="mx-auto">Admins</h3>
        <MainButton :path="'/admins'">Create admin</MainButton>
        <MainButton :path="'/admins/new'">View admins</MainButton>
    </section>
</template>