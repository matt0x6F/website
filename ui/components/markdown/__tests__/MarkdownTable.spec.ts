import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'
import MarkdownTable from '../MarkdownTable.vue'

describe('MarkdownTable', () => {
  it('renders a table with columns and rows', () => {
    const columns = [
      { field: 'name', header: 'Name' },
      { field: 'age', header: 'Age' }
    ]
    const rows = [
      { name: 'Alice', age: 30 },
      { name: 'Bob', age: 25 }
    ]
    const wrapper = mount(MarkdownTable, { props: { columns, rows } })
    expect(wrapper.find('.markdown-table').exists()).toBe(true)
    expect(wrapper.html()).toContain('Alice')
    expect(wrapper.html()).toContain('Bob')
    expect(wrapper.html()).toContain('Name')
    expect(wrapper.html()).toContain('Age')
  })
}) 