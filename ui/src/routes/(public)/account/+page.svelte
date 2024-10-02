<script lang="ts">
	import { goto } from "$app/navigation";
	import { PUBLIC_BASE_URL } from "$env/static/public";
	import { AccountsApi, Configuration, TokenApi, type UpdateAccount } from "$lib/api";


	import { Button, ButtonGroup, Input, InputAddon, Label } from "flowbite-svelte";
    import { LockSolid, UserCircleSolid, TrashBinSolid, EnvelopeSolid } from 'flowbite-svelte-icons';
	import { getAccessToken, getRefreshToken, removeAccessToken, removeRefreshToken, removeUserData, removeUsername, setAccessToken, setRefreshToken, setUserData } from "../../../stores/auth";
	import { addToast } from "../../../stores/notifications";
	import type { PageData } from "./$types";

    export let data: PageData

    let username = data.account.username;
    let email = data.account.email;
    let oldPassword = "";
    let newPassword = "";
    let newPassword2 = "";
    let firstName = data.account.firstName;
    let lastName = data.account.lastName;

    const saveUserData = async () => {
        if ((oldPassword !== "") && (newPassword !== newPassword2)) {
            addToast({
                message: "Passwords do not match"
            })
            return
        }

        let token = await getAccessToken()

        const config = new Configuration({
            basePath: PUBLIC_BASE_URL,
            headers: {
                "Authorization": `Bearer ${token}`
            }
        })

        const tokenAPI = new TokenApi(config)
        const accountsAPI = new AccountsApi(config)
        
        try {
            let payload: UpdateAccount = {
                    username: username,
                    email: email,
                    firstName: firstName,
                    lastName: lastName
                }

            if (oldPassword !== "") {
                payload.oldPassword = oldPassword
            }

            if (newPassword !== "") {
                payload.newPassword = newPassword
            }

            let user = await accountsAPI.accountsApiUpdateSelf({
                updateAccount: payload
            })

            let refreshToken = await getRefreshToken()

            if (refreshToken === undefined) {
                addToast({
                    message: "You're not logged in!"
                })

                goto("/login")

                return
            }

            let tokens = await tokenAPI.tokenRefresh({
                tokenRefreshInputSchema: {
                    refresh: refreshToken
                }
            })

            if ((tokens.access === null) || (tokens.refresh === null)) {
                addToast({
                    message: "You're not logged in!"
                })

                goto("/login")

                return
            }

            setAccessToken(tokens.access);
            setRefreshToken(tokens.refresh);

            // populates user data
            await setUserData()
            
            addToast({
                message: "Account updated!"
            })
        } catch (error) {
            console.log("Error while updating account: " + error)
        }
    }

    const deleteAccount = async () => {
        let token = await getAccessToken()

        const config = new Configuration({
            basePath: PUBLIC_BASE_URL,
            headers: {
                "Authorization": `Bearer ${token}`
            }
        })

        const accountsAPI = new AccountsApi(config)

        try {
            await accountsAPI.accountsApiDeleteSelf()

            removeAccessToken()
            removeRefreshToken()
            removeUsername()
            removeUserData()

            addToast({
                message: "Account deleted!"
            })

            goto("/login")

            return
        } catch (error) {
            console.log("Error while deleting account: " + error)
        }
    }
</script>

<form on:submit|preventDefault={() => saveUserData()}>
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
            <Label for="old-password" class="block mb-2">Old Password</Label>
            <ButtonGroup class="w-full">
                <InputAddon>
                    <LockSolid class="w-4 h-4 text-gray-500 dark:text-gray-400" />
                </InputAddon>
                <Input id="old-password" bind:value={oldPassword} placeholder="old password" type="password" />
            </ButtonGroup>
        </div>
        
        <div class="mb-6">
            <Label for="new-password" class="block mb-2">New Password</Label>
            <ButtonGroup class="w-full">
                <InputAddon>
                    <LockSolid class="w-4 h-4 text-gray-500 dark:text-gray-400" />
                </InputAddon>
                <Input id="new-password" disabled={oldPassword === ""} bind:value={newPassword} placeholder="new password" type="password" />
            </ButtonGroup>
        </div>

        <div class="mb-6">
            <Label for="new-password-verification" class="block mb-2">New Password verification</Label>
            <ButtonGroup class="w-full">
                <InputAddon>
                    <LockSolid class="w-4 h-4 text-gray-500 dark:text-gray-400" />
                </InputAddon>
                <Input id="new-password-verification" disabled={newPassword === ""} bind:value={newPassword2} placeholder="new password" type="password" />
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

        <div class="text-center">
            <Button type="submit">Save details</Button> 
        </div>

        <div class="text-center mt-10">
            <p class="text-sm">Account deletions are permanent and cannot be undone.</p>
            <Button color="red" class="mt-4" type="button" on:click={() => deleteAccount()}>
                <TrashBinSolid class="w-4 h-4" />
                Delete account
            </Button>
        </div>
    </div>
</form>