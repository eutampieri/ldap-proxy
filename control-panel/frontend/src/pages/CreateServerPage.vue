<script lang="ts" setup>
import { computed, ref } from 'vue';
import GenericInput from '@/components/GenericInput.vue';
import CheckBox from '@/components/CheckBox.vue';
import { Server } from '@ldap-proxy-config/models/src/generated/server';
import { useUserStore } from '@/store/user';
import { useNotificationsStore } from '@/store/notifications';
import SectionContainerItem from '@/components/SectionContainerItem.vue';
import SectionContainer from '@/components/SectionContainer.vue';
import { useRouter } from 'vue-router';
const router = useRouter();

const baseDN = ref("");
const password = ref("");
const bindDN = ref("");
const ip = ref("");
const port = ref("");
const tls = ref(false);

const usernameValid = ref(false);
const passwordValid = ref(false);
const firstNameValid = ref(false);
const lastNameValid = ref(false);

const submitButtonEnabled = computed(() => usernameValid.value &&
    passwordValid.value &&
    firstNameValid.value &&
    lastNameValid.value
);

const client = useUserStore().client;
const notification = useNotificationsStore();

const props = defineProps<{ id?: string }>();

if (props.id) {
    client.getServerById(props.id).then(r => {
        if (r) {
            baseDN.value = r.base_dn;
            bindDN.value = r.bind_dn;
            password.value = '*******';
            ip.value = r.ip;
            port.value = r.port
            tls.value = r.tls;
        } else {
            notification.fire({
                title: 'Error',
                body: 'This server could not be found',
                background: 'danger'
            })
        }
    })
}
const createRequest = () => ({
    base_dn: baseDN.value,
    bind_dn: bindDN.value,
    bind_password: password.value == '*******' ? undefined : password.value,
    ip: ip.value,
    port: port.value,
    tls: tls.value,
}) as Server;

async function handleUpdateServer() {
    try {
        const request = createRequest();
        const id = props.id!;
        const response = await client.updateServer(id, request);

        if (response) {
            notification.fire({
                title: 'Success',
                body: `Server ${ip.value} successfully updated!`,
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

async function handleCreateServer() {
    try {
        const request = createRequest();
        const response = await client.createServer(request);

        if (response) {
            notification.fire({
                title: 'Success',
                body: `Server ${ip} successfully created!`,
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
            body: 'Error while creating the server',
            background: 'danger',
            when: new Date(),
        });
    }
}
</script>

<template>
    <h2 v-if="props.id" class="text-center">Update {{ ip || 'Server' }}</h2>
    <h2 v-else class="text-center">Create {{ ip != '' ? ip : 'a new Server' }}</h2>
    <SectionContainer>
        <SectionContainerItem>
            <form>
                <GenericInput :dont-autocapitalize="true" type="text" id="baseDN" v-model="baseDN">
                    Base DN
                </GenericInput>

                <GenericInput :dont-autocapitalize="true" type="text" id="bindDN" v-model="bindDN">
                    Bind DN
                </GenericInput>

                <GenericInput type="password" id="password" v-model="password" v-model:valid="passwordValid">
                    Bind password
                </GenericInput>

                <GenericInput type="text" id="ip" v-model="ip">
                    IP or host name
                </GenericInput>

                <GenericInput type="number" id="port" v-model="port">Port
                </GenericInput>

                <CheckBox type="boolean" id="tls" v-model="tls">
                    TLS
                </CheckBox>

                <button v-if="props.id" class="btn btn-primary" type="button" @click="handleUpdateServer"
                    :disabled="!submitButtonEnabled">Update Server {{ ip }}</button>
                <button v-else class="btn btn-primary" type="button" @click="handleCreateServer"
                    :disabled="!submitButtonEnabled">Create Server {{ ip }}</button>
            </form>
        </SectionContainerItem>
    </SectionContainer>

</template>