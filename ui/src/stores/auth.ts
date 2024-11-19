import { AccountsApi, Configuration, TokenApi, type UserSelf } from "$lib/api";
import { getCookie, setCookie, removeCookie } from "typescript-cookie"
import { PUBLIC_BASE_URL } from "$env/static/public";
import  { type Writable, writable } from "svelte/store";

export const userDetailsStore: Writable<UserSelf | undefined> = writable(undefined);

export const getUserDetails = async (): Promise<UserSelf> => {
    const accessToken = getCookie("access_token");

    if (!accessToken) {
        throw new Error("Access token not found");
    }

    const config = new Configuration({
        basePath: PUBLIC_BASE_URL,
        headers: {
            "Authorization": "Bearer " + accessToken
        }
    })

    const api = new AccountsApi(config)

    const payload = await api.accountsApiWhoami()

    userDetailsStore.set(payload)

    return payload
}

export const retrieveAccessToken = async (): Promise<string> => {
    let accessToken = getCookie("access_token");
    let refreshToken = getCookie("refresh_token");

    // verify the token
    if (accessToken && refreshToken) {
        const config = new Configuration({
            basePath: PUBLIC_BASE_URL,
        })

        const api = new TokenApi(config);

        try {
            await api.tokenVerify({tokenVerifyInputSchema: {token: accessToken}})
        } catch (error) {
            console.error("Error validating access token");

            removeCookie("access_token");
            accessToken = undefined;
        }
    }

    // refresh the token
    if (!accessToken && refreshToken) {
        console.log("Attempting to refresh access token");

        const config = new Configuration({
            basePath: PUBLIC_BASE_URL,
        })

        const api = new TokenApi(config);

        try {
            const response = await api.tokenRefresh({tokenRefreshInputSchema: { refresh: refreshToken}})
            if (!response.access) {
                throw new Error("Error refreshing access token");
            }

            // expires in 5 minutes
            setCookie("access_token", response.access, {path:"/", expires: new Date().getTime() + 300000});
            // expires in 24 hours
            setCookie("refresh_token", response.refresh, {path: "/", expires: new Date().getTime() + 86400000});

            accessToken = response.access;
            refreshToken = response.refresh;
        } catch (error) {
            console.error("Error refreshing access token: ", error);

            removeCookie("access_token");
            removeCookie("refresh_token");

            accessToken = "";
            refreshToken = "";

            throw new Error("Error refreshing access token");
        }
    }

    if (!accessToken) {
        throw new Error("Access token not found");
    }

    console.log("Access token: ", accessToken);

    return accessToken;
}
