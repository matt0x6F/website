import MarkdownIt from 'markdown-it'
import hljs from 'highlight.js/lib/core'

export interface Block {
  type: 'code' | 'table' | 'html' | 'task';
  [key: string]: any;
}

export interface TableData {
  columns: { field: string; header: string }[];
  rows: Record<string, any>[];
}

export class MarkdownParser {
  private md: MarkdownIt;

  constructor(highlight?: (str: string, lang: string) => string) {
    this.md = new MarkdownIt({
      html: true,
      linkify: true,
      typographer: true,
      highlight: highlight || ((str: string, lang: string): string => {
        if (lang && hljs.getLanguage(lang)) {
          try {
            return hljs.highlight(str, { language: lang, ignoreIllegals: true }).value
          } catch (__) {}
        }
        return this.md.utils.escapeHtml(str)
      })
    }).enable(['list', 'table'])
  }

  public escapeHtml(str: string): string {
    return this.md.utils.escapeHtml(str);
  }

  public parse(content: string): Block[] {
    const tokens = this.md.parse(content || '', {})
    return this.parseBlocks(tokens)
  }

  private parseCodeBlock(token: any): Block {
    const lang = token.info ? this.md.utils.unescapeAll(token.info).trim().split(/\s+/g)[0] : ''
    return {
      type: 'code',
      lang,
      content: encodeURIComponent(token.content)
    }
  }

  private parseTableData(tokens: any[], startIndex: number): { tableData: TableData; endIndex: number } {
    const columns: { field: string; header: string }[] = []
    const rows: Record<string, any>[] = []
    let i = startIndex + 1
    let headerCells: string[] = []

    // Parse header
    while (i < tokens.length && tokens[i].type !== 'thead_close') {
      if (tokens[i].type === 'th_open') {
        i++
        if (tokens[i].type === 'inline') {
          headerCells.push(tokens[i].content)
        }
      }
      i++
    }
    columns.push(...headerCells.map((header, idx) => ({ field: `col${idx}`, header })))

    // Parse rows
    while (i < tokens.length && tokens[i].type !== 'table_close') {
      if (tokens[i].type === 'tr_open') {
        const rowCells: string[] = []
        i++
        while (i < tokens.length && tokens[i].type !== 'tr_close') {
          if (tokens[i].type === 'td_open') {
            i++
            if (tokens[i].type === 'inline') {
              rowCells.push(tokens[i].content)
            }
          }
          i++
        }
        if (rowCells.length) {
          const row: Record<string, any> = {}
          rowCells.forEach((cell, idx) => {
            row[`col${idx}`] = cell
          })
          rows.push(row)
        }
      }
      i++
    }

    return {
      tableData: { columns, rows },
      endIndex: i
    }
  }

  private parseListContent(tokens: any[], startIndex: number, depth: number = 0): { html: string; endIndex: number; taskBlocks: Block[] } {
    const token = tokens[startIndex]
    const isOrdered = token.type === 'ordered_list_open'
    const start = isOrdered ? parseInt(token.info || '1', 10) : null
    let html = `<${isOrdered ? 'ol' : 'ul'} class="${isOrdered ? 'list-decimal unpadded-ol' : 'list-disc unpadded-ul'} ${depth === 0 ? 'list-outside' : ''}"${start ? ` start="${start}"` : ''}>`;
    let i = startIndex + 1
    const taskBlocks: Block[] = []

    while (i < tokens.length && tokens[i].type !== (isOrdered ? 'ordered_list_close' : 'bullet_list_close')) {
      if (tokens[i].type === 'list_item_open') {
        // Process list item content
        let j = i + 1
        let hasNestedList = false
        let isTask = false
        
        while (j < tokens.length && tokens[j].type !== 'list_item_close') {
          if (tokens[j].type === 'ordered_list_open' || tokens[j].type === 'bullet_list_open') {
            hasNestedList = true
            const { html: nestedHtml, endIndex, taskBlocks: nestedTasks } = this.parseListContent(tokens, j, depth + 1)
            html += nestedHtml
            taskBlocks.push(...nestedTasks)
            j = endIndex
          } else if (tokens[j].type === 'inline') {
            const match = tokens[j].content.trim().match(/^\[( |x|X)\]\s+(.*)$/)
            if (match) {
              isTask = true
              taskBlocks.push({
                type: 'task',
                modelValue: match[1].toLowerCase() === 'x',
                label: this.md.renderInline(match[2])
              })
            } else {
              html += '<li class="my-2">' + this.md.renderInline(tokens[j].content)
              if (!hasNestedList) {
                html += '</li>'
              }
            }
          }
          j++
        }
        
        if (hasNestedList && !isTask) {
          html += '</li>'
        }
        i = j
      }
      i++
    }

    html += `</${isOrdered ? 'ol' : 'ul'}>`
    return { html, endIndex: i, taskBlocks }
  }

  private parseBlocks(tokens: any[]): Block[] {
    const blocks: Block[] = []
    let i = 0

    while (i < tokens.length) {
      const token = tokens[i]

      if (token.type === 'fence') {
        blocks.push(this.parseCodeBlock(token))
        i++
      } else if (token.type === 'table_open') {
        const { tableData, endIndex } = this.parseTableData(tokens, i)
        blocks.push({ type: 'table', ...tableData })
        i = endIndex + 1
      } else if (token.type === 'ordered_list_open' || token.type === 'bullet_list_open') {
        const { html, endIndex, taskBlocks } = this.parseListContent(tokens, i, 0)
        if (html.includes('<li')) { // Only add the list if it has items
          blocks.push({ type: 'html', html })
        }
        blocks.push(...taskBlocks)
        i = endIndex + 1
      } else {
        // Collect consecutive non-special tokens into a single HTML block
        let html = ''
        while (i < tokens.length && 
               !['fence', 'table_open', 'ordered_list_open', 'bullet_list_open'].includes(tokens[i].type)) {
          html += this.md.renderer.render([tokens[i]], this.md.options, {})
          i++
        }
        if (html.trim()) {
          // Normalize: remove newlines after opening tags like <p>\nText</p> => <p>Text</p>
          html = html.replace(/<(p|ul|ol|li|h[1-6])>\s*\n\s*/g, '<$1>');
          blocks.push({ type: 'html', html })
        }
      }
    }

    return blocks
  }
} 