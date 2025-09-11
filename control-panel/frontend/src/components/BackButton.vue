<script setup lang="ts">
import { faChevronLeft } from '@fortawesome/free-solid-svg-icons';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import { computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
defineProps<{ buttonText?: string }>(); // Permette di personalizzare il testo

const router = useRouter();
const route = useRoute();
const goBack = () => {
    router.back(); // Torna alla pagina precedente
};
const showBackButton = computed(() =>
    (route.path != "/" as string) &&
    (route.path != "/login" as string));
</script>

<template>
    <button :class="'btn' + (showBackButton ? '' : ' invisible')" @click="goBack" aria-label="Go back">
        <FontAwesomeIcon :icon="faChevronLeft"></FontAwesomeIcon>
    </button>
</template>
