import { mockServer } from './mockServer.js';
import type { CompletedRequest } from 'mockttp';
import { URL } from 'url';

const posts = [
  {
    title: 'JSON-LD Test Post',
    slug: 'test-post-jsonld',
    year: 2025,
    content: 'This is a test post for JSON-LD.'
  },
  {
    title: "Hello! I'm Matt",
    slug: 'hello-i-m-matt',
    year: 2025,
    content: 'This is a test post.'
  },
  {
    title: 'Test Post',
    slug: 'test-post',
    year: 2025,
    content: 'This is a test post.'
  },
  {
    title: 'Published Post',
    slug: 'published-post',
    year: 2025,
    content: 'Published content.'
  },
  {
    title: 'This is a test post',
    slug: 'this-is-a-test-post',
    year: 2025,
    content: 'Test content',
    sharecode: 'MHMip6m7DZKn3fmF',
    sharecodeResponse: {
      code: 200,
      body: {
        id: 5,
        title: 'This is a test post',
        content: 'Test content',
        created_at: '2025-05-18T02:53:01.410Z',
        updated_at: '2025-05-28T03:55:08.889Z',
        published_at: null,
        author: { id: 1, username: 'matt', email: 'm@ooo-yay.com', is_staff: true },
        slug: 'this-is-a-test-post',
        series: null,
      }
    },
    invalidSharecodeResponse: {
      code: 404,
      body: { detail: 'Post not found' }
    }
  },
  {
    title: 'OpenGraph Test Post',
    slug: 'test-post-og',
    year: 2025,
    content: 'This is a test post for OpenGraph.'
  }
];

export default async function globalSetup() {
  console.log('--- Starting globalSetup ---');
  await mockServer.start(4100);
  console.log('Mockttp started on 4100 (global setup)');

  // Log all requests received by mockttp for debugging
  await mockServer.forAnyRequest().thenCallback(req => {
    console.log('MOCKTTP RECEIVED:', req.url);
    return {};
  });

  // Register all post mocks, including sharecode logic
  for (const post of posts) {
    const path = `/api/posts/slug/${post.year}/${post.slug}`;
    console.log('Registering mock for:', path, 'sharecode:', post.sharecode);
    // If sharecode logic is present, register the sharecode variant and invalid handler
    if (post.sharecode && post.sharecodeResponse && post.invalidSharecodeResponse) {
      // Valid sharecode
      await mockServer.forGet(path)
        .withQuery({ sharecode: post.sharecode })
        .asPriority(2)
        .thenJson(post.sharecodeResponse.code, post.sharecodeResponse.body);

      // Any other sharecode (invalid)
      await mockServer.forGet(path)
        .matching((req: { url: string }) => {
          try {
            const url = new URL(req.url, 'http://localhost');
            const sharecode = url.searchParams.get('sharecode');
            const isInvalid = sharecode !== post.sharecode && sharecode !== null;
            if (isInvalid) {
              console.log('Returning 404 for', req.url);
            }
            return isInvalid;
          } catch {
            return false;
          }
        })
        .asPriority(2)
        .thenJson(post.invalidSharecodeResponse.code, post.invalidSharecodeResponse.body);
    }
    // Default: no sharecode (lowest priority)
    await mockServer.forGet(path)
      .matching((req: { url: string }) => {
        try {
          const url = new URL(req.url, 'http://localhost');
          const hasSharecode = url.searchParams.has('sharecode');
          const query = url.search;
          const isDefault = !query || query === '' || (!hasSharecode && url.searchParams.toString() === '');
          console.log('[Default handler] url:', req.url, 'query:', query, 'hasSharecode:', hasSharecode, 'isDefault:', isDefault);
          return isDefault;
        } catch (e) {
          console.log('[Default handler] error parsing url:', req.url, e);
          return true;
        }
      })
      .asPriority(1)
      .thenJson(200, {
        id: 100,
        title: post.title,
        content: post.content,
        created_at: '2025-05-18T02:53:01.410Z',
        updated_at: '2025-05-28T03:55:08.889Z',
        published_at: '2025-05-28T03:55:08.889Z',
        author: { id: 1, username: 'matt', email: 'm@ooo-yay.com', is_staff: true },
        slug: post.slug,
        series: null,
      });
    console.log('Registered mock for:', path);
  }

  // Register comments mock last
  await mockServer.forGet(/\/api\/comments\/.*/).thenJson(200, { items: [], count: 0 });
  console.log('Registered mock for: /api/comments/.*');

  // Catch-all logger for unmatched requests
  await mockServer.forAnyRequest().thenCallback(req => {
    console.log('[Catch-all] Unmatched request:', req.url);
    return { status: 501, body: 'No matching mock rule' };
  });
} 