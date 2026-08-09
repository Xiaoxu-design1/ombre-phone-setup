# 🎓 Ombre Brain 手机系统 · 操作卡片

> 永久留档版。本卡片由搭建过程整理而成，遇到问题照着抄即可。
> 配套：`README.md`（完整搭建教程）· `.env.example`（钥匙模板）· `start_ombre.sh`（一键托管脚本）· `downloads.md`（下载清单）

---

## 一、系统组成

| 部件 | 是什么 | 位置 |
|---|---|---|
| 记忆服务 | Ombre Brain | 手机本地 Ubuntu（Termux + proot）里 |
| 大脑 | DeepSeek（deepseek-chat） | 云端 |
| 联想 | 硅基流动（BAAI/bge-m3） | 云端 |
| 使用入口 | RikkaHub app | 手机 |

## 二、日常使用（3 句口诀）

1. **新对话第一句**：让 AI「先 breath 一下」→ 唤醒记忆
2. **想让 AI 记住**：说「记住……」
3. **想回忆**：问「你还记得……吗」

## 三、常用命令（Termux 里）

| 场景 | 命令 |
|---|---|
| 进入小电脑 | `proot-distro login ubuntu` |
| 🚀 一键启动服务 | `cd ~/Ombre-Brain && bash start_ombre.sh` |
| 看服务日志 | `tmux attach -t ob`（退出按 Ctrl+B 再 D） |
| 重启服务 | 再跑一次 `bash start_ombre.sh` |
| 体检服务 | `curl http://127.0.0.1:18001/health` |
| 管理面板 | 手机浏览器开 `http://127.0.0.1:18001` |

> ⚠️ 命令提示符下**一次粘一行**（多行会乱）；nano 编辑器里才整段粘。

## 四、⚠️ 注意事项（铁律）

1. **服务在跑时**：别 `exit` 退出 Ubuntu、别按 Ctrl+C、别在"最近任务"里划掉 Termux
2. **防后台杀**：Termux 电池优化设"不限制" + `termux-wake-lock`（重启手机后要重设）
3. **钥匙安全**：DeepSeek / 硅基流动 / GitHub 三把 Key 都别泄露；建议定期重新生成轮换
4. **记忆有保险**：已开 GitHub 自动备份 → 私有仓库 `Xiaoxu-design1/ombre-brain-backup`
5. **换机/重装前**：先确认备份成功（GitHub 仓库里有文件）再动手

## 五、🔄 重启手机后的恢复流程（5 步）

```bash
# 1. 打开 Termux
termux-wake-lock                          # 2. 重新锁防杀
proot-distro login ubuntu                 # 3. 进小电脑
cd ~/Ombre-Brain && bash start_ombre.sh   # 4. 一键启动
# 5. 浏览器开 http://127.0.0.1:18001 验证 / 直接用 RikkaHub
```

## 六、服务挂了怎么办（清后台 / 被系统杀掉）

```bash
termux-wake-lock
proot-distro login ubuntu
cd ~/Ombre-Brain && bash start_ombre.sh
```

> 记忆不会丢：存在手机磁盘 + GitHub 备份双保险。服务只是"开关"，随时能拉起来。

## 七、后台要不要一直挂着？

- 想"随叫随到" → 让 Termux 挂后台别划掉（空闲耗电极小）
- 不用了 → 清掉省电，记忆不丢，要用再启动

## 八、当前配置快照

- Ombre Brain 版本：v2.16.7（Ubuntu 内 `~/Ombre-Brain`）
- 端口：18001（MCP：`http://127.0.0.1:18001/mcp`）
- 传输：streamable-http，绑定 127.0.0.1，MCP 免鉴权（仅本地回环）
- 备份仓库：`Xiaoxu-design1/ombre-brain-backup`（私有）
