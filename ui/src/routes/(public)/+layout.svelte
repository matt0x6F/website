<script lang="ts">
	import Navigation from '$lib/components/Navigation.svelte';
    import '../../app.css';
</script>

<Navigation staffOnly={false}>
    <slot></slot>
</Navigation>