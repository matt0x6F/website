import type { ToastPositionType } from "flowbite-svelte";
import { writable, type Writable } from "svelte/store";
import { slide, type TransitionConfig } from "svelte/transition";

interface Input {
  id?: number,
  dismissable?: boolean,
  color?: string,
  position?: ToastPositionType,
  divClass?: string,
  defaultIconClass?: string,
  contentClass?: string,
  align?: boolean,
  transition?: (node: HTMLElement, params: any) => TransitionConfig,
  params?: string,
  toastStatus?: boolean,
  timeout?: number,
  message: string
}

interface Notification {
    id: number,
    dismissable: boolean,
    color: string,
    position: ToastPositionType,
    divClass: string,
    defaultIconClass: string,
    contentClass: string,
    align: boolean,
    transition: (node: HTMLElement, params: any) => TransitionConfig,
    params: string,
    toastStatus: boolean,
    timeout: number,
    message: string
}

export const notifications: Writable<Notification[]> = writable([]);

export const addToast = (input: Input) => {
  const id = Math.floor(Math.random() * 10000);

  const defaults: Notification = {
    id: id,
    dismissable: true, 
    color: "primary", 
    position: "top-right", 
    divClass: "w-full max-w-xs p-4 text-gray-500 bg-white shadow dark:text-gray-400 dark:bg-gray-800 gap-3", 
    defaultIconClass: "w-8 h-8", 
    contentClass:  "w-full text-sm font-normal", 
    align: true, 
    transition: slide, 
    params:  "{}", 
    toastStatus: true,
    timeout: 6,
    message: ""
  }

  const notification = {...defaults, ...input}

  // Push the toast to the top of the list of toasts
  notifications.update((all) => [notification, ...all]);

  // If toast is dismissible, dismiss it after "timeout" amount of time.
  if (notification.timeout) setTimeout(() => dismissToast(id), notification.timeout * 1000);
};

export const dismissToast = (id: number) => {
  // update toastStatus to false where notification matches id
  notifications.update((all) => all.map((t) => {
    if (t.id === id) {
      return {...t, toastStatus: false}
    }
    return t
  }));
};