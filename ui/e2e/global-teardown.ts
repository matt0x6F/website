import { mockServer } from './mockServer.js';

export default async function globalTeardown() {
  await mockServer.stop();
  console.log('Mockttp stopped (global teardown)');
} 