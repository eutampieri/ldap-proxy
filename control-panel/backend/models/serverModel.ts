import { Schema, model } from 'mongoose';
import { Server } from '@ldap-proxy-config/models/src/generated/server.js';
import jsonSchemaToMongooseSchema from '@simplyhexagonal/json-schema-to-mongoose-schema';

import schema from "../../../schemas/server.json"with { type: 'json' };


// Definition of the schema for the server model
const serverSchema = jsonSchemaToMongooseSchema({
    "$schema": "http://json-schema.org/draft-07/schema#",
    "definitions": {
        "Server": {
            properties: JSON.parse(JSON.stringify(schema.properties)),
            required: schema.required,
            type: "object",
        }
    }
}, "Server") as Schema<Server>;

// Creation of the server model
export default model("Server", serverSchema)
