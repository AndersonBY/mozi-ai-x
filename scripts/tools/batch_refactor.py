import argparse
from pathlib import Path
import libcst as cst
from libcst import FunctionDef, Decorator, Attribute, Name

VALIDATOR_IMPORT_LINE = "from mozi_ai_x.utils.validator import validate_literal_args, validate_uuid4_args\n"


def has_validator_import(module: cst.Module) -> bool:
    for imp in module.body:
        if isinstance(imp, cst.SimpleStatementLine) and hasattr(imp, "body"):
            for s in imp.body:
                t = getattr(s, "module", None)
                if t and isinstance(t, cst.Name) and "validator" in t.value:
                    return True
    return False


def is_literal_annotation(ann):
    # ann: libcst.Annotation.annotation
    # Need to match Literal[...], string/number等
    if isinstance(ann, cst.Subscript):
        # ann.value: cst.Name("Literal") or cst.Attribute
        if isinstance(ann.value, cst.Name) and ann.value.value == "Literal":
            return True
    return False


class MethodTransformer(cst.CSTTransformer):
    def __init__(self):
        # 参数名 -> 装饰器
        self.uuid_param_names = []

    def leave_FunctionDef(self, original_node: FunctionDef, updated_node: FunctionDef) -> FunctionDef:
        # only public method (skip _private)
        if original_node.name.value.startswith("_"):
            return updated_node

        # skip if already decorated
        names = (
            [
                getattr(dec.decorator, "attr", None)
                if isinstance(dec.decorator, Attribute)
                else getattr(dec.decorator, "value", None)
                for dec in updated_node.decorators
            ]
            if updated_node.decorators
            else []
        )
        names = [v.value if isinstance(v, Name) else None for v in names]
        has_lit = "validate_literal_args" in (names or [])
        has_uuid = "validate_uuid4_args" in (names or [])

        param_list = list(original_node.params.params)
        hints = {p.name.value: p.annotation.annotation for p in param_list if p.annotation}

        # Find Literal
        to_add_lit = any(is_literal_annotation(ann) for ann in hints.values())

        # Find guid-like string params for UUID4
        uuid_params = []
        for n, ann in hints.items():
            # param name like guid, xxx_guid, yyyGuid
            if ("guid" in n or "Guid" in n) and isinstance(ann, Name) and ann.value == "str":
                uuid_params.append(n)
        # Compose decorators:
        new_decorators = list(updated_node.decorators or [])
        if to_add_lit and not has_lit:
            new_decorators.insert(0, Decorator(decorator=Name("validate_literal_args")))
        if uuid_params and not has_uuid:
            new_decorators.insert(
                0,
                cst.Decorator(
                    decorator=cst.Call(
                        func=cst.Name("validate_uuid4_args"),
                        args=[
                            cst.Arg(
                                value=cst.List(
                                    elements=[cst.Element(value=cst.SimpleString(f'"{name}"')) for name in uuid_params]
                                )
                            )
                        ],
                    )
                ),
            )

        return updated_node.with_changes(decorators=new_decorators)


def patch_file(path: Path, write_changes: bool = False):
    with open(path, encoding="utf-8") as f:
        code = f.read()
    module = cst.parse_module(code)
    changed = False

    transformer = MethodTransformer()
    module2 = module.visit(transformer)
    out_code = module2.code
    # Insert import if needed
    if "validate_uuid4_args" in out_code or "validate_literal_args" in out_code:
        if not has_validator_import(module):
            out_code = VALIDATOR_IMPORT_LINE + out_code
            changed = True
    if out_code != code:
        print(f"Patched: {path}")
        # Write changes if requested
        if write_changes:
            with open(path, "w", encoding="utf-8") as f:
                f.write(out_code)
            print("  Changes written to file")
        else:
            # Just diff-print
            import difflib

            print(
                "".join(
                    difflib.unified_diff(
                        code.splitlines(True), out_code.splitlines(True), fromfile="before", tofile="after"
                    )
                )
            )
        changed = True
    return changed


def parse_args():
    parser = argparse.ArgumentParser(description="批量重构工具：添加参数验证装饰器")
    parser.add_argument("--write", action="store_true", help="实际写入更改到文件（默认只显示diff）")
    parser.add_argument(
        "--dir",
        type=str,
        default="src/mozi_ai_x/simulation",
        help="要处理的目录路径（默认：src/mozi_ai_x/simulation）",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    SRC = Path(args.dir)
    cnt = 0
    if SRC.is_file():
        if patch_file(SRC, write_changes=args.write):
            cnt += 1
    else:
        for file in SRC.rglob("*.py"):
            if patch_file(file, write_changes=args.write):
                cnt += 1
    print(f"总共修改: {cnt} 个文件{' (已写入)' if args.write else ' (仅diff)'}")


if __name__ == "__main__":
    main()
