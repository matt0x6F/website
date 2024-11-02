import { PUBLIC_BASE_URL } from "$env/static/public";
import { AccountsApi, Configuration, type AdminUserDetails } from "$lib/api";
import type { PageLoad } from "./$types";
import { retrieveAccessToken } from "../../../../../stores/auth";
import { goto } from "$app/navigation";

export const load: PageLoad = async (params) => {
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
 
    const api = new AccountsApi(config);

    let user: AdminUserDetails = {
        id: 0,
        username: "",
        email: "",
        groups: [],
        firstName: "",
        lastName: "",
        avatarLink: "",
        isStaff: false,
        isActive: false,
        isSuperuser: false,
        dateJoined: new Date(),
        lastLogin: new Date(),
        userPermissions: [],
    }

    try {
        user = (await api.accountsApiGetUser({ userId: +params.params.id }));
    } catch (e) {
        console.error(e);
    }
    
    return {
        user: user
    };
}