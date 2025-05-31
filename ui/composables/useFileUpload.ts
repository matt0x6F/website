import { useAuthStore } from '@/stores/auth'

/**
 * Upload files to the backend with authentication.
 * @param files Array of File objects to upload
 * @param postId Optional post ID to associate files with
 * @returns Array of uploaded file URLs
 */
export async function uploadFilesWithAuth(
  files: File[],
  postId?: number
): Promise<string[]> {
  const auth = useAuthStore()
  const uploadedUrls: string[] = []
  for (const file of files) {
    const formData = new FormData()
    formData.append('upload', file)
    if (postId) {
      const metadata = {
        visibility: 'public',
        posts: [postId],
      }
      formData.append('metadata', JSON.stringify(metadata))
    }
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/files/`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${auth.storedAccessToken}`,
        },
        body: formData,
      })
      if (!response.ok) {
        throw new Error(`Upload failed: ${response.statusText}`)
      }
      const fileMetadata = await response.json()
      uploadedUrls.push(fileMetadata.location)
    } catch (error) {
      console.error('Error uploading file:', error)
      // Optionally, you could throw or return error info here
    }
  }
  return uploadedUrls
} 