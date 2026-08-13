# 👁️ 识图 MCP · 使用卡片（永久留档）

> 识图服务 = DeepSeek（大脑，纯文本） + 硅基流动 Qwen-VL（眼睛）。
> 服务文件：`~/Ombre-Brain/vision_mcp.py`，端口 18003。

---

## 一、怎么用（喂图方式）

| 要点 | 说明 |
|---|---|
| 必须用图片网址（URL） | 手机相册的图要先传图床拿"直链" |
| 直链特征 | 结尾 .jpg/.png/.webp，浏览器打开只有图、没有网页 |
| 推荐图床 | 路过图床（imgse.com）、SM.MS |
| 能问具体问题 | 用 prompt 参数，如"把图里的字打出来""这是什么动物" |

## 二、注意事项（嘱托）

1. 当前模型：`Qwen/Qwen3-VL-32B-Instruct`（存在 `.env` 的 `VISION_MODEL`）
2. 要更准 → 32B-Thinking（慢+贵）；要省钱 → 8B 或 30B-A3B
3. 提问要具体：问"图里有哪些物品"比"描述一下"准得多
4. 图片越清晰越准
5. 每次识图消耗硅基流动额度，余额不足要充值
6. 图太大（几 MB）会慢，耐心等
7. 报 `Model does not exist` = 模型名打错
8. 报 `Model disabled` = 模型下线，换 VISION_MODEL 名字
9. 报 `image URL must be valid` = 图片网址下载不了，换图/换图床

## 三、换模型方法（不用改代码）

改 `.env` 里这一行，然后重启：
```
VISION_MODEL=Qwen/Qwen3-VL-32B-Instruct
```

## 四、管理命令

| 想干什么 | 命令 |
|---|---|
| 看日志 | `cat ~/Ombre-Brain/vision.log` |
| 停服务 | `pkill -f vision_mcp.py` |
| 重启手机后恢复 | `pkill -f vision_mcp.py` → `sleep 2` → `set -a && . ./.env && set +a` → `nohup python3 vision_mcp.py > vision.log 2>&1 &` |

## 五、全服务总表（重启手机后逐个恢复）

| 服务 | 端口 | 启动命令（先进 Ubuntu + cd ~/Ombre-Brain + 加载 .env） |
|---|---|---|
| Ombre Brain 记忆 | 18001 | `nohup python3 src/server.py > ob.log 2>&1 &` |
| IP 定位 | 18002 | `nohup python3 ip_mcp.py > ip.log 2>&1 &` |
| 识图 | 18003 | `nohup python3 vision_mcp.py > vision.log 2>&1 &` |
| TTS 朗读 | RikkaHub 内置 | 无需本机服务 |
