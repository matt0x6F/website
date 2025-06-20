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


import * as runtime from '../runtime';
import type {
  AdminUserDetails,
  AdminUserModify,
  AuthError,
  NewAccount,
  PagedAdminUserDetails,
  UpdateAccount,
  UserSelf,
} from '../models/index';
import {
    AdminUserDetailsFromJSON,
    AdminUserDetailsToJSON,
    AdminUserModifyFromJSON,
    AdminUserModifyToJSON,
    AuthErrorFromJSON,
    AuthErrorToJSON,
    NewAccountFromJSON,
    NewAccountToJSON,
    PagedAdminUserDetailsFromJSON,
    PagedAdminUserDetailsToJSON,
    UpdateAccountFromJSON,
    UpdateAccountToJSON,
    UserSelfFromJSON,
    UserSelfToJSON,
} from '../models/index';

export interface DeleteUserRequest {
    userId: number;
}

export interface GetUserRequest {
    userId: number;
}

export interface ListUsersRequest {
    isStaff?: boolean;
    isActive?: boolean;
    limit?: number;
    offset?: number;
}

export interface SignUpRequest {
    newAccount: NewAccount;
}

export interface UpdateSelfRequest {
    updateAccount: UpdateAccount;
}

export interface UpdateUserRequest {
    userId: number;
    adminUserModify: AdminUserModify;
}

/**
 * 
 */
export class AccountsApi extends runtime.BaseAPI {

    /**
     * Deletes the calling user
     * Delete Self
     */
    async deleteSelfRaw(initOverrides?: RequestInit | runtime.InitOverrideFunction): Promise<runtime.ApiResponse<void>> {
        const queryParameters: any = {};

        const headerParameters: runtime.HTTPHeaders = {};

        if (this.configuration && this.configuration.accessToken) {
            const token = this.configuration.accessToken;
            const tokenString = await token("JWTAuth", []);

            if (tokenString) {
                headerParameters["Authorization"] = `Bearer ${tokenString}`;
            }
        }
        const response = await this.request({
            path: `/api/accounts/me`,
            method: 'DELETE',
            headers: headerParameters,
            query: queryParameters,
        }, initOverrides);

        return new runtime.VoidApiResponse(response);
    }

    /**
     * Deletes the calling user
     * Delete Self
     */
    async deleteSelf(initOverrides?: RequestInit | runtime.InitOverrideFunction): Promise<void> {
        await this.deleteSelfRaw(initOverrides);
    }

    /**
     * Deletes a user
     * Delete User
     */
    async deleteUserRaw(requestParameters: DeleteUserRequest, initOverrides?: RequestInit | runtime.InitOverrideFunction): Promise<runtime.ApiResponse<void>> {
        if (requestParameters['userId'] == null) {
            throw new runtime.RequiredError(
                'userId',
                'Required parameter "userId" was null or undefined when calling deleteUser().'
            );
        }

        const queryParameters: any = {};

        const headerParameters: runtime.HTTPHeaders = {};

        if (this.configuration && this.configuration.accessToken) {
            const token = this.configuration.accessToken;
            const tokenString = await token("JWTAuth", []);

            if (tokenString) {
                headerParameters["Authorization"] = `Bearer ${tokenString}`;
            }
        }
        const response = await this.request({
            path: `/api/accounts/{user_id}`.replace(`{${"user_id"}}`, encodeURIComponent(String(requestParameters['userId']))),
            method: 'DELETE',
            headers: headerParameters,
            query: queryParameters,
        }, initOverrides);

        return new runtime.VoidApiResponse(response);
    }

    /**
     * Deletes a user
     * Delete User
     */
    async deleteUser(requestParameters: DeleteUserRequest, initOverrides?: RequestInit | runtime.InitOverrideFunction): Promise<void> {
        await this.deleteUserRaw(requestParameters, initOverrides);
    }

    /**
     * Returns a specific user
     * Get User
     */
    async getUserRaw(requestParameters: GetUserRequest, initOverrides?: RequestInit | runtime.InitOverrideFunction): Promise<runtime.ApiResponse<AdminUserDetails>> {
        if (requestParameters['userId'] == null) {
            throw new runtime.RequiredError(
                'userId',
                'Required parameter "userId" was null or undefined when calling getUser().'
            );
        }

        const queryParameters: any = {};

        const headerParameters: runtime.HTTPHeaders = {};

        if (this.configuration && this.configuration.accessToken) {
            const token = this.configuration.accessToken;
            const tokenString = await token("JWTAuth", []);

            if (tokenString) {
                headerParameters["Authorization"] = `Bearer ${tokenString}`;
            }
        }
        const response = await this.request({
            path: `/api/accounts/{user_id}`.replace(`{${"user_id"}}`, encodeURIComponent(String(requestParameters['userId']))),
            method: 'GET',
            headers: headerParameters,
            query: queryParameters,
        }, initOverrides);

        return new runtime.JSONApiResponse(response, (jsonValue) => AdminUserDetailsFromJSON(jsonValue));
    }

    /**
     * Returns a specific user
     * Get User
     */
    async getUser(requestParameters: GetUserRequest, initOverrides?: RequestInit | runtime.InitOverrideFunction): Promise<AdminUserDetails> {
        const response = await this.getUserRaw(requestParameters, initOverrides);
        return await response.value();
    }

    /**
     * Returns a list of all users, with optional filtering by staff and active status
     * List Users
     */
    async listUsersRaw(requestParameters: ListUsersRequest, initOverrides?: RequestInit | runtime.InitOverrideFunction): Promise<runtime.ApiResponse<PagedAdminUserDetails>> {
        const queryParameters: any = {};

        if (requestParameters['isStaff'] != null) {
            queryParameters['is_staff'] = requestParameters['isStaff'];
        }

        if (requestParameters['isActive'] != null) {
            queryParameters['is_active'] = requestParameters['isActive'];
        }

        if (requestParameters['limit'] != null) {
            queryParameters['limit'] = requestParameters['limit'];
        }

        if (requestParameters['offset'] != null) {
            queryParameters['offset'] = requestParameters['offset'];
        }

        const headerParameters: runtime.HTTPHeaders = {};

        if (this.configuration && this.configuration.accessToken) {
            const token = this.configuration.accessToken;
            const tokenString = await token("JWTAuth", []);

            if (tokenString) {
                headerParameters["Authorization"] = `Bearer ${tokenString}`;
            }
        }
        const response = await this.request({
            path: `/api/accounts/`,
            method: 'GET',
            headers: headerParameters,
            query: queryParameters,
        }, initOverrides);

        return new runtime.JSONApiResponse(response, (jsonValue) => PagedAdminUserDetailsFromJSON(jsonValue));
    }

    /**
     * Returns a list of all users, with optional filtering by staff and active status
     * List Users
     */
    async listUsers(requestParameters: ListUsersRequest = {}, initOverrides?: RequestInit | runtime.InitOverrideFunction): Promise<PagedAdminUserDetails> {
        const response = await this.listUsersRaw(requestParameters, initOverrides);
        return await response.value();
    }

    /**
     * Creates a new user
     * Sign Up
     */
    async signUpRaw(requestParameters: SignUpRequest, initOverrides?: RequestInit | runtime.InitOverrideFunction): Promise<runtime.ApiResponse<UserSelf>> {
        if (requestParameters['newAccount'] == null) {
            throw new runtime.RequiredError(
                'newAccount',
                'Required parameter "newAccount" was null or undefined when calling signUp().'
            );
        }

        const queryParameters: any = {};

        const headerParameters: runtime.HTTPHeaders = {};

        headerParameters['Content-Type'] = 'application/json';

        if (this.configuration && this.configuration.accessToken) {
            const token = this.configuration.accessToken;
            const tokenString = await token("JWTAuth", []);

            if (tokenString) {
                headerParameters["Authorization"] = `Bearer ${tokenString}`;
            }
        }
        const response = await this.request({
            path: `/api/accounts/sign_up`,
            method: 'POST',
            headers: headerParameters,
            query: queryParameters,
            body: NewAccountToJSON(requestParameters['newAccount']),
        }, initOverrides);

        return new runtime.JSONApiResponse(response, (jsonValue) => UserSelfFromJSON(jsonValue));
    }

    /**
     * Creates a new user
     * Sign Up
     */
    async signUp(requestParameters: SignUpRequest, initOverrides?: RequestInit | runtime.InitOverrideFunction): Promise<UserSelf> {
        const response = await this.signUpRaw(requestParameters, initOverrides);
        return await response.value();
    }

    /**
     * Updates the calling users details
     * Update Self
     */
    async updateSelfRaw(requestParameters: UpdateSelfRequest, initOverrides?: RequestInit | runtime.InitOverrideFunction): Promise<runtime.ApiResponse<UserSelf>> {
        if (requestParameters['updateAccount'] == null) {
            throw new runtime.RequiredError(
                'updateAccount',
                'Required parameter "updateAccount" was null or undefined when calling updateSelf().'
            );
        }

        const queryParameters: any = {};

        const headerParameters: runtime.HTTPHeaders = {};

        headerParameters['Content-Type'] = 'application/json';

        if (this.configuration && this.configuration.accessToken) {
            const token = this.configuration.accessToken;
            const tokenString = await token("JWTAuth", []);

            if (tokenString) {
                headerParameters["Authorization"] = `Bearer ${tokenString}`;
            }
        }
        const response = await this.request({
            path: `/api/accounts/me`,
            method: 'PUT',
            headers: headerParameters,
            query: queryParameters,
            body: UpdateAccountToJSON(requestParameters['updateAccount']),
        }, initOverrides);

        return new runtime.JSONApiResponse(response, (jsonValue) => UserSelfFromJSON(jsonValue));
    }

    /**
     * Updates the calling users details
     * Update Self
     */
    async updateSelf(requestParameters: UpdateSelfRequest, initOverrides?: RequestInit | runtime.InitOverrideFunction): Promise<UserSelf> {
        const response = await this.updateSelfRaw(requestParameters, initOverrides);
        return await response.value();
    }

    /**
     * Updates a user
     * Update User
     */
    async updateUserRaw(requestParameters: UpdateUserRequest, initOverrides?: RequestInit | runtime.InitOverrideFunction): Promise<runtime.ApiResponse<AdminUserDetails>> {
        if (requestParameters['userId'] == null) {
            throw new runtime.RequiredError(
                'userId',
                'Required parameter "userId" was null or undefined when calling updateUser().'
            );
        }

        if (requestParameters['adminUserModify'] == null) {
            throw new runtime.RequiredError(
                'adminUserModify',
                'Required parameter "adminUserModify" was null or undefined when calling updateUser().'
            );
        }

        const queryParameters: any = {};

        const headerParameters: runtime.HTTPHeaders = {};

        headerParameters['Content-Type'] = 'application/json';

        if (this.configuration && this.configuration.accessToken) {
            const token = this.configuration.accessToken;
            const tokenString = await token("JWTAuth", []);

            if (tokenString) {
                headerParameters["Authorization"] = `Bearer ${tokenString}`;
            }
        }
        const response = await this.request({
            path: `/api/accounts/{user_id}`.replace(`{${"user_id"}}`, encodeURIComponent(String(requestParameters['userId']))),
            method: 'PUT',
            headers: headerParameters,
            query: queryParameters,
            body: AdminUserModifyToJSON(requestParameters['adminUserModify']),
        }, initOverrides);

        return new runtime.JSONApiResponse(response, (jsonValue) => AdminUserDetailsFromJSON(jsonValue));
    }

    /**
     * Updates a user
     * Update User
     */
    async updateUser(requestParameters: UpdateUserRequest, initOverrides?: RequestInit | runtime.InitOverrideFunction): Promise<AdminUserDetails> {
        const response = await this.updateUserRaw(requestParameters, initOverrides);
        return await response.value();
    }

    /**
     * Returns the calling users details
     * Whoami
     */
    async whoamiRaw(initOverrides?: RequestInit | runtime.InitOverrideFunction): Promise<runtime.ApiResponse<UserSelf>> {
        const queryParameters: any = {};

        const headerParameters: runtime.HTTPHeaders = {};

        if (this.configuration && this.configuration.accessToken) {
            const token = this.configuration.accessToken;
            const tokenString = await token("JWTAuth", []);

            if (tokenString) {
                headerParameters["Authorization"] = `Bearer ${tokenString}`;
            }
        }
        const response = await this.request({
            path: `/api/accounts/me`,
            method: 'GET',
            headers: headerParameters,
            query: queryParameters,
        }, initOverrides);

        return new runtime.JSONApiResponse(response, (jsonValue) => UserSelfFromJSON(jsonValue));
    }

    /**
     * Returns the calling users details
     * Whoami
     */
    async whoami(initOverrides?: RequestInit | runtime.InitOverrideFunction): Promise<UserSelf> {
        const response = await this.whoamiRaw(initOverrides);
        return await response.value();
    }

}
