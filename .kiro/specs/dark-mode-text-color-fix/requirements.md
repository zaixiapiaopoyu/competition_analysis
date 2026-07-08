# 需求文档: 深色模式文字颜色修复

## 引言

本文档定义了Streamlit多Agent竞品分析系统深色模式文字颜色修复功能的功能需求。该功能旨在解决当用户浏览器或操作系统启用深色模式时,应用中部分文本元素仍显示为黑色导致无法清晰阅读的问题。修复范围覆盖`app_beautiful.py`、`app.py`和`styles.css`三个文件中的所有文本元素。

## 术语表

- **System**: Streamlit多Agent竞品分析系统
- **Dark_Mode**: 浏览器或操作系统的深色模式设置,通过CSS媒体查询`prefers-color-scheme: dark`检测
- **Text_Element**: 任何显示文本内容的DOM元素,包括标题、段落、标签、按钮文字、表格文字等
- **CSS_Rule**: 定义在深色模式媒体查询内的CSS样式规则
- **Contrast_Ratio**: 文本颜色与背景颜色的对比度,按照WCAG标准计算
- **Light_Mode**: 浏览器或操作系统的浅色模式设置(默认模式)
- **Text_Color**: 文本元素的CSS `color`属性值
- **Selector**: CSS选择器,用于匹配目标DOM元素

## 需求

### 需求 1: 深色模式文本颜色一致性

**用户故事**: 作为应用用户,我希望在启用深色模式时所有文本都显示为白色或浅色,以便在深色背景上清晰阅读内容。

#### 验收标准

1. WHEN Dark_Mode is activated THEN THE System SHALL set all Text_Element color properties to #FFFFFF or light color values (>= #DDDDDD)
2. WHEN a user views any page in Dark_Mode THEN THE System SHALL render headings (h1-h6) with color #FFFFFF
3. WHEN a user views any page in Dark_Mode THEN THE System SHALL render paragraphs, spans, and labels with color #FFFFFF
4. WHEN a user views any page in Dark_Mode THEN THE System SHALL render Streamlit components (.stMarkdown, .stText, .stMetric) with color #FFFFFF
5. WHEN a user views data tables in Dark_Mode THEN THE System SHALL render all table text with color #FFFFFF
6. WHEN a user interacts with buttons in Dark_Mode THEN THE System SHALL render button text with color #FFFFFF
7. WHEN a user views alerts or info boxes in Dark_Mode THEN THE System SHALL render alert text with color #FFFFFF

### 需求 2: CSS优先级保证

**用户故事**: 作为开发者,我希望深色模式的文本颜色规则不被其他样式覆盖,以确保修复的稳定性和可靠性。

#### 验收标准

1. WHEN THE System defines a Dark_Mode text color CSS_Rule THEN it SHALL include the !important declaration
2. FOR ALL Text_Element selectors in Dark_Mode THEN THE CSS_Rule priority SHALL be set to !important
3. WHEN conflicting CSS rules exist THEN THE Dark_Mode text color rules SHALL override other rules due to !important priority
4. WHEN new CSS rules are added THEN THE System SHALL maintain !important priority for all Dark_Mode text color rules

### 需求 3: 对比度合规性

**用户故事**: 作为视力障碍用户,我希望文本与背景的对比度足够高,以便轻松阅读内容并符合无障碍标准。

#### 验收标准

1. WHEN Dark_Mode is activated THEN THE System SHALL ensure all text-to-background Contrast_Ratio values are >= 4.5:1
2. WHEN measuring any Text_Element against its background container in Dark_Mode THEN THE Contrast_Ratio SHALL meet WCAG AA standard (>= 4.5:1)
3. WHEN white text (#FFFFFF) is used in Dark_Mode THEN THE System SHALL provide dark background colors that achieve >= 4.5:1 contrast
4. IF a color combination results in Contrast_Ratio < 4.5:1 THEN THE System SHALL adjust the background color to achieve compliant contrast

### 需求 4: 选择器全覆盖

**用户故事**: 作为开发者,我希望所有文本元素类型都有对应的深色模式CSS规则,确保没有遗漏的元素。

#### 验收标准

1. THE System SHALL define Dark_Mode CSS rules for generic text elements (*, p, span, div, li, label)
2. THE System SHALL define Dark_Mode CSS rules for heading elements (h1, h2, h3, h4, h5, h6)
3. THE System SHALL define Dark_Mode CSS rules for Streamlit components (.stMarkdown, .stText, .stMetric, .stButton)
4. THE System SHALL define Dark_Mode CSS rules for input elements (input, textarea, select)
5. THE System SHALL define Dark_Mode CSS rules for data tables (.dataframe, th, td)
6. THE System SHALL define Dark_Mode CSS rules for alert components (.stAlert, .stInfo, .stSuccess, .stWarning, .stError)
7. THE System SHALL define Dark_Mode CSS rules for tab components (.stTabs)
8. THE System SHALL define Dark_Mode CSS rules for custom classes (.main-title, .subtitle, .info-card, .feature-badge)
9. WHEN a new Text_Element type is introduced THEN THE System SHALL include it in Dark_Mode CSS rules

### 需求 5: 媒体查询响应性

**用户故事**: 作为应用用户,我希望当我切换操作系统的深色模式设置时,应用能立即响应并更新样式。

#### 验收标准

1. THE System SHALL use CSS media query @media (prefers-color-scheme: dark) to detect Dark_Mode
2. WHEN a user toggles Dark_Mode in browser or OS settings THEN THE System SHALL apply Dark_Mode styles immediately without page refresh
3. WHEN Dark_Mode is deactivated THEN THE System SHALL revert to Light_Mode styles immediately
4. THE System SHALL rely on native browser media query support for Dark_Mode detection

### 需求 6: 浅色模式不受影响

**用户故事**: 作为应用用户,我希望在浅色模式下应用样式保持不变,深色模式修复不应影响默认的浅色模式体验。

#### 验收标准

1. WHEN Light_Mode is active THEN THE System SHALL render text elements with original light mode colors (typically black or dark colors)
2. WHEN Dark_Mode CSS rules are defined THEN they SHALL be scoped within @media (prefers-color-scheme: dark) and not affect Light_Mode
3. WHEN a user views the application in Light_Mode THEN THE text colors SHALL remain as defined in non-media-query CSS rules
4. THE System SHALL maintain separate color definitions for Light_Mode and Dark_Mode without interference

### 需求 7: 多文件一致性

**用户故事**: 作为开发者,我希望所有CSS文件中的深色模式实现保持一致,便于维护和调试。

#### 验收标准

1. WHEN Dark_Mode rules are defined in app_beautiful.py THEN they SHALL use the same text color values (#FFFFFF) as app.py and styles.css
2. WHEN Dark_Mode rules are defined across multiple files THEN they SHALL all use !important priority consistently
3. WHEN background colors are defined in Dark_Mode THEN they SHALL use consistent dark color schemes across all files
4. THE System SHALL maintain consistent Selector naming and structure across app_beautiful.py, app.py, and styles.css
5. WHEN updating Dark_Mode rules THEN THE System SHALL synchronize changes across all three CSS-containing files

### 需求 8: CSS解析和应用

**用户故事**: 作为开发者,我希望深色模式CSS规则能够正确解析并应用到目标元素上。

#### 验收标准

1. WHEN THE System loads CSS files THEN it SHALL parse @media (prefers-color-scheme: dark) blocks correctly
2. WHEN Selectors are defined in Dark_Mode CSS_Rule THEN they SHALL match the intended Text_Element types in the DOM
3. WHEN CSS_Rule specificity conflicts occur THEN THE !important declaration SHALL resolve conflicts in favor of Dark_Mode rules
4. THE System SHALL apply Dark_Mode styles to dynamically generated Streamlit components

### 需求 9: 背景颜色适配

**用户故事**: 作为应用用户,我希望在深色模式下背景色也调整为深色调,与白色文字形成良好的视觉对比。

#### 验收标准

1. WHEN Dark_Mode is activated THEN THE System SHALL apply dark background colors to the main container
2. WHEN Dark_Mode is activated THEN THE System SHALL use dark gradients or solid colors for element containers
3. THE System SHALL define Dark_Mode background colors that harmonize with white text and maintain visual hierarchy
4. WHEN input elements are rendered in Dark_Mode THEN THE System SHALL apply dark backgrounds (e.g., rgba(50, 50, 70, 0.95)) for readability

### 需求 10: 特殊组件处理

**用户故事**: 作为应用用户,我希望所有Streamlit特有组件(如指标、选项卡、进度条)在深色模式下也能正确显示。

#### 验收标准

1. WHEN Dark_Mode is activated THEN THE System SHALL render metric labels ([data-testid="stMetricLabel"]) with color #FFFFFF
2. WHEN Dark_Mode is activated THEN THE System SHALL render metric values ([data-testid="stMetricValue"]) with color #FFFFFF
3. WHEN Dark_Mode is activated THEN THE System SHALL render active tabs with color #FFFFFF
4. WHEN Dark_Mode is activated THEN THE System SHALL render progress container text with color #FFFFFF
5. WHEN Dark_Mode is activated THEN THE System SHALL render footer text with color #FFFFFF
