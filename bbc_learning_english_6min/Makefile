PY ?= python
ROOT := .
DATA := $(ROOT)/tmp

NO_ROBOTS ?= 1
ROBOTS_FLAG :=
ifeq ($(NO_ROBOTS),1)
ROBOTS_FLAG := --no-robots
endif

INDEX_URL ?= https://www.bbc.co.uk/learningenglish/english/features/6-minute-english
INDEX_HTML ?= $(DATA)/bbc_6min_index.html
EP_URLS ?= $(DATA)/bbc_6min_episode_urls.txt
LIST ?= $(EP_URLS)
HTML_DIR ?= $(DATA)/html
MD_DIR ?= $(DATA)/md

# For single-episode operations
URL ?=
HTML ?=
OUT ?=

.PHONY: help fetch-index parse-index index fetch-episode parse-episode batch-transcript

help:
	@echo "Targets:"
	@echo "  make fetch-index           # fetch directory page -> $(INDEX_HTML)"
	@echo "  make parse-index           # parse $(INDEX_HTML) -> $(EP_URLS)"
	@echo "  make index                 # fetch-index + parse-index"
	@echo ""
	@echo "Single episode:"
	@echo "  make fetch-episode URL=<episode_url> OUT=<html_path>"
	@echo "  make parse-episode HTML=<html_path> OUT=<md_path>"
	@echo ""
	@echo "Batch:"
	@echo "  make batch-transcript LIST=<url_txt>"

fetch-index:
	@mkdir -p $(DATA)
	$(PY) $(ROOT)/fetch_html.py "$(INDEX_URL)" -o "$(INDEX_HTML)" $(ROBOTS_FLAG)

parse-index:
	$(PY) $(ROOT)/parse_6min_index_pyquery.py "$(INDEX_HTML)" -o "$(EP_URLS)"

index: fetch-index parse-index

fetch-episode:
	@if [ -z "$(URL)" ] || [ -z "$(OUT)" ]; then \
		echo "Usage: make fetch-episode URL=<episode_url> OUT=<html_path>"; \
		exit 2; \
	fi
	$(PY) $(ROOT)/fetch_html.py "$(URL)" -o "$(OUT)" $(ROBOTS_FLAG)

parse-episode:
	@if [ -z "$(HTML)" ] || [ -z "$(OUT)" ]; then \
		echo "Usage: make parse-episode HTML=<html_path> OUT=<md_path>"; \
		exit 2; \
	fi
	$(PY) $(ROOT)/parse_transcript_pyquery.py "$(HTML)" -o "$(OUT)"

batch-transcript:
	$(PY) $(ROOT)/batch_fetch_transcripts.py "$(LIST)" \
		--html-dir "$(HTML_DIR)" --md-dir "$(MD_DIR)" $(ROBOTS_FLAG)
