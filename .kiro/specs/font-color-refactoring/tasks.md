# Implementation Plan: Font Color Refactoring

## Overview

本实施计划将指导完成字体颜色相关代码的全面重构。通过建立基于CSS变量的统一颜色管理系统,清晰分离浅色/深色模式样式,减少!important使用,提升代码可维护性。重构将分阶段进行,每个阶段都包含验证步骤,确保重构不破坏现有功能。

## Tasks

- [x] 1. 建立CSS变量系统基础架构
  - [x] 1.1 在styles.css中定义浅色模式CSS变量
    - 在`:root`选择器中定义所有颜色变量
    - 包含文本颜色变量: `--text-primary`, `--text-secondary`, `--text-placeholder`
    - 包含背景颜色变量: `--bg-primary`, `--bg-sidebar`, `--bg-card`, `--bg-input`
    - 包含UI元素颜色变量: `--border-color`, `--accent-color`, `--success-color`, `--warning-color`, `--error-color`
    - 确保变量值符合WCAG AA级对比度标准(文本:背景 >= 4.5:1)
    - _Requirements: FR-1.1, FR-1.2, NFR-5.1_
  
  - [x] 1.2 在styles.css中定义深色模式CSS变量
    - 在`@media (prefers-color-scheme: dark)`块中定义所有颜色变量
    - 使用与浅色模式相同的变量名,但值为深色模式适配的颜色
    - 确保主要文本颜色为浅色(接近`#FFFFFF`)
    - 确保背景颜色为深色
    - 验证对比度标准符合WCAG AA级
    - _Requirements: FR-1.1, FR-1.3, NFR-5.1_
  
  - [x] 1.3 为所有CSS变量添加备用值
    - 为每个`var()`调用添加备用颜色值
    - 格式: `color: var(--text-primary, #000000);`
    - 确保在变量未定义时有合理的默认显示
    - _Requirements: FR-1.1_

- [x] 2. Checkpoint - 验证CSS变量系统
  - 在浏览器中加载应用,使用DevTools检查CSS变量是否正确定义
  - 切换浅色/深色模式,验证变量值是否正确切换
  - 确保没有CSS语法错误
  - 如有问题请询问用户

- [x] 3. 重构styles.css中的颜色规则
  - [x] 3.1 替换全局文本颜色规则
    - 删除通配符选择器`*`的全局`!important`规则
    - 将硬编码的`#000000`和`#FFFFFF`替换为CSS变量引用
    - 使用更具体的选择器(如`.main *`)替代通配符
    - _Requirements: FR-1.4, FR-1.7_
  
  - [x] 3.2 重构标题样式(h1-h6)
    - 将所有标题的颜色值替换为`var(--text-primary)`
    - 移除不必要的`!important`
    - 保持浅色/深色模式的结构清晰分离
    - _Requirements: FR-1.2, FR-1.3, FR-1.4, FR-1.5_
  
  - [x] 3.3 重构卡片和容器样式
    - 将`.element-container`的背景和文本颜色改为CSS变量
    - 更新`.info-card`, `.metric-card`, `.progress-container`等卡片样式
    - 确保浅色/深色模式都有正确的背景和文本颜色
    - _Requirements: FR-1.2, FR-1.3, FR-1.5_
  
  - [x] 3.4 重构输入框和表单元素样式
    - 更新`.stTextInput`, `input`, `textarea`, `select`的颜色
    - 将`::placeholder`伪元素颜色改为`var(--text-placeholder)`
    - 确保输入框在两种模式下都清晰可读
    - _Requirements: FR-1.2, FR-1.3, FR-1.6_
  
  - [x] 3.5 重构按钮样式
    - 更新`.stButton > button`, `.stDownloadButton > button`的文本颜色
    - 使用CSS变量替代硬编码颜色
    - 保持渐变背景的同时确保文本可读
    - _Requirements: FR-1.2, FR-1.3, FR-1.6_
  
  - [x] 3.6 重构数据框和表格样式
    - 更新`.dataframe`及其子元素的颜色
    - 确保表头、单元格文本使用CSS变量
    - 在深色模式下使用深色背景和浅色文本
    - _Requirements: FR-1.2, FR-1.3, FR-1.6_
  
  - [x] 3.7 重构Alert和消息框样式
    - 更新`.stAlert`, `.stInfo`, `.stSuccess`, `.stWarning`, `.stError`的文本颜色
    - 确保所有消息框在两种模式下都清晰可读
    - 使用CSS变量管理颜色
    - _Requirements: FR-1.2, FR-1.3, FR-1.6_

- [x] 4. Checkpoint - 验证styles.css重构
  - 在浏览器中测试styles.css的所有样式
  - 验证浅色模式下文本为黑色,背景为浅色
  - 验证深色模式下文本为白色,背景为深色
  - 检查是否有视觉回归
  - 如有问题请询问用户

- [ ] 5. 重构app_beautiful.py中的内联CSS
  - [~] 5.1 提取内联CSS到变量定义部分
    - 识别`load_custom_css()`函数中所有硬编码的颜色值
    - 将浅色模式的颜色值替换为`var(--text-primary)`等CSS变量引用
    - 将深色模式的颜色值替换为CSS变量引用
    - _Requirements: FR-1.1, FR-1.2, FR-1.3_
  
  - [~] 5.2 重构主容器和背景样式
    - 更新`.main`, `.stApp`, `.block-container`的背景和文本颜色
    - 使用CSS变量替代硬编码的渐变背景(或保持渐变但统一文本颜色)
    - 确保浅色/深色模式分离清晰
    - _Requirements: FR-1.5, FR-1.7_
  
  - [~] 5.3 重构侧边栏样式
    - 更新`section[data-testid="stSidebar"]`及其子元素的颜色
    - 在浅色模式下使用深色文本,深色模式下使用浅色文本
    - 移除冗余的`!important`声明
    - _Requirements: FR-1.2, FR-1.3, FR-1.4, FR-1.6_
  
  - [~] 5.4 重构Streamlit特定元素样式
    - 更新`[data-testid="stMetricLabel"]`, `[data-testid="stMetricValue"]`, `[data-testid="stMetricDelta"]`
    - 更新`.stTabs`, `.stButton`, `.dataframe`等元素
    - 确保所有Streamlit元素使用CSS变量
    - _Requirements: FR-1.6_
  
  - [~] 5.5 重构自定义类样式
    - 更新`.main-title`, `.subtitle`, `.info-card`, `.feature-badge`, `.success-box`, `.footer`等自定义类
    - 将所有文本颜色改为CSS变量引用
    - 确保`-webkit-text-fill-color`等特殊属性也使用CSS变量
    - _Requirements: FR-1.2, FR-1.3, FR-1.7_
  
  - [~] 5.6 消除重复的媒体查询规则
    - 识别并合并重复的`@media (prefers-color-scheme: dark)`块
    - 删除完全相同的CSS规则
    - 保持代码结构清晰,避免规则混杂
    - _Requirements: FR-1.5, FR-1.7_

- [~] 6. Checkpoint - 验证app_beautiful.py重构
  - 运行Streamlit应用: `streamlit run app_beautiful.py`
  - 在浏览器中测试所有页面元素
  - 验证浅色/深色模式切换正常
  - 检查所有文本是否清晰可读
  - 如有问题请询问用户

- [ ] 7. 优化CSS选择器特异性
  - [~] 7.1 审计!important使用情况
    - 统计styles.css和app_beautiful.py中`!important`的数量
    - 识别可以通过增加选择器特异性替代的`!important`
    - 记录必须保留的`!important`(用于覆盖Streamlit内置样式)
    - _Requirements: FR-1.4_
  
  - [~] 7.2 替换不必要的!important
    - 将可以替代的`!important`改为更具体的选择器
    - 例如: 将`* { color: #000 !important; }`改为`.main .stMarkdown p { color: var(--text-primary); }`
    - 确保最终`!important`使用率<10%
    - _Requirements: FR-1.4_
  
  - [~] 7.3 为保留的!important添加注释
    - 为每个必须保留的`!important`添加注释说明原因
    - 注释格式: `/* !important needed to override Streamlit default styles */`
    - _Requirements: FR-1.4, NFR-4.1_

- [~] 8. Checkpoint - 验证CSS优先级优化
  - 使用浏览器DevTools检查关键元素的样式优先级
  - 验证`!important`使用率是否<10%
  - 确保样式覆盖正确,没有意外的样式失效
  - 如有问题请询问用户

- [ ] 9. 代码质量和文档完善
  - [~] 9.1 在styles.css中添加结构化注释
    - 为CSS文件添加章节划分注释
    - 章节包括: Variables, Global Styles, Components, Streamlit Elements, Dark Mode
    - 为重要的样式规则添加说明注释
    - _Requirements: NFR-4.1_
  
  - [~] 9.2 在app_beautiful.py中添加CSS结构说明
    - 在`load_custom_css()`函数顶部添加文档字符串
    - 说明CSS变量系统的使用方式
    - 列出所有定义的CSS变量及其用途
    - _Requirements: NFR-4.1, NFR-4.2_
  
  - [~] 9.3 创建颜色方案文档
    - 在项目根目录创建`COLOR_SCHEME.md`文档
    - 记录所有CSS变量的定义和用途
    - 说明浅色/深色模式的颜色对比度
    - 提供颜色使用指南
    - _Requirements: NFR-4.2_

- [ ] 10. 最终测试和验证
  - [ ]* 10.1 运行对比度检查
    - 使用axe DevTools或类似工具检查所有文本/背景组合
    - 验证所有主要文本对比度 >= 4.5:1
    - 验证大文本对比度 >= 3:1
    - 记录检查结果
    - _Requirements: NFR-5.1, NFR-6.1_
  
  - [ ]* 10.2 跨浏览器测试
    - 在Chrome, Firefox, Safari, Edge中加载应用
    - 验证CSS变量和媒体查询在所有浏览器中正常工作
    - 检查颜色显示一致性
    - 记录任何浏览器特定问题
    - _Requirements: NFR-3.1, NFR-6.3_
  
  - [ ]* 10.3 性能基准测试
    - 使用Lighthouse测试重构前后的性能分数
    - 比较CSS文件大小
    - 测量首次内容绘制(FCP)时间
    - 验证性能没有劣化
    - _Requirements: NFR-2.1_
  
  - [ ]* 10.4 视觉回归测试
    - 生成重构前后的UI截图
    - 比对关键页面的视觉差异
    - 确认所有变化都是预期的改进
    - 记录任何意外的视觉变化
    - _Requirements: NFR-6.2_

- [~] 11. 最终Checkpoint - 完整验证
  - 运行Streamlit应用,完整测试所有功能
  - 验证浅色/深色模式在所有页面元素上正常工作
  - 确认没有功能回归或视觉错误
  - 检查所有验收标准是否满足
  - 询问用户是否满意重构结果

## Notes

- 任务标记`*`的为可选测试任务,可根据时间安排跳过
- 每个Checkpoint任务都是验证点,确保增量验证和及时发现问题
- CSS变量系统是核心,所有颜色必须通过变量引用
- 浅色模式使用深色文本(`#000000`系),深色模式使用浅色文本(`#FFFFFF`系)
- 优先通过选择器特异性控制优先级,最小化`!important`使用
- 重构不改变任何功能行为,仅改进样式代码的可维护性
- 所有颜色对比度必须满足WCAG AA级标准(4.5:1)
- 建议在重构前备份原文件: `app_beautiful.py.backup`, `styles.css.backup`

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1.1", "1.2"] },
    { "id": 1, "tasks": ["1.3"] },
    { "id": 2, "tasks": ["3.1", "3.2", "3.3"] },
    { "id": 3, "tasks": ["3.4", "3.5", "3.6", "3.7"] },
    { "id": 4, "tasks": ["5.1", "5.2"] },
    { "id": 5, "tasks": ["5.3", "5.4", "5.5"] },
    { "id": 6, "tasks": ["5.6"] },
    { "id": 7, "tasks": ["7.1"] },
    { "id": 8, "tasks": ["7.2", "7.3"] },
    { "id": 9, "tasks": ["9.1", "9.2", "9.3"] },
    { "id": 10, "tasks": ["10.1", "10.2", "10.3", "10.4"] }
  ]
}
```
