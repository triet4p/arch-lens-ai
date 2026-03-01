import os
import subprocess
import platform
import sys

# 1. Xác định đường dẫn tuyệt đối (Giữ nguyên logic legacy)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

# 2. Cấu hình đường dẫn
BINARY_NAME = "arch-lens-ai-backend"
SRC_PATH = os.path.join(PROJECT_ROOT, "src", "main.py")
# Lưu ý: Legacy dùng .env từ root, nếu bạn chưa có hãy tạo file trống
ENV_PATH = os.path.join(PROJECT_ROOT, ".env") 
DIST_DIR = os.path.abspath(os.path.join(PROJECT_ROOT, "..", "src-tauri", "binaries"))
WORK_PATH = os.path.join(PROJECT_ROOT, "build")

def get_target_triple():
    machine = platform.machine().lower()
    system = platform.system().lower()
    
    if system == "windows":
        return "x86_64-pc-windows-msvc"
    elif system == "darwin": 
        return "aarch64-apple-darwin" if machine == "arm64" else "x86_64-apple-darwin"
    elif system == "linux":
        return "x86_64-unknown-linux-gnu"
    else:
        raise Exception(f"Unsupported platform: {system}")

def build():
    print(f"🚀 Starting Build Process (Legacy Logic)...")
    print(f"   Root:   {PROJECT_ROOT}")
    print(f"   Output: {DIST_DIR}")

    os.makedirs(DIST_DIR, exist_ok=True)

    separator = ";" if platform.system() == "Windows" else ":"
    # Chỉ add data nếu file tồn tại để tránh lỗi
    add_data_arg = []
    if os.path.exists(ENV_PATH):
        add_data_arg = ["--add-data", f"{ENV_PATH}{separator}."]

    # --- FIX: AGGRESSIVE IMPORTS (Theo chuẩn legacy bạn đã dùng) ---
    aggressive_args = [
        # Gom toàn bộ module AI và xử lý tài liệu
        "--collect-all", "pydantic_ai",
        "--collect-all", "markitdown",
        "--collect-all", "pymupdf4llm",
        "--collect-all", "pymupdf",
        
        # Copy metadata để tránh lỗi 'Package not found' lúc runtime
        "--copy-metadata", "tqdm",
        "--copy-metadata", "regex",
        "--copy-metadata", "requests",
        "--copy-metadata", "packaging",
        "--copy-metadata", "filelock",
        "--copy-metadata", "numpy",
        "--copy-metadata", "pydantic_ai",
        "--copy-metadata", "markitdown",
        "--copy-metadata", "genai_prices",
    ]

    cmd = [
        "pyinstaller",
        "--clean",
        "--noconfirm",
        "--onefile",
        "--name", BINARY_NAME,
        "--distpath", DIST_DIR,
        "--workpath", WORK_PATH,
        "--specpath", PROJECT_ROOT,
    ] + add_data_arg + aggressive_args + [SRC_PATH]
    
    try:
        print("🔨 Running PyInstaller (This might take a while)...")
        # Tuyệt đối KHÔNG có flag --strip ở đây trên Windows
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError:
        print("❌ Build Failed.")
        sys.exit(1)
    
    # Rename logic (Chuẩn Tauri Sidecar)
    target_triple = get_target_triple()
    ext = ".exe" if platform.system() == "Windows" else ""
    
    original_file = os.path.join(DIST_DIR, f"{BINARY_NAME}{ext}")
    target_file = os.path.join(DIST_DIR, f"{BINARY_NAME}-{target_triple}{ext}")
    
    if os.path.exists(target_file):
        os.remove(target_file)
        
    if os.path.exists(original_file):
        os.rename(original_file, target_file)
        print(f"✅ Build Success! Binary ready at: {target_file}")
    else:
        print(f"❌ Error: Original binary not found at {original_file}")
        sys.exit(1)

if __name__ == "__main__":
    build()