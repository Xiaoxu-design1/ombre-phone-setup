from mcp.server.fastmcp import FastMCP
import httpx
import os

mcp = FastMCP("ip-locator")

def _lookup():
    # 1) try ip-api (free, no key)
    try:
        r = httpx.get("http://ip-api.com/json/?lang=zh-CN", timeout=8)
        d = r.json()
        if d.get("status") == "success":
            return ("IP: %s\nCountry: %s\nRegion: %s\nCity: %s\nISP: %s\nLat,Lon: %s,%s" % (
                d.get("query"), d.get("country"), d.get("regionName"),
                d.get("city"), d.get("isp"), d.get("lat"), d.get("lon")))
    except Exception:
        pass
    # 2) fallback to Chinese endpoint
    try:
        r = httpx.get("https://myip.ipip.net", timeout=8)
        t = r.text.strip()
        if t:
            return t
    except Exception:
        pass
    return "query failed: cannot get IP info now"

@mcp.tool()
def get_my_ip() -> str:
    """Get this device's public IP and rough location"""
    return _lookup()

@mcp.tool()
def ip_lookup(ip: str) -> str:
    """Lookup location of any IP. arg ip: e.g. 8.8.8.8"""
    try:
        r = httpx.get(f"http://ip-api.com/json/{ip}?lang=zh-CN", timeout=8)
        d = r.json()
        if d.get("status") == "success":
            return ("IP: %s\nCountry: %s\nRegion: %s\nCity: %s\nISP: %s\nLat,Lon: %s,%s" % (
                d.get("query"), d.get("country"), d.get("regionName"),
                d.get("city"), d.get("isp"), d.get("lat"), d.get("lon")))
        return "query failed: %s" % d
    except Exception as e:
        return "query failed: %s" % e

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(mcp.streamable_http_app(), host="127.0.0.1", port=18002)
