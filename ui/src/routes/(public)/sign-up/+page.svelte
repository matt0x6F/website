<script lang="ts">
	import { goto } from "$app/navigation";
	import { PUBLIC_BASE_URL } from "$env/static/public";
	import { AccountsApi, Configuration, TokenApi } from "$lib/api";


	import { Button, ButtonGroup, Input, InputAddon, Label } from "flowbite-svelte";
    import { LockSolid, UserCircleSolid, EnvelopeSolid } from 'flowbite-svelte-icons';
	import { setAccessToken, setRefreshToken, setUserData, setUsername } from "../../../stores/auth";
	import { addToast } from "../../../stores/notifications";

    let username = "";
    let email = "";
    let password = "";
    let password2 = "";
    let firstName = "";
    let lastName = "";

    const signUp = async () => {
        if (password !== password2) {
            addToast({
                message: "Passwords do not match"
            })
            return
        }

        const config = new Configuration({
            basePath: PUBLIC_BASE_URL
        })

        const tokenAPI = new TokenApi(config)
        const accountsAPI = new AccountsApi(config)
        
        try {
            let user = await accountsAPI.accountsApiSignUp({
                newAccount: {
                    username: username,
                    email: email,
                    password: password,
                    firstName: firstName,
                    lastName: lastName
                }
            })

            let tokens = await tokenAPI.tokenObtainPair({
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

<form on:submit|preventDefault={() => signUp()}>
    <div class="max-w-sm mx-auto">
        <div class="mb-6">
            <Label for="username" class="block mb-2">Username</Label>
            <ButtonGroup class="w-full">
                <InputAddon>
                    <UserCircleSolid class="w-4 h-4 text-gray-500 dark:text-gray-400" />
                </InputAddon>
                <Input id="username" bind:value={username} placeholder="mandretti" />
            </ButtonGroup>
        </div>

        <div class="mb-6">
            <Label for="email" class="block mb-2">Email</Label>
            <ButtonGroup class="w-full">
                <InputAddon>
                    <EnvelopeSolid class="w-4 h-4 text-gray-500 dark:text-gray-400" />
                </InputAddon>
                <Input type="email" id="email" bind:value={email} placeholder="mario@andretti.com" />
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

        <div class="mb-6">
            <Label for="password-verification" class="block mb-2">Password verification</Label>
            <ButtonGroup class="w-full">
                <InputAddon>
                    <LockSolid class="w-4 h-4 text-gray-500 dark:text-gray-400" />
                </InputAddon>
                <Input id="password-verification" disabled={password === ""} bind:value={password2} placeholder="password" type="password" />
            </ButtonGroup>
        </div>

        <div class="mb-6">
            <Label for="first-name" class="block mb-2">First name</Label>
            <ButtonGroup class="w-full">
                <InputAddon>
                    <UserCircleSolid class="w-4 h-4 text-gray-500 dark:text-gray-400" />
                </InputAddon>
                <Input id="first-name" bind:value={firstName} placeholder="Mario" />
            </ButtonGroup>
        </div>

        <div class="mb-6">
            <Label for="last-name" class="block mb-2">Last name</Label>
            <ButtonGroup class="w-full">
                <InputAddon>
                    <UserCircleSolid class="w-4 h-4 text-gray-500 dark:text-gray-400" />
                </InputAddon>
                <Input id="last-name" bind:value={lastName} placeholder="Andretti" />
            </ButtonGroup>
        </div>

        <div>
            <p>Already a user? <a href="/login">Log in!</a></p>
        </div>

        <div class="text-center">
            <Button type="submit">Sign up</Button>
        </div>
    </div>
</form>