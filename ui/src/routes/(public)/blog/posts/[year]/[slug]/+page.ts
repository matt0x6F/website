import { PUBLIC_BASE_URL } from "$env/static/public";
import { Configuration, PostsApi, type PostDetails } from "$lib/api";
import { getAccessToken } from "../../../../../../stores/auth"
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
        slug: params.slug,
        createdAt: new Date(),
        updatedAt: new Date(),
        authorId: 0,
    }

    try {
        post = await api.blogApiGetPostBySlug({slug: params.slug, year: +params.year});

        console.log("Fetched post: " + post.id);
    } catch (error)
    {
        console.log("Error fetching posts: " + error);
    }

    return {
        post
    }
}