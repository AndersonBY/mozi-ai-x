# 分析工具脚本

本目录包含用于分析 Mozi-AI-X 态势解析完整性的工具脚本。

## 脚本说明

### `analyze_var_maps.py`
**用途**: 分析 var_map 字段映射完整性
- 检查 `situation_data.json` 中的字段是否在 `situ_interpret.py` 的 var_map 中有对应映射
- 支持字典解包继承语法 `**ParentDict.var_map`
- 生成详细的缺失字段报告

**使用方法**:
```bash
cd /path/to/mozi-ai-x
python scripts/analysis/analyze_var_maps.py
```

**输出文件**:
- `var_map_analysis_report.md` - 详细分析报告
- `var_map_analysis_raw.json` - 原始数据

### `analyze_class_attributes.py`
**用途**: 分析 Python 类属性完整性
- 检查 var_map 映射的属性是否在对应 Python 类中有 `self.xxx` 定义
- 支持继承关系分析 (CActiveUnit 基类)
- 识别缺失的属性定义

**使用方法**:
```bash
cd /path/to/mozi-ai-x
python scripts/analysis/analyze_class_attributes.py
```

**输出文件**:
- `class_attributes_analysis_report.md` - 详细分析报告
- `class_attributes_analysis_raw.json` - 原始数据

## 使用场景

### 开发阶段
- 新增字段后验证映射完整性
- 重构类结构后检查属性完整性
- 数据结构变更的影响分析

### 维护阶段
- 定期健康检查
- 问题诊断和定位
- 代码质量评估

## 前置条件

1. **数据文件**: 需要 `situation_data.json` 和 `fields_by_class.json`
2. **Python 环境**: Python 3.8+
3. **工作目录**: 需要在项目根目录运行
