#!/usr/bin/env python3
"""
深度分析 Python 类属性完整性
检查 var_map 中映射的字段是否在对应的 Python 类中有对应的属性定义
"""

import json
import re
from pathlib import Path


def extract_var_maps(file_path: str) -> dict[str, dict[str, str]]:
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
                fields = {}

                # 1. 检测字典解包继承 (例如: **CActiveUnitDict.var_map)
                parent_matches = re.findall(r'\*\*(\w+Dict)\.var_map', map_text)
                for parent_dict_class in parent_matches:
                    parent_class = parent_dict_class.replace('Dict', '')
                    # 如果父类已解析过，继承其字段
                    if parent_class in var_maps:
                        fields.update(var_maps[parent_class])

                # 2. 提取当前类直接定义的字段映射（JSON字段名 -> Python属性名）
                for match in re.finditer(r'["\']([^"\']+)["\']\s*:\s*["\']([^"\']+)["\']', map_text):
                    json_field = match.group(1)
                    python_attr = match.group(2)
                    fields[json_field] = python_attr

                if current_class:
                    var_maps[current_class] = fields

                in_var_map = False
                current_map_content = []

    return var_maps


def extract_class_attributes(file_path: str) -> set[str]:
    """从 Python 类文件中提取 self.xxx 属性定义"""
    try:
        with open(file_path, encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        return set()

    attributes = set()

    # 匹配 self.attribute = xxx 的模式
    for match in re.finditer(r'self\.(\w+)\s*=', content):
        attr_name = match.group(1)
        # 排除一些不相关的属性
        if attr_name not in ['var_map']:  # var_map 不算业务属性
            attributes.add(attr_name)

    return attributes


def get_class_with_inheritance_attributes(class_name: str, class_files: dict[str, str]) -> set[str]:
    """获取类及其父类的所有属性"""
    all_attributes = set()

    # 类继承关系
    inheritance_map = {
        'CShip': ['CActiveUnit'],
        'CAircraft': ['CActiveUnit'],
        'CFacility': ['CActiveUnit'],
        # 可以根据需要添加更多继承关系
    }

    # 首先添加当前类的属性
    if class_name in class_files:
        all_attributes.update(extract_class_attributes(class_files[class_name]))

    # 然后添加父类的属性
    if class_name in inheritance_map:
        for parent_class in inheritance_map[class_name]:
            if parent_class in class_files:
                parent_attrs = extract_class_attributes(class_files[parent_class])
                all_attributes.update(parent_attrs)

    return all_attributes


def find_class_files() -> dict[str, str]:
    """查找所有 Python 类文件"""
    class_files = {}

    # 类名到文件路径的映射
    class_mappings = {
        'CShip': 'src/mozi_ai_x/simulation/active_unit/ship.py',
        'CAircraft': 'src/mozi_ai_x/simulation/active_unit/aircraft.py',
        'CFacility': 'src/mozi_ai_x/simulation/active_unit/facility.py',
        'CActiveUnit': 'src/mozi_ai_x/simulation/active_unit/base.py',  # 添加基类
        'CContact': 'src/mozi_ai_x/simulation/contact.py',
        'CCurrentScenario': 'src/mozi_ai_x/simulation/scenario.py',
        'CDoctrine': 'src/mozi_ai_x/simulation/doctrine.py',
        'CLoadout': 'src/mozi_ai_x/simulation/loadout/base.py',
        'CMagazine': 'src/mozi_ai_x/simulation/magazine/__init__.py',
        'CMount': 'src/mozi_ai_x/simulation/mount.py',
        'CReferencePoint': 'src/mozi_ai_x/simulation/reference_point.py',
        'CResponse': 'src/mozi_ai_x/simulation/response.py',
        'CSensor': 'src/mozi_ai_x/simulation/sensor.py',
        'CSide': 'src/mozi_ai_x/simulation/side.py',
        'CSideWay': 'src/mozi_ai_x/simulation/sideway.py',
        'CSimEvent': 'src/mozi_ai_x/simulation/sim_event.py',
        'CStrikeMission': 'src/mozi_ai_x/simulation/mission/strike.py',
        'CSupportMission': 'src/mozi_ai_x/simulation/mission/support.py',
        'CTriggerUnitDetected': 'src/mozi_ai_x/simulation/trigger/unit_detected.py',
        'CWayPoint': 'src/mozi_ai_x/simulation/waypoint.py',
        'CWeather': 'src/mozi_ai_x/simulation/weather.py',
        'CActionChangeMissionStatus': 'src/mozi_ai_x/simulation/action/change_mission_status.py',
    }

    for class_name, file_path in class_mappings.items():
        if Path(file_path).exists():
            class_files[class_name] = file_path

    return class_files


def analyze_attribute_completeness():
    """分析属性完整性"""
    print("开始分析 Python 类属性完整性...")

    # 1. 提取 var_map 映射
    print("  - 解析 var_map 定义...")
    var_maps = extract_var_maps('src/mozi_ai_x/simulation/situ_interpret.py')
    print(f"    发现 {len(var_maps)} 个类的 var_map 定义")

    # 2. 查找类文件
    print("  - 查找 Python 类文件...")
    class_files = find_class_files()
    print(f"    发现 {len(class_files)} 个类文件")

    # 3. 分析每个类
    results = []

    for class_name in sorted(var_maps.keys()):
        if class_name not in class_files:
            results.append({
                'class_name': class_name,
                'status': 'FILE_NOT_FOUND',
                'file_path': 'N/A',
                'expected_attrs': list(var_maps[class_name].values()),
                'actual_attrs': [],
                'missing_attrs': list(var_maps[class_name].values()),
                'coverage': 0.0
            })
            continue

        file_path = class_files[class_name]

        # 提取类中定义的属性（包括继承的属性）
        actual_attrs = get_class_with_inheritance_attributes(class_name, class_files)

        # 从 var_map 中获取期望的属性（Python 属性名）
        expected_attrs = set(var_maps[class_name].values())

        # 计算缺失的属性
        missing_attrs = expected_attrs - actual_attrs

        # 计算覆盖率
        coverage = ((len(expected_attrs) - len(missing_attrs)) / len(expected_attrs) * 100) if expected_attrs else 100.0

        results.append({
            'class_name': class_name,
            'status': 'COMPLETE' if not missing_attrs else 'INCOMPLETE',
            'file_path': file_path,
            'expected_attrs': sorted(expected_attrs),
            'actual_attrs': sorted(actual_attrs),
            'missing_attrs': sorted(missing_attrs),
            'coverage': round(coverage, 2)
        })

    return results


def generate_attribute_report(results: list[dict]):
    """生成属性完整性报告"""
    report_lines = []
    report_lines.append("# Python 类属性完整性分析报告\n\n")
    report_lines.append("**分析时间**: 2025-09-30\n")
    report_lines.append("**目的**: 检查 var_map 映射的属性是否在 Python 类中有对应定义\n\n")

    # 统计
    total_classes = len(results)
    complete_classes = len([r for r in results if r['status'] == 'COMPLETE'])
    incomplete_classes = len([r for r in results if r['status'] == 'INCOMPLETE'])
    missing_files = len([r for r in results if r['status'] == 'FILE_NOT_FOUND'])

    report_lines.append("## 总览\n\n")
    report_lines.append(f"- 总类数: {total_classes}\n")
    report_lines.append(f"- ✅ 属性完整: {complete_classes}/{total_classes} ({complete_classes/total_classes*100:.1f}%)\n")
    report_lines.append(f"- ⚠️ 属性不完整: {incomplete_classes}/{total_classes} ({incomplete_classes/total_classes*100:.1f}%)\n")
    report_lines.append(f"- ❌ 文件未找到: {missing_files}/{total_classes} ({missing_files/total_classes*100:.1f}%)\n\n")

    # 按覆盖率排序
    results.sort(key=lambda x: x['coverage'])

    report_lines.append("## 详细分析（按覆盖率从低到高排序）\n\n")

    for result in results:
        class_name = result['class_name']

        if result['status'] == 'FILE_NOT_FOUND':
            report_lines.append(f"### ❌ {class_name}\n\n")
            report_lines.append(f"**文件**: `{result['file_path']}` (未找到)\n")
            report_lines.append(f"**期望属性数**: {len(result['expected_attrs'])}\n\n")
            report_lines.append("**所有期望属性**:\n")
            for attr in result['expected_attrs']:
                report_lines.append(f"- `self.{attr}`\n")
            report_lines.append("\n---\n\n")
            continue

        status_icon = '✅' if result['status'] == 'COMPLETE' else '⚠️'
        report_lines.append(f"### {status_icon} {class_name}\n\n")
        report_lines.append(f"**文件**: `{result['file_path']}`\n")
        report_lines.append(f"**覆盖率**: {result['coverage']}% ({len(result['expected_attrs']) - len(result['missing_attrs'])}/{len(result['expected_attrs'])})\n")

        if result['missing_attrs']:
            report_lines.append(f"**缺失属性数**: {len(result['missing_attrs'])}\n\n")
            report_lines.append("**缺失属性列表**:\n")
            for attr in result['missing_attrs']:
                report_lines.append(f"- `self.{attr}`\n")
            report_lines.append("\n")

        report_lines.append("---\n\n")

    # 问题汇总
    report_lines.append("## 问题汇总\n\n")

    # 最严重的缺失
    incomplete_results = [r for r in results if r['status'] == 'INCOMPLETE']
    incomplete_results.sort(key=lambda x: len(x['missing_attrs']), reverse=True)

    if incomplete_results:
        report_lines.append("### 缺失属性最多的类（Top 10）\n\n")
        report_lines.append("| 类名 | 缺失属性数 | 总属性数 | 覆盖率 | 状态 |\n")
        report_lines.append("|------|------------|----------|--------|------|\n")
        for result in incomplete_results[:10]:
            status_text = '⚠️ 不完整'
            report_lines.append(
                f"| {result['class_name']} | {len(result['missing_attrs'])} | {len(result['expected_attrs'])} | {result['coverage']}% | {status_text} |\n"
            )
        report_lines.append("\n")

    return ''.join(report_lines)


def main():
    results = analyze_attribute_completeness()

    # 生成报告
    print("  - 生成属性完整性报告...")
    report = generate_attribute_report(results)

    # 保存报告
    with open('class_attributes_analysis_report.md', 'w', encoding='utf-8') as f:
        f.write(report)

    # 保存原始数据
    with open('class_attributes_analysis_raw.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print("\n✓ 分析完成！")
    print("  - 报告已保存到: class_attributes_analysis_report.md")
    print("  - 原始数据已保存到: class_attributes_analysis_raw.json")

    # 统计
    complete = len([r for r in results if r['status'] == 'COMPLETE'])
    incomplete = len([r for r in results if r['status'] == 'INCOMPLETE'])
    missing = len([r for r in results if r['status'] == 'FILE_NOT_FOUND'])
    total = len(results)

    print("\n统计:")
    print(f"  - 属性完整: {complete}/{total} ({complete/total*100:.1f}%)")
    print(f"  - 属性不完整: {incomplete}/{total} ({incomplete/total*100:.1f}%)")
    print(f"  - 文件未找到: {missing}/{total} ({missing/total*100:.1f}%)")

    total_missing = sum(len(r['missing_attrs']) for r in results)
    total_expected = sum(len(r['expected_attrs']) for r in results)
    print(f"  - 总缺失属性: {total_missing}/{total_expected} ({total_missing/total_expected*100:.1f}%)")


if __name__ == '__main__':
    main()
