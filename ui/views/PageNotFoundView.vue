<script setup lang="ts">
import { ref, onMounted } from 'vue'

const messages = [
  "Looks like this page took a wrong turn at Albuquerque...",
  "This page is playing hide and seek (and winning!)",
  "Whoops! This page has gone on vacation without leaving a forwarding address",
  "Error 404: Page got lost in the digital wilderness",
  "This page has achieved quantum superposition - it both exists and doesn't exist",
  "Looks like you've found our page collection's empty spot",
  "This page is in another castle",
  "The page you're looking for is having an existential crisis",
  "Our hamsters lost this page while powering the servers",
  "Plot twist: This page was never here to begin with"
]

const randomMessage = ref(messages[0])

onMounted(() => {
  document.title = '404 – Page Not Found – ooo-yay.com'
  randomMessage.value = messages[Math.floor(Math.random() * messages.length)]
})
</script>

<template>
  <div class="flex flex-col items-center justify-center min-h-[80vh] text-center p-5">
    <h1 class="text-[120px] m-0 font-bold neon-text relative">
      <span class="neon-flicker">4</span>
      <span class="neon-flicker-alt">0</span>
      <span class="neon-flicker">4</span>
    </h1>
    <div class="my-5">
      <h2 class="text-3xl mb-3">Oops! Page Not Found</h2>
      <p class="text-lg">{{ randomMessage }}</p>
      <p class="text-4xl font-mono my-5">¯\_(ツ)_/¯</p>
    </div>
    <NuxtLink 
      to="/" 
      class="inline-block px-6 py-3 bg-blue-500 text-white rounded-lg transition-colors hover:bg-blue-600"
    >
      Take me back home
    </NuxtLink>
  </div>
</template>

<style>
.neon-text {
  color: #fff;
  text-shadow: 
    0 0 4px #fff,
    0 0 8px #fff,
    0 0 12px #fff,
    0 0 20px #a855f7,
    0 0 35px #a855f7,
    0 0 40px #a855f7,
    0 0 50px #a855f7;
}

@keyframes flicker {
  0%, 18%, 22%, 25%, 53%, 57%, 100% {
    text-shadow: 
      0 0 4px #fff,
      0 0 8px #fff,
      0 0 12px #fff,
      0 0 20px #a855f7,
      0 0 35px #a855f7,
      0 0 40px #a855f7,
      0 0 50px #a855f7;
  }
  20%, 24%, 55% {
    text-shadow: none;
  }
}

@keyframes flicker-alt {
  0%, 19%, 21%, 23%, 25%, 54%, 56%, 100% {
    text-shadow: 
      0 0 4px #fff,
      0 0 8px #fff,
      0 0 12px #fff,
      0 0 20px #a855f7,
      0 0 35px #a855f7,
      0 0 40px #a855f7,
      0 0 50px #a855f7;
  }
  20%, 22%, 55% {
    text-shadow: none;
  }
}

.neon-flicker {
  animation: flicker 2.5s infinite alternate;
}

.neon-flicker-alt {
  animation: flicker-alt 3s infinite alternate;
}

/* Add a subtle reflection effect */
.neon-text::after {
  content: "";
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  height: 100px;
  background: linear-gradient(180deg, rgba(168, 85, 247, 0.2) 0%, transparent 100%);
  filter: blur(20px);
  opacity: 0.5;
  transform: scaleY(-1);
  pointer-events: none;
}
</style>
