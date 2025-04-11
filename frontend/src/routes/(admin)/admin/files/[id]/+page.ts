import { PUBLIC_BASE_URL } from "$env/static/public";
import { Configuration, FilesApi, type FileDetails } from "$lib/api";
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
 
    const api = new FilesApi(config);

    let file: FileDetails = {
        id: 0,
        name: "",
        size: 0,
        visibility: "",
        location: "",
        createdAt: new Date(),
        contentType: "",
        charset: "",
        posts: []
    }

    try {
        file = (await api.blogApiGetFile({ id: +params.params.id }));
    } catch (e) {
        console.error(e);
    }
    
    return {
        file
    };
}