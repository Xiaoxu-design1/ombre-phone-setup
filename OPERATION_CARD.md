# 🎓 Ombre Brain 手机系统 · 操作卡片（v2 · 2026-10 更新）

> 永久留档版。v2 变化：服务扩至 **5 个**（记忆 / IP / 识图 / 象棋 / 记忆桥）；一键脚本统一为 **restart_all.sh**。
> 配套：`README.md`（搭建教程）· `PROACTIVE_MESSAGE_SYSTEM.md`（AI 主动消息系统）· `.env.example`（钥匙模板）

---

## 一、系统组成

| 部件 | 是什么 | 位置 |
|---|---|---|
| 记忆服务 | Ombre Brain | 手机本地 Ubuntu（Termux + proot）里 |
| 记忆桥 | hook_bridge.py（取记忆 / 随机时间） | 手机本地 Ubuntu |
| IP 定位 | ip_mcp.py | 手机本地 Ubuntu |
| 识图 | vision_mcp.py（硅基流动 Qwen3-VL） | 手机本地 Ubuntu |
| 国际象棋 | chess_mcp.py | 手机本地 Ubuntu |
| 主动消息 | MacroDroid（每天 4 条） | 手机 App + DeepSeek 云端 |
| 大脑 | DeepSeek（deepseek-flash / v4-pro） | 云端 |
| 联想 | 硅基流动（BAAI/bge-m3） | 云端 |
| 使用入口 | RikkaHub app | 手机 |

## 二、五个服务一览

| 端口 | 服务 | 脚本 |
|---|---|---|
| 18001 | Ombre Brain 记忆（含 Dashboard） | src/server.py |
| 18002 | IP 定位 | ip_mcp.py |
| 18003 | 识图 | vision_mcp.py |
| 18004 | 国际象棋 | chess_mcp.py |
| 18005 | 记忆桥 | hook_bridge.py |

## 三、日常使用（3 句口诀）

1. **新对话第一句**：让 AI「先 breath 一下」→ 唤醒记忆
2. **想让 AI 记住**：说「记住……」
3. **想回忆**：问「你还记得……吗」

## 四、常用命令（Termux / Ubuntu 里）

| 场景 | 命令 |
|---|---|
| 进入小电脑 | `proot-distro login ubuntu` |
| 🚀 一键启动/重启全部服务 | `cd ~/Ombre-Brain && bash restart_all.sh` |
| 体检记忆 | `curl -s http://127.0.0.1:18001/health` |
| 体检记忆桥 | `curl -s http://127.0.0.1:18005/random-time` |
| 看桥在不在 | `pgrep -f hook_bridge.py` |
| 管理面板 | 手机浏览器开 `http://127.0.0.1:18001` |

> ⚠️ 命令提示符下**一次粘一行**（多行会乱）；nano 编辑器里才整段粘。

## 五、🔄 重启手机后的恢复流程（3 步 + 验证）

```bash
# 1. 打开 Termux，先锁防杀
termux-wake-lock
# 2. 进小电脑
proot-distro login ubuntu
# 3. 一键拉起全部服务（5 个）
cd ~/Ombre-Brain && bash restart_all.sh
```

**验证（全对 = 健康）：**

```bash
curl -s http://127.0.0.1:18001/health        # 期望 {"status":"ok",...}
curl -s http://127.0.0.1:18005/random-time   # 期望类似 21|47|33
pgrep -f hook_bridge.py                      # 输出数字 = 桥在跑
```

> RikkaHub / MacroDroid 不需要做任何事，服务起来后自动生效。

## 六、服务被杀的症状 & 处理

- **症状**：Dashboard（18001）打不开 / 主动消息"变呆"（没记忆味）/ 消息不存信
- **处理**：照上面"恢复流程"跑一遍，1 分钟满血；**不需要改任何设置**
- **断档期**的消息不会补档；想补：聊天时说「把刚才那条记住」即可

## 七、⚠️ 铁律

1. **服务在跑时**：别 `exit` 退出 Ubuntu、别按 Ctrl+C、别在"最近任务"里划掉 Termux
2. **防杀**：Termux 电池优化设"不限制" + `termux-wake-lock`；MacroDroid 同样做"防杀三连"（启动管理手动全开 / 电池不限制 / 最近任务锁定）
3. **钥匙安全**：DeepSeek / 硅基流动 / GitHub / OMBRE_HOOK_TOKEN 都别外传
4. **记忆双保险**：GitHub 自动备份 → 私有仓库 `Xiaoxu-design1/ombre-brain-backup`
5. **改过 Dashboard 密码** → 主动消息宏（登录动作）里的密码记得同步改

## 八、当前配置快照

- Ombre Brain：v2.16.9（Ubuntu 内 `~/Ombre-Brain`；绑定 127.0.0.1；MCP 免鉴权仅本地）
- 端口：18001 ~ 18005
- 备份仓库：`Xiaoxu-design1/ombre-brain-backup`（私有）
- 主动消息系统：每天 4 条（早/午/晚随机 + 22:00 晚安固定）→ 详见 `PROACTIVE_MESSAGE_SYSTEM.md`
- 记忆桥 token：存于 `.env` 的 `OMBRE_HOOK_TOKEN`
- 旧脚本 `start_ombre.sh`（tmux 时代）已停用，改用 `restart_all.sh`
