<template>
  <div class="py-4">
    <div class="flex flex-col md:flex-row items-center gap-8 mb-10">
      <img src="/avatar_resized.png" alt="Matt" class="w-32 h-32 md:w-40 md:h-40 rounded-3xl object-cover shadow-lg flex-shrink-0">
      <div class="text-center md:text-left">
        <h1 class="text-4xl md:text-5xl mb-4">Hey, I'm Matt 👋</h1>
        <p>
          I'm a software engineer with a passion for platform engineering and developer tools.
          Throughout my career, I've worked on diverse platform and internal product teams,
          focusing on everything from compute scheduling to security and reliability products.
        </p>
      </div>
    </div>

    <div class="text-left">
      <section class="my-10">
        <h2 class="text-2xl md:text-3xl mb-4">What I'm Into</h2>
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div class="flex items-center gap-2 p-4 rounded-lg bg-gray-100 dark:bg-gray-800">
            <span class="text-2xl">🎵</span>
            <span>Music</span>
          </div>
          <div class="flex items-center gap-2 p-4 rounded-lg bg-gray-100 dark:bg-gray-800">
            <span class="text-2xl">💻</span>
            <span>Coding</span>
          </div>
          <div class="flex items-center gap-2 p-4 rounded-lg bg-gray-100 dark:bg-gray-800">
            <span class="text-2xl">🏔️</span>
            <span>Outdoors</span>
          </div>
          <div class="flex items-center gap-2 p-4 rounded-lg bg-gray-100 dark:bg-gray-800">
            <span class="text-2xl">🌱</span>
            <span>Urban Agriculture</span>
          </div>
        </div>
      </section>

      <section class="mb-10">
        <h2 class="text-2xl md:text-3xl mb-4">Currently</h2>
        <p class="mb-4">
          I live in the Pacific Northwest with my dog Peach 🐕. 
          When I'm not coding, you might find me tending to my urban garden
          or exploring the beautiful PNW outdoors.
        </p>
        <p>
          I'm also proud to be a co-maintainer of the 
          <a href="https://gomods.io" target="_blank" rel="noopener" class="text-primary hover:underline">Athens Project</a>,
          helping to build better tools for the Go community.
        </p>
      </section>
    </div>
  </div>
</template>
