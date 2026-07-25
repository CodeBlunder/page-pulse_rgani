import httpx
import time
from bs4 import BeautifulSoup


def calculate_seo_score(data: dict) -> dict:
    score = 100
    issues = []

    
    if not data["title"]:
        score -= 15
        issues.append("Missing page title")
    elif len(data["title"]) > 60:
        score -= 5
        issues.append(f"Title too long ({len(data['title'])} chars, keep it under 60)")
    elif len(data["title"]) < 10:
        score -= 5
        issues.append("Title is too short")

    
    if not data["meta_description"]:
        score -= 15
        issues.append("Missing meta description")
    elif len(data["meta_description"]) > 160:
        score -= 5
        issues.append(f"Meta description too long ({len(data['meta_description'])} chars, aim for under 160)")

    
    if data["h1_count"] == 0:
        score -= 20
        issues.append("No H1 tag found on the page")
    elif data["h1_count"] > 1:
        score -= 10
        issues.append(f"Found {data['h1_count']} H1 tags — there should only be one")

    
    if data["images_missing_alt"] > 0:
        penalty = min(data["images_missing_alt"] * 5, 20)
        score -= penalty
        issues.append(f"{data['images_missing_alt']} image(s) missing alt text")

    
    if data["word_count"] < 300:
        score -= 10
        issues.append(f"Low content volume ({data['word_count']} words) — search engines generally prefer 300+")

    score = max(score, 0)

    if score >= 80:
        grade = "Good"
    elif score >= 50:
        grade = "Needs Work"
    else:
        grade = "Poor"

    return {
        "score": score,
        "grade": grade,
        "issues": issues
    }


async def audit_url(url: str) -> dict:
    start = time.time()

    try:
        async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
            response = await client.get(
                url,
                headers={"User-Agent": "Mozilla/5.0 (compatible; PagePulse/1.0)"}
            )
    except httpx.TimeoutException:
        return {"error": "request timed out after 10 seconds"}
    except httpx.RequestError as e:
        return {"error": f"could not reach the url: {str(e)}"}

    response_time = round((time.time() - start) * 1000)

    
    content_type = response.headers.get("content-type", "")
    if "text/html" not in content_type:
        return {"error": f"non-html response received ({content_type.split(';')[0].strip()})"}

    soup = BeautifulSoup(response.text, "html.parser")


    title = None
    if soup.title and soup.title.string:
        title = soup.title.string.strip()

    
    meta_description = None
    meta_tag = soup.find("meta", attrs={"name": "description"})
    if meta_tag and meta_tag.get("content"):
        meta_description = meta_tag["content"].strip()

    
    h1_count = len(soup.find_all("h1"))

    
    images = soup.find_all("img")
    missing_alt = sum(1 for img in images if img.get("alt") is None)

    
    body_text = soup.get_text(separator=" ")
    word_count = len([w for w in body_text.split() if w.strip()])

    seo = calculate_seo_score({
        "title": title,
        "meta_description": meta_description,
        "h1_count": h1_count,
        "images_missing_alt": missing_alt,
        "word_count": word_count
    })

    return {
        "url": url,
        "http_status": response.status_code,
        "response_time_ms": response_time,
        "title": title,
        "meta_description": meta_description,
        "h1_count": h1_count,
        "images_missing_alt": missing_alt,
        "word_count": word_count,
        "seo_score": seo["score"],
        "seo_grade": seo["grade"],
        "seo_issues": seo["issues"]
    }
