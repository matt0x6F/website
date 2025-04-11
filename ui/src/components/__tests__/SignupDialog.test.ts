import { describe, it, expect, vi, beforeEach } from 'vitest';
import { mount, VueWrapper } from '@vue/test-utils';
import { createTestingPinia } from '@pinia/testing';
import { useAuthStore } from '../../stores/auth';
import SignupDialog from '../SignupDialog.vue';
import type { StoreGeneric } from 'pinia';
import type { ComponentPublicInstance } from 'vue';

interface SignupDialogInstance extends ComponentPublicInstance {
  visible: boolean;
  loading: boolean;
  formData: {
    username: string;
    email: string;
    password: string;
    firstName: string;
    lastName: string;
  };
}

describe('SignupDialog', () => {
  let wrapper: VueWrapper<SignupDialogInstance>;
  let authStore: StoreGeneric;

  beforeEach(() => {
    wrapper = mount(SignupDialog, {
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
              :type="type || 'text'"
              :value="modelValue" 
              v-bind="disabled ? { disabled: 'disabled' } : {}"
              @input="$emit('update:modelValue', $event.target.value)" 
            />`,
            props: ['modelValue', 'disabled', 'type'],
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
    }) as unknown as VueWrapper<SignupDialogInstance>;
    
    authStore = useAuthStore();
  });

  it('renders properly', () => {
    expect(wrapper.find('label[for="username"]').text()).toBe('Username*');
    expect(wrapper.find('label[for="email"]').text()).toBe('Email*');
    expect(wrapper.find('label[for="password"]').text()).toBe('Password*');
    expect(wrapper.find('label[for="firstName"]').text()).toBe('First Name');
    expect(wrapper.find('label[for="lastName"]').text()).toBe('Last Name');
  });

  it('shows error message on failed signup', async () => {
    authStore.signup.mockRejectedValueOnce(new Error('Signup failed'));

    await wrapper.find('#username').setValue('testuser');
    await wrapper.find('#email').setValue('test@example.com');
    await wrapper.find('#password').setValue('password123');
    await wrapper.find('#firstName').setValue('Test');
    await wrapper.find('#lastName').setValue('User');
    await wrapper.find('.p-button').trigger('click');

    expect(wrapper.find('.text-red-500').text()).toBe('Failed to create account. Please try again.');
  });

  it('successful signup clears form and closes dialog', async () => {
    authStore.signup.mockResolvedValueOnce();

    await wrapper.find('#username').setValue('testuser');
    await wrapper.find('#email').setValue('test@example.com');
    await wrapper.find('#password').setValue('password123');
    await wrapper.find('#firstName').setValue('Test');
    await wrapper.find('#lastName').setValue('User');
    await wrapper.find('.p-button').trigger('click');

    expect(wrapper.vm.formData.username).toBe('');
    expect(wrapper.vm.formData.email).toBe('');
    expect(wrapper.vm.formData.password).toBe('');
    expect(wrapper.vm.formData.firstName).toBe('');
    expect(wrapper.vm.formData.lastName).toBe('');
    expect(wrapper.vm.visible).toBe(false);
    expect(wrapper.find('.text-red-500').exists()).toBe(false);
  });

  it('disables form during signup attempt', async () => {
    // Create a Promise we can control
    let resolvePromise: () => void;
    const signupPromise = new Promise<void>(resolve => {
      resolvePromise = resolve;
    });
    
    authStore.signup.mockImplementationOnce(() => signupPromise);

    // Fill out the form
    await wrapper.find('#username').setValue('testuser');
    await wrapper.find('#email').setValue('test@example.com');
    await wrapper.find('#password').setValue('password123');
    await wrapper.find('#firstName').setValue('Test');
    await wrapper.find('#lastName').setValue('User');

    // Start the signup process
    await wrapper.find('.p-button').trigger('click');
    await wrapper.vm.$nextTick();

    // Check loading state
    expect(wrapper.vm.loading).toBe(true);
    
    // Check if inputs are disabled
    const inputs = ['username', 'email', 'password', 'firstName', 'lastName'];
    inputs.forEach(id => {
      const input = wrapper.find(`#${id}`).element as HTMLInputElement;
      expect(input.disabled).toBe(true);
    });
    
    expect(wrapper.find('.p-button').attributes('data-loading')).toBe('true');

    // Clean up
    resolvePromise!();
    await signupPromise;
  });
}); 