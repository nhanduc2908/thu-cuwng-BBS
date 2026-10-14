from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent / "mobile"
WINDOWS = os.name == "nt"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Khởi động giao diện PetCare Mobile bằng Expo."
    )
    platform = parser.add_mutually_exclusive_group()
    platform.add_argument(
        "--android",
        action="store_true",
        help="Mở trên thiết bị/emulator Android đã kết nối.",
    )
    platform.add_argument(
        "--ios",
        action="store_true",
        help="Mở trên iOS Simulator (cần macOS và Xcode).",
    )
    platform.add_argument(
        "--web",
        action="store_true",
        help="Chạy giao diện web để xem trước.",
    )
    parser.add_argument(
        "--host",
        choices=("lan", "tunnel", "localhost"),
        default="lan",
        help="Cách Expo kết nối thiết bị (mặc định: lan).",
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Xóa cache Metro trước khi khởi động.",
    )
    parser.add_argument(
        "--install",
        action="store_true",
        help="Cài lại dependency bằng npm ci trước khi khởi động.",
    )
    parser.add_argument(
        "--skip-install",
        action="store_true",
        help="Không tự cài dependency nếu thư mục node_modules chưa có.",
    )
    return parser.parse_args()


def find_executable(*names: str) -> str | None:
    for name in names:
        executable = shutil.which(name)
        if executable:
            return executable
    return None


def run_npm(npm: str, args: list[str]) -> int:
    try:
        if WINDOWS:
            command = f'call "{npm}" {subprocess.list2cmdline(args)}'
            return subprocess.run(
                command,
                cwd=PROJECT_DIR,
                shell=True,
                check=False,
            ).returncode
        return subprocess.run([npm, *args], cwd=PROJECT_DIR, check=False).returncode
    except OSError as error:
        print(f"Không thể chạy npm: {error}")
        return 1


def expo_arguments(options: argparse.Namespace) -> list[str]:
    arguments = ["--", "--host", options.host]
    if options.android:
        arguments.append("--android")
    elif options.ios:
        arguments.append("--ios")
    elif options.web:
        arguments.append("--web")
    if options.clear:
        arguments.append("--clear")
    return arguments


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    options = parse_args()

    package_json = PROJECT_DIR / "package.json"
    lock_file = PROJECT_DIR / "package-lock.json"
    if not package_json.is_file() or not lock_file.is_file():
        print(f"Không tìm thấy dự án Expo hoặc package lock tại:\n{PROJECT_DIR}")
        return 1

    node = find_executable("node.exe", "node")
    npm = find_executable("npm.cmd", "npm.exe", "npm")
    if node is None or npm is None:
        print("Máy chưa có Node.js/npm hoặc chưa được thêm vào PATH.")
        print("Hãy cài Node.js LTS, đóng/mở lại terminal rồi chạy lại file này.")
        return 1

    try:
        node_version = subprocess.run(
            [node, "--version"],
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError as error:
        print(f"Không thể chạy Node.js: {error}")
        return 1
    if node_version.returncode != 0:
        print("Không kiểm tra được Node.js. Hãy kiểm tra lại cài đặt Node.js.")
        return node_version.returncode
    print(f"Node.js {node_version.stdout.strip()}")

    expo_cli = PROJECT_DIR / "node_modules" / "expo" / "bin" / "cli"
    should_install = options.install or not expo_cli.is_file()
    if should_install:
        if options.skip_install:
            print("Chưa có Expo trong node_modules và bạn đã chọn bỏ qua cài đặt.")
            print("Chạy lại không dùng --skip-install để cài các dependency cần thiết.")
            return 1
        print("Đang cài dependency của PetCare Mobile bằng npm ci...")
        install_status = run_npm(npm, ["ci"])
        if install_status != 0:
            print("Cài dependency thất bại. Kiểm tra kết nối mạng và log npm.")
            return install_status

    print()
    print("Đang khởi động PetCare Mobile...")
    print("Quét mã QR bằng Expo Go hoặc chọn thiết bị trong cửa sổ Expo.")
    if options.ios and WINDOWS:
        print("Lưu ý: Windows không chạy được iOS Simulator; dùng Mac/Xcode hoặc EAS Build.")

    try:
        return run_npm(npm, ["run", "start", *expo_arguments(options)])
    except KeyboardInterrupt:
        print("\nĐã dừng Expo.")
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
