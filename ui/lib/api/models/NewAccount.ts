/* tslint:disable */
/* eslint-disable */
/**
 * ooo-yay.com API
 * Resource-based API for ooo-yay.com.
 *
 * The version of the OpenAPI document: 1.0.0
 * 
 *
 * NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).
 * https://openapi-generator.tech
 * Do not edit the class manually.
 */

import { mapValues } from '../runtime';
/**
 * Specifies fields that users can provide to create an account
 * @export
 * @interface NewAccount
 */
export interface NewAccount {
    /**
     * 
     * @type {string}
     * @memberof NewAccount
     */
    username: string;
    /**
     * 
     * @type {string}
     * @memberof NewAccount
     */
    email: string;
    /**
     * 
     * @type {string}
     * @memberof NewAccount
     */
    password: string;
    /**
     * 
     * @type {string}
     * @memberof NewAccount
     */
    firstName?: string | null;
    /**
     * 
     * @type {string}
     * @memberof NewAccount
     */
    lastName?: string | null;
}

/**
 * Check if a given object implements the NewAccount interface.
 */
export function instanceOfNewAccount(value: object): value is NewAccount {
    if (!('username' in value) || value['username'] === undefined) return false;
    if (!('email' in value) || value['email'] === undefined) return false;
    if (!('password' in value) || value['password'] === undefined) return false;
    return true;
}

export function NewAccountFromJSON(json: any): NewAccount {
    return NewAccountFromJSONTyped(json, false);
}

export function NewAccountFromJSONTyped(json: any, ignoreDiscriminator: boolean): NewAccount {
    if (json == null) {
        return json;
    }
    return {
        
        'username': json['username'],
        'email': json['email'],
        'password': json['password'],
        'firstName': json['first_name'] == null ? undefined : json['first_name'],
        'lastName': json['last_name'] == null ? undefined : json['last_name'],
    };
}

export function NewAccountToJSON(value?: NewAccount | null): any {
    if (value == null) {
        return value;
    }
    return {
        
        'username': value['username'],
        'email': value['email'],
        'password': value['password'],
        'first_name': value['firstName'],
        'last_name': value['lastName'],
    };
}

