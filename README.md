# ComfyUI_Global_Notify

ComfyUI Global Callback Notification

```shell
curl --location --request POST 'http://192.168.10.13:46539/prompt_queue' \
--header 'Content-Type: application/json' \
--header 'Accept: */*' \
--header 'Host: 192.168.10.13:46539' \
--header 'Connection: keep-alive' \
--data-raw '{
    "prompt": {
        "3": {
            "inputs": {
                "seed": 123123123123,
                "steps": 20,
                "cfg": 8,
                "sampler_name": "euler",
                "scheduler": "normal",
                "denoise": 1,
                "model": [
                    "4",
                    0
                ],
                "positive": [
                    "6",
                    0
                ],
                "negative": [
                    "7",
                    0
                ],
                "latent_image": [
                    "5",
                    0
                ]
            },
            "class_type": "KSampler",
            "_meta": {
                "title": "K采样器"
            }
        },
        "4": {
            "inputs": {
                "ckpt_name": "Anything-ink.safetensors"
            },
            "class_type": "CheckpointLoaderSimple",
            "_meta": {
                "title": "Checkpoint加载器(简易)"
            }
        },
        "5": {
            "inputs": {
                "width": 512,
                "height": 512,
                "batch_size": 1
            },
            "class_type": "EmptyLatentImage",
            "_meta": {
                "title": "空Latent"
            }
        },
        "6": {
            "inputs": {
                "text": "beautiful scenery nature glass bottle landscape, , purple galaxy bottle,",
                "clip": [
                    "4",
                    1
                ]
            },
            "class_type": "CLIPTextEncode",
            "_meta": {
                "title": "CLIP文本编码器"
            }
        },
        "7": {
            "inputs": {
                "text": "text, watermark",
                "clip": [
                    "4",
                    1
                ]
            },
            "class_type": "CLIPTextEncode",
            "_meta": {
                "title": "CLIP文本编码器"
            }
        },
        "8": {
            "inputs": {
                "samples": [
                    "3",
                    0
                ],
                "vae": [
                    "4",
                    2
                ]
            },
            "class_type": "VAEDecode",
            "_meta": {
                "title": "VAE解码"
            }
        },
        "9": {
            "inputs": {
                "filename_prefix": "ComfyUI",
                "images": [
                    "8",
                    0
                ]
            },
            "class_type": "SaveImage",
            "_meta": {
                "title": "save images"
            }
        }
    },
    "callback_url": "https://example.com/comfyui_callback"
}'
```

```json
{
    "prompt": "your_prompt_here",
    "callback_url": "http://your_callback_url_here",
    "s3_config": {
        "enabled": true,
        "endpoint_url": "https://your_s3_endpoint_here",
        "aws_access_key_id": "your_access_key_id_here",
        "aws_secret_access_key": "your_secret_access_key_here",
        "region_name": "your_region_name_here",
        "bucket_name": "your_bucket_name_here",
        "folder": "your_folder_name_here", 
        "bucket_url": "https://your_bucket_url_here"
    }
}
```
