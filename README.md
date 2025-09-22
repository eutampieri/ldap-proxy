# LDAP Proxying Service

_Michele Ravaioli - michele.ravaioli3@studio.unibo.it_
    
_Eugenio Tampieri - eugenio.tampieri@studio.unibo.it_

## Overview

This project presents the design and implementation of a _Lightweight Directory Access Protocol_ (LDAP) proxying service deployed within a containerized environment. The service accepts incoming LDAP requests and forwards them to one or more target servers, aggregating all the responses into a single result.

Its primary use case is the consolidation of multiple Active Directory domains, allowing authentication queries to be executed from a single entry point while transparently returning results as if all users resided within the same domain. While remaining online, the service can be configured through a control panel web app accessible to administrators, who can add and remove servers and clients dynamically.

## Features

- **LDAP Request Forwarding** – Routes requests to one or more backend servers.  
- **Response Aggregation** – Merges results from multiple servers into a single response.  
- **Runtime Configurability** – Administrators can add/remove servers and clients without downtime.  
- **Web-based Control Panel** – User-friendly interface for system configuration.  
- **Containerized Deployment** – Supports _Docker_ and _Kubernetes_ for scalability and portability.  

## Validation

- Automated tests for LDAP Merger and Control Panel.  
- Continuous Integration workflows on GitHub.  
- Mock-based testing for servers, clients, and database.  


## Getting Started

The system can be deployed using **Docker Swarm** or **Kubernetes**.  
This repository provides a `docker-compose.yaml` file and deployment manifests under the `k8s/` directory.  

### Docker

1. If not already done, initialize Swarm:  
```bash
docker swarm init
```
2. Deploy the stack:

```bash
docker stack deploy -c ./docker-compose.yaml ldapProxy
```
3. Get the ID of a MongoDB container:

```bash
docker ps
```
4. Start a Mongo shell:

```bash
docker exec -it <container_id> mongosh
```

5. Initialize the replica set:

```javascript
rs.initiate({
    _id: "rs0", members: [
        {_id: 0, host: "mongodb1"},
        {_id: 1, host: "mongodb2"},
        {_id: 2, host: "mongodb3"}
    ]
});
rs.status(); // verify that the replica set is healthy
```

The application runs on port 8080.

### Kubernetes

Manifests deploy the app under the `ldap-proxy` namespace. To use a different one, edit all manifests.

1. Set the domain name in the Control Panel Ingress (`k8s/ingress.yaml`).

2. Deploy with:

```bash
kubectl apply -f k8s
```

3. Attach to a MongoDB pod:

```bash
kubectl -n ldap-proxy exec -it statefulset/mongodb -- mongosh
```

4. Initialize the replica set:

```javascript
rs.initiate({
    _id: "rs0", members: [
        {_id: 0, host: "mongodb-0.mongodb"},
        {_id: 1, host: "mongodb-1.mongodb"},
        {_id: 2, host: "mongodb-2.mongodb"}
    ]
});
rs.status(); // verify that the replica set is healthy
```