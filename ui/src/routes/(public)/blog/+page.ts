import { PUBLIC_BASE_URL } from "$env/static/public";
import { Configuration, PostsApi, type PostDetails } from "$lib/api";
import { getAccessToken } from "../../../stores/auth"
import type { PageLoad } from "./$types"

export const load: PageLoad = async () => {
    const token = await getAccessToken();
    const config = new Configuration({
        basePath: PUBLIC_BASE_URL,
        headers: {
            "Authorization": "Bearer " + token
        }
    });
    const api = new PostsApi(config);

    let posts: PostDetails[] = [];

    try {
        posts = (await api.blogApiListPosts({all: false, limit: 10, offset: 0})).items;

        console.log("Fetched posts: " + posts.length);
    } catch (error)
    {
        console.log("Error fetching posts: " + error);
    }

    return {
        posts
    }
}