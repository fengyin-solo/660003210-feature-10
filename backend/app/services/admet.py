import numpy as np

ATOM_COLORS = {"C": "#6b7280", "N": "#3b82f6", "O": "#ef4444", "S": "#eab308", "P": "#f97316", "H": "#e5e7eb", "F": "#22c55e", "Cl": "#16a34a"}
ATOM_RADII = {"C": 0.3, "N": 0.25, "O": 0.22, "S": 0.35, "P": 0.35, "H": 0.15, "F": 0.18, "Cl": 0.3}

def parse_smiles(smiles: str):
    atoms, bonds = [], []
    last_atom = -1
    pending_bond = 1
    i = 0
    while i < len(smiles):
        ch = smiles[i]
        if ch in '()[]':
            i += 1
            continue
        elif ch == '=':
            pending_bond = 2; i += 1; continue
        elif ch == '#':
            pending_bond = 3; i += 1; continue
        elif ch in '-+@':
            i += 1; continue
        elif ch.isupper():
            element = ch
            if i + 1 < len(smiles) and smiles[i + 1].islower():
                element += smiles[i + 1]; i += 1
            idx = len(atoms)
            atoms.append({
                "element": element,
                "x": float((idx % 3 - 1) * 1.5 + np.random.uniform(-0.3, 0.3)),
                "y": float((idx // 3 % 3 - 1) * 1.5 + np.random.uniform(-0.3, 0.3)),
                "z": float((idx // 9 - 1) * 1.5 + np.random.uniform(-0.3, 0.3)),
                "color": ATOM_COLORS.get(element, "#888888"),
                "radius": ATOM_RADII.get(element, 0.25)
            })
            if last_atom >= 0:
                bonds.append({"atom1": last_atom, "atom2": idx, "order": pending_bond})
            last_atom = idx
            pending_bond = 1
        i += 1
    return atoms, bonds

def compute_admet(mw: float, log_p: float, formula: str) -> dict:
    log_s = round(0.5 - 0.01 * (mw - 20) - log_p, 2)
    hbd = formula.count("O")
    hba = formula.count("N") + hbd
    violations = (1 if mw > 500 else 0) + (1 if log_p > 5 else 0) + (1 if hbd > 5 else 0) + (1 if hba > 10 else 0)
    toxicity = "高毒性风险" if log_p > 3 else "中等毒性" if log_p > 1 else "低毒性"
    protein_binding = min(99, max(10, round(log_p * 15 + 30)))
    metabolic_stability = "稳定" if mw < 300 else "中等" if mw < 450 else "不稳定"
    bioavailability = max(0, min(100, round(100 - log_p * 8 - mw * 0.05)))

    risk_score = 0
    risk_alerts = []

    if log_p > 5:
        risk_score += 3
        risk_alerts.append({
            "type": "danger",
            "title": "脂溶性过高",
            "detail": f"LogP={log_p:.2f}，可能导致组织蓄积和毒性增加"
        })
    elif log_p > 3:
        risk_score += 1
        risk_alerts.append({
            "type": "warning",
            "title": "脂溶性偏高",
            "detail": f"LogP={log_p:.2f}，需关注代谢清除率"
        })
    elif log_p < 0:
        risk_score += 1
        risk_alerts.append({
            "type": "warning",
            "title": "脂溶性偏低",
            "detail": f"LogP={log_p:.2f}，可能影响膜通透性"
        })

    if log_s < -4:
        risk_score += 2
        risk_alerts.append({
            "type": "danger",
            "title": "溶解度极差",
            "detail": f"LogS={log_s:.2f}，可能严重影响口服吸收"
        })
    elif log_s < -2:
        risk_score += 1
        risk_alerts.append({
            "type": "warning",
            "title": "溶解度偏低",
            "detail": f"LogS={log_s:.2f}，可能需要制剂优化"
        })

    if toxicity == "高毒性风险":
        risk_score += 4
        risk_alerts.append({
            "type": "danger",
            "title": "毒性风险高",
            "detail": "预测具有较高毒性，需重点关注安全性评价"
        })
    elif toxicity == "中等毒性":
        risk_score += 2
        risk_alerts.append({
            "type": "warning",
            "title": "中等毒性风险",
            "detail": "建议进行详细的毒理学研究"
        })

    if metabolic_stability == "不稳定":
        risk_score += 3
        risk_alerts.append({
            "type": "danger",
            "title": "代谢不稳定",
            "detail": f"分子量={mw}，可能代谢过快导致半衰期短"
        })
    elif metabolic_stability == "中等":
        risk_score += 1
        risk_alerts.append({
            "type": "info",
            "title": "代谢稳定性中等",
            "detail": "需关注主要代谢途径和代谢产物"
        })

    if bioavailability < 30:
        risk_score += 3
        risk_alerts.append({
            "type": "danger",
            "title": "生物利用度低",
            "detail": f"预测仅{bioavailability}%，口服给药可能效果不佳"
        })
    elif bioavailability < 50:
        risk_score += 1
        risk_alerts.append({
            "type": "warning",
            "title": "生物利用度偏低",
            "detail": f"预测{bioavailability}%，可考虑制剂改进"
        })

    if protein_binding > 90:
        risk_score += 2
        risk_alerts.append({
            "type": "warning",
            "title": "蛋白结合率过高",
            "detail": f"结合率{protein_binding}%，可能存在药物相互作用风险"
        })
    elif protein_binding > 70:
        risk_score += 1
        risk_alerts.append({
            "type": "info",
            "title": "蛋白结合率偏高",
            "detail": f"结合率{protein_binding}%，游离药物浓度需监测"
        })

    if violations > 0:
        risk_score += violations * 2
        if violations >= 2:
            risk_alerts.append({
                "type": "danger",
                "title": "Lipinski规则严重违反",
                "detail": f"违反{violations}条规则，成药性风险高"
            })
        else:
            risk_alerts.append({
                "type": "warning",
                "title": "Lipinski规则轻微违反",
                "detail": "违反1条规则，仍有优化空间"
            })

    if len(risk_alerts) == 0:
        risk_alerts.append({
            "type": "info",
            "title": "整体性质良好",
            "detail": "各项ADMET指标均在理想范围内，成药性潜力大"
        })

    risk_score = min(14, risk_score)

    if risk_score >= 12:
        risk_level = "D"
    elif risk_score >= 8:
        risk_level = "C"
    elif risk_score >= 4:
        risk_level = "B"
    else:
        risk_level = "A"

    return {
        "logP": round(log_p, 2), "logS": log_s, "toxicity": toxicity,
        "proteinBinding": protein_binding, "metabolicStability": metabolic_stability,
        "bioavailability": bioavailability, "ruleOfFive": violations <= 1, "violations": violations,
        "riskLevel": risk_level, "riskScore": risk_score, "riskAlerts": risk_alerts
    }
