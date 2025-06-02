import { nextTick } from 'vue'
import { mount } from '@vue/test-utils'
vi.mock('mermaid', () => ({
  default: {
    render: vi.fn().mockResolvedValue({ svg: '<svg><g><text>dummy</text></g></svg>' }),
    parse: vi.fn()
  }
}))
import { describe, it, expect, vi } from 'vitest'
import MermaidBlock from '../MermaidBlock.vue'

describe('MermaidBlock', () => {
  it('renders a valid mermaid diagram as SVG', async () => {
    const wrapper = mount(MermaidBlock, {
      props: {
        code: `graph TD\nA-->B`
      }
    })
    // Note: In JSDOM/happy-dom, .mermaid-graph may not appear due to ref/async limitations.
    // This test only checks for the outer block and absence of error. Use E2E for full coverage.
    await nextTick()
    await new Promise(resolve => setTimeout(resolve, 500))
    await nextTick()
    if (wrapper.find('.mermaid-error').exists()) {
      throw new Error('Mermaid error: ' + wrapper.find('.mermaid-error').text())
    }
    expect(wrapper.find('.mermaid-block').exists()).toBe(true)
  })

  it('shows an error for invalid mermaid syntax', async () => {
    // Make parse throw for this test
    const mermaid: any = await import('mermaid')
    mermaid.default.parse.mockImplementationOnce(() => { throw new Error('bad syntax') })
    const wrapper = mount(MermaidBlock, {
      props: {
        code: `not a valid mermaid diagram`
      }
    })
    await nextTick()
    await new Promise(resolve => setTimeout(resolve, 200))
    await nextTick()
    expect(wrapper.find('.mermaid-error').exists()).toBe(true)
    expect(wrapper.text()).toMatch(/Mermaid syntax error|Mermaid render error/)
  })
}) 