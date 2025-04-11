import { describe, it, expect, vi, beforeEach } from 'vitest';
import { mount, VueWrapper } from '@vue/test-utils';
import { createTestingPinia } from '@pinia/testing';
import { useAuthStore } from '../../stores/auth';
import LoginDialog from '../LoginDialog.vue';
import type { StoreGeneric } from 'pinia';
import type { ComponentPublicInstance } from 'vue';

// Mock child components
vi.mock('../components/SignupDialog.vue', () => ({
  default: {
    name: 'SignupDialog',
    template: '<div></div>'
  }
}));

interface LoginDialogInstance extends ComponentPublicInstance {
  email: string;
  password: string;
  visible: boolean;
  showSignup: boolean;
  loading: boolean;
}

describe('LoginDialog', () => {
  let wrapper: VueWrapper<LoginDialogInstance>;
  let authStore: StoreGeneric;

  beforeEach(() => {
    // Create fresh pinia and mount component for each test
    wrapper = mount(LoginDialog, {
      global: {
        plugins: [createTestingPinia({
          createSpy: vi.fn
        })],
        stubs: {
          'Dialog': {
            template: `
              <div class="dialog">
                <slot></slot>
                <slot name="footer"></slot>
              </div>
            `,
            props: {
              visible: {
                type: Boolean,
                required: true
              }
            },
            emits: ['update:visible']
          },
          'InputText': {
            template: `<input 
              type="email" 
              :value="modelValue" 
              v-bind="disabled ? { disabled: 'disabled' } : {}"
              @input="$emit('update:modelValue', $event.target.value)" 
            />`,
            props: ['modelValue', 'disabled'],
            emits: ['update:modelValue']
          },
          'Password': {
            template: `<input 
              type="password" 
              :value="modelValue" 
              v-bind="disabled ? { disabled: 'disabled' } : {}"
              @input="$emit('update:modelValue', $event.target.value)" 
            />`,
            props: ['modelValue', 'disabled'],
            emits: ['update:modelValue']
          },
          'Button': {
            template: '<button class="p-button" :label="label" :loading="loading" :data-loading="loading" @click="$emit(\'click\')">{{ label }}</button>',
            props: ['label', 'loading'],
            emits: ['click']
          }
        }
      },
      props: {
        visible: true
      }
    }) as unknown as VueWrapper<LoginDialogInstance>;
    
    authStore = useAuthStore();
  });

  // Add more test cases as needed

  it('renders properly', () => {
    expect(wrapper.find('label[for="email"]').text()).toBe('Email');
    expect(wrapper.find('label[for="password"]').text()).toBe('Password');
    expect(wrapper.find('.hover\\:underline').text()).toBe('Create Account');
  });

  it('shows error message on failed login', async () => {
    authStore.login.mockRejectedValueOnce(new Error('Invalid credentials'));

    const emailInput = wrapper.find('input[type="email"]');
    const passwordInput = wrapper.find('input[type="password"]');
    const loginButton = wrapper.find('.p-button');

    await emailInput.setValue('test@example.com');
    await passwordInput.setValue('password123');
    await loginButton.trigger('click');

    expect(wrapper.find('.text-red-500').text()).toBe('Invalid email or password');
  });

  it('successful login clears form and closes dialog', async () => {
    authStore.login.mockResolvedValueOnce();

    await wrapper.find('input[type="email"]').setValue('test@example.com');
    await wrapper.find('input[type="password"]').setValue('password123');
    await wrapper.find('.p-button').trigger('click');

    expect(wrapper.vm.email).toBe('');
    expect(wrapper.vm.password).toBe('');
    expect(wrapper.vm.visible).toBe(false);
    expect(wrapper.find('.text-red-500').exists()).toBe(false);
  });

  it('opens signup dialog when create account is clicked', async () => {
    expect(wrapper.vm.showSignup).toBe(false); // Initial state
    expect(wrapper.vm.visible).toBe(true);     // Dialog starts visible

    await wrapper.find('.hover\\:underline').trigger('click');
    await wrapper.vm.$nextTick();              // Wait for updates

    expect(wrapper.vm.visible).toBe(false);    // Main dialog should close
    expect(wrapper.vm.showSignup).toBe(true);  // Signup dialog should open
  });

  it('disables form during login attempt', async () => {
    // Create a Promise we can control
    let resolvePromise: () => void;
    const loginPromise = new Promise<void>(resolve => {
      resolvePromise = resolve;
    });
    
    authStore.login.mockImplementationOnce(() => loginPromise);

    // Set email and password values first
    await wrapper.find('input[type="email"]').setValue('test@example.com');
    await wrapper.find('input[type="password"]').setValue('password123');

    // Start the login process
    await wrapper.find('.p-button').trigger('click');
    await wrapper.vm.$nextTick();

    // Now check the loading state
    expect(wrapper.vm.loading).toBe(true);
    
    // Check if inputs are actually disabled in the DOM
    const emailInput = wrapper.find('input[type="email"]').element as HTMLInputElement;
    const passwordInput = wrapper.find('input[type="password"]').element as HTMLInputElement;
    const createAccountButton = wrapper.find('.hover\\:underline').element as HTMLButtonElement;
    
    expect(emailInput.disabled).toBe(true);
    expect(passwordInput.disabled).toBe(true);
    expect(wrapper.find('.p-button').attributes('data-loading')).toBe('true');
    expect(createAccountButton.disabled).toBe(true);

    // Clean up by resolving the promise
    resolvePromise!();
    await loginPromise;
  });
}); 