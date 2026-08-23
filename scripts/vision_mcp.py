from mcp.server.fastmcp import FastMCP
import httpx
import os
import base64

mcp = FastMCP("vision")

API_KEY = os.environ.get("SILICONFLOW_API_KEY") or os.environ.get("OMBRE_EMBED_API_KEY", "")
MODEL = os.environ.get("VISION_MODEL", "Qwen/Qwen3-VL-32B-Instruct")
BASE_URL = "https://api.siliconflow.cn/v1/chat/completions"

HEADERS = {"User-Agent": "Mozilla/5.0 (Linux; Android 12)"}

def _to_data_uri(image_url: str) -> str:
    if image_url.startswith("data:"):
        return image_url
    img = httpx.get(image_url, headers=HEADERS, timeout=30, follow_redirects=True)
    ctype = img.headers.get("content-type", "image/jpeg")
    if not ctype.startswith("image/"):
        ctype = "image/jpeg"
    b64 = base64.b64encode(img.content).decode()
    return "data:%s;base64,%s" % (ctype, b64)

def _describe(image_url: str, prompt: str) -> str:
    if not API_KEY:
        return "error: no API key found"
    try:
        data_uri = _to_data_uri(image_url)
    except Exception as e:
        return "error downloading image: %s" % e
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "user", "content": [
                {"type": "image_url", "image_url": {"url": data_uri}},
                {"type": "text", "text": prompt}
            ]}
        ],
        "max_tokens": 1024
    }
    try:
        r = httpx.post(BASE_URL, json=payload,
                       headers={"Authorization": "Bearer %s" % API_KEY}, timeout=60)
        if r.status_code != 200:
            return "error %s: %s" % (r.status_code, r.text[:500])
        d = r.json()
        return d["choices"][0]["message"]["content"]
    except Exception as e:
        return "error: %s" % e

@mcp.tool()
def describe_image(image_url: str, prompt: str = "Describe this image in detail.") -> str:
    """Understand an image. image_url: http(s) URL or base64 data URI. prompt: question about the image."""
    return _describe(image_url, prompt)

if __name__ == "__main__":
    print("vision model = %s" % MODEL)
    import uvicorn
    uvicorn.run(mcp.streamable_http_app(), host="127.0.0.1", port=18003)
