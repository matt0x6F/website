import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'
import BlockquoteBlock from '../BlockquoteBlock.vue'

describe('BlockquoteBlock', () => {
  it('renders nested blocks (heading, paragraph, list, blockquote)', () => {
    const blocks = [
      { type: 'heading', level: 3, content: 'Title' },
      { type: 'paragraph', content: 'Some <b>text</b>' },
      { type: 'list', ordered: false, items: [
        { type: 'list_item', content: 'Item 1' },
        { type: 'list_item', content: 'Item 2' }
      ] },
      { type: 'blockquote', content: [
        { type: 'paragraph', content: 'Nested quote' }
      ] }
    ]
    const wrapper = mount(BlockquoteBlock, { props: { blocks } })
    expect(wrapper.find('blockquote').exists()).toBe(true)
    expect(wrapper.html()).toContain('Title')
    expect(wrapper.html()).toContain('Some <b>text</b>')
    expect(wrapper.html()).toContain('Item 1')
    expect(wrapper.html()).toContain('Nested quote')
  })
}) 