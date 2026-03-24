cd "C:\Users\91780\.openclaw\workspace\business\compliance-forge"
git init
git add -A
git commit -m "Initial MVP: ComplianceForge - 中国法规合规文档自动生成SaaS"
gh repo create compliance-forge --public --source=. --push
