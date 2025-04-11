import { PUBLIC_BASE_URL } from "$env/static/public";
import { Configuration, FilesApi, type FileDetails } from "$lib/api";
import type { PageLoad } from "./$types";
import { retrieveAccessToken } from "../../../../stores/auth";
import { goto } from "$app/navigation";

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
 
    const api = new FilesApi(config);
    const limit = 25;
    const offset = 0;

    let files: FileDetails[] = [];
    let count: number = 0;

    try {
        const response = (await api.blogApiListFiles({ visibility: "all" }));
        files = response.items;
        count = response.count;
    } catch (e) {
        console.error(e);
    }
    
    return {
        files,
        count,
        limit,
        offset
    };
}