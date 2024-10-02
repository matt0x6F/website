<script lang="ts">
	import { goto } from "$app/navigation";
	import { PUBLIC_BASE_URL } from "$env/static/public";
	import { Configuration, TokenApi } from "$lib/api";


	import { Button, ButtonGroup, Input, InputAddon, Label } from "flowbite-svelte";
    import { LockSolid, UserCircleSolid } from 'flowbite-svelte-icons';
	import { setAccessToken, setRefreshToken, setUserData, setUsername } from "../../../stores/auth";
	import { addToast } from "../../../stores/notifications";

    let username = "";
    let password = "";

    const signIn = async () => {
        const config = new Configuration({
            basePath: PUBLIC_BASE_URL
        })

        const client = new TokenApi(config)
        
        try {
            let tokens = await client.tokenObtainPair({
                tokenObtainPairInputSchema: {
                    username: username,
                    password: password
                }
            })

            setAccessToken(tokens.access);
            setRefreshToken(tokens.refresh);
            setUsername(tokens.username);

            // populates user data
            await setUserData()
            
            addToast({
                message: "You're logged in!"
            })

            goto("/");
        } catch (error) {
            console.log("Error while signing in " + error)
        }
    }
</script>

<form on:submit|preventDefault={() => signIn()}>
    <div class="max-w-sm mx-auto">
        <div class="mb-6">
            <Label for="username" class="block mb-2">Username</Label>
            <ButtonGroup class="w-full">
                <InputAddon>
                    <UserCircleSolid class="w-4 h-4 text-gray-500 dark:text-gray-400" />
                </InputAddon>
                <Input id="username" bind:value={username} placeholder="your username" />
            </ButtonGroup>
        </div>
        
        <div class="mb-6">
            <Label for="password" class="block mb-2">Password</Label>
            <ButtonGroup class="w-full">
                <InputAddon>
                    <LockSolid class="w-4 h-4 text-gray-500 dark:text-gray-400" />
                </InputAddon>
                <Input id="password" bind:value={password} placeholder="password" type="password" />
            </ButtonGroup>
        </div>

        <div>
            <p>Not a user? <a href="/sign-up">Sign up!</a></p>
        </div>

        <div class="text-center">
            <Button type="submit">Login</Button>
        </div>
    </div>
</form>