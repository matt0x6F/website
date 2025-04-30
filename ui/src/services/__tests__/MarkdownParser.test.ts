import { describe, it, expect } from 'vitest'
import { MarkdownParser } from '../MarkdownParser'

describe('MarkdownParser', () => {
  const parser = new MarkdownParser()

  describe('parse', () => {
    it('should parse regular text as html block', () => {
      const result = parser.parse('Hello world')
      expect(result).toHaveLength(1)
      expect(result[0]).toEqual({
        type: 'html',
        html: '<p>Hello world</p>\n'
      })
    })

    it('should parse code blocks', () => {
      const result = parser.parse('```javascript\nconst x = 1;\n```')
      expect(result).toHaveLength(1)
      expect(result[0]).toEqual({
        type: 'code',
        lang: 'javascript',
        content: encodeURIComponent('const x = 1;\n')
      })
    })

    it('should parse tables', () => {
      const markdown = `
| Header 1 | Header 2 |
|----------|----------|
| Cell 1   | Cell 2   |
`
      const result = parser.parse(markdown)
      expect(result).toHaveLength(1)
      expect(result[0]).toEqual({
        type: 'table',
        columns: [
          { field: 'col0', header: 'Header 1' },
          { field: 'col1', header: 'Header 2' }
        ],
        rows: [
          { col0: 'Cell 1', col1: 'Cell 2' }
        ]
      })
    })

    describe('lists', () => {
      it('should parse unordered lists', () => {
        const result = parser.parse('- Item 1\n- Item 2')
        expect(result).toHaveLength(1)
        expect(result[0].type).toBe('html')
        expect(result[0].html).toContain('<ul')
        expect(result[0].html).toContain('Item 1')
        expect(result[0].html).toContain('Item 2')
      })

      it('should parse ordered lists', () => {
        const result = parser.parse('1. Item 1\n2. Item 2')
        expect(result).toHaveLength(1)
        expect(result[0].type).toBe('html')
        expect(result[0].html).toContain('<ol')
        expect(result[0].html).toContain('Item 1')
        expect(result[0].html).toContain('Item 2')
      })

      it('should parse nested lists', () => {
        const markdown = `
1. Item 1
   1. Nested 1
   2. Nested 2
2. Item 2
`
        const result = parser.parse(markdown)
        expect(result).toHaveLength(1)
        expect(result[0].type).toBe('html')
        const html = result[0].html
        expect(html).toMatch(/<ol[^>]*>.*<ol[^>]*>.*<\/ol>.*<\/ol>/)
      })

      it('should parse task lists', () => {
        const result = parser.parse('- [ ] Task 1\n- [x] Task 2')
        expect(result).toHaveLength(2)
        expect(result[0]).toEqual({
          type: 'task',
          modelValue: false,
          label: 'Task 1'
        })
        expect(result[1]).toEqual({
          type: 'task',
          modelValue: true,
          label: 'Task 2'
        })
      })

      it('should parse mixed regular and task list items', () => {
        const result = parser.parse('- Regular item\n- [ ] Task item')
        expect(result).toHaveLength(2)
        expect(result[0].type).toBe('html')
        expect(result[0].html).toContain('Regular item')
        expect(result[1]).toEqual({
          type: 'task',
          modelValue: false,
          label: 'Task item'
        })
      })

      it('should parse nested task lists', () => {
        const markdown = `
1. Top level
   - [ ] Nested task
2. [ ] Another task
`
        const result = parser.parse(markdown)
        expect(result.filter(b => b.type === 'task')).toHaveLength(2)
        expect(result.find(b => b.type === 'html')).toBeTruthy()
      })
    })

    it('should handle empty input', () => {
      const result = parser.parse('')
      expect(result).toHaveLength(0)
    })

    it('should handle null input', () => {
      const result = parser.parse(null as any)
      expect(result).toHaveLength(0)
    })

    it('should parse image markdown', () => {
      const result = parser.parse('![alt text](https://example.com/image.png)')
      expect(result).toHaveLength(1)
      expect(result[0].type).toBe('html')
      expect(result[0].html).toContain('<img')
      expect(result[0].html).toContain('src="https://example.com/image.png"')
      expect(result[0].html).toContain('alt="alt text"')
    })
  })
}) 