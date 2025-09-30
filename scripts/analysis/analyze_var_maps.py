#!/usr/bin/env python3
"""
深度分析 var_map 的字段映射完整性
对比 situation_data.json 中的实际字段与 situ_interpret.py 中的 var_map 定义
"""

import json
import re


def extract_var_maps(file_path: str) -> dict[str, set[str]]:
    """从 situ_interpret.py 提取所有类的 var_map 定义（支持字典解包继承）"""
    with open(file_path, encoding='utf-8') as f:
        content = f.read()

    var_maps = {}
    current_class = None
    in_var_map = False
    current_map_content = []

    for line in content.split('\n'):
        # 检测类定义
        class_match = re.match(r'class (\w+Dict):', line)
        if class_match:
            current_class = class_match.group(1).replace('Dict', '')

        # 检测 var_map 开始
        if 'var_map = {' in line:
            in_var_map = True
            current_map_content = [line]
            continue

        if in_var_map:
            current_map_content.append(line)
            # 检测 var_map 结束（注意括号平衡）
            if line.strip() == '}':
                # 解析 var_map 内容
                map_text = '\n'.join(current_map_content)
                fields = set()

                # 1. 检测字典解包继承 (例如: **CActiveUnitDict.var_map)
                parent_matches = re.findall(r'\*\*(\w+Dict)\.var_map', map_text)
                for parent_dict_class in parent_matches:
                    parent_class = parent_dict_class.replace('Dict', '')
                    # 如果父类已经解析过，继承其字段
                    if parent_class in var_maps:
                        fields.update(var_maps[parent_class])

                # 2. 提取当前类直接定义的字段（JSON字段名）
                for match in re.finditer(r'["\']([^"\']+)["\']\s*:', map_text):
                    field = match.group(1)
                    fields.add(field)

                if current_class:
                    var_maps[current_class] = fields

                in_var_map = False
                current_map_content = []

    return var_maps


def load_actual_fields() -> dict[str, set[str]]:
    """加载实际数据中的字段"""
    with open('scripts/analysis/fields_by_class.json', encoding='utf-8') as f:
        data = json.load(f)

    # 移除 ClassName 字段
    result = {}
    for class_name, fields in data.items():
        field_set = set(fields)
        field_set.discard('ClassName')
        result[class_name] = field_set

    return result


def generate_detailed_report(actual_fields: dict[str, set[str]], var_maps: dict[str, set[str]]):
    """生成详细的字段级缺失报告"""

    report_lines = []
    report_lines.append("# var_map 字段映射完整性深度分析报告\n\n")
    report_lines.append("**分析时间**: 2025-09-30\n")
    report_lines.append("**数据源**: situation_data.json\n")
    report_lines.append("**代码文件**: src/mozi_ai_x/simulation/situ_interpret.py\n\n")

    # 统计
    total_classes = len(actual_fields)
    complete_classes = 0
    incomplete_classes = 0
    missing_classes = 0

    class_details = []

    for class_name in sorted(actual_fields.keys()):
        expected_fields = actual_fields[class_name]

        if class_name not in var_maps:
            missing_classes += 1
            class_details.append({
                'class_name': class_name,
                'status': 'NO_VAR_MAP',
                'expected_count': len(expected_fields),
                'mapped_count': 0,
                'missing_count': len(expected_fields),
                'missing_fields': sorted(expected_fields),
                'extra_fields': [],
                'coverage': 0.0
            })
            continue

        mapped_fields = var_maps[class_name]
        missing_fields = expected_fields - mapped_fields
        extra_fields = mapped_fields - expected_fields

        coverage = (len(mapped_fields & expected_fields) / len(expected_fields) * 100) if expected_fields else 100.0

        if not missing_fields:
            complete_classes += 1
            status = 'COMPLETE'
        else:
            incomplete_classes += 1
            status = 'INCOMPLETE'

        class_details.append({
            'class_name': class_name,
            'status': status,
            'expected_count': len(expected_fields),
            'mapped_count': len(mapped_fields & expected_fields),
            'missing_count': len(missing_fields),
            'extra_count': len(extra_fields),
            'missing_fields': sorted(missing_fields),
            'extra_fields': sorted(extra_fields),
            'coverage': round(coverage, 2)
        })

    # 总览
    report_lines.append("## 总览\n\n")
    report_lines.append(f"- 总类数: {total_classes}\n")
    report_lines.append(f"- ✅ 完全映射: {complete_classes}/{total_classes} ({complete_classes/total_classes*100:.1f}%)\n")
    report_lines.append(f"- ⚠️ 部分映射: {incomplete_classes}/{total_classes} ({incomplete_classes/total_classes*100:.1f}%)\n")
    report_lines.append(f"- ❌ 缺少 var_map: {missing_classes}/{total_classes} ({missing_classes/total_classes*100:.1f}%)\n\n")

    # 统计总缺失字段
    total_missing = sum(d['missing_count'] for d in class_details)
    total_expected = sum(d['expected_count'] for d in class_details)
    report_lines.append(f"- **总缺失字段**: {total_missing}/{total_expected} ({total_missing/total_expected*100:.1f}%)\n\n")

    # 按覆盖率排序
    class_details.sort(key=lambda x: x['coverage'])

    report_lines.append("## 详细分析（按覆盖率从低到高排序）\n\n")

    for detail in class_details:
        class_name = detail['class_name']

        if detail['status'] == 'NO_VAR_MAP':
            report_lines.append(f"### ❌ {class_name}\n\n")
            report_lines.append("**状态**: 缺少 var_map 定义\n")
            report_lines.append(f"**数据中字段数**: {detail['expected_count']}\n\n")
            report_lines.append("**所有字段列表**:\n")
            for field in detail['missing_fields']:
                report_lines.append(f"- `{field}`\n")
            report_lines.append("\n---\n\n")
            continue

        status_icon = '✅' if detail['status'] == 'COMPLETE' else '⚠️'
        report_lines.append(f"### {status_icon} {class_name}\n\n")
        report_lines.append(f"**覆盖率**: {detail['coverage']}% ({detail['mapped_count']}/{detail['expected_count']})\n")

        if detail['missing_count'] > 0:
            report_lines.append(f"**缺失字段数**: {detail['missing_count']}\n\n")
            report_lines.append("**缺失字段列表**:\n")
            for field in detail['missing_fields']:
                report_lines.append(f"- `{field}`\n")
            report_lines.append("\n")

        if detail['extra_count'] > 0:
            report_lines.append(f"**冗余字段数**: {detail['extra_count']} (var_map 中定义但数据中不存在)\n\n")
            report_lines.append("**冗余字段列表** (可能是旧版本字段或错误):\n")
            for field in detail['extra_fields'][:20]:
                report_lines.append(f"- `{field}`\n")
            if len(detail['extra_fields']) > 20:
                report_lines.append(f"- ... 还有 {len(detail['extra_fields']) - 20} 个\n")
            report_lines.append("\n")

        report_lines.append("---\n\n")

    # 问题汇总
    report_lines.append("## 问题汇总\n\n")

    # 最严重的缺失
    top_incomplete = [d for d in class_details if d['status'] in ('INCOMPLETE', 'NO_VAR_MAP')]
    top_incomplete.sort(key=lambda x: x['missing_count'], reverse=True)

    if top_incomplete[:15]:
        report_lines.append("### 缺失字段最多的类（Top 15）\n\n")
        report_lines.append("| 类名 | 缺失字段数 | 总字段数 | 覆盖率 | 状态 |\n")
        report_lines.append("|------|------------|----------|--------|------|\n")
        for detail in top_incomplete[:15]:
            status_text = '❌ 无var_map' if detail['status'] == 'NO_VAR_MAP' else '⚠️ 不完整'
            report_lines.append(
                f"| {detail['class_name']} | {detail['missing_count']} | {detail['expected_count']} | {detail['coverage']}% | {status_text} |\n"
            )
        report_lines.append("\n")

    return ''.join(report_lines), class_details


def main():
    print("开始分析 var_map 字段映射完整性...")

    # 提取 var_map
    print("  - 解析 situ_interpret.py ...")
    var_maps = extract_var_maps('src/mozi_ai_x/simulation/situ_interpret.py')
    print(f"    发现 {len(var_maps)} 个 var_map 定义")

    # 加载实际字段
    print("  - 加载 fields_by_class.json ...")
    actual_fields = load_actual_fields()
    print(f"    发现 {len(actual_fields)} 个类的字段定义")

    # 生成报告
    print("  - 生成详细报告...")
    report, details = generate_detailed_report(actual_fields, var_maps)

    # 保存报告
    with open('var_map_analysis_report.md', 'w', encoding='utf-8') as f:
        f.write(report)

    # 保存原始数据
    with open('var_map_analysis_raw.json', 'w', encoding='utf-8') as f:
        json.dump({
            'var_maps': {k: sorted(v) for k, v in var_maps.items()},
            'actual_fields': {k: sorted(v) for k, v in actual_fields.items()},
            'details': details
        }, f, indent=2, ensure_ascii=False)

    print("\n✓ 分析完成！")
    print("  - 报告已保存到: var_map_analysis_report.md")
    print("  - 原始数据已保存到: var_map_analysis_raw.json")

    # 统计
    complete = sum(1 for d in details if d['status'] == 'COMPLETE')
    incomplete = sum(1 for d in details if d['status'] == 'INCOMPLETE')
    no_map = sum(1 for d in details if d['status'] == 'NO_VAR_MAP')
    total = len(details)

    print("\n统计:")
    print(f"  - 完全映射: {complete}/{total} ({complete/total*100:.1f}%)")
    print(f"  - 部分映射: {incomplete}/{total} ({incomplete/total*100:.1f}%)")
    print(f"  - 缺少var_map: {no_map}/{total} ({no_map/total*100:.1f}%)")

    total_missing = sum(d['missing_count'] for d in details)
    total_fields = sum(d['expected_count'] for d in details)
    print(f"  - 总缺失字段: {total_missing}/{total_fields} ({total_missing/total_fields*100:.1f}%)")


if __name__ == '__main__':
    main()
