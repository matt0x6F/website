import { goto } from "$app/navigation";
import { PUBLIC_BASE_URL } from "$env/static/public";
import { Configuration, PostsApi, type PostDetails } from "$lib/api";
import { retrieveAccessToken } from "../../../../../stores/auth";
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
 
    const api = new PostsApi(config);
    const limit = 100;
    
    let offset = 0;
    let posts: PostDetails[] = [];
    let count: number = limit;
    let retry = 0;

    while (offset <= count) {
        try {
            const response = (await api.blogApiListPosts({ all: true, limit, offset }));
            // add posts to the posts array
            posts = posts.concat(response.items);
            count = response.count;

            offset += limit;
        } catch (e) {
            retry++;
            console.error(e);

            if (retry > 2) {
                break;
            }
        }
    }

    return {
        posts
    };
}