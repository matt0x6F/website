import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'
import HeadingBlock from '../HeadingBlock.vue'

describe('HeadingBlock', () => {
  it('renders the correct heading tag and content', () => {
    const wrapper = mount(HeadingBlock, {
      props: { level: 2, content: 'Hello <em>world</em>' }
    })
    const h2 = wrapper.find('h2')
    expect(h2.exists()).toBe(true)
    expect(h2.html()).toContain('Hello <em>world</em>')
  })
}) 