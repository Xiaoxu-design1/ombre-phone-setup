# 📱 手机本地跑 Ombre Brain + RikkaHub 一键配置

> 纯手机、无电脑、无需境外支付、不用魔法。国内镜像优化。
> Ombre Brain 版本：v2.16.7 ｜ 适用：RikkaHub（安卓）+ DeepSeek API

---

## 一、要准备的东西（3 个）

| 用途 | 注册 | 拿什么 |
|---|---|---|
| 聊天 + 记忆打标 | https://platform.deepseek.com | DeepSeek API Key |
| 向量化（DeepSeek 没有 embedding，必须配） | https://siliconflow.cn （免费领额度） | SiliconFlow API Key |
| 终端模拟器 | 见下方「二、下载」 | Termux APK |

---

## 二、下载（国内可直连，慢就多试几次）

### 1. Termux APK（认准官方）
- GitHub Releases 页：https://github.com/termux/termux-app/releases
  - 选 `termux-app_v0.118.0+github-debug_arm64-v8a.apk`（最新稳定版，arm64 机型）
  - 不知道架构就下 `universal` 版
- 或 F-Droid 搜「Termux」（包名 com.termux，作者 Fredrik Fornwall）
- GitHub 慢的替代：APKMirror 搜 Termux

### 2. Ombre Brain 源码
- 整包 ZIP（手机浏览器直接下）：
  `https://github.com/P0luz/Ombre-Brain/archive/refs/heads/main.zip`
- 仓库地址：https://github.com/P0luz/Ombre-Brain
- GitHub 慢就用加速前缀：`https://ghfast.top/https://github.com/P0luz/Ombre-Brain.git`

### 3. RikkaHub APK
- 官网直接下：https://rikka-ai.com/download

---

## 三、安装 Termux + 换清华源

```
pkg update -y && pkg upgrade -y
termux-change-repo   # 选 Tsinghua / 清华大学
pkg install -y proot-distro
```

## 四、装 Ubuntu 并换 apt 清华源

```
proot-distro install ubuntu
proot-distro login ubuntu
apt update && apt upgrade -y
apt install -y python3 python3-pip git nano curl tmux
```

## 五、下载并安装 Ombre Brain（GitHub 加速）

```bash
cd ~
git clone https://ghfast.top/https://github.com/P0luz/Ombre-Brain.git
cd Ombre-Brain
python3 -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
```

> pip 那步要装 mcp / numpy / scikit-learn 等，耐心等 5~15 分钟。

## 六、填 Key（环境变量模板）

```bash
cp env.example .env
nano .env          # 把两个 change-me 换成你的真实 Key，Ctrl+X → Y → 回车保存
```

```
OMBRE_COMPRESS_API_KEY=你的DeepSeekKey
OMBRE_COMPRESS_BASE_URL=https://api.deepseek.com/v1
OMBRE_COMPRESS_MODEL=deepseek-chat
OMBRE_EMBED_API_KEY=你的硅基流动Key
OMBRE_EMBED_BASE_URL=https://api.siliconflow.cn/v1
OMBRE_EMBED_MODEL=BAAI/bge-m3
OMBRE_TRANSPORT=streamable-http
OMBRE_BIND_HOST=127.0.0.1
OMBRE_MCP_REQUIRE_AUTH=false
```

## 七、启动

```bash
tmux new -s ob
set -a && . ./.env && set +a
python3 src/server.py
```

看到 `Uvicorn running on http://127.0.0.1:18001` 就成功了。
手机浏览器打开 `http://127.0.0.1:18001` 设置 Dashboard 密码。

## 八、RikkaHub 连接

1. 加 DeepSeek 对话模型：OpenAI 兼容，Base URL `https://api.deepseek.com/v1`，模型 `deepseek-chat`
2. 加 MCP：类型 **Streamable HTTP**，URL **`http://127.0.0.1:18001/mcp`**，请求头不填
3. 开对话让 DeepSeek 先调用 `breath` 验证

## 九、重启手机后一键恢复

```bash
proot-distro login ubuntu
cd ~/Ombre-Brain && bash start_ombre.sh
```

## 十、防杀后台

- 系统设置里把 Termux 的电池优化/后台限制改为「不限制」
- Termux（非 Ubuntu 里）执行 `termux-wake-lock`
- 建议到 Dashboard → GitHub 同步，配一个私有仓库做记忆备份

---

## 常见坑

- 连不上 → URL 用 `127.0.0.1`（别用 localhost），末尾必须是 `/mcp`，transport 必须 streamable-http
- 记忆全「未分类」→ `dehydration.max_tokens` 设 4096+，或打标模型太弱
- 向量化 404 → base_url 漏 `/v1`；Model does not exist → model 漏 `BAAI/` 前缀
- 重启记忆丢失 → 本地是文件目录正常不会丢；重点是重装 Termux 前先备份 buckets/ 目录
