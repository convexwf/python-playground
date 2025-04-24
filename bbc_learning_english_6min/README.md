# tools

这里是抓取/解析 BBC Learning English（6 Minute English）页面的脚本集合。

## 依赖

- Python 3
- `requests`
- `pyquery`（依赖 `lxml`、`cssselect`）

如果缺依赖：

```bash
pip install requests pyquery lxml cssselect
```

## 推荐流程（先抓 HTML，再离线解析）

### 1) 抓取目录页（index）

```bash
python tools/fetch_html.py "https://www.bbc.co.uk/learningenglish/english/features/6-minute-english" -o data/bbc_6min_index.html
```

`-o` 可选；不传时会默认写到 `data/` 下（文件名由 URL 派生）。

### 2) 从目录页提取每集 URL

```bash
python tools/parse_6min_index_pyquery.py data/bbc_6min_index.html -o data/bbc_6min_episode_urls.txt
```

可选参数：

- 只输出前 N 条：

```bash
python tools/parse_6min_index_pyquery.py data/bbc_6min_index.html --limit 20
```

- 输出相对路径（以 `/...` 开头）：

```bash
python tools/parse_6min_index_pyquery.py data/bbc_6min_index.html --relative
```

### 3) 抓取某一集页面 HTML

```bash
python tools/fetch_html.py "https://www.bbc.co.uk/learningenglish/english/features/6-minute-english_2026/260122" -o data/bbc_260122.html
```

### 4) 解析某一集页面并生成 Markdown

```bash
python tools/parse_transcript_pyquery.py data/bbc_260122.html -o data/bbc_260122.md
```

## Makefile 快捷命令

在 `tools/` 目录下执行：

```bash
cd tools
make index
```

如果遇到 `robots.txt` 检查失败（例如网络超时），可以临时跳过（不推荐）：

```bash
cd tools
make index NO_ROBOTS=1
```

单集：

```bash
cd tools
make fetch-episode URL="https://www.bbc.co.uk/learningenglish/english/features/6-minute-english_2026/260122" OUT="../data/bbc_260122.html"
make parse-episode HTML="../data/bbc_260122.html" OUT="../data/bbc_260122.md"
```

## 注意

- `tools/fetch_html.py` 默认会检查 `robots.txt`；如果不允许抓取会直接退出。
- 目录页/列表页可能会更新；如果你看到网页上的条目更多但本地 HTML 没有，通常是分页或动态加载导致，需要抓取更多页再汇总。
