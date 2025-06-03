import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'
import OrderedList from '../OrderedList.vue'

describe('OrderedList', () => {
  it('renders ordered list with correct start and content', () => {
    const items = [
      { content: 'First' },
      { content: 'Second' }
    ]
    const wrapper = mount(OrderedList, { props: { items, start: 5 } })
    const ol = wrapper.find('ol')
    expect(ol.exists()).toBe(true)
    expect(ol.attributes('start')).toBe('5')
    expect(wrapper.html()).toContain('First')
    expect(wrapper.html()).toContain('Second')
  })
}) 