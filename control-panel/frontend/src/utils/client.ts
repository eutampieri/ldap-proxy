import { Server } from "@ldap-proxy-config/models/src/generated/server";
import { Client as LDAPClient } from "@ldap-proxy-config/models/src/generated/client";
import { jwtDecode, JwtPayload } from "jwt-decode";
import { User } from "@ldap-proxy-config/models/src/generated/user";
import { AuthRequest } from "@ldap-proxy-config/models";

interface UserJwt extends JwtPayload {
    profile: User,
    role: string,
}

export class Client {
    private token_storage_name: string = 'gym-token';
    private jwt?: string = localStorage.getItem(this.token_storage_name) || undefined;


    private apiRequest(method: string, endpoint: string, body?: object, headers?: Headers) {
        const h = headers || new Headers;
        if (this.jwt !== undefined) {
            h.append("Authorization", "Bearer " + this.jwt);
        }
        h.append("Content-Type", "application/json");
        return fetch(`/api${endpoint}`, { method: method, body: JSON.stringify(body), headers: h })
    }

    public get isLoggedIn(): boolean {
        // check if token is defined and valid
        try {
            const now = new Date();
            const expDate = new Date(jwtDecode<UserJwt>(this.jwt!).exp! * 1000);

            return now <= expDate;
        } catch (e) {
            return false;
        }
    }

    public get authToken(): string | undefined {
        return this.jwt;
    }


    public async login(username: string, password: string): Promise<boolean> {
        const request: AuthRequest = {
            username: username,
            password: password
        }
        const response = await this.apiRequest("POST", "/auth/authenticate", request);
        if (response.status !== 200) {
            return false;
        }
        else {
            this.jwt = await response.text();
            localStorage.setItem(this.token_storage_name, this.jwt);
            return true;
        }
    }
    public async logout(): Promise<boolean> {
        const ret = this.isLoggedIn;
        this.jwt = undefined;
        localStorage.removeItem(this.token_storage_name);
        return ret;
    }

    public get userDetails(): undefined | User {
        if (this.jwt !== undefined) {
            return jwtDecode<UserJwt>(this.jwt!).profile;
        } else {
            return undefined;
        }
    }

    public createServer(server: Server): Promise<boolean> {
        return this.apiRequest("POST", "/servers/", server).then(r => r.status == 201);
    }
    public updateServer(id: string, server: Server): Promise<boolean> {
        return this.apiRequest("PUT", "/servers/", { _id: id, ...server }).then(r => r.status == 201);
    }
    public listServers(): Promise<Server[]> {
        return this.apiRequest("GET", "/servers/").then(r => r.json());
    }
    public getServerById(id: string): Promise<Server> {
        return this.apiRequest("GET", `/servers/${id}`).then(r => r.json());
    }
    public deleteServer(id: string): Promise<boolean> {
        return this.apiRequest("DELETE", `/servers/${id}`).then(r => r.status == 200);
    }

    public createClient(client: LDAPClient): Promise<boolean> {
        return this.apiRequest("POST", "/clients/", client).then(r => r.status == 201);
    }
    public updateClient(id: string, server: LDAPClient): Promise<boolean> {
        return this.apiRequest("PUT", "/clients/", { _id: id, ...server }).then(r => r.status == 201);
    }
    public listClients(): Promise<LDAPClient[]> {
        return this.apiRequest("GET", "/clients/").then(r => r.json());
    }
    public getClientById(id: string): Promise<LDAPClient> {
        return this.apiRequest("GET", `/clients/${id}`).then(r => r.json());
    }
    public deleteClient(id: string): Promise<boolean> {
        return this.apiRequest("DELETE", `/clients/${id}`).then(r => r.status == 200);
    }


    public createUsers(user: User): Promise<boolean> {
        return this.apiRequest("POST", "/users/", user).then(r => r.status == 201);
    }
    public updateUsers(id: string, server: User): Promise<boolean> {
        return this.apiRequest("PUT", "/users/", { _id: id, ...server }).then(r => r.status == 201);
    }
    public listUsers(): Promise<User[]> {
        return this.apiRequest("GET", "/users/").then(r => r.json());
    }
    public getUserById(id: string): Promise<User> {
        return this.apiRequest("GET", `/users/${id}`).then(r => r.json());
    }
    public deleteUsers(id: string): Promise<boolean> {
        return this.apiRequest("DELETE", `/users/${id}`).then(r => r.status == 200);
    }
}
