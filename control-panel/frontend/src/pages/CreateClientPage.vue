<script lang="ts" setup>
import { ref } from 'vue';
import GenericInput from '@/components/GenericInput.vue';
import { useUserStore } from '../store/user';
import { useNotificationsStore } from '@/store/notifications';
import SectionContainer from '@/components/SectionContainer.vue';
import SectionContainerItem from '@/components/SectionContainerItem.vue';
import { Client } from '@ldap-proxy-config/models/src/generated/client';
import { useRouter } from 'vue-router';
const router = useRouter();

const dn = ref("");
const password = ref("");

const client = useUserStore().client;
const notification = useNotificationsStore();

const props = defineProps<{ id?: string }>();

if (props.id) {
    client.getClientById(props.id).then(r => {
        if (r) {
            dn.value = r.dn;
            password.value = '*******';
        } else {
            notification.fire({
                title: 'Error',
                body: 'This client could not be found',
                background: 'danger'
            })
        }
    })
}
const createRequest = () => ({
    dn: dn.value,
    password: password.value == '*******' ? undefined : password.value,
}) as Client;

async function handleUpdateCustomer() {
    try {
        const request = createRequest()
        const id = props.id!;
        const response = await client.updateClient(id, request);

        if (response) {
            notification.fire({
                title: 'Success',
                body: `Client ${dn.value} successfully updated!`,
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
            body: 'Error while updating the client',
            background: 'danger',
            when: new Date(),
        });
    }
}
async function handleCreateCustomer() {
    try {
        const request = createRequest();
        const response = await client.createClient(request);

        if (response) {
            notification.fire({
                title: 'Success',
                body: `Client ${dn.value} successfully created!`,
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
            body: 'Error while creating the client',
            background: 'danger',
            when: new Date(),
        });
    }
}
</script>

<template>
    <h2 v-if="props.id" class="text-center">Update {{ dn != '' ? dn : 'Client' }}</h2>
    <h2 v-else class="text-center">Create {{ dn != '' ? dn : 'a new Client' }}</h2>
    <SectionContainer>
        <SectionContainerItem>
            <form>
                <GenericInput :dont-autocapitalize="true" type="text" id="username" v-model="dn">
                    DN
                </GenericInput>

                <GenericInput type="password" id="password" v-model="password">
                    Password
                </GenericInput>

                <button v-if="props.id" class="btn btn-primary" type="button" @click="handleUpdateCustomer">Update
                    Client {{ dn }}</button>
                <button v-else class="btn btn-primary" type="button" @click="handleCreateCustomer">Create Client {{
                    dn }}</button>
            </form>
        </SectionContainerItem>
    </SectionContainer>

</template>