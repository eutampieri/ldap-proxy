<script lang="ts" setup>
import { useUserStore } from '../store/user';
import { ref } from 'vue';
import SectionContainer from '@/components/SectionContainer.vue';
import SectionContainerItem from '@/components/SectionContainerItem.vue';
import router from '@/routes/router';
import { useModalsStore } from '@/store/modals';
import { User } from '@ldap-proxy-config/models/src/generated/user';

interface ProfileEntry {
    label: string,
    value: string,
    linkPrefix?: string
}

const client = useUserStore().client;
const confirm = useModalsStore().confirm;
const user = ref<User>();
const profileData = ref<Array<ProfileEntry>>();

function getUser(): Promise<undefined | User> {
    return Promise.resolve(client.userDetails);
}
const fieldNameMapper = {
    username: 'Username',
}
// prepare the display data
getUser().then((x: undefined | User) => {
    if (x) {
        user.value = x;
        profileData.value = Object.keys(x)
            .filter(k => Object.keys(fieldNameMapper).includes(k))
            .map(k => {
                let value = x[k as keyof typeof x] as string;

                return {
                    label: fieldNameMapper[k as keyof typeof fieldNameMapper],
                    value: value,
                }
            });
    }
});

async function logout() {
    if (await client.logout()) {
        router.push({ "path": "/login" });
    }
}
</script>

<template>
    <SectionContainer>
        <SectionContainerItem id="profile">
            <div class="d-flex flex-column justify-content-center">
                <dl>
                    <template v-for="item in profileData">
                        <dt class="text-center">{{ item.label }}</dt>
                        <dd class="text-center" v-if="item.linkPrefix"><a :href="item.linkPrefix + item.value">{{
                            item.value }}</a></dd>
                        <dd class="text-center" v-else>{{ item.value }}</dd>
                    </template>
                </dl>
                <div class="d-flex justify-content-evenly mt-2">
                    <button type="button" class="btn btn-secondary m-2" @click="logout">Logout</button>
                </div>
            </div>
        </SectionContainerItem>
    </SectionContainer>
</template>