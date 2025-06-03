import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'
import ParagraphBlock from '../ParagraphBlock.vue'

describe('ParagraphBlock', () => {
  it('renders content as HTML in a <p>', () => {
    const wrapper = mount(ParagraphBlock, {
      props: { content: '<b>hello</b> world' }
    })
    const p = wrapper.find('p')
    expect(p.exists()).toBe(true)
    expect(p.html()).toContain('<b>hello</b> world')
  })
}) 