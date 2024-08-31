import { goto } from "$app/navigation";
import { PUBLIC_BASE_URL } from "$env/static/public";
import { Configuration, PostsApi, type PostDetails } from "$lib/api";
import { getAccessToken } from "../../../../../stores/auth"
import type { PageLoad } from "./$types"

export const load: PageLoad = async ({ params }) => {
    const token = await getAccessToken();
    const config = new Configuration({
        basePath: PUBLIC_BASE_URL,
        headers: {
            "Authorization": "Bearer " + token
        }
    });
    const api = new PostsApi(config);
    let post: PostDetails = {
        id: 0,
        title: "",
        content: "",
        createdAt: new Date(),
        updatedAt: new Date(),
        authorId: 0,
        slug: ""
    }

    try {
        // conver string param to number
        post = (await api.blogApiGetPostById({id: +params.id}));

        
    } catch (error)
    {
        console.log("Error fetching posts: " + error);
        goto("/admin/write");
    }

    return {
        post
    }
}