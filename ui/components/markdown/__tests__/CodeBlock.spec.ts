import { mount } from '@vue/test-utils'
import { describe, it, expect, vi } from 'vitest'
import CodeBlock from '../CodeBlock.vue'

globalThis.navigator = { clipboard: { writeText: vi.fn().mockResolvedValue(undefined) } } as any

describe('CodeBlock', () => {
  it('renders code and highlights', () => {
    const wrapper = mount(CodeBlock, { props: { lang: 'javascript', code: encodeURIComponent('const x = 1;') } })
    expect(wrapper.find('pre').text()).toContain('const x = 1;')
    expect(wrapper.find('.code-block-lang').text()).toBe('javascript')
  })
  it('toggles collapse', async () => {
    const wrapper = mount(CodeBlock, { props: { lang: 'js', code: encodeURIComponent('let y = 2;') } })
    const vm = wrapper.vm as any
    expect(vm.isCollapsed).toBe(false)
    await wrapper.find('.collapse-button').trigger('click')
    expect(vm.isCollapsed).toBe(true)
    await wrapper.find('.collapse-button').trigger('click')
    expect(vm.isCollapsed).toBe(false)
  })
  it('copy button works', async () => {
    const wrapper = mount(CodeBlock, { props: { lang: 'js', code: encodeURIComponent('copy me!') } })
    await wrapper.find('.copy-button').trigger('click')
    expect(navigator.clipboard.writeText).toHaveBeenCalledWith('copy me!')
  })
}) 