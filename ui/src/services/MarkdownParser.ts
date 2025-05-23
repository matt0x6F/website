import MarkdownIt from 'markdown-it'
import hljs from 'highlight.js/lib/core'

export interface Block {
  type: string;
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

  private parseList(tokens: any[], startIndex: number): { block: Block; endIndex: number } {
    const token = tokens[startIndex]
    const isOrdered = token.type === 'ordered_list_open'
    const start = isOrdered ? parseInt(token.info || '1', 10) : undefined
    let i = startIndex + 1
    const items: any[] = []
    while (i < tokens.length && tokens[i].type !== (isOrdered ? 'ordered_list_close' : 'bullet_list_close')) {
      if (tokens[i].type === 'list_item_open') {
        let j = i + 1
        const children: any[] = []
        let content = ''
        let taskMatch = null
        let isTask = false
        let checked = false
        let label = ''
        while (j < tokens.length && tokens[j].type !== 'list_item_close') {
          if (tokens[j].type === 'ordered_list_open' || tokens[j].type === 'bullet_list_open') {
            const { block: nestedBlock, endIndex } = this.parseList(tokens, j)
            children.push(nestedBlock)
            j = endIndex + 1
          } else if (tokens[j].type === 'inline') {
            // Detect task list item: [ ] or [x] at the start
            taskMatch = tokens[j].content.match(/^\s*\[( |x|X)\]\s+(.*)$/)
            if (taskMatch) {
              isTask = true
              checked = taskMatch[1].toLowerCase() === 'x'
              label = this.md.renderInline(taskMatch[2])
            } else {
              content += this.md.renderInline(tokens[j].content)
            }
            j++
          } else {
            j++
          }
        }
        if (isTask) {
          items.push({ type: 'task', checked, label })
        } else {
          items.push({ type: 'list_item', content, children: children.length ? children : undefined })
        }
        i = j
      }
      i++
    }
    return {
      block: {
        type: 'list',
        ordered: isOrdered,
        start,
        items
      },
      endIndex: i
    }
  }

  private parseBlockquote(tokens: any[], startIndex: number): { block: Block; endIndex: number } {
    let i = startIndex + 1
    const childTokens: any[] = []
    let depth = 1
    while (i < tokens.length && depth > 0) {
      if (tokens[i].type === 'blockquote_open') {
        depth++
        childTokens.push(tokens[i])
      } else if (tokens[i].type === 'blockquote_close') {
        depth--
        if (depth > 0) childTokens.push(tokens[i])
      } else {
        childTokens.push(tokens[i])
      }
      i++
    }
    const content = this.parseBlocks(childTokens)
    return {
      block: {
        type: 'blockquote',
        content
      },
      endIndex: i - 1
    }
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
      } else if (token.type === 'heading_open') {
        const level = parseInt(token.tag.replace('h', ''), 10)
        const contentToken = tokens[i + 1]
        blocks.push({
          type: 'heading',
          level,
          content: contentToken.type === 'inline' ? this.md.renderInline(contentToken.content) : ''
        })
        i += 3 // heading_open, inline, heading_close
      } else if (token.type === 'paragraph_open') {
        const contentToken = tokens[i + 1]
        blocks.push({
          type: 'paragraph',
          content: contentToken.type === 'inline' ? this.md.renderInline(contentToken.content) : ''
        })
        i += 3 // paragraph_open, inline, paragraph_close
      } else if (token.type === 'blockquote_open') {
        const { block, endIndex } = this.parseBlockquote(tokens, i)
        blocks.push(block)
        i = endIndex + 1
      } else if (token.type === 'ordered_list_open' || token.type === 'bullet_list_open') {
        const { block, endIndex } = this.parseList(tokens, i)
        blocks.push(block)
        i = endIndex + 1
      } else if (token.type === 'hr') {
        blocks.push({ type: 'hr' })
        i++
      } else {
        i++
      }
    }
    return blocks
  }
} 