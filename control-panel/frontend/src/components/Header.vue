<script lang="ts" setup>
import BackButton from '@/components/BackButton.vue';
import PageTitle from '@/components/PageTitle.vue';
import UserProfile from './UserProfile.vue';
import { useRoute } from 'vue-router';
</script>

<template>
    <header class="sticky-top d-flex justify-content-between navbar bg-body-tertiary px-2 border-bottom mb-2">
        <BackButton buttonText="Back" />

        <PageTitle title="LDAP proxy" class="header-title" />
        <UserProfile class="profile-icon" />

    </header>
</template>

<style scoped>
.profile-icon:hover {
    transform: scale(1.1);
}

.profile-icon {
    height: 3em;
    width: 3em;
    max-width: 3em;
    transition: transform 0.2s ease-in-out;
}
</style>
