<script lang="ts" setup>
import { ref } from 'vue';
import GenericInput from '@/components/GenericInput.vue';
import { useUserStore } from '../store/user';
import { useNotificationsStore } from '@/store/notifications';
import SectionContainer from '@/components/SectionContainer.vue';
import SectionContainerItem from '@/components/SectionContainerItem.vue';
import { useRouter } from 'vue-router';
import { User } from '@ldap-proxy-config/models/src/generated/user';
import CheckBox from '@/components/CheckBox.vue';
const router = useRouter();

const user = ref("");
const password = ref("");
const admin = ref(false);

const client = useUserStore().client;
const notification = useNotificationsStore();

const props = defineProps<{ id?: string }>();

if (props.id) {
    client.getUserById(props.id).then(r => {
        if (r) {
            user.value = r.user;
            password.value = '*******';
            admin.value = r.is_admin;
        } else {
            notification.fire({
                title: 'Error',
                body: 'This admin could not be found',
                background: 'danger'
            })
        }
    })
}
const createRequest = () => ({
    user: user.value,
    password: password.value == '*******' ? undefined : password.value,
    is_admin: admin.value
}) as User;

async function handleUpdateAdmin() {
    try {
        const request = createRequest()
        const id = props.id!;
        const response = await client.updateUser(id, request);

        if (response) {
            notification.fire({
                title: 'Success',
                body: `Admin ${user.value} successfully updated!`,
                background: 'success',
                when: new Date(),
            });
            router.back();
        } else {
            throw new Error();
        }
    } catch (error) {
        notification.fire({
            title: 'Error',
            body: 'Error while updating the admin',
            background: 'danger',
            when: new Date(),
        });
    }
}
async function handleCreateAdmin() {
    try {
        const request = createRequest();
        const response = await client.createUser(request);

        if (response) {
            notification.fire({
                title: 'Success',
                body: `Admin ${user.value} successfully created!`,
                background: 'success',
                when: new Date(),
            });
            router.back();
        } else {
            throw new Error();
        }
    } catch (error) {
        notification.fire({
            title: 'Error',
            body: 'Error while creating the admin',
            background: 'danger',
            when: new Date(),
        });
    }
}
</script>

<template>
    <h2 v-if="props.id" class="text-center">Update {{ user != '' ? user : 'Admin' }}</h2>
    <h2 v-else class="text-center">Create {{ user != '' ? user : 'a new Admin' }}</h2>
    <SectionContainer>
        <SectionContainerItem>
            <form>
                <GenericInput :dont-autocapitalize="true" type="text" id="username" v-model="user">
                    Username
                </GenericInput>

                <GenericInput type="password" id="password" v-model="password">
                    Password
                </GenericInput>

                <CheckBox type="boolean" id="tls" v-model="admin">
                    Full privileges
                </CheckBox>


                <button v-if="props.id" class="btn btn-primary" type="button" @click="handleUpdateAdmin">Update
                    Admin {{ user }}</button>
                <button v-else class="btn btn-primary" type="button" @click="handleCreateAdmin">Create Admin {{
                    user }}</button>
            </form>
        </SectionContainerItem>
    </SectionContainer>

</template>