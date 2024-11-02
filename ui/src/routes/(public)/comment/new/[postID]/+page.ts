import { PUBLIC_BASE_URL } from '$env/static/public';
import { CommentsApi, Configuration, type CommentList } from '$lib/api';
import { retrieveAccessToken } from '../../../../../stores/auth';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({params, url}) => {
    const parentID = url.searchParams.get("parent");
    let parent: CommentList | null = null;
    const postID = params.postID;

    if (parentID !== null) {
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
    
        try {
            const commentsAPI = new CommentsApi(config);

            parent = await commentsAPI.blogApiGetComment({id: +parentID});
            
            console.log("Fetched parent comment: " + parent.id);
        } catch (error) {
            console.log("Error fetching parent comment: " + error);
        }
        
    }

    return {
        parentID,
        parent,
        postID
    }
}