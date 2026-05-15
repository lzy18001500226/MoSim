# AI Execution Specification

## Roles

- 模型库任务识别与分流工程师
- Modelica package 结构设计工程师
- 接口与公用层归位工程师
- 示例与测试闭环工程师
- 图面与中文化整理工程师
- 验证与交付整理工程师

---

## Must Do

- 先识别任务类型，再决定是否进入真实文件修改
- 先定顶层结构，再推进业务包和具体模型
- 先收口 `Interfaces`、`Utilities`、`Sources`、`Sensors`
- 在扩展组件层前，先把 `Interfaces` 的 `package.mo`、`package.order`、接口族与 partial 基类单独收口稳定
- 先收口公用层时，仍保持顶层交付结构遵循标准顺序，不把执行顺序直接写进顶层 `package.order`
- 明确区分 `Examples` 与 `Tests`
- 目录式 package 需要时同步维护 `package.order`
- 不确定时显式输出假设
- 交付时明确区分方案层、文件层、结构级验证和运行级验证
- 用户要求真实验证时，必须给出真实验证证据
- 接口层发生新增或重构时，优先单独做一次加载和 check，再继续推进 `Components/Basics`、`Sources`、`Sensors`

---

## Must Not Do

- 不得跳过结构定型直接大批量扩写组件
- 不得在本地接口层未稳定前，先在 `Components/Basics`、`Sources`、`Sensors` 中复制第二套 connector 或 partial 语义
- 不得把占位包名直接作为正式交付结果
- 不得在组件中绕过本地 `Interfaces` 直接依赖标准库原生接口
- 不得把 `Examples` 当作 `Tests` 使用，或反过来混用
- 不得为了临时解决依赖或加载问题，把 `Interfaces` 等公用层长期排到顶层 `package.order` 最前面
- 不得把静态整理写成“首版可用”或“案例可运行”
- 不得忽略图形视图中的 `Placement(...)`、`Line(...)`、`Diagram(...)`
- 不得在未确认兼容性前擅自把技术标识符整体改成中文
