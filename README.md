# telegraph-cli

A command-line tool to publish content to [telegra.ph](https://telegra.ph) from your terminal.

## Features

- Post Markdown or HTML files (auto-detected by extension)
- Read from stdin with `-`
- YAML frontmatter support for title and author
- Edit existing pages
- List all pages on your account
- Account management (create, inspect, revoke token)

## Installation

Requires Python 3.10+. Install with [pipx](https://pipx.pypa.io) for a global `telegraph` command:

```bash
pipx install /path/to/telegraph
```

Or into a virtualenv:

```bash
uv pip install -e /path/to/telegraph
```

## Setup

Create a Telegraph account and save the access token:

```bash
telegraph account create
```

The token is stored at `~/.config/telegraph/config.json`.

## Usage

```
telegraph account create          # create account and save token
telegraph account info            # show account details
telegraph account revoke          # revoke current token

telegraph post <file>             # post a file
telegraph post -                  # post from stdin
telegraph edit <path> <file>      # update an existing page
telegraph list                    # list all your pages
```

### Options for `post` and `edit`

| Flag | Description |
|---|---|
| `-t, --title TEXT` | Page title (required if not in frontmatter) |
| `-a, --author TEXT` | Override author name |
| `--format [markdown\|html]` | Force input format (default: auto-detect) |

### Options for `list`

| Flag | Default | Description |
|---|---|---|
| `--limit N` | 50 | Number of pages to return |
| `--offset N` | 0 | Pagination offset |

## Examples

### Post from stdin

```bash
echo "# Hello World

This is my first post." | telegraph post - --title "Hello World"
```

### Post a Markdown file

```bash
telegraph post article.md --title "My Article"
```

### Post with YAML frontmatter (no `--title` needed)

```markdown
---
title: My Article
author: Jane Doe
---

# My Article

Content goes here.
```

```bash
telegraph post article.md
```

### Post an HTML file

```bash
telegraph post page.html --title "My Page"
```

### Force format

```bash
cat notes.txt | telegraph post - --title "Notes" --format markdown
```

### Edit an existing page

The `path` is the last segment of the page URL (e.g. `My-Article-01-01`):

```bash
telegraph edit My-Article-01-01 article.md
telegraph edit My-Article-01-01 - --title "Updated Title"
```

### List pages

```bash
telegraph list
telegraph list --limit 10
telegraph list --limit 10 --offset 20
```

## Format Detection

| Source | Format |
|---|---|
| `--format markdown` or `--format html` | Forced |
| File with `.html` or `.htm` extension | HTML |
| Any other file extension | Markdown |
| Stdin (`-`) | Markdown (override with `--format`) |

## Config

Token and account info are stored in `~/.config/telegraph/config.json` (mode `0600`).
