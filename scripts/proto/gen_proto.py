import sys
import argparse
import subprocess
from pathlib import Path


def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="调用 betterproto 生成文件到指定位置")
    parser.add_argument("--output", "-o", required=True, help="指定生成的文件输出目录,例如 ./proto/src")
    args = parser.parse_args()

    output_dir = args.output
    proto_dir = Path(__file__).parent / "src"

    # 查找所有 proto 文件
    proto_files = list(proto_dir.glob("*.proto"))

    if not proto_files:
        print(f"错误: 在 {proto_dir} 中未找到 proto 文件")
        sys.exit(1)

    print(f"找到 {len(proto_files)} 个 proto 文件:")
    for proto_file in proto_files:
        print(f"  - {proto_file.name}")

    # 为每个 proto 文件生成代码
    for proto_file in proto_files:
        print(f"\n正在处理: {proto_file.name}")

        # 构造命令行参数，-I 指定 proto 文件所在目录为搜索路径
        command = [
            sys.executable,
            "-m",
            "grpc_tools.protoc",
            "-I",
            str(proto_dir.as_posix()),  # 使用 proto 文件所在目录作为搜索路径
            f"--python_betterproto_out={output_dir}",
            str(proto_file.name),
        ]

        print("正在执行命令：", " ".join(command))
        result = subprocess.run(command, capture_output=True, text=True)

        if result.returncode != 0:
            print(f"生成 {proto_file.name} 失败:")
            print(result.stderr)
            sys.exit(result.returncode)
        else:
            print(f"✓ {proto_file.name} 生成成功！")

    # 搜索生成文件里的内容，替换路径： /grpc.gRPC/ -> /GRPC.gRPC/
    # 墨子系统这里没注意处理大小写问题
    print("\n正在处理生成的文件...")
    for file in Path(output_dir).glob("**/*.py"):
        with open(file, encoding="utf-8") as f:
            content = f.read()
        content = content.replace("/grpc.gRPC/", "/GRPC.gRPC/")
        with open(file, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  处理: {file.name}")

    print("\n✓ 所有文件生成成功！")


if __name__ == "__main__":
    main()
