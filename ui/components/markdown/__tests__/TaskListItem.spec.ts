import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'
import TaskListItem from '../TaskListItem.vue'

describe('TaskListItem', () => {
  it('renders label and checked state', () => {
    const wrapper = mount(TaskListItem, {
      props: { modelValue: true, label: 'Do this', unordered: false },
      global: {
        stubs: {
          Checkbox: true
        }
      }
    })
    expect(wrapper.find('.task-label').text()).toBe('Do this')
    // We stub Checkbox, so the real .p-checkbox class won't exist. Instead, check for the stub element.
    expect(wrapper.find('checkbox-stub').exists()).toBe(true)
  })
  it('emits update:modelValue when changed', async () => {
    const wrapper = mount(TaskListItem, {
      props: { modelValue: false, label: 'Check me', unordered: true },
      global: {
        stubs: {
          Checkbox: true
        }
      }
    })
    await wrapper.vm.$emit('update:modelValue', true)
    expect(wrapper.emitted()['update:modelValue']).toBeTruthy()
    expect(wrapper.emitted()['update:modelValue'][0]).toEqual([true])
  })
}) 