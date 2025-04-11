import { PUBLIC_BASE_URL } from "$env/static/public";
import { Configuration, PostsApi, type PostDetails } from "$lib/api";
import { retrieveAccessToken } from "../../../../../../stores/auth"
import type { PageLoad } from "./$types"

export const load: PageLoad = async ({ params }) => {
    let token = undefined;
    try {
        token = await retrieveAccessToken();
    } catch {
        console.log("No access token found, fetching without one")
    }

    const config = new Configuration({
        basePath: PUBLIC_BASE_URL,
        headers: {
            "Authorization": "Bearer " + token
        }
    });
    const api = new PostsApi(config);

    let post: PostDetails = {
        id: +params.id,
        title: "",
        content: "",
        slug: "",
        createdAt: new Date(),
        updatedAt: new Date(),
        authorId: 0,
    }

    try {
        post = await api.blogApiGetPostById({id: +params.id});

        console.log("Fetched post: " + post.id);
    } catch (error)
    {
        console.log("Error fetching posts: " + error);
    }

    return {
        post
    }
}