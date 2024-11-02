import { AccountsApi, Configuration, TokenApi, type UserSelf } from "$lib/api";
import { getCookie, setCookie, removeCookie } from "typescript-cookie"
import { PUBLIC_BASE_URL } from "$env/static/public";

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

    return await api.accountsApiWhoami()
}


// This function will remove both the access and refresh tokens from the cookies.
export const getRefreshToken = async (): Promise<string | undefined> => {
    const refreshToken = getCookie("refresh_token");

    if (!refreshToken) {
        return undefined;
    }

    return refreshToken;
}

export const getUserData = (): UserSelf | undefined => {
    const userData = getCookie("user_data")
    if (!userData) {
        return undefined
    }

    return JSON.parse(userData)
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
            console.error("Error validating access token. Attempting to refresh token: ", error);

            accessToken = undefined;    
        }
    }

    // refresh the token
    if (!accessToken && refreshToken) {
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
            setCookie("access_token", response.access, {expires: new Date().getTime() + 300000});
            // expires in 24 hours
            setCookie("refresh_token", response.refresh, {expires: new Date().getTime() + 86400000});

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

    return accessToken;
}
