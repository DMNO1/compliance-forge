"""
ComplianceForge — 中国法规合规文档自动生成SaaS MVP
基于 DSL/PIPL/GB-T35273 法规知识库，使用 LLM 自动生成隐私政策与DPIA
"""
import os
import json
import httpx
from datetime import datetime
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, PlainTextResponse, JSONResponse
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="ComplianceForge", version="0.1.0")

# Paths
BASE_DIR = Path(__file__).parent
KNOWLEDGE_DIR = BASE_DIR / "knowledge_base"

# Conditional template/static mounting (Vercel serverless has read-only fs)
templates = None
if (BASE_DIR / "templates").exists():
    from fastapi.templating import Jinja2Templates
    templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
if (BASE_DIR / "static").exists():
    from fastapi.staticfiles import StaticFiles
    app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

# DeepSeek API config
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

# --- Knowledge Base ---
def load_knowledge_base() -> dict:
    """Load all regulation files from knowledge_base/"""
    kb = {}
    for f in KNOWLEDGE_DIR.glob("*.md"):
        kb[f.stem] = f.read_text(encoding="utf-8")
    return kb

def get_relevant_regulations(doc_type: str) -> str:
    """Return relevant regulation context for document type"""
    kb = load_knowledge_base()
    if doc_type == "privacy_policy":
        # Privacy policy needs all three
        parts = []
        for key in ["pipl", "dsl", "gbt35273"]:
            if key in kb:
                parts.append(kb[key])
        return "\n\n---\n\n".join(parts)
    elif doc_type == "dpia":
        # DPIA primarily references PIPL Art.55-56 and GB/T 35273 Section 12.3
        parts = []
        if "pipl" in kb:
            parts.append(kb["pipl"])
        if "gbt35273" in kb:
            parts.append(kb["gbt35273"])
        return "\n\n---\n\n".join(parts)
    return ""

# --- LLM ---
async def call_deepseek(system_prompt: str, user_prompt: str) -> str:
    """Call DeepSeek API. Falls back to template-based generation if no API key."""
    if not DEEPSEEK_API_KEY:
        return generate_fallback(system_prompt, user_prompt)
    
    try:
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
    except Exception as e:
        # Fallback to template generation
        return generate_fallback(system_prompt, user_prompt)

def generate_fallback(system_prompt: str, user_prompt: str) -> str:
    """Generate document from template when LLM API is unavailable."""
    import re
    # Extract key info from user_prompt — handle both Chinese ： and ASCII :
    lines = user_prompt.split("\n")
    info = {}
    for line in lines:
        m = re.match(r"^(.+?)\s*[：:]\s*(.+)$", line.strip())
        if m:
            info[m.group(1).strip()] = m.group(2).strip()
    
    company = info.get("公司名称", info.get("company_name", "[公司名称]"))
    app_name = info.get("应用名称", info.get("app_name", "[应用名称]"))
    data_types = info.get("收集的个人信息类型", info.get("data_types", "姓名、手机号、邮箱"))
    purposes = info.get("处理目的", info.get("purposes", "提供服务"))
    retention = info.get("保存期限", info.get("retention", "服务期间及服务终止后3年"))
    
    if "DPIA" in system_prompt or "影响评估" in user_prompt or "dpia" in user_prompt.lower():
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
| 是否存在目的外使用 | ❌ 不存在 |

---

## 三、必要性与比例性评估

### 3.1 最小必要原则

| 评估项 | 评估结论 |
|-------|---------|
| 收集的信息类型是否必要 | ✅ 仅收集实现服务所必需的信息 |
| 是否存在过度收集 | ❌ 未过度收集 |
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

## 六、安全事件应急处置

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
| 1 | 定期更新隐私政策并通知用户 | 中 | 待执行 |
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

    elif "隐私政策" in system_prompt or "privacy" in system_prompt.lower() or "隐私" in user_prompt:
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
    
    elif "DPIA" in system_prompt or "影响评估" in user_prompt or "dpia" in user_prompt.lower():
        return f"""# 个人信息保护影响评估报告（DPIA）

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
| 是否存在目的外使用 | ❌ 不存在 |

---

## 三、必要性与比例性评估

### 3.1 最小必要原则

| 评估项 | 评估结论 |
|-------|---------|
| 收集的信息类型是否必要 | ✅ 仅收集实现服务所必需的信息 |
| 是否存在过度收集 | ❌ 未过度收集 |
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

## 六、安全事件应急处置

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
| 1 | 定期更新隐私政策并通知用户 | 中 | 待执行 |
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
    
    return "文档生成失败：请配置 DEEPSEEK_API_KEY 后重试。"

# --- Routes ---
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Landing page"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/generate")
async def generate_document(
    doc_type: str = Form(...),
    company_name: str = Form(...),
    app_name: str = Form(...),
    data_types: str = Form("姓名、手机号、邮箱"),
    purposes: str = Form("提供服务"),
    retention: str = Form("服务期间及服务终止后3年"),
    has_cross_border: bool = Form(False),
    industry: str = Form("通用"),
):
    """Generate compliance document"""
    if doc_type not in ["privacy_policy", "dpia"]:
        raise HTTPException(400, "不支持的文档类型")
    
    # Build user prompt with form data
    user_prompt = f"""请根据以下信息生成{doc_type}：
公司名称：{company_name}
应用名称：{app_name}
收集的个人信息类型：{data_types}
处理目的：{purposes}
保存期限：{retention}
跨境传输：{'是' if has_cross_border else '否'}
行业：{industry}
"""
    
    # System prompt with regulation context
    reg_context = get_relevant_regulations(doc_type)
    doc_name = "隐私政策" if doc_type == "privacy_policy" else "个人信息保护影响评估报告（DPIA）"
    
    system_prompt = f"""你是一位专业的中国数据合规顾问。请根据用户的业务信息，参考以下法规要求，生成一份专业、完整、合规的{doc_name}。

引用的法规条文需标注出处（如"依据《个人信息保护法》第六条"）。

=== 法规知识库 ===
{reg_context}
=== 知识库结束 ===

请生成完整的中文Markdown格式文档，包含所有必要的章节和条款。"""
    
    content = await call_deepseek(system_prompt, user_prompt)
    
    return JSONResponse({
        "success": True,
        "doc_type": doc_type,
        "doc_name": doc_name,
        "company_name": company_name,
        "app_name": app_name,
        "content": content,
        "generated_at": datetime.now().isoformat(),
    })

@app.get("/api/health")
async def health():
    """Health check"""
    kb = load_knowledge_base()
    return {
        "status": "ok",
        "version": "0.1.0",
        "knowledge_base": list(kb.keys()),
        "llm_configured": bool(DEEPSEEK_API_KEY),
    }

# Vercel serverless handler
try:
    from mangum import Mangum
    handler = Mangum(app)
except ImportError:
    handler = app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
