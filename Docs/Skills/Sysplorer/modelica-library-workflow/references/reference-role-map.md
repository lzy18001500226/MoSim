# 参考资料角色映射

## 目的

把当前 `modelica-library-workflow` 的参考资料与执行流程做一一对应，减少“目录结构不像模板就不知道先读什么”的问题。

## 当前文件与标准角色映射

| 当前文件 | 主要职责 | 对齐 V2.0 的角色 |
| --- | --- | --- |
| `shared-standards.md` | 全局执行纪律、串行 gate 和禁止事项 | global execution rules |
| `ai-execution-spec.md` | 执行角色、必须做到和禁止事项 | execution spec |
| `requirement-mapper.md` | 把用户自然语言请求分流成建库、整理、扩展、评审、中文化、图面修复等任务类型 | requirement map |
| `template-package-scheme.md` | 顶层 package、业务包、`Interfaces`、`Utilities` 和中文命名方案 | component/package map |
| `cross-domain-business-package-strategy.md` | 在新领域、混合领域或模板示例不足时，按组件角色和领域画像推导业务包 | domain-to-package mapping |
| `executor-base.md` | 执行顺序、最小闭环、首版验证门槛、接口与图面硬规则落地 | execution baseline |
| `phase-output-templates.md` | 各阶段结构化输出字段与模板 | phase output templates |
| `workflow-checklist.md` | 阶段性自检、结构检查、接口检查、图面检查、验证闭环检查 | process checklist / validation rules |
| `common-errors.md` | 高频错误、误区和修复优先级 | common errors |
| `acceptance-checklist.md` | 判断是否能宣称“完成”“可交付”“可发布” | acceptance checklist |
| `input-output-contract.md` | 结论输出口径、风险表达和验证说明结构 | output contract |
| `promotion-checklist.md` | 技能对外推广前的一致性和元数据复核 | promotion checklist |

## 推荐读取顺序

1. 先读 `shared-standards.md` 和 `ai-execution-spec.md`
2. 再读 `requirement-mapper.md`
3. 再读 `template-package-scheme.md`；若领域新、跨域或业务包不明显，补读 `cross-domain-business-package-strategy.md`
4. 再读 `executor-base.md`
5. 输出阶段结果时对照 `phase-output-templates.md`
6. 执行中持续对照 `workflow-checklist.md`
7. 遇到混乱结构或异常时查 `common-errors.md`
8. 准备收口时看 `acceptance-checklist.md` 和 `input-output-contract.md`
9. 准备对外推广时再看 `promotion-checklist.md`

## 使用原则

- 当前 skill 已有的参考文件名可继续沿用，不必为了贴模板而机械重命名。
- 若后续新增参考文件，优先按“一个文件只解决一类问题”的方式扩展，避免职责交叉。
- 当某条规则同时出现在多个参考文件时，应回收至一个主文件，其余文件只保留引用说明。
- 主工作流尽量保持精简，把细节规则下沉到 `references/`，避免 `SKILL.md` 重新长成“第二套完整文档”。
