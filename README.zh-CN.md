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
| [helix-logic-review](skills/helix-logic-review/SKILL.md) | 依据逻辑学四条基本规律、定义与划分规则（MECE）和常见谬误（稻草人、滑坡、虚假两难等），审查任何内容中的谬误、矛盾、重叠与缺失 | “用 rule review 检查这份规则有没有互相矛盾的地方。” |
| [helix-skill-review](skills/helix-skill-review/SKILL.md) | 按批判性思维、MECE、奥卡姆剃刀、独立性以及 Agent Skills 规范和渐进式披露评估 skill，找出改进点；也判断外部 skill 有什么值得借鉴 | “检查这个 skill 的结构；需要评分时再做完整评估。” |

`helix-clarify`、`helix-handoff`、`helix-ip`、`helix-logic-review` 只含指令或模板。Delegation 使用宿主运行时，其可选本地用量统计脚本需要 Python 3.10+；`helix-skill-review` 的脚本需要 Python 3.11+ 和 PyYAML。

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

Codex 中，`helix-clarify`、`helix-delegation` 和 `helix-ip` 可按描述自动选择；`helix-handoff`、`helix-logic-review` 和 `helix-skill-review` 默认仅显式调用，分别使用 `$helix-handoff`、`$helix-logic-review` 和 `$helix-skill-review`；`helix-handoff` 和 `helix-logic-review` 在 Claude Code 中同样仅显式调用（`/helix-handoff`、`/helix-logic-review`）。其他运行时按其本地 skill 发现与调用方式使用。

也可以直接让 Agent 读取某个 `SKILL.md`，按其中流程处理当前任务。

Delegation 的角色模板按 [Codex 适配说明](skills/helix-delegation/references/runtime-codex.md) 或 [Claude Code 适配说明](skills/helix-delegation/references/runtime-claude-code.md) 安装。模型默认值是可替换示例；skill 本身不安装或修改运行时配置。

## 更新与卸载

使用符号链接安装时，在源码仓库运行 `git pull --ff-only` 即可更新，下一次新会话使用更新后的文件。直接复制安装时，更新源码后重新复制完整的 skill 目录；先检查安装目录内是否有自己修改的内容。

卸载上述链接示例时，先确认 `~/.agents/skills/helix-clarify` 是指向本仓库的符号链接，再运行：

```bash
unlink "$HOME/.agents/skills/helix-clarify"
```

直接复制安装的 skill，由所用运行时的管理功能或手动移除对应安装目录。Delegation 另行安装的角色模板需单独移除。

## 统一检查

检查需要 Python 3.11+ 和 PyYAML。在仓库根目录准备环境：

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r skills/helix-skill-review/scripts/requirements.txt
```

运行全部自动检查：

```bash
.venv/bin/python scripts/check.py
```

该命令逐个检查 `skills/` 下的 skill 结构、相对 Markdown 链接与个人主目录路径，并递归运行 `tests/` 下的 `test_*.py`。结构错误、个人主目录路径、测试加载错误、测试失败或没有发现测试时返回非零退出码；兼容的运行时扩展仅显示警告。GitHub Actions 在 push、pull request 和手动触发时运行相同入口。

自动测试覆盖 Delegation 用量统计、Skill Review 的脚本入口契约，以及统一检查的测试发现与失败传递。测试使用合成轨迹和临时样本，不读取真实会话。`tests/skills/helix-logic-review/cases.md` 是需单独执行的模型行为验收案例，不属于自动测试；结构检查和脚本测试通过不代表模型行为已经验证。

仅检查一个 skill 时，可调用现有入口：

```bash
printf '%s\n' '{"command":"validate","skill_dir":"skills/helix-clarify","public":true}' | .venv/bin/python skills/helix-skill-review/scripts/run.py
```

结果中的 `conformant` 表示结构是否合规；公开路径扫描结果单独列于 `isolation_findings`。完整评价的判断与证据由调用者提供，脚本校验输入并汇总结果；结构通过或评分本身都不能证明实际运行效果。完整流程见 [helix-skill-review](skills/helix-skill-review/SKILL.md)。

## 许可证

采用 [MIT](LICENSE) 许可证，允许使用、修改、分发和商用，并要求保留版权及许可声明。
