import { PUBLIC_BASE_URL } from "$env/static/public";
import { AccountsApi, Configuration, type FileDetails, type UserDetails } from "$lib/api";
import type { PageLoad } from "./$types";
import { getAccessToken } from "../../../../../stores/auth";

export const load: PageLoad = async (params) => {
    const token = await getAccessToken();
    const config = new Configuration({
        basePath: PUBLIC_BASE_URL,
        headers: {
            "Authorization": "Bearer " + token
        }
    });
 
    const api = new AccountsApi(config);

    let user: UserDetails = {
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