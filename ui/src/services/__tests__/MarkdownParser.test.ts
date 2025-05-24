import { describe, it, expect } from 'vitest'
import { MarkdownParser } from '../MarkdownParser'

describe('MarkdownParser', () => {
  const parser = new MarkdownParser()

  describe('parse', () => {
    it('should parse regular text as html block', () => {
      const result = parser.parse('Hello world')
      expect(result).toHaveLength(1)
      expect(result[0]).toEqual({
        type: 'paragraph',
        content: 'Hello world'
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
        expect(result[0].type).toBe('list')
        expect(result[0].ordered).toBe(false)
        expect(result[0].items.map((i: any) => i.content)).toEqual(['Item 1', 'Item 2'])
      })

      it('should parse ordered lists', () => {
        const result = parser.parse('1. Item 1\n2. Item 2')
        expect(result).toHaveLength(1)
        expect(result[0].type).toBe('list')
        expect(result[0].ordered).toBe(true)
        expect(result[0].items.map((i: any) => i.content)).toEqual(['Item 1', 'Item 2'])
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
        expect(result[0].type).toBe('list')
        expect(result[0].ordered).toBe(true)
        expect(result[0].items[0].content).toBe('Item 1')
        expect(result[0].items[0].children[0].type).toBe('list')
        expect(result[0].items[0].children[0].items.map((i: any) => i.content)).toEqual(['Nested 1', 'Nested 2'])
        expect(result[0].items[1].content).toBe('Item 2')
      })

      it('should parse task lists', () => {
        const result = parser.parse('- [ ] Task 1\n- [x] Task 2')
        expect(result).toHaveLength(1)
        expect(result[0].type).toBe('list')
        expect(result[0].items[0]).toEqual({
          type: 'task',
          checked: false,
          label: 'Task 1'
        })
        expect(result[0].items[1]).toEqual({
          type: 'task',
          checked: true,
          label: 'Task 2'
        })
      })

      it('should parse mixed regular and task list items', () => {
        const result = parser.parse('- Regular item\n- [ ] Task item')
        expect(result).toHaveLength(1)
        expect(result[0].type).toBe('list')
        expect(result[0].items[0]).toEqual({
          type: 'list_item',
          content: 'Regular item',
          children: undefined
        })
        expect(result[0].items[1]).toEqual({
          type: 'task',
          checked: false,
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
        function findTasks(items: any[]): any[] {
          let tasks: any[] = [];
          for (const item of items) {
            if (item.type === 'task') {
              tasks.push(item);
            }
            if (item.children) {
              for (const child of item.children) {
                if (child.items) {
                  tasks = tasks.concat(findTasks(child.items));
                }
              }
            }
          }
          return tasks;
        }
        const tasks = findTasks(result[0].items);
        expect(tasks).toHaveLength(2);
        expect(tasks[0].label).toContain('Nested task');
        expect(tasks[1].label).toContain('Another task');
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
      expect(result[0].type).toBe('paragraph')
      expect(result[0].content).toContain('<img')
      expect(result[0].content).toContain('src="https://example.com/image.png"')
      expect(result[0].content).toContain('alt="alt text"')
    })
  })
}) 