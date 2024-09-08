import { AccountsApi, Configuration, TokenApi, type UserSelf } from "$lib/api";
import { getCookie, setCookie, removeCookie } from "typescript-cookie"
import { PUBLIC_BASE_URL } from "$env/static/public";
import { writable, type Writable } from "svelte/store";

// This function will check if the user is authenticated. It will return true if the user is authenticated, and false otherwise.
// It will refresh the access token if it is expired and a valid refresh token is present.
export const isAuthenticated = async (): Promise<boolean> => {
    let accessToken = await getAccessToken();

    console.log("Checking if user is authenticated");

    if (!accessToken) {
        console.log("User is not authenticated");

        return false;
    }

    return true;
}

export const setUsername = (username: string) => {
    console.log("Setting username");

    usernameStore.set(username);
    authenticatedStore.set(true);

    setCookie("username", username, { path: "/", expires: new Date(Date.now() + 24*60*60000)})
}

// This function will set the access token in the cookies. It will expire in 5 minutes.
export const setAccessToken = (token: string) => {
    console.log("Setting access token");

    authenticatedStore.set(true);

    // 5 * 60000 = 5 minutes
    setCookie("access_token", token, { path: "/", expires: new Date(Date.now() + 5*60000)});
}

// This function will set the refresh token in the cookies. It will expire in 24 hours.
export const setRefreshToken = (token: string) => {
    console.log("Setting refresh token");

    authenticatedStore.set(true);

    // 24 * 60 * 60000 = 24 hours
    setCookie("refresh_token", token, { path: "/", expires: new Date(Date.now() + 24*60*60000)});
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
    await api.accountsApiWhoami().then((user) => {
        userDataStore.set(user)
        setCookie("user_data", JSON.stringify(user), { path: "/", expires: new Date(Date.now() + 24*60*60000)})

        setUsername(user.username);
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
    userDataStore.set({
        username: "",
        email: "",
        firstName: "",
        lastName: "",
        id: 0,
        isActive: false,
        isStaff: false,
        dateJoined: new Date(),
    })
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

    let config = new Configuration({
        basePath: PUBLIC_BASE_URL,
    })

    let api = new TokenApi(config);


    // access token is missing
    if (!accessToken) {
        let refreshToken = await getRefreshToken();
        if (!refreshToken) {
            return undefined;
        }

        console.log("Making call to refresh token with URL: " + PUBLIC_BASE_URL);

        api.tokenRefresh({tokenRefreshInputSchema: { refresh: refreshToken}}).then((response) => {
            if (!response.access) {
                refreshToken = undefined;
                return
            }

            setAccessToken(response.access);
            setRefreshToken(response.refresh);

            accessToken = response.access;
            refreshToken = response.refresh;

            return accessToken
        }).catch((error) => {
            console.error(error);

            refreshToken = undefined;
            return ""
        });
    }

    // validate the access token
    if (accessToken !== undefined) {
        try {
            api.tokenVerify({tokenVerifyInputSchema: {token: accessToken}})
        } catch {
            let refreshToken = await getRefreshToken();
            if (!refreshToken) {
                return undefined;
            }
    
            console.log("Making call to refresh token with URL: " + PUBLIC_BASE_URL);
    
            api.tokenRefresh({tokenRefreshInputSchema: { refresh: refreshToken}}).then((response) => {
                if (!response.access) {
                    refreshToken = undefined;
                    return
                }
    
                setAccessToken(response.access);
                setRefreshToken(response.refresh);
    
                accessToken = response.access;
                refreshToken = response.refresh;

                return accessToken
            }).catch((error) => {
                console.error(error);
    
                refreshToken = undefined;
                return ""
            });
        }
    }


    return accessToken;
}

export const usernameStore = writable("");
export const authenticatedStore = writable(false);
export const userDataStore: Writable<UserSelf> = writable({
    username: "",
    email: "",
    firstName: "",
    lastName: "",
    id: 0,
    isActive: false,
    isStaff: false,
    isSuperuser: false,
    dateJoined: new Date(),
    lastLogin: new Date(),
    groups: [],
    userPermissions: [],
    userGroups: []
});
