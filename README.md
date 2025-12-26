# Pulse - Module Extraction

An application (CLI, Streamlit UI, and API) that crawls documentation help websites, extracts meaningful content, infers product modules and submodules, and returns clean structured outputs. All results are based solely on the content of the provided URLs.

## Overview
This tool processes documentation sites to identify key modules (major categories) and their submodules (specific functions/features). For example, a “Manage Account” module might have submodules such as “Delete Account” and “Deactivate Account”. The extractor crawls relevant pages, filters out navigation/boilerplate, and generates concise descriptions for modules and submodules from the page content.

## Features
- Multiple input URLs (CLI/UI/API)
- Resilient in-domain crawler (respects robots.txt, retries/backoff)
- Content cleaning: drops header/footer/nav, focuses main/article
- Hierarchy inference via headings and structure
- Descriptions for modules and submodules from content only
- Confidence score added for each description
- JSON output (specified format), plus CSV/YAML exports in Streamlit
- Per-URL result boxes with individual downloads
- Combined “Download All” (JSON/CSV/YAML)
- Optional throttling via delay; caching enabled
- Dockerfile provided for UI/API deployment

## Getting Started (Windows)
1. Create a virtual environment and install dependencies:
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```
2. Run the CLI (unlimited by default):
```powershell
python module_extractor.py --urls https://help.instagram.com
```
Optional limits:
```powershell
python module_extractor.py --urls https://help.instagram.com --max-pages 200 --per-domain-limit 150 --delay 0.3
```
3. Run the Streamlit UI:
```powershell
streamlit run streamlit_app.py
```
UI tips:
- Paste one or more URLs (newline or space separated)
- Defaults to “No limits”; set limits only if you want to restrict crawling
- Per-URL boxes with JSON/CSV/YAML, plus “Download All” for combined results
- Use “Clear Result” to reset and run again

4. Run the FastAPI server (optional):
```powershell
uvicorn fastapi_app:app --host 0.0.0.0 --port 8000
```

5. Docker (optional):
```powershell
docker build -t pulse-extractor .
docker run -p 8501:8501 pulse-extractor
```
Run API instead:
```powershell
docker run -p 8000:8000 --entrypoint uvicorn pulse-extractor fastapi_app:app --host 0.0.0.0 --port 8000
```

## Requirements
### Core Functionality
1. Accept one or more documentation URLs as input
2. Automatically crawl and process relevant pages linked within the URL(s)
3. Identify and extract:
   - Key modules representing major documentation categories
   - Submodules under each module
   - Detailed descriptions for both modules and submodules
4. Return a structured JSON output in the specified format

### Technical Requirements
#### Input Handling
- Accept one or more URLs via CLI/UI/API
- Validate and normalize input URLs
- Recursively crawl relevant documentation pages
- Handle redirects, broken links, and unsupported formats

#### Content Processing
- Extract meaningful documentation content; exclude header, footer, navigation
- Maintain content hierarchy based on document structure and layout
- Handle HTML content formats including text, lists, and tables
- Normalize content into a consistent internal representation

#### Module/Submodule Inference
- Infer top-level modules from sections or primary topics
- Group logically connected subtopics under each module as submodules
- Generate detailed descriptions for each using extracted content only

## Output Format
Produces a list of objects:
```json
[
  {
    "module": "Module_1",
    "Description": "Detailed description of the module",
    "Submodules": {
      "submodule_1": "Detailed description of submodule 1",
      "submodule_2": "Detailed description of submodule 2"
    },
    "confidence": 0.82
  }
]
```

## Example Usage
CLI:
```powershell
python module_extractor.py --urls https://help.instagram.com
```

Streamlit:
```powershell
streamlit run streamlit_app.py
```

FastAPI:
```powershell
uvicorn fastapi_app:app --host 0.0.0.0 --port 8000
```

## Sample Output
```json
[
  {
    "module": "Account Settings",
    "Description": "Includes features and tools for managing account preferences, privacy, and credentials.",
    "Submodules": {
      "Change Username": "Explains how to update the handle and display name via account settings."
    },
    "confidence": 0.83
  },
  {
    "module": "Content Sharing",
    "Description": "Covers tools and workflows for creating, editing, and publishing content.",
    "Submodules": {
      "Creating Reels": "Instructions for recording, editing, and sharing short-form video content.",
      "Tagging Users": "Details on tagging individuals or businesses in posts and stories for engagement."
    },
    "confidence": 0.79
  }
]
```

## Evaluation Criteria
- Accuracy & Structure (40%): correct identification, grouping, and precise descriptions
- Technical Implementation (30%): intelligent hierarchy extraction, resilient crawler/parser, efficient pipeline
- Code Quality (15%): modular architecture, clean style, error handling/logging, clear docs
- Visual Demonstration (15%): ≤5 min screen recording showing inputs, outputs, and successful processing

## Bonus Points
1. Advanced Features
   - Support multiple documentation sources
   - Caching mechanism
   - Support different documentation formats
   - Confidence scores
2. Technical Improvements
   - Docker containerization
   - API endpoint
   - Performance optimizations

## Architecture
- `src/pulse_extractor/crawler.py`: URL validation, BFS crawler, robots respect, link filtering, retries/backoff
- `src/pulse_extractor/extractor.py`: Content extraction (BeautifulSoup/lxml, markdown support), structure focus on main/article
- `src/pulse_extractor/inference.py`: Hierarchy parsing and mapping to modules/submodules; description generation; confidence scoring
- `src/pulse_extractor/output.py`: Output formatting
- `src/pulse_extractor/cache.py`: Requests caching configuration
- `module_extractor.py`: CLI entry
- `streamlit_app.py`: Streamlit interface (per-URL boxes, downloads, Download All, Clear Result)
- `fastapi_app.py`: FastAPI endpoint
- `Dockerfile`: Containerization for UI/API

## Notes
1. Language: Python
2. Third-party libraries: streamlit, requests, beautifulsoup4, trafilatura, lxml, tldextract, requests-cache, readability-lxml, urllib3, fastapi, uvicorn, markdown, pdfminer.six, pyyaml
3. Assumptions: documentation headings reflect hierarchy; descriptions can be formed from nearby text
4. Limitations: heavy JS-rendered docs may need headless browsing; multilingual content not detected; performance optimizations (async/batching) not implemented

## Testing
- Run on at least 4 different URLs (see tests and samples)
```powershell
python tests/run_four_small_samples.py
```
- Saved outputs in `samples/`

## Submission Requirements
1. Repository: private repo with clear README, setup instructions, usage examples, design rationale, known limitations
2. Documentation: technical architecture description, approach notes, assumptions, edge case handling
3. Testing: sample inputs and expected outputs across multiple URLs

## License
Private repository; usage limited to evaluation and demo purposes.
# Pulse - Module Extraction

A Streamlit application and CLI that crawls documentation sites, extracts meaningful content, infers modules and submodules, and generates structured JSON with descriptions — using only the provided URLs.

## Features
- Accepts one or more documentation URLs
- Recursively crawls relevant pages (respecting domain and robots.txt)
- Extracts cleaned content (headers/body) and normalizes it
- Infers modules/submodules via document hierarchy and structure cues
- Generates detailed descriptions and confidence scores from extracted content
- Outputs consistent JSON and provides a Streamlit UI and CLI
- Caching and rate limiting for resilience
- Streamlit downloads: JSON, CSV, YAML

## Quickstart (Windows)
1. Create env and install deps:
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```
2. Run CLI:
```powershell
python module_extractor.py --urls https://help.instagram.com --max-pages 10 --per-domain-limit 10 --delay 0.3
```
3. Run Streamlit UI:
```powershell
streamlit run streamlit_app.py
```
## Run-All Script
- One-command setup + smoke + samples:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
scripts\run_all.ps1 -Task All -MaxPages 10 -PerDomainLimit 10
```
- Launch only UI or API:
```powershell
scripts\run_all.ps1 -Task UI
scripts\run_all.ps1 -Task API
```
- Docker options:
```powershell
scripts\run_all.ps1 -Task DockerBuild
scripts\run_all.ps1 -Task DockerUI
scripts\run_all.ps1 -Task DockerAPI
```

4. Run FastAPI (optional):
```powershell
uvicorn fastapi_app:app --host 0.0.0.0 --port 8000
```

## Usage Examples
- Multiple URLs:
```powershell
python module_extractor.py --urls https://support.neo.space/hc/en-us https://wordpress.org/documentation/ https://help.zluri.com/ https://www.chargebee.com/docs/2.0/ --max-pages 12 --per-domain-limit 6 --delay 0.3
```

## Output Format
Produces a list of objects:
```json
[
  {
    "module": "Module_1",
    "Description": "Detailed description of the module",
    "Submodules": {
      "submodule_1": "Detailed description of submodule 1",
      "submodule_2": "Detailed description of submodule 2"
    },
    "confidence": 0.82
  }
]
```

### Downloads (Streamlit)
- JSON: Full structured output
- CSV: Flattened rows with columns `module`, `description`, `submodule`, `sub_description`, `confidence`
- YAML: Preserves nested structure and keys

## Architecture
- `src/pulse_extractor/crawler.py`: URL validation, BFS crawler, robots respect, link filtering
- `src/pulse_extractor/extractor.py`: Content extraction (trafilatura, BeautifulSoup fallbacks)
- `src/pulse_extractor/inference.py`: Hierarchy parsing, module/submodule inference, description generation
- `src/pulse_extractor/output.py`: JSON serialization and formatting
- `src/pulse_extractor/cache.py`: Requests caching and rate limiting helpers
- `module_extractor.py`: CLI entry
- `streamlit_app.py`: Streamlit interface
  - Offers JSON/CSV/YAML downloads after extraction

## Assumptions
 - Per-URL results with individual downloads
 - "Download All" section to export combined JSON/CSV/YAML

## Testing
- See `tests/run_samples.py` to run against 4 sample B2B docs:
  - https://support.neo.space/hc/en-us
  - https://wordpress.org/documentation/
  - https://help.zluri.com/
   - Use the "No limits" checkbox to crawl without page limits.
  - https://www.chargebee.com/docs/2.0/

 - Per-URL boxes: One set of downloads per input URL
 - Download All: Exports combined results across all URLs
```
Small smoke test:
  - Per-URL result boxes and combined "Download All" exports
```powershell
python module_extractor.py --urls https://wordpress.org/documentation/ --max-pages 10 --per-domain-limit 10 --delay 0.3

## Bonus (Optional)
- Dockerfile for containerization
 - Unlimited:
```powershell
python module_extractor.py --urls https://wordpress.org/documentation/ https://www.chargebee.com/docs/2.0/ --max-pages 0 --per-domain-limit 0
```
- Simple FastAPI endpoint to serve results

### Docker
Build and run the Streamlit UI (port 8501):
```powershell
docker build -t pulse-extractor .
docker run -p 8501:8501 pulse-extractor
```

Run the FastAPI server instead:
```powershell
docker run -p 8000:8000 --entrypoint uvicorn pulse-extractor fastapi_app:app --host 0.0.0.0 --port 8000
```

### Visuals
Include a short demo video showing:
- Input URLs in UI
- Progress spinner and resulting JSON
 - Downloading JSON/CSV/YAML
- CLI run with console output
Add link here when available.

## License
Private repository; usage limited to evaluation and demo purposes.
