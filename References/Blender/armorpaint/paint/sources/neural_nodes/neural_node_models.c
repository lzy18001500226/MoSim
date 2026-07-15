
#include "../global.h"

void neural_node_models_init() {
	gc_unroot(neural_node_models);
	neural_node_models = any_array_create_from_raw(
	    (void *[]){
	        GC_ALLOC_INIT(neural_node_model_t,
	                      {.name   = "Stable Diffusion",
	                       .memory = "4GB",
	                       .size   = "4.3GB",
	                       .nodes  = "Inpaint Image, Outpaint Image, Text to Image, Tile Image, Vary Image",
	                       .urls   = any_array_create_from_raw(
                               (void *[]){
                                   "https://huggingface.co/stable-diffusion-v1-5/stable-diffusion-v1-5/resolve/main/v1-5-pruned-emaonly.safetensors",
                               },
                               1),
	                       .web     = "https://huggingface.co/stable-diffusion-v1-5/stable-diffusion-v1-5",
	                       .license = "openrail"}),

	        GC_ALLOC_INIT(neural_node_model_t, {.name   = "Z-Image-Turbo",
	                                            .memory = "4GB",
	                                            .size   = "6.7GB",
	                                            .nodes  = "Text to Image",
	                                            .urls   = any_array_create_from_raw(
                                                    (void *[]){
                                                        "https://huggingface.co/armory3d/z_image_turbo/resolve/main/Qwen3-4B-Instruct-2507-Q4_K_S.gguf",
                                                        "https://huggingface.co/armory3d/z_image_turbo/resolve/main/ae.safetensors",
                                                        "https://huggingface.co/armory3d/z_image_turbo/resolve/main/z_image_turbo-Q4_K.gguf",
                                                    },
                                                    3),
	                                            .web     = "https://huggingface.co/armory3d/z_image_turbo",
	                                            .license = "apache-2.0"}),

	        GC_ALLOC_INIT(neural_node_model_t,
	                      {.name   = "FLUX 2 klein",
	                       .memory = "4GB",
	                       .size   = "8.2GB",
	                       .nodes  = "Text to Image, Edit Image",
	                       .urls   = any_array_create_from_raw(
                               (void *[]){
                                   "https://huggingface.co/leejet/FLUX.2-klein-4B-GGUF/resolve/main/flux-2-klein-4b-Q8_0.gguf",
                                   "https://huggingface.co/black-forest-labs/FLUX.2-small-decoder/resolve/main/full_encoder_small_decoder.safetensors",
                                   "https://huggingface.co/unsloth/Qwen3-4B-GGUF/resolve/main/Qwen3-4B-Q8_0.gguf",
                               },
                               3),
	                       .web     = "https://huggingface.co/leejet/FLUX.2-klein-4B-GGUF",
	                       .license = "apache-2.0"}),

	        GC_ALLOC_INIT(neural_node_model_t,
	                      {.name   = "Qwen Image",
	                       .memory = "13GB",
	                       .size   = "16.9GB",
	                       .nodes  = "Text to Image",
	                       .urls   = any_array_create_from_raw(
                               (void *[]){
                                   "https://huggingface.co/unsloth/Qwen-Image-2512-GGUF/resolve/main/qwen-image-2512-Q4_K_S.gguf",
                                   "https://huggingface.co/QuantStack/Qwen-Image-GGUF/resolve/main/VAE/Qwen_Image-VAE.safetensors",
                                   "https://huggingface.co/unsloth/Qwen2.5-VL-7B-Instruct-GGUF/resolve/main/Qwen2.5-VL-7B-Instruct-Q4_K_S.gguf",
                               },
                               3),
	                       .web     = "https://huggingface.co/unsloth/Qwen-Image-2512-GGUF",
	                       .license = "apache-2.0"}),

	        GC_ALLOC_INIT(neural_node_model_t,
	                      {.name   = "Qwen Image Edit",
	                       .memory = "13GB",
	                       .size   = "18.3GB",
	                       .nodes  = "Edit Image, Inpaint Image, Outpaint Image, Tile Image, Vary Image",
	                       .urls   = any_array_create_from_raw(
                               (void *[]){
                                   "https://huggingface.co/unsloth/Qwen-Image-Edit-2511-GGUF/resolve/main/qwen-image-edit-2511-Q4_K_S.gguf",
                                   "https://huggingface.co/QuantStack/Qwen-Image-GGUF/resolve/main/VAE/Qwen_Image-VAE.safetensors",
                                   "https://huggingface.co/unsloth/Qwen2.5-VL-7B-Instruct-GGUF/resolve/main/Qwen2.5-VL-7B-Instruct-Q4_K_S.gguf",
                                   "https://huggingface.co/unsloth/Qwen2.5-VL-7B-Instruct-GGUF/resolve/main/mmproj-F16.gguf",
                               },
                               4),
	                       .web     = "https://huggingface.co/unsloth/Qwen-Image-Edit-2511-GGUF",
	                       .license = "apache-2.0"}),

	        GC_ALLOC_INIT(neural_node_model_t,
	                      {.name   = "Marigold",
	                       .memory = "6GB",
	                       .size   = "13.7GB",
	                       .nodes  = "Image to Depth, Image to Normal Map Node, Image to PBR",
	                       .urls   = any_array_create_from_raw(
                               (void *[]){
                                   "https://huggingface.co/armory3d/marigold-v1-1-gguf/resolve/main/marigold-depth-v1-1.q8_0.gguf",
                                   "https://huggingface.co/armory3d/marigold-v1-1-gguf/resolve/main/marigold-normals-v1-1.q8_0.gguf",
                                   "https://huggingface.co/armory3d/marigold-v1-1-gguf/resolve/main/marigold-iid-appearance-v1-1.q8_0.gguf",
                                   "https://huggingface.co/armory3d/marigold-v1-1-gguf/resolve/main/marigold-iid-lighting-v1-1.q8_0.gguf",
                               },
                               4),
	                       .web     = "https://huggingface.co/armory3d/marigold-v1-1-gguf",
	                       .license = "openrail"}),

	        GC_ALLOC_INIT(neural_node_model_t, {.name   = "Real-ESRGAN",
	                                            .memory = "1GB",
	                                            .size   = "0.07GB",
	                                            .nodes  = "Upscale Image",
	                                            .urls   = any_array_create_from_raw(
                                                    (void *[]){
                                                        "https://huggingface.co/armory3d/Real-ESRGAN/resolve/main/RealESRGAN_x4plus.pth",
                                                    },
                                                    1),
	                                            .web     = "https://huggingface.co/armory3d/Real-ESRGAN",
	                                            .license = "bsd-3-clause"}),

	        GC_ALLOC_INIT(neural_node_model_t, {.name   = "Hunyuan3D",
	                                            .memory = "12GB",
	                                            .size   = "12.6GB",
	                                            .nodes  = "Image to 3D Mesh",
	                                            .urls   = any_array_create_from_raw(
                                                    (void *[]){
                                                        "https://huggingface.co/armory3d/hunyuan3d21_portable/resolve/main/Hunyuan3D_win64.tar",
                                                    },
                                                    1),
	                                            .web     = "https://huggingface.co/armory3d/hunyuan3d21_portable",
	                                            .license = "hunyuan3d"}),

	        GC_ALLOC_INIT(neural_node_model_t, {.name   = "Qwen",
	                                            .memory = "16GB",
	                                            .size   = "15.7GB",
	                                            .nodes  = "Text to Text, Console",
	                                            .urls   = any_array_create_from_raw(
                                                    (void *[]){
                                                        "https://huggingface.co/unsloth/Qwen3.6-27B-GGUF/resolve/main/Qwen3.6-27B-Q4_K_M.gguf",
                                                        // "https://huggingface.co/unsloth/Qwen3.6-27B-GGUF/resolve/main/mmproj-F16.gguf",
                                                    },
                                                    1),
	                                            .web     = "https://huggingface.co/unsloth/Qwen3.6-27B-GGUF",
	                                            .license = "apache-2.0"}),
	    },
	    9);
	gc_root(neural_node_models);
}
