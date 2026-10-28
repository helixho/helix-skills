# Helix Skills Box

[English](README.md) | 简体中文

可复用的 Agent Skills：把需求说清楚、委派工作、交接会话、定义品牌、逻辑审查规则与论证，以及评估 skills。

每个 skill 都是独立目录，包含 `SKILL.md` 入口和所需的模板、参考或脚本。指令以中文为主，部分参考和代码使用英文。

## Skills

| Skill | 用途 | 请求示例 |
|---|---|---|
| [helix-clarify](skills/helix-clarify/SKILL.md) | 校准中文口语中的省略、指代与自我修正；只追问影响执行的缺口 | “先帮我把这件事问清楚，再决定怎么做。” |
| [helix-delegation](skills/helix-delegation/SKILL.md) | 拆分实质工作、编写任务说明并验收委派结果，适配 Codex 和 Claude Code | “把互不依赖的部分派出去，最后检查结果。” |
| [helix-handoff](skills/helix-handoff/SKILL.md) | 生成可审阅、跨工具的会话交接说明 | “交接一下，下一场会话继续完成剩余验证。” |
| [helix-ip](skills/helix-ip/SKILL.md) | 整理品牌事实、定位、口径和视觉方向；对照检查物料 | “根据这些材料，整理我的品牌 IP.md。” |
| [helix-rule-review](skills/helix-rule-review/SKILL.md) | 对规则或论证做逻辑审查：规则查矛盾、空档、优先级、概念、冗余与失效引用；论证查依据、因果、前提与手段 | “用 rule review 检查这份规则有没有互相矛盾的地方。” |
| [helix-skill-eval](skills/helix-skill-eval/SKILL.md) | 检查 skill 包结构，并按版本化标准记录评价与证据 | “检查这个 skill 的结构；需要评分时再做完整评估。” |

`helix-clarify`、`helix-handoff`、`helix-ip`、`helix-rule-review` 只含指令或模板。Delegation 使用宿主运行时，其可选本地用量统计脚本需要 Python 3.10+；`helix-skill-eval` 的脚本需要 Python 3.11+ 和 PyYAML。

## 开始使用

取得源码：

```bash
git clone https://github.com/helixho/helix-skills-box.git
cd helix-skills-box
```

把需要的 skill 目录放到所用 Agent 的 skills 目录，或创建指向源码的符号链接。每个 skill 都可独立使用。

例如，在 Codex 的用户级 skills 目录安装 `helix-clarify`：

```bash
mkdir -p "$HOME/.agents/skills"
ln -s "$PWD/skills/helix-clarify" "$HOME/.agents/skills/helix-clarify"
```

目标名称已存在时，先查看已有安装并决定使用哪一份。新会话中可以用 `$helix-clarify` 显式调用。

Codex 中，`helix-clarify`、`helix-delegation` 和 `helix-ip` 可按描述自动选择；`helix-handoff`、`helix-rule-review` 和 `helix-skill-eval` 默认仅显式调用，分别使用 `$helix-handoff`、`$helix-rule-review` 和 `$helix-skill-eval`；`helix-rule-review` 在 Claude Code 中同样仅显式调用（`/helix-rule-review`）。其他运行时按其本地 skill 发现与调用方式使用。

也可以直接让 Agent 读取某个 `SKILL.md`，按其中流程处理当前任务。

Delegation 的角色模板按 [Codex 适配说明](skills/helix-delegation/references/runtime-codex.md) 或 [Claude Code 适配说明](skills/helix-delegation/references/runtime-claude-code.md) 安装。模型默认值是可替换示例；skill 本身不安装或修改运行时配置。

## 运行结构检查

在仓库根目录创建 Python 环境并安装脚本依赖：

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r skills/helix-skill-eval/scripts/requirements.txt
```

查看支持的命令与评价标准元信息：

```bash
printf '%s\n' '{"command":"describe"}' | .venv/bin/python skills/helix-skill-eval/scripts/run.py
```

检查某个 skill 的目录与 frontmatter：

```bash
printf '%s\n' '{"command":"validate","skill_dir":"skills/helix-clarify"}' | .venv/bin/python skills/helix-skill-eval/scripts/run.py
```

结果中的 `conformant` 表示结构是否合规。完整评价的判断与证据由调用者提供，脚本校验输入并汇总结果；结构通过或评分本身都不能证明实际运行效果。完整流程见 [helix-skill-eval](skills/helix-skill-eval/SKILL.md)。

## 运行业为测试

Delegation 用量统计使用合成轨迹测试，不读取你的真实会话：

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests/skills/helix-delegation
```

## 许可证

采用 [MIT](LICENSE) 许可证，允许使用、修改、分发和商用，并要求保留版权及许可声明。
