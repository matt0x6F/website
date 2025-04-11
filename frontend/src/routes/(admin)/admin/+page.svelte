<script lang="ts">
	import {
		Button,
		ButtonGroup,
		Table,
		TableBody,
		TableBodyCell,
		TableBodyRow,
		TableHead,
		TableHeadCell
	} from 'flowbite-svelte';
	import type { PageData } from './$types';
	import { EyeSolid } from 'flowbite-svelte-icons';
	import DeleteButton from '$lib/components/DeleteButton.svelte';
	import { addToast } from '../../../stores/notifications';
	import { formatBytes } from '$lib/utils';

	export let data: PageData;

	let draftPosts = data.draftPosts;
	let publishedPosts = data.publishedPosts;
	let users = data.users;
	let files = data.files;
	let comments = data.comments;

	function formatDate(date: Date | null | undefined): string {
		if (!date) {
			return '';
		}

		const daysOfWeek = [
			'Sunday',
			'Monday',
			'Tuesday',
			'Wednesday',
			'Thursday',
			'Friday',
			'Saturday'
		];
		const months = [
			'January',
			'February',
			'March',
			'April',
			'May',
			'June',
			'July',
			'August',
			'September',
			'October',
			'November',
			'December'
		];

		const dayOfWeek = daysOfWeek[date.getDay()];
		const month = months[date.getMonth()];
		const day = date.getDate();
		const year = date.getFullYear();
		const hours = String(date.getHours()).padStart(2, '0');
		const minutes = String(date.getMinutes()).padStart(2, '0');

		// Function to get the correct ordinal suffix
		function getOrdinalSuffix(day: number): string {
			if (day > 3 && day < 21) return 'th'; // Handles 11th, 12th, 13th
			switch (day % 10) {
				case 1:
					return 'st';
				case 2:
					return 'nd';
				case 3:
					return 'rd';
				default:
					return 'th';
			}
		}

		const dayWithSuffix = day + getOrdinalSuffix(day);

		return `${dayOfWeek}, ${month} the ${dayWithSuffix}, ${year} @ ${hours}:${minutes}`;
	}

	function formatPostYear(date: Date | null | undefined): string {
		if (!date) {
			return new Date().getFullYear().toString();
		}

		return date.getFullYear().toString();
	}

	async function removeDraft(event: CustomEvent<{ postID: number }>) {
		// search through draftPosts and delete the post with the matching ID
		draftPosts = draftPosts.filter((post) => post.id !== event.detail.postID);

		addToast({
			message: 'Deleted draft post'
		});
	}
</script>

<p class="my-4">The admin interface provides a birds-eye view of the admin utilities.</p>

<div class="my-6 space-x-4">
	<p class="inline-block"><a href="/admin/write">Write something new</a></p>
	<p class="inline-block">
		<a href="/admin/comments/queue">Manage comment queue ({comments.length})</a>
	</p>
</div>

<div class="w-screen-2xl flex max-w-screen-2xl flex-col space-y-2">
	<div class="flex-auto basis-1/2">
		<h2 class="text-lg font-bold">Published posts</h2>
		<Table hoverable>
			<TableHead>
				<TableHeadCell>Title</TableHeadCell>
				<TableHeadCell>Author</TableHeadCell>
				<TableHeadCell>Published</TableHeadCell>
				<TableHeadCell></TableHeadCell>
			</TableHead>
			<TableBody tableBodyClass="divide-y">
				{#each publishedPosts as publishedPost}
					{#key publishedPost.id}
						<TableBodyRow>
							<TableBodyCell
								><a href="/admin/write/{publishedPost.id}">{publishedPost.title}</a></TableBodyCell
							>
							<TableBodyCell>{publishedPost.authorId}</TableBodyCell>
							<TableBodyCell>{formatDate(publishedPost.published)}</TableBodyCell>
							<TableBodyCell class="text-right">
								<ButtonGroup class="*:!ring-primary-700">
									<Button
										size="xs"
										href="/blog/posts/{formatPostYear(
											publishedPost.published
										)}/{publishedPost.slug}"
									>
										<EyeSolid class="inline-block" ariaLabel="Preview this post" />
										View
									</Button>
								</ButtonGroup>
							</TableBodyCell>
						</TableBodyRow>
					{/key}
				{:else}
					<TableBodyRow>
						<TableBodyCell>No published posts</TableBodyCell>
						<TableBodyCell></TableBodyCell>
						<TableBodyCell></TableBodyCell>
						<TableBodyCell></TableBodyCell>
					</TableBodyRow>
				{/each}
			</TableBody>
		</Table>
	</div>
	<!-- Drafts -->
	<div class="flex-auto basis-1/2">
		<h2 class="text-lg font-bold">Draft posts</h2>
		<Table hoverable>
			<TableHead>
				<TableHeadCell>Title</TableHeadCell>
				<TableHeadCell>Author</TableHeadCell>
				<TableHeadCell></TableHeadCell>
			</TableHead>
			<TableBody tableBodyClass="divide-y">
				{#each draftPosts as draftPost}
					{#key draftPost.id}
						<TableBodyRow>
							<TableBodyCell
								><a href="/admin/write/{draftPost.id}">{draftPost.title}</a></TableBodyCell
							>
							<TableBodyCell>{draftPost.authorId}</TableBodyCell>
							<TableBodyCell class="text-right">
								<ButtonGroup class="*:!ring-primary-700">
									<Button
										size="xs"
										href="/blog/drafts/{formatPostYear(draftPost.published)}/{draftPost.id}"
									>
										<EyeSolid class="inline-block" ariaLabel="Preview this post" />
										Preview
									</Button>
									<DeleteButton postID={draftPost.id} on:postDeleted={removeDraft} />
								</ButtonGroup>
							</TableBodyCell>
						</TableBodyRow>
					{/key}
				{:else}
					<TableBodyRow>
						<TableBodyCell>No drafts</TableBodyCell>
						<TableBodyCell></TableBodyCell>
						<TableBodyCell></TableBodyCell>
					</TableBodyRow>
				{/each}
			</TableBody>
		</Table>
	</div>
</div>

<hr class="my-4 border-orange-300" />

<div class="flex w-full flex-row space-x-4">
	<div class="flex-grow">
		<h2 class="text-lg font-bold">Users</h2>
		<Table hoverable>
			<TableHead>
				<TableHeadCell>Username</TableHeadCell>
				<TableHeadCell>Name</TableHeadCell>
				<TableHeadCell>Email</TableHeadCell>
				<TableHeadCell>Groups</TableHeadCell>
				<TableHeadCell></TableHeadCell>
			</TableHead>
			<TableBody tableBodyClass="divide-y">
				{#each users as user}
					{#key user.id}
						<TableBodyRow>
							<TableBodyCell>{user.username}</TableBodyCell>
							<TableBodyCell>{user.firstName} {user.lastName}</TableBodyCell>
							<TableBodyCell>{user.email}</TableBodyCell>
							<TableBodyCell>{user.groups}</TableBodyCell>
							<TableBodyCell class="text-right">
								<ButtonGroup class="*:!ring-primary-700">
									<Button size="xs" href="/admin/users/{user.id}">View</Button>
									<Button size="xs" href="/admin/users/{user.id}/edit">Edit</Button>
								</ButtonGroup>
							</TableBodyCell>
						</TableBodyRow>
					{/key}
				{:else}
					<TableBodyRow>
						<TableBodyCell>No users</TableBodyCell>
						<TableBodyCell></TableBodyCell>
						<TableBodyCell></TableBodyCell>
						<TableBodyCell></TableBodyCell>
					</TableBodyRow>
				{/each}
			</TableBody>
		</Table>
	</div>
</div>

<hr class="my-4 border-orange-300" />

<div class="flex w-full flex-row space-x-4">
	<div class="flex-grow">
		<h2 class="text-lg font-bold">Files</h2>
		<Table hoverable>
			<TableHead>
				<TableHeadCell>Filename</TableHeadCell>
				<TableHeadCell>Size</TableHeadCell>
				<TableHeadCell>Uploaded</TableHeadCell>
				<TableHeadCell>Visibility</TableHeadCell>
				<TableHeadCell></TableHeadCell>
			</TableHead>
			<TableBody tableBodyClass="divide-y">
				{#each files as file}
					{#key file.id}
						<TableBodyRow>
							<TableBodyCell>{file.name}</TableBodyCell>
							<TableBodyCell>{formatBytes(file.size)}</TableBodyCell>
							<TableBodyCell>{formatDate(file.createdAt)}</TableBodyCell>
							<TableBodyCell>{file.visibility}</TableBodyCell>
							<TableBodyCell class="text-right">
								<ButtonGroup class="*:!ring-primary-700">
									<Button size="xs" href="/admin/files/{file.id}">View</Button>
								</ButtonGroup>
							</TableBodyCell>
						</TableBodyRow>
					{/key}
				{:else}
					<TableBodyRow>
						<TableBodyCell>No files</TableBodyCell>
						<TableBodyCell></TableBodyCell>
						<TableBodyCell></TableBodyCell>
						<TableBodyCell></TableBodyCell>
					</TableBodyRow>
				{/each}
			</TableBody>
		</Table>
	</div>
</div>
