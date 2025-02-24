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
    proto_file = proto_dir / "GRPCServerBase.proto"

    if not proto_file.exists():
        print(f"错误: proto 文件 {proto_file} 不存在")
        sys.exit(1)

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
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    if result.returncode != 0:
        print("生成文件失败:")
        print(result.stderr)
        sys.exit(result.returncode)
    else:
        print("文件生成成功！")

    # 搜索生成文件里的内容，替换路径： /grpc.gRPC/ -> /GRPC.gRPC/
    # 墨子系统这里没注意处理大小写问题
    for file in Path(output_dir).glob("**/*.py"):
        with open(file, "r", encoding="utf-8") as f:
            content = f.read()
        content = content.replace("/grpc.gRPC/", "/GRPC.gRPC/")
        with open(file, "w", encoding="utf-8") as f:
            f.write(content)


if __name__ == "__main__":
    main()
