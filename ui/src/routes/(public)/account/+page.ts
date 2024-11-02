import { goto } from "$app/navigation";
import { PUBLIC_BASE_URL } from "$env/static/public";
import { AccountsApi, Configuration, type UserSelf } from "$lib/api";
import { retrieveAccessToken } from "../../../stores/auth";
import type { PageLoad } from "./$types";

export const load: PageLoad = async () => {
    let token = undefined;
    try {
        token = await retrieveAccessToken();
    } catch {
        goto('/login');
    }

    const config = new Configuration({
        basePath: PUBLIC_BASE_URL,
        headers: {
            "Authorization": "Bearer " + token
        }
    });

    const accountsAPI = new AccountsApi(config);

    let account: UserSelf = {
        id: -1,
        email: "",
        username: "",
        firstName: "",
        lastName: "",
        avatarLink: "",
        dateJoined: new Date(),
        isStaff: false,
        isActive: false,
    };
    

    try {
        account = await accountsAPI.accountsApiWhoami();
    } catch (error) {
        console.log("Error fetching account: " + error);
    }

    return {
        account: account
    }
}