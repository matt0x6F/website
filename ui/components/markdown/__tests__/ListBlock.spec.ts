import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'
import ListBlock from '../ListBlock.vue'

describe('ListBlock', () => {
  it('renders unordered list', () => {
    const items = [
      { type: 'list_item', content: 'A' },
      { type: 'list_item', content: 'B' }
    ]
    const wrapper = mount(ListBlock, { props: { ordered: false, items } })
    expect(wrapper.find('ul').exists()).toBe(true)
    expect(wrapper.html()).toContain('A')
    expect(wrapper.html()).toContain('B')
  })
  it('renders ordered list', () => {
    const items = [
      { type: 'list_item', content: '1' },
      { type: 'list_item', content: '2' }
    ]
    const wrapper = mount(ListBlock, { props: { ordered: true, items, start: 3 } })
    expect(wrapper.find('ol').exists()).toBe(true)
    expect(wrapper.find('ol').attributes('start')).toBe('3')
    expect(wrapper.html()).toContain('1')
    expect(wrapper.html()).toContain('2')
  })
  it('renders task items', () => {
    const items = [
      { type: 'task', checked: true, label: 'Task 1' },
      { type: 'task', checked: false, label: 'Task 2' }
    ]
    const wrapper = mount(ListBlock, {
      props: { ordered: false, items },
      global: {
        stubs: {
          Checkbox: true
        }
      }
    })
    expect(wrapper.findAll('.task-list-item').length).toBe(2)
    expect(wrapper.html()).toContain('Task 1')
    expect(wrapper.html()).toContain('Task 2')
  })
}) 