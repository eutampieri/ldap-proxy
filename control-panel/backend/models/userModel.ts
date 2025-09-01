import { Schema, model } from 'mongoose';
import { User } from '@ldap-proxy-config/models/src/generated/user.js';
import jsonSchemaToMongooseSchema from '@simplyhexagonal/json-schema-to-mongoose-schema';

import schema from "../../../schemas/user.json" with { type: 'json' };

const userSchema = jsonSchemaToMongooseSchema({
    "$schema": "http://json-schema.org/draft-07/schema#",
    "definitions": {
        "User": {
            properties: JSON.parse(JSON.stringify(schema.properties)),
            required: schema.required,
            type: "object",
        }
    }
}, "User") as Schema<User>;

// Creation of the client model
export default model("User", userSchema)
