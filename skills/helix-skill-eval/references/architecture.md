---
type: architecture
---

# Architecture — Helix Skill Eval

## purpose

这是一个本地、单用户的 skill 评估能力：验证 Agent Skills 目录与 SKILL.md 规范，并基于内置 rubric 形成评价、证据、findings 和 source profile。它只读 source，不管理 runtime link，不承担 skill 安装、部署或生命周期操作。

## components

- name: Eval
  responsibility: 验证 skill 结构并形成评价、review findings 与建议。
  boundary: 不修改 source，不执行 runtime 操作，不替用户做生命周期决定。
  interfaces: validation, assessment and report contract
- name: Management Core
  responsibility: 计算评价与 source profile。
  boundary: 只处理评估输入与结果，不介入外部运行时状态。
  interfaces: evaluation and source-profile contracts

## stack_decisions

- decision: evaluation execution
  chosen: stateless Python 3.12 CLI
  rationale: 评估结果可由输入和内容快照重建，不需要 inventory、daemon 或持久化数据库。
  rejected_alternatives: SQLite assessment registry; always-on service
- decision: source boundary
  chosen: evaluate source content directly
  rationale: source project / skill unit 是评价对象，runtime 投影不是评价事实。
  rejected_alternatives: runtime-copy inventory; deployment state as source truth

## conventions

- area: source boundary
  convention: 评估只读取目标 source；不得修改或自动迁移被评估 skill。
  rationale: 保持 review 与被评估对象独立。
- area: persistence
  convention: Eval 不持久化 inventory、部署状态或生命周期决定。
  rationale: 避免把评价结果误作运行时事实。
- area: tests
  convention: 核心契约使用 deterministic tests，仓库验证不写入真实 runtime。
  rationale: 独立验证且不改变外部状态。
