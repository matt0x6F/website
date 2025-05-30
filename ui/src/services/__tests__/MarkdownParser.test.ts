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

    // --- Additional tests for new/edge cases ---
    
    describe('blockquotes', () => {
      it('should parse a simple blockquote', () => {
        const result = parser.parse('> This is a quote')
        expect(result).toHaveLength(1)
        expect(result[0].type).toBe('blockquote')
        expect(result[0].content[0].type).toBe('paragraph')
        expect(result[0].content[0].content).toContain('This is a quote')
      })

      it('should parse nested blockquotes', () => {
        const markdown = '> Outer\n> > Inner'
        const result = parser.parse(markdown)
        expect(result).toHaveLength(1)
        expect(result[0].type).toBe('blockquote')
        expect(result[0].content[1].type).toBe('blockquote')
        expect(result[0].content[1].content[0].content).toContain('Inner')
      })

      it('should parse blockquotes containing lists', () => {
        const markdown = '> - Item 1\n> - Item 2'
        const result = parser.parse(markdown)
        expect(result).toHaveLength(1)
        expect(result[0].type).toBe('blockquote')
        expect(result[0].content[0].type).toBe('list')
        expect(result[0].content[0].items.map((i: any) => i.content)).toEqual(['Item 1', 'Item 2'])
      })
    })

    describe('headings', () => {
      it('should parse all heading levels', () => {
        for (let level = 1; level <= 6; level++) {
          const hashes = '#'.repeat(level)
          const result = parser.parse(`${hashes} Heading ${level}`)
          expect(result).toHaveLength(1)
          expect(result[0].type).toBe('heading')
          expect(result[0].level).toBe(level)
          expect(result[0].content).toContain(`Heading ${level}`)
        }
      })

      it('should parse headings with inline formatting', () => {
        const result = parser.parse('# Heading with **bold** and _italic_')
        expect(result).toHaveLength(1)
        expect(result[0].type).toBe('heading')
        expect(result[0].content).toContain('<strong>bold</strong>')
        expect(result[0].content).toContain('<em>italic</em>')
      })
    })

    describe('horizontal rules', () => {
      it('should parse horizontal rules', () => {
        const result = parser.parse('---')
        expect(result).toHaveLength(1)
        expect(result[0].type).toBe('hr')
      })
    })

    describe('mixed content', () => {
      it('should parse a document with paragraph, list, code, and table', () => {
        const markdown = `Paragraph\n\n- List item\n\n\`\`\`js\ncode\n\`\`\`\n\n| H1 | H2 |\n|----|----|\n| a  | b  |`
        const result = parser.parse(markdown)
        expect(result.some(b => b.type === 'paragraph')).toBe(true)
        expect(result.some(b => b.type === 'list')).toBe(true)
        expect(result.some(b => b.type === 'code')).toBe(true)
        expect(result.some(b => b.type === 'table')).toBe(true)
      })
    })

    describe('edge cases', () => {
      it('should handle unclosed code block gracefully', () => {
        const result = parser.parse('```js\nlet x = 1;')
        // Should still parse as a code block or paragraph
        expect(result.length).toBeGreaterThan(0)
      })

      it('should parse special characters and HTML entities', () => {
        const result = parser.parse('5 > 3 &amp; 2 < 4')
        expect(result[0].content).toContain('5 &gt; 3 &amp; 2 &lt; 4')
      })
    })

    it('should render single newlines as <br> in paragraphs', () => {
      const result = parser.parse('Line one\nLine two\nLine three')
      expect(result).toHaveLength(1)
      expect(result[0].type).toBe('paragraph')
      expect(result[0].content).toContain('Line one<br>\nLine two<br>\nLine three')
    })
  })
}) 