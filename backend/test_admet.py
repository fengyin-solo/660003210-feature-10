import sys
sys.path.insert(0, ".")
from app.services.admet import compute_admet

result = compute_admet(180.16, 1.19, "C9H8O4")
print("阿司匹林测试:")
print(f"  风险等级: {result[\"riskLevel\"]}")
print(f"  风险评分: {result[\"riskScore\"]}")
print(f"  提示数量: {len(result[\"riskAlerts\"])}")
print("测试通过!")

