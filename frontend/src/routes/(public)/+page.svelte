<script lang="ts">
	import BrandPython from 'svelte-tabler/BrandPython.svelte';
	import BrandGolang from 'svelte-tabler/BrandGolang.svelte';
	import Wood from 'svelte-tabler/Wood.svelte';
	import Sun from 'svelte-tabler/Sun.svelte';
	import Music from 'svelte-tabler/Music.svelte';
	import Braces from 'svelte-tabler/Braces.svelte';
</script>

<div class="text-center">
	<h1
		class="inline-block bg-gradient-to-r from-orange-500 via-orange-600 to-purple-600 bg-clip-text text-2xl font-semibold text-transparent dark:border-2 dark:border-white"
	>
		Hello! I'm Matt
	</h1>

	<p>I'm a <span class="font-semibold">distributed systems software engineer</span> by trade.</p>

	<p>
		I enjoy <Wood size="24" class="inline-block text-amber-700" /> woodworking, <Sun
			size="24"
			class="inline-block text-yellow-400"
		/> the outdoors, <Music size="24" class="inline-block text-blue-500" /> music, and <Braces
			size="24"
			class="inline-block text-green-500"
		/> computers. I also like to build things.
	</p>

	<p>
		My favorite programming languages are <BrandPython size="24" class="inline-block" /> Python and <BrandGolang
			size="24"
			class="inline-block"
		/> Go, but I can write in a lot of languages.
	</p>

	<p>You can catch me around the Pacific Northwest or the Bay Area.</p>
</div>
