import json
import os
import aiohttp
import time
import base64
import asyncio
from .find_port import find_comfyui_port
import server
from aiohttp import web

NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']

port = "8188"
SERVER_ADDRESS = f"127.0.0.1:{port}"

current_directory = os.path.dirname(os.path.abspath(__file__))
server_address_file = os.path.join(current_directory, 'server_address.txt')

global start_time
global end_time

def read_server_address():
    global SERVER_ADDRESS
    if os.path.exists(server_address_file):
        with open(server_address_file, 'r') as f:
            SERVER_ADDRESS = f.read().strip()
    print("Read SERVER_ADDRESS from file:", SERVER_ADDRESS)

read_server_address()

def update_server_address():
    global SERVER_ADDRESS
    comfyui_port = find_comfyui_port()
    if comfyui_port:
        SERVER_ADDRESS = f"127.0.0.1:{comfyui_port}"
    print("Updated SERVER_ADDRESS:", SERVER_ADDRESS)

def write_server_address():
    with open(server_address_file, 'w') as f:
        f.write(SERVER_ADDRESS)

async def queue_prompt(prompt):
    update_server_address()
    write_server_address()  # 写入文件
    """Submit prompt to the server and return the server response."""
    data = json.dumps({"prompt": prompt}).encode('utf-8')
    async with aiohttp.ClientSession() as session:
        async with session.post(f"http://{SERVER_ADDRESS}/prompt", data=data) as response:
            return await response.json()

async def get_image(filename, subfolder, folder_type):
    """Retrieve image data from the server."""
    data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
    async with aiohttp.ClientSession() as session:
        async with session.get(f"http://{SERVER_ADDRESS}/view", params=data) as response:
            return await response.read()

async def get_history(prompt_id):
    """Retrieve history of the specified prompt from the server."""
    async with aiohttp.ClientSession() as session:
        async with session.get(f"http://{SERVER_ADDRESS}/history/{prompt_id}") as response:
            return await response.json()

async def get_images(prompt_id):
    """Retrieve image data based on the given prompt."""
    output_images = {}
    
    while True:
        await asyncio.sleep(1)
        res = await get_history(prompt_id)
        if prompt_id not in res:
            continue
        
        history = res[prompt_id]
        latest_status = history['status']['status_str']
        if latest_status == 'success':
            for node_id, node_output in history['outputs'].items():
                images_output = []
                if 'images' in node_output:
                    for image in node_output['images']:
                        image_data = await get_image(image['filename'], image['subfolder'], image['type'])
                        base64_image = "data:image/png;base64," + base64.b64encode(image_data).decode('utf-8')
                        images_output.append(base64_image)
                output_images[node_id] = images_output
            return {"prompt_id": prompt_id, "status": "success", "images": output_images}
        else:
            return {"prompt_id": prompt_id, "status": "failed", "message": "Execution status is not success."}

async def send_callback(res_task, callback_url):
    global start_time
    global end_time
    result = await get_images(res_task['prompt_id'])
    end_time = time.time()
    total_time = end_time - start_time
    result["total_time"] = total_time
    data = json.dumps(result).encode('utf-8')
    headers = {'content-type': 'application/json'}
    async with aiohttp.ClientSession() as session:
        async with session.post(callback_url, data=data, headers=headers) as response:
            pass

@server.PromptServer.instance.routes.post("/prompt_queue")
async def prompt_queue(request):
    try:
        data = await request.json()  # Get POST data from the request
        prompt = data['prompt']
        callback_url = data['callback_url']
        global start_time
        start_time = time.time()
        res_task = await queue_prompt(prompt)
        asyncio.create_task(send_callback(res_task, callback_url))
        return web.json_response(res_task)
    except Exception as e:
        return web.Response(text=json.dumps({"error": str(e)}), status=500)
