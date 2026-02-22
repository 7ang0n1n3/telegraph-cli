# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-02-22

### Added
- `telegraph view <path>` command — fetches and renders a page in the terminal with rich formatting (headings, bold, italic, links, code blocks, lists, blockquotes)

## [0.1.0] - 2026-02-22

### Added
- `telegraph post <file>` — create a new page from a Markdown or HTML file, or stdin
- `telegraph edit <path> <file>` — update an existing page
- `telegraph list` — list all pages with title, URL, and view count
- `telegraph account create` — register a new Telegraph account and save token
- `telegraph account info` — display account details
- `telegraph account revoke` — revoke the current access token
- YAML frontmatter support (`title:`, `author:`) in post and edit commands
- Auto-detection of input format by file extension (`.html`/`.htm` → HTML, everything else → Markdown)
- Config stored at `~/.config/telegraph/config.json` (mode 0600)
