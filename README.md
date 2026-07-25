
# Page Pulse

A URL auditing tool I built for a take-home task. Give it a URL, 
it fetches the page and returns a report — SEO fields, load time, 
structural stuff like missing alt text, and a rough SEO score I 
added on top.

Live: [your-url-here]

---

## Stack

Python, FastAPI, BeautifulSoup4. I picked FastAPI 
over Flask mostly because the main thing this does is make a network 
request, and blocking on that felt wrong.

Frontend is plain HTML/CSS/JS — no React, no build step. 


---

## Running it locally

```bash
git clone https://github.com/yourusername/page-pulse
cd page-pulse/backend

python -m venv venv
source venv/bin/activate

pip install -r requirements.txt
uvicorn main:app --reload
```

Open `frontend/index.html` in your browser. 
Make sure `API_BASE` at the top of the script tag says `http://localhost:8000`.

---

## API

Returns this shape on success:

```json
{
  "url": "https://example.com",
  "http_status": 200,
  "response_time_ms": 284,
  "title": "Example Domain",
  "meta_description": null,
  "h1_count": 1,
  "images_missing_alt": 0,
  "word_count": 28,
  "seo_score": 70,
  "seo_grade": "Needs Work",
  "seo_issues": ["Missing meta description"]
}
```

On failure (invalid URL, timeout, non-HTML):

```json
{ "error": "Request timed out after 10 seconds" }
```

Errors always come back as 200 with an `error` key. 
I know that's not REST-correct. But it meant the frontend 
only needs one code path to handle everything, which felt 
like the right trade for a tool this small.

---

## Tests

```bash
pytest tests/ -v
```

Three tests — happy path, timeout, and a PDF/non-HTML response. 
Used mocks so nothing hits the real network during testing.

---

## Three decisions worth explaining

**Splitting auditor.py out from main.py**

This was honestly the most useful thing I did. Once the parsing 
logic was in its own file, testing it was straightforward — 
no need to spin up the server, no HTTP client setup in the tests. 
I almost didn't bother separating them on a project this small, 
but I'm glad I did.

**The SEO score is opinionated and that's fine**

The scoring weights are ones I picked. Losing 20 points for no 
H1 feels right to me, losing 5 for a title over 60 chars also 
feels right. Someone else would weigh it differently. I'd rather 
have a score with a clear, stated logic than one that pretends 
to be objective.

**Word count is a known approximation**

`soup.get_text()` grabs everything — nav links, button labels, 
footer text. The count is inflated as a result. I thought about 
stripping `<nav>`, `<footer>`, `<aside>` before counting, 
but it added complexity and the ballpark number is still useful. 
If I had more time, I'd fix this properly.

---

## What I'd change with more time

Caching. Right now the same URL hits the target server fresh 
every single request. Even a 60-second in-memory cache with 
something like `cachetools` would make it noticeably better.

Also the frontend could show a score history if you audit 
multiple URLs — right now each result replaces the last one.



---

## AI usage
I Used Claude to help with the async mock syntax in the tests 
(it's genuinely unintuitive), and to sanity-check my 
BeautifulSoup selectors. The SEO scoring logic, the 
auditor/main split decision, and the error handling approach 
are all mine.

---

*Built for Digital Heroes Training Task — [digitalheroesco.com](https://digitalheroesco.com)*
