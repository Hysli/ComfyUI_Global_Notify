import os
import sys
import subprocess
import threading
import locale
import traceback
import re

# 获取当前文件所在目录
root_path = os.path.dirname(os.path.abspath(__file__))

# 处理子进程的输出流
def handle_stream(stream, is_stdout):
    stream.reconfigure(encoding=locale.getpreferredencoding(), errors='replace')
    for msg in stream:
        if is_stdout:
            print(msg, end="", file=sys.stdout)
        else:
            print(msg, end="", file=sys.stderr)

# 包装子进程执行命令
def process_wrap(cmd_str, cwd=None, handler=None):
    print(f"EXECUTE: {cmd_str} in '{cwd}'")
    process = subprocess.Popen(cmd_str, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)

    if handler is None:
        handler = handle_stream

    stdout_thread = threading.Thread(target=handler, args=(process.stdout, True))
    stderr_thread = threading.Thread(target=handler, args=(process.stderr, False))

    stdout_thread.start()
    stderr_thread.start()

    stdout_thread.join()
    stderr_thread.join()

    return process.wait()

# 已安装的包列表
pip_list = None

# 获取已安装的 pip 包
def get_installed_packages():
    global pip_list
    if pip_list is None:
        try:
            result = subprocess.check_output([sys.executable, '-m', 'pip', 'list'], universal_newlines=True)
            pip_list = set([line.split()[0].lower() for line in result.split('\n') if line.strip()])
        except subprocess.CalledProcessError:
            print("Failed to retrieve the information of installed pip packages.")
            return set()
    return pip_list

# 检查包是否已安装
def is_installed(name):
    name = name.strip()
    pattern = r'([^<>!=]+)([<>!=]=?)'
    match = re.search(pattern, name)
    if match:
        name = match.group(1)
    return name.lower() in get_installed_packages()

# 检查并安装依赖项
def check_and_install_requirements(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            lines = file.readlines()
            for line in lines:
                print(f"check {line}")
                if not is_installed(line):
                    print(f"install {line}")
                    process_wrap(pip_install + [line], cwd=root_path)
                else:
                    print(f"{line} is installed")
            return False
    return True

try:
    import platform

    print("### : ComfyUI_Global_Notify Check dependencies")
    if "python_embed" in sys.executable or "python_embedded" in sys.executable:
        pip_install = [sys.executable, '-s', '-m', 'pip', 'install', '-q']
    else:
        pip_install = [sys.executable, '-m', 'pip', 'install', '-q']

    subpack_req = os.path.join(root_path, "requirements.txt")
    check_and_install_requirements(subpack_req)
    
    if sys.argv[0] == 'install.py':
        sys.path.append('..')  # for portable version

except Exception as e:
    print("Dependency installation has failed. Please install manually.")
    traceback.print_exc()
