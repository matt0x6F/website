import { AccountsApi, Configuration, TokenApi, type UserSelf } from "$lib/api";
import { getCookie, setCookie, removeCookie } from "typescript-cookie"
import { PUBLIC_BASE_URL } from "$env/static/public";
import { writable } from "svelte/store";

// This function will check if the user is authenticated. It will return true if the user is authenticated, and false otherwise.
// It will refresh the access token if it is expired and a valid refresh token is present.
export const isAuthenticated = async (): Promise<boolean> => {
    let accessToken = await getAccessToken();

    if (!accessToken) {
        return false;
    }

    return true;
}

export const setUsername = (username: string) => {
    console.log("Setting username");

    usernameStore.set(username);
    authenticatedStore.set(true);

    setCookie("username", username, { expires: new Date(Date.now() + 24*60*60000)})
}

// This function will set the access token in the cookies. It will expire in 5 minutes.
export const setAccessToken = (token: string) => {
    console.log("Setting access token");

    authenticatedStore.set(true);

    // 5 * 60000 = 5 minutes
    setCookie("access_token", token, { expires: new Date(Date.now() + 5*60000)});
}

// This function will set the refresh token in the cookies. It will expire in 24 hours.
export const setRefreshToken = (token: string) => {
    console.log("Setting refresh token");

    authenticatedStore.set(true);

    // 24 * 60 * 60000 = 24 hours
    setCookie("refresh_token", token, { expires: new Date(Date.now() + 24*60*60000)});
}

export const setUserData = async () => {
    const token = await getAccessToken()

    const config = new Configuration({
        basePath: PUBLIC_BASE_URL,
        headers: {
            "Authorization": "Bearer " + token
        }
    })

    let api = new AccountsApi(config)
    await api.accountsUrlsWhoami().then((user) => {
        userDataStore.set(user)
        setCookie("user_data", JSON.stringify(user), { expires: new Date(Date.now() + 24*60*60000)})
    }).catch((error) => {
        console.log("Error while fetching WhoAmI endpoint " + error)
    })
}

// This function will remove the access token from the cookies.
export const removeAccessToken = () => {
    console.log("Removing access token");

    authenticatedStore.set(false);

    removeCookie("access_token");
}

export const removeUsername = () => {
    removeCookie("username")

    usernameStore.set("");
    authenticatedStore.set(false);
}

// This function will remove the refresh token from the cookies.
export const removeRefreshToken = () => {
    console.log("Removing refresh token");

    authenticatedStore.set(false);

    removeCookie("refresh_token");
}

export const removeUserData = () => {
    userDataStore.set({})
    removeCookie("userData")
}

export const getUsername = (): string => {
    const username = getCookie("username")
    if (username != undefined) {
        return username
    }

    return ""
}

// This function will remove both the access and refresh tokens from the cookies.
export const getRefreshToken = async (): Promise<string | undefined> => {
    let refreshToken = getCookie("refresh_token");

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

// This function will return the access token if it is present in the cookies. If a refresh token is present, it will attempt to refresh the access token.
export const getAccessToken = async (): Promise<string | undefined> => {
    let accessToken = getCookie("access_token");

    if (!accessToken) {
        let refreshToken = await getRefreshToken();
        if (!refreshToken) {
            return undefined;
        }

        console.log("Making call to refresh token with URL: " + PUBLIC_BASE_URL);

        let config = new Configuration({
            basePath: PUBLIC_BASE_URL,
        })

        let api = new TokenApi(config);
        api.tokenRefresh({tokenRefreshInputSchema: { refresh: refreshToken}}).then((response) => {
            if (!response.access) {
                refreshToken = undefined;
                return
            }

            setAccessToken(response.access);
            setRefreshToken(response.refresh);

            accessToken = response.access;
            refreshToken = response.refresh;
        }).catch((error) => {
            console.error(error);

            refreshToken = undefined;
            return
        });
    }

    return accessToken;
}

export const usernameStore = writable(getUsername());
export const authenticatedStore = writable(false);
export const userDataStore = writable({})

