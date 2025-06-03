import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'
import MarkdownListRenderer from '../MarkdownListRenderer.vue'

describe('MarkdownListRenderer', () => {
  it('renders unordered list', () => {
    const block = { type: 'ul', items: [
      { type: 'li', content: 'A' },
      { type: 'li', content: 'B' }
    ] }
    const wrapper = mount(MarkdownListRenderer, { props: { block } })
    expect(wrapper.find('ul').exists()).toBe(true)
    expect(wrapper.html()).toContain('A')
    expect(wrapper.html()).toContain('B')
  })
  it('renders ordered list', () => {
    const block = { type: 'ol', items: [
      { type: 'li', content: '1' },
      { type: 'li', content: '2' }
    ] }
    const wrapper = mount(MarkdownListRenderer, { props: { block } })
    expect(wrapper.find('ol').exists()).toBe(true)
    expect(wrapper.html()).toContain('1')
    expect(wrapper.html()).toContain('2')
  })
  it('renders task list', () => {
    const block = { type: 'ul', items: [
      { type: 'task', checked: true, label: 'Task 1' },
      { type: 'task', checked: false, label: 'Task 2' }
    ] }
    const wrapper = mount(MarkdownListRenderer, {
      props: { block },
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
  it('renders nested lists', () => {
    const block = { type: 'ul', items: [
      { type: 'li', content: 'Parent', children: [
        { type: 'ul', items: [ { type: 'li', content: 'Child' } ] }
      ] }
    ] }
    const wrapper = mount(MarkdownListRenderer, {
      props: { block },
      global: {
        stubs: {
          Checkbox: true
        }
      }
    })
    expect(wrapper.html()).toContain('Parent')
    expect(wrapper.html()).toContain('Child')
  })
}) 