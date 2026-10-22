---
type: ontology
revision: 3
---

# Ontology — Helix Skill Eval

## purpose

描述 skill 来源、可评估单元与评价记录。评价只针对 source 内容及其快照，不把 runtime link、安装状态或部署状态建模为本能力的对象。

## concepts

- id: c_source_project
  name: Source Project
  meaning: 提供一个或多个 skill 的上游或本地来源项目身份。
  examples: Git repository, managed local project
  aliases: source
- id: c_skill_unit
  name: Skill Unit
  meaning: 来源项目内由规范子路径标识的可评估 skill；显示名不是身份。
  examples: source project plus SKILL.md subpath
  aliases: skill
- id: c_assessment
  name: Assessment
  meaning: 基于版本化 rubric 的评价、评分、证据与 review findings。
  examples: individual skill evaluation
  aliases: evaluation

## relationships

- name: contains
  from: c_source_project
  to: c_skill_unit
  meaning: 一个来源项目可包含多个可评估 skill 单元。
  cardinality: one-to-many
- name: evaluates
  from: c_assessment
  to: c_skill_unit
  meaning: 一个评价对应一个 skill 单元与其内容快照。
  cardinality: many-to-one

## rules

- Source Project 与 Skill Unit 只描述被评估 source，不表达安装或 runtime 状态。
- Assessment 必须绑定明确内容快照和证据；不能据此自动执行修改、部署或生命周期决定。
- upstream 项目级判断与单个 Skill Unit 的评价必须分开表达。

## operations

- validate a Skill Unit
- evaluate a Skill Unit
- build a Source Profile
