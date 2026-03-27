"""
ComplianceForge - Vercel Serverless Entry Point (v3 - Pure Flask)
Self-contained Flask app. No FastAPI/Jinja2/yaml/dotenv deps.
Definitive fix for Vercel Python 500 errors.
"""
import os
import json
import re
from datetime import datetime
from flask import Flask, jsonify, request, render_template_string

app = Flask(__name__)

# DeepSeek API config
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

# --- Document Generation (Fallback Templates) ---
def generate_fallback(doc_type: str, company: str, app_name: str,
                      data_types: str, purposes: str, retention: str) -> str:
    """Generate document from template when LLM API is unavailable."""
    if doc_type == "dpia":
        return f"""# {app_name} 个人信息保护影响评估报告（DPIA）
**评估对象：** {app_name}
**评估机构：** {company}
**评估日期：** {datetime.now().strftime("%Y年%m月%d日")}
**评估编号：** DPIA-{datetime.now().strftime("%Y%m%d")}-001

---

## 一、评估概述
### 1.1 评估背景

依据《个人信息保护法》第五十五条，{company}在处理个人信息前，对{app_name}的个人信息处理活动进行个人信息保护影响评估，以识别和降低个人信息安全风险。

### 1.2 评估范围

- **产品/服务名称：** {app_name}
- **处理的个人信息类型：** {data_types}
- **处理目的：** {purposes}
- **保存期限：** {retention}
- **涉及的处理活动：** 收集、存储、使用、（如有）共享

### 1.3 评估依据

- 《中华人民共和国个人信息保护法》
- 《中华人民共和国网络安全法》
- GB/T 35273-2020《信息安全技术 个人信息安全规范》
- 《个人信息安全影响评估指南》

---

## 二、合法性基础评估

### 2.1 同意的合法性
| 评估项 | 评估结论 |
|-------|---------|
| 是否取得个人同意 | ✅ 已在服务协议和隐私政策中明确告知并取得同意 |
| 同意是否自愿 | ✅ 未以拒绝服务为要挟强迫同意 |
| 同意是否知情 | ✅ 以清晰易懂的语言告知处理目的、方式、范围 |
| 同意是否明确 | ✅ 通过勾选/点击确认方式获取明确同意 |
| 是否提供撤回机制 | ✅ 提供便捷的撤回同意方式 |

### 2.2 目的限制评估

| 评估项 | 评估结论 |
|-------|---------|
| 处理目的是否明确 | ✅ 目的明确：{purposes} |
| 是否与收集时声明目的一致 | ✅ 一致 |
| 是否存在目的外使用 | ✅ 不存在 |

---

## 三、必要性与比例性评估
### 3.1 最小必要原则
| 评估项 | 评估结论 |
|-------|---------|
| 收集的信息类型是否必要 | ✅ 仅收集实现服务所必需的信息 |
| 是否存在过度收集 | ✅ 未过度收集 |
| 保存期限是否合理 | ✅ 保存期限为{retention}，符合最小化原则 |

### 3.2 对个人权益的影响

| 影响维度 | 影响程度 | 说明 |
|---------|---------|------|
| 隐私侵害风险 | 🟢 低 | 仅收集必要的业务信息 |
| 财产安全风险 | 🟢 低 | 不涉及敏感金融信息 |
| 人格尊严风险 | 🟢 低 | 不涉及生物识别、宗教信仰等敏感信息 |
| 歧视性对待风险 | 🟢 低 | 不进行自动化决策/用户画像 |

---

## 四、安全风险评估
### 4.1 数据生命周期风险

| 阶段 | 风险等级 | 主要风险 | 已采取的保护措施 |
|------|---------|---------|----------------|
| 收集 | 🟢 低 | 未授权收集 | 用户同意机制、最小化收集 |
| 存储 | 🟡 中 | 数据泄露 | 加密存储、访问控制 |
| 使用 | 🟢 低 | 越权访问 | 权限管理、操作审计 |
| 共享 | 🟢 低 | 未经授权共享 | 合同约束、安全评估 |
| 删除 | 🟢 低 | 残留数据 | 定期清理机制 |

### 4.2 安全技术措施
依据《网络安全法》第二十一条和《个人信息保护法》第五十一条，已采取以下安全措施：

- [x] 数据传输加密（TLS 1.2+）
- [x] 数据存储加密
- [x] 访问控制与权限管理
- [x] 操作日志记录与审计
- [x] 安全事件应急预案
- [x] 定期安全培训

---

## 五、跨境传输评估（如适用）
**本次评估不涉及个人信息跨境传输。**

若未来需要向境外提供个人信息，将依据《个人信息保护法》第三十八条至第四十条重新评估，包括但不限于：
- 通过国家网信部门组织的安全评估；
- 经专业机构进行个人信息保护认证；
- 按照国家网信部门制定的标准合同与境外接收方订立合同。

---

## 六、安全事件应急处理
### 6.1 应急预案
| 项目 | 内容 |
|------|------|
| 事件分级 | 按影响范围分为一般事件、较大事件、重大事件 |
| 响应时间 | 发现后30分钟内启动应急响应 |
| 通知义务 | 72小时内通知受影响的个人信息主体和监管部门 |
| 补救措施 | 立即止损、排查原因、修复漏洞、恢复服务 |

---

## 七、评估结论
### 7.1 总体风险等级

**🟢 低风险**

{app_name}的个人信息处理活动总体风险可控，处理目的明确合法，收集信息符合最小必要原则，已采取合理的技术和管理安全保护措施。

### 7.2 风险缓解建议

| 序号 | 建议 | 优先级 | 状态 |
|------|------|-------|------|
| 1 | 定期更新隐私政策并通知用户 | 高 | 待执行 |
| 2 | 建立个人信息主体权利响应流程 | 高 | 待执行 |
| 3 | 每年进行一次安全审计 | 中 | 待执行 |
| 4 | 建立供应商安全评估机制 | 中 | 待执行 |

### 7.3 评估人签字
| 角色 | 姓名 | 日期 |
|------|------|------|
| 个人信息保护负责人 | [姓名] | {datetime.now().strftime("%Y-%m-%d")} |
| 技术安全负责人 | [姓名] | {datetime.now().strftime("%Y-%m-%d")} |
| 法务负责人 | [姓名] | {datetime.now().strftime("%Y-%m-%d")} |

---

*本评估报告依据《个人信息保护法》第五十五条、第五十六条，GB/T 35273-2020第12.3节编制。评估报告应保存至少三年。*
"""
    else:  # privacy_policy
        return f"""# {app_name} 隐私政策

**生效日期：{datetime.now().strftime("%Y年%m月%d日")}**
**最后更新：{datetime.now().strftime("%Y年%m月%d日")}**

{company}（以下简称"我们"）深知个人信息对您的重要性，我们将按法律法规要求，采取相应安全保护措施来保护您的个人信息。本隐私政策适用于{app_name}的全部产品及服务。

---

## 一、我们如何收集和使用您的个人信息

### 1.1 收集的个人信息类型
为向您提供{app_name}服务，我们在以下业务功能中收集和使用您的个人信息：

| 业务功能 | 收集的信息类型 | 处理目的 |
|---------|-------------|---------|
| 核心服务 | {data_types} | {purposes} |
| 账号管理 | 手机号码、邮箱 | 账号注册与登录 |
| 安全保障 | 设备信息、日志信息 | 保障服务安全 |

**特别提示：** 我们仅收集实现{app_name}核心功能所必要的个人信息，遵循最小必要原则。

### 1.2 处理目的

我们处理您的个人信息基于以下目的：
- 为您提供{app_name}的核心服务；
- 处理{purposes}相关业务；
- 保障您的账户安全和交易安全；
- 遵守法律法规规定的义务。

### 1.3 同意与授权
依据《个人信息保护法》第十三条及第十四条，我们在收集您的个人信息前，将以显著方式告知您收集的目的、方式和范围，并取得您的同意。您有权随时撤回您的同意。

---

## 二、我们如何存储和保护您的个人信息

### 2.1 存储地点

我们将在中华人民共和国境内存储您在使用{app_name}服务时收集和产生的个人信息。

### 2.2 存储期限

我们仅在实现处理目的所必要的最短期间内保留您的个人信息。您的个人信息保存期限为{retention}，超过保存期限后，我们将对您的个人信息进行删除或匿名化处理。

### 2.3 安全措施

依据《网络安全法》第二十一条及《个人信息保护法》第五十一条，我们采取以下措施保护您的个人信息：
- **技术措施**：采用加密传输（TLS）、数据加密存储、访问控制等技术手段；
- **管理措施**：制定内部安全管理制度，明确信息安全负责人；
- **人员管理**：对接触个人信息的人员进行安全培训和权限控制；
- **应急措施**：制定信息安全事件应急预案，定期演练。

---

## 三、我们如何使用Cookie和同类技术
我们使用Cookie和类似技术来保障{app_name}的正常运行、优化用户体验和提供个性化服务。您可以通过浏览器设置管理Cookie偏好。

---

## 四、我们如何共享、转让、公开披露您的个人信息

### 4.1 共享

我们不会与任何公司、组织和个人共享您的个人信息，但以下情况除外：
- 获得您的明确同意；
- 根据法律法规或政府主管部门的强制性要求；
- 与授权合作伙伴共享必要的信息以提供服务（如支付服务商）。

### 4.2 转让

我们不会将您的个人信息转让给任何公司、组织和个人，但以下情况除外：
- 获得您的明确同意；
- 涉及合并、分立、解散、被宣告破产等情形。

### 4.3 公开披露

我们不会公开披露您的个人信息，除非获得您的单独同意。

---

## 五、您的权利
依据《个人信息保护法》第四十四条至第四十八条，您享有以下权利：

### 5.1 知情权与决定权
您有权了解我们处理您个人信息的规则、目的、方式和范围，并有权决定是否同意我们的处理行为。

### 5.2 查阅和复制权
您有权向我们查阅、复制您的个人信息。

### 5.3 更正和补充权
您发现个人信息不准确或不完整时，有权请求我们更正、补充。

### 5.4 删除权
符合法定情形时，您有权要求我们删除您的个人信息。

### 5.5 撤回同意权
您有权随时撤回对我们处理您个人信息的同意，撤回同意不影响撤回前已进行的处理活动的效力。

### 5.6 注销账户权
您有权注销{app_name}账户。我们将在不超过15个工作日内完成注销处理。

### 5.7 获取本政策副本权
您有权获取本隐私政策的副本。

**行使权利的方式：** 您可以通过以下方式联系我们行使上述权利：
- 邮箱：[privacy@example.com]
- 电话：[400-XXX-XXXX]

我们将在收到您的请求后15个工作日内予以答复。

---

## 六、未成年人个人信息保护
我们非常重视对未成年人个人信息的保护。若您是未满14周岁的未成年人，我们将在取得您的监护人同意后处理您的个人信息。

---

## 七、本隐私政策的更新
我们可能会适时修订本隐私政策。当隐私政策发生重大变更时，我们将在{app_name}内显著位置发布通知。

---

## 八、如何联系我们
如您对本隐私政策有任何疑问、意见或建议，或需要行使您的个人信息权利，请通过以下方式联系我们：
- **公司名称：** {company}
- **联系邮箱：** [privacy@example.com]
- **联系电话：** [400-XXX-XXXX]
- **联系地址：** [公司地址]

一般情况下，我们将在15个工作日内回复。

如果您对我们的回复不满意，特别是认为我们的个人信息处理行为损害了您的合法权益，您可以向履行个人信息保护职责的部门投诉或举报，也可以向有管辖权的人民法院提起诉讼。

---

*本隐私政策依据《中华人民共和国个人信息保护法》《中华人民共和国网络安全法》《GB/T 35273-2020 信息安全技术 个人信息安全规范》制定。*
"""


async def call_deepseek(system_prompt: str, user_prompt: str) -> str:
    """Call DeepSeek API. Returns None on failure."""
    if not DEEPSEEK_API_KEY:
        return None
    try:
        import httpx
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                DEEPSEEK_API_URL,
                headers={
                    "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "deepseek-chat",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    "temperature": 0.3,
                    "max_tokens": 4096,
                },
            )
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]
    except Exception:
        return None


# --- HTML Templates ---
INDEX_HTML = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>合规Forge - 中国法规合规文档自动生成</title>
<style>
body{font-family:system-ui,-apple-system,sans-serif;max-width:800px;margin:0 auto;padding:20px;background:#f5f5f5}
h1{color:#333;text-align:center}h2{color:#555}
.card{background:#fff;border-radius:12px;padding:24px;box-shadow:0 2px 8px rgba(0,0,0,.1);margin:16px 0}
label{display:block;margin:8px 0 4px;font-weight:600;color:#555}
input,select,textarea{width:100%;padding:10px;border:1px solid #ddd;border-radius:8px;box-sizing:border-box;font-size:14px}
textarea{height:80px;resize:vertical}
button{margin-top:16px;padding:12px 24px;background:#4caf50;color:#fff;border:none;border-radius:8px;cursor:pointer;font-size:16px;width:100%}
button:hover{background:#43a047}
.result{background:#f9f9f9;border:1px solid #ddd;border-radius:8px;padding:20px;margin-top:16px;white-space:pre-wrap;line-height:1.8;font-size:14px;max-height:600px;overflow-y:auto}
.badge{display:inline-block;padding:4px 12px;border-radius:20px;font-size:12px;font-weight:600}
.badge-ok{background:#e8f5e9;color:#2e7d32}
.loading{text-align:center;color:#999;padding:40px}
</style>
</head>
<body>
<h1>🛡️ 合规Forge</h1>
<p style="text-align:center;color:#888">中国法规合规文档自动生成SaaS · 基于《个人信息保护法》《网络安全法》GB/T 35273</p>

<div class="card">
<h2>📄 生成合规文档</h2>
<form id="form" onsubmit="return generate(event)">
<label>文档类型 *</label>
<select name="doc_type" required>
<option value="privacy_policy">隐私政策</option>
<option value="dpia">个人信息保护影响评估报告（DPIA）</option>
</select>

<label>公司名称 *</label>
<input name="company_name" placeholder="例：北京某某科技有限公司" required>

<label>应用/产品名称 *</label>
<input name="app_name" placeholder="例：某某App" required>

<label>收集的个人信息类型</label>
<input name="data_types" value="姓名、手机号、邮箱" placeholder="例：姓名、手机号、邮箱、地址">

<label>处理目的</label>
<input name="purposes" value="提供服务" placeholder="例：用户注册、订单处理、客户服务">

<label>保存期限</label>
<input name="retention" value="服务期间及服务终止后3年">

<label>行业</label>
<select name="industry">
<option value="通用">通用</option>
<option value="电商">电商</option>
<option value="金融">金融</option>
<option value="医疗">医疗</option>
<option value="教育">教育</option>
<option value="SaaS">SaaS/互联网</option>
</select>

<button type="submit">🚀 生成合规文档</button>
</form>
<div id="result"></div>
</div>

<div class="card">
<h2>ℹ️ 支持的法规</h2>
<ul>
<li>《中华人民共和国个人信息保护法》（PIPL）</li>
<li>《中华人民共和国网络安全法》（CSL）</li>
<li>《中华人民共和国数据安全法》（DSL）</li>
<li>GB/T 35273-2020《信息安全技术 个人信息安全规范》</li>
</ul>
<p><span class="badge badge-ok">AI + 模板双引擎</span> 有DeepSeek API key时使用AI生成，否则使用内置法规模板</p>
</div>

<script>
async function generate(e){
e.preventDefault();
const fd=new FormData(document.getElementById('form'));
document.getElementById('result').innerHTML='<div class="loading">⏳ 正在生成合规文档，请稍候...</div>';
try{
const r=await fetch('/api/generate',{method:'POST',body:fd});
const d=await r.json();
if(d.success){
document.getElementById('result').innerHTML='<h3>✅ '+d.doc_name+' 生成成功</h3><div class="result">'+d.content.replace(/\\n/g,'<br>')+'</div>';
}else{
document.getElementById('result').innerHTML='<p style="color:red">❌ '+(d.error||'生成失败')+'</p>';
}
}catch(err){
document.getElementById('result').innerHTML='<p style="color:red">❌ 请求失败: '+err.message+'</p>';
}
return false;
}
</script>
</body>
</html>"""


# --- Routes ---
@app.get("/")
def index():
    return INDEX_HTML


@app.post("/api/generate")
async def generate_document():
    """Generate compliance document."""
    # Support both form data and JSON
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form.to_dict()

    doc_type = data.get("doc_type", "")
    company_name = data.get("company_name", "")
    app_name = data.get("app_name", "")
    data_types = data.get("data_types", "姓名、手机号、邮箱")
    purposes = data.get("purposes", "提供服务")
    retention = data.get("retention", "服务期间及服务终止后3年")
    industry = data.get("industry", "通用")

    if doc_type not in ["privacy_policy", "dpia"]:
        return jsonify({"success": False, "error": "不支持的文档类型"}), 400

    if not company_name or not app_name:
        return jsonify({"success": False, "error": "缺少必填字段：公司名称、应用名称"}), 400

    doc_name = "隐私政策" if doc_type == "privacy_policy" else "个人信息保护影响评估报告（DPIA）"

    # Try LLM first, fall back to template
    user_prompt = f"""请根据以下信息生成{doc_name}：
公司名称：{company_name}
应用名称：{app_name}
收集的个人信息类型：{data_types}
处理目的：{purposes}
保存期限：{retention}
行业：{industry}
"""

    system_prompt = f"""你是一位专业的中国数据合规顾问。请根据用户的业务信息，参考《个人信息保护法》《网络安全法》《GB/T 35273-2020》，生成一份专业、完整、合规的{doc_name}。引用的法规条文需标注出处。请生成完整的中文Markdown格式文档。"""

    content = await call_deepseek(system_prompt, user_prompt)
    if not content:
        content = generate_fallback(doc_type, company_name, app_name, data_types, purposes, retention)

    return jsonify({
        "success": True,
        "doc_type": doc_type,
        "doc_name": doc_name,
        "company_name": company_name,
        "app_name": app_name,
        "content": content,
        "generated_at": datetime.now().isoformat(),
    })


@app.get("/api/health")
def health():
    return jsonify({
        "status": "ok",
        "version": "0.1.0-v3flask",
        "llm_configured": bool(DEEPSEEK_API_KEY),
    })


# Vercel entry point - the app object is WSGI compatible
handler = app
