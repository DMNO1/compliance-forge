# ComplianceForge — 中国法规合规文档自动生成SaaS

> 基于 DSL/PIPL/GB-T 35273 法规知识库，使用 LLM 自动生成合规文档

## 产品定位

帮中小企业一键生成**隐私政策**和**DPIA（个人信息保护影响评估报告）**的AI工具。

**目标用户**：需要上线App/网站但没有法务团队的中小企业、独立开发者、创业公司。

**核心价值**：填表 → 生成 → 下载，3分钟搞定原本需要请律师花¥5000-20000才能完成的合规文档。

## 功能

| 功能 | 说明 |
|------|------|
| 📋 隐私政策生成 | 符合PIPL要求的完整隐私政策，自动引用法规条文 |
| 🔍 DPIA评估报告 | 个人信息保护影响评估报告，含风险矩阵 |
| ⚖️ 法规知识库 | DSL/PIPL/GB-T 35273 核心条文，自动关联引用 |
| 🤖 LLM驱动 | DeepSeek API生成专业文档（可选，无API时使用内置模板） |
| ⬇️ 一键下载 | Markdown格式导出，方便转换为PDF/Word |

## 快速开始

### 1. 安装依赖

```bash
cd business/compliance-forge
pip install -r requirements.txt
```

### 2. 配置环境变量（可选）

```bash
copy .env.example .env
# 编辑 .env，填入 DEEPSEEK_API_KEY（可选，不填使用内置模板）
```

### 3. 启动服务

```bash
py main.py
# 访问 http://localhost:8000
```

## 技术栈

- **后端**: Python FastAPI
- **前端**: HTML + Tailwind CSS
- **LLM**: DeepSeek API（可选）
- **法规知识库**: Markdown文件（DSL、PIPL、GB/T 35273）

## 商业模式

| 版本 | 价格 | 功能 |
|------|------|------|
| 基础版 | ¥299/月 | 隐私政策生成（2次/月） |
| 专业版 | ¥999/月 | 隐私政策 + DPIA（不限次） |
| 企业版 | ¥3,999/月 | 定制模板 + 法规更新推送 + 专属顾问 |

## 成本结构

| 项目 | 月费用 | 备注 |
|------|--------|------|
| LLM API（Deepseek） | ¥100-300 | 国产模型，极低成本 |
| VPS服务器 | ¥50-100 | 阿里云/腾讯云轻量 |
| 域名 | ¥10 | .cn年费分摊 |
| **月总计** | **¥160-410** | 远低于¥1,000阈值 |

## 目录结构

```
compliance-forge/
├── knowledge_base/           # 法规知识库
│   ├── dsl.md               # 网络安全法核心条文
│   ├── pipl.md              # 个人信息保护法核心条文
│   └── gbt35273.md          # GB/T 35273-2020核心条文
├── static/                   # 静态资源
├── templates/
│   └── index.html           # 前端页面
├── main.py                   # FastAPI应用
├── requirements.txt          # Python依赖
├── .env.example              # 环境变量模板
└── README.md                 # 本文件
```

## API接口

### POST /api/generate

生成合规文档。

**参数：**
- `doc_type` (必填): `privacy_policy` 或 `dpia`
- `company_name` (必填): 公司名称
- `app_name` (必填): 应用/产品名称
- `data_types`: 收集的个人信息类型
- `purposes`: 处理目的
- `retention`: 保存期限
- `has_cross_border`: 是否跨境传输
- `industry`: 所属行业

**返回：**
```json
{
  "success": true,
  "doc_type": "privacy_policy",
  "doc_name": "隐私政策",
  "content": "生成的Markdown文档内容...",
  "generated_at": "2026-03-24T15:00:00"
}
```

### GET /api/health

健康检查。

## MVP验收标准

- [x] 法规知识库包含DSL/PIPL/GB/T 35273核心条文
- [x] 2种文档模板可生成（隐私政策 + DPIA）
- [x] Web界面运行：填写表单 → 生成文档 → 下载
- [ ] 部署上线可通过URL访问

## 后续优化

- [ ] 增加《数据安全法》条文
- [ ] 增加《儿童个人信息网络保护规定》
- [ ] PDF/Word导出
- [ ] 用户注册与文档历史
- [ ] 支付系统集成
- [ ] 法规更新自动推送

## 许可证

MIT License

---

**状态**: 💻 代码完成，待部署
**创建时间**: 2026-03-24
**推荐来源**: pending_plan.md（连续7轮Analyst审查推荐）
