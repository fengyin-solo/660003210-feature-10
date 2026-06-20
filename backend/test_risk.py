import sys
sys.path.insert(0, '.')
from app.services.admet import compute_admet

test_cases = [
    ("阿司匹林", 180.16, 1.19, "C9H8O4"),
    ("维生素C", 176.12, -2.41, "C6H8O6"),
    ("辛伐他汀", 418.57, 4.68, "C25H38O5"),
    ("布洛芬", 206.28, 3.97, "C13H18O2"),
    ("吉非罗齐", 250.33, 4.77, "C15H22O3"),
]

print("=== 综合风险评级 最小校验 ===")
print()

for name, mw, logp, formula in test_cases:
    result = compute_admet(mw, logp, formula)
    level_marks = {"A": "[A]", "B": "[B]", "C": "[C]", "D": "[D]"}
    mark = level_marks.get(result["riskLevel"], "?")
    print(f"{name}:")
    print(f"  风险等级: {mark} {result['riskLevel']}级 ({result['riskScore']}/14分)")
    print(f"  重点提示: {len(result['riskAlerts'])}条")
    for alert in result["riskAlerts"][:3]:
        icon = "[!]" if alert["type"] == "danger" else "[~]" if alert["type"] == "warning" else "[i]"
        print(f"    {icon} {alert['title']}: {alert['detail'][:40]}...")
    print()

print("=== 数据结构完整性验证 ===")
required_fields = [
    "logP", "logS", "toxicity", "proteinBinding", "metabolicStability",
    "bioavailability", "ruleOfFive", "violations", "riskLevel", "riskScore", "riskAlerts"
]
sample = compute_admet(180.16, 1.19, "C9H8O4")
all_present = all(f in sample for f in required_fields)
print(f"所有必需字段存在: {'PASS' if all_present else 'FAIL'}")
if not all_present:
    missing = [f for f in required_fields if f not in sample]
    print(f"缺失字段: {missing}")

print(f"riskAlerts 是列表: {'PASS' if isinstance(sample['riskAlerts'], list) else 'FAIL'}")
print(f"riskLevel 在 A/B/C/D 中: {'PASS' if sample['riskLevel'] in ['A','B','C','D'] else 'FAIL'}")
print(f"riskScore 在 0-14 范围: {'PASS' if 0 <= sample['riskScore'] <= 14 else 'FAIL'}")
print()

high_risk = [name for name, mw, logp, formula in test_cases 
             if compute_admet(mw, logp, formula)["riskLevel"] in ["C", "D"]]
print(f"高风险分子(C/D级): {high_risk if high_risk else '无'}")
print()
print("校验完成!")
