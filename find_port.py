import psutil

def find_process_port(process_name):
    print("Searching for process port:", process_name)
    for proc in psutil.process_iter(['pid', 'cmdline']):
        if process_name in proc.info['cmdline']:
            for conn in proc.connections():
                if conn.status == psutil.CONN_LISTEN:
                    print("Found process port:", conn.laddr.port)
                    return conn.laddr.port
    print("No process port found.")
    return None

def find_main_py_processes():
    main_py_processes = []
    print("Searching for main.py processes...")
    for proc in psutil.process_iter(['pid', 'cmdline', 'cwd']):
        if 'main.py' in proc.info['cmdline']:
            main_py_processes.append(proc)
    print("Found main.py processes:", main_py_processes)
    return main_py_processes

def find_comfyui_port():
    comfyui_processes = []
    main_py_processes = find_main_py_processes()
    print("Searching for comfyui port among main.py processes...")
    for proc in main_py_processes:
        cwd = proc.info.get('cwd', None)
        if cwd and 'comfyui' in cwd.lower():
            print("Found comfyui path:", cwd)
            port = find_process_port(proc.info['cmdline'][0])  # Pass the process name as argument
            if port:
                comfyui_processes.append((cwd, port))
    if comfyui_processes:
        for path, port in comfyui_processes:
            return port
    print("No comfyui port found.")
    return None
