<script setup lang="ts">
import { faUser } from '@fortawesome/free-solid-svg-icons';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import { useRouter } from 'vue-router';
defineProps<{ buttonText?: string }>(); // Permette di personalizzare il testo

const router = useRouter();
const userProfile = () => {
    router.push("/profile"); // Torna alla pagina precedente
};
</script>

<template>
    <button class="btn" @click="userProfile" aria-label="Go back">
        <FontAwesomeIcon :icon="faUser"></FontAwesomeIcon>
    </button>
</template>
