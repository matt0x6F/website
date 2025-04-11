<script setup lang="ts">
import { PiLog, PiSun, PiMusicNote, PiBracketsCurly } from 'vue-icons-plus/pi'
import { BiLogoPython, BiLogoGoLang } from 'vue-icons-plus/bi'
</script>

<template>
  <div class="text-center">
    <h1 class="text-2xl font-semibold bg-clip-text inline-block text-transparent bg-gradient-to-r from-orange-500 via-orange-600 to-purple-600">Hello! I'm Matt</h1>

    <p>I'm a <span class="font-semibold">distributed systems software engineer</span> by trade</p>

    <p>I enjoy <PiLog size=24 class="text-amber-700 inline-block" /> woodworking, <PiSun size=24 class="inline-block text-yellow-500 dark:text-yellow-400" /> the outdoors, <PiMusicNote size=24 class="inline-block text-blue-500" /> music, and <PiBracketsCurly size=24 class="inline-block text-green-500" /> computers. I also like to build things</p>

    <p>My favorite programming languages are <BiLogoPython size=24 class="inline-block" /> Python and <BiLogoGoLang size=24 class="inline-block" /> Go, but I can write in a lot of languages</p>

    <p>You can catch me around the Pacific Northwest or the Bay Area</p>
  </div>
</template>

<style scoped>

</style>