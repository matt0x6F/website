import { getLocal } from 'mockttp';

export const mockServer = getLocal();

mockServer.on('request', req => {
  console.log('Mockttp received:', req.method, req.url);
  if (typeof req.url === 'string') {
    console.log('Raw URL string:', req.url);
  }
});
mockServer.on('request-initiated', req => {
  console.log('Request initiated:', req.method, req.url);
});

// Add a helper to start and log
export async function startMockServer() {
  await mockServer.start(4100);
  console.log('Mockttp started on 4100');
} 