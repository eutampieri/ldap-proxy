import { Schema, model } from 'mongoose';
import { Client } from '@ldap-proxy-config/models/src/generated/client.js';
import jsonSchemaToMongooseSchema from '@simplyhexagonal/json-schema-to-mongoose-schema';

import schema from "../../../schemas/client.json" with { type: 'json' };


// Definition of the schema for the client model
const clientSchema = jsonSchemaToMongooseSchema({
    "$schema": "http://json-schema.org/draft-07/schema#",
    "definitions": {
        "Client": {
            properties: JSON.parse(JSON.stringify(schema.properties)),
            required: schema.required,
            type: "object",
        }
    }
}, "Client") as Schema<Client>;

// Creation of the client model
export default model("Client", clientSchema)
