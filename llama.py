# import requests
# import torch
# from PIL import Image
# from transformers import MllamaForConditionalGeneration, AutoProcessor

# model_id = "unsloth/Llama-3.2-11B-Vision-Instruct"
# hf_token="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"
# model = MllamaForConditionalGeneration.from_pretrained(
#     model_id, torch_dtype=torch.bfloat16, device_map="auto", use_auth_token=hf_token
# )
# prvcessor = AutoProcessor.from_pretrained(model_id)

# url = "https://huggingface.co/datasets/huggingface/documentation-images/resolve/0052a70beed5bf71b92610a43a52df6d286cd5f3/diffusers/rabbit.jpg"
# image = Image.open(requests.get(url, stream=True).raw)

# messages = [
#     {
#         "role": "user",
#         "content": [
#             {"type": "image"},
#             {
#                 "type": "text",
#                 "text": "If I had to write a haiku for this one, it would be: ",
#             },
#         ],
#     }
# ]
# input_text = processor.apply_chat_template(messages, add_generation_prompt=True)
# inputs = processor(image, input_text, add_special_tokens=False, return_tensors="pt").to(
#     model.device
# )

# output = model.generate(**inputs, max_new_tokens=30)
# print(processor.decode(output[0]))

!huggingface-cli login

# Install Unsloth (if not already installed)
!pip install git+https://github.com/huggingface/transformers
!pip install "unsloth [colab-new] @ git+https://github.com/unslothai/unsloth.git"
!pip install xformers "trl<0.9.0" peft accelerate bitsandbytes datasets
# !pip uninstall transformers
# !pip install git+https://github.com/huggingface/transformers


from datasets import load_dataset


# Import required libraries
import requests
import torch
from PIL import Image
from transformers import MllamaForConditionalGeneration, AutoProcessor,BitsAndBytesConfig
import unsloth

# Clear unused CUDA memory
torch.cuda.empty_cache()
torch.cuda.memory_summary(device=None, abbreviated=False)

# Define model ID
model_id = "unsloth/Llama-3.2-11B-Vision-Instruct"

prompt= """Create a Food Report based on the provided Image. Only return the report with Food Quality rated 0 to 1 and Edible in boolean. The description should be Professional and for a better for user experience.
"""

system_message = "You are an Food Inspection Officer who assigns the quality."

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True, bnb_4bit_use_double_quant=True, bnb_4bit_quant_type="nf4", bnb_4bit_compute_dtype=torch.bfloat16
)

# Load model with Unsloth for optimized execution
# with unsloth.optimize():
model = MllamaForConditionalGeneration.from_pretrained(
       model_id, torch_dtype=torch.float16, device_map="auto",
    quantization_config=bnb_config

)
model.gradient_checkpointing_enable()

# Load the processor
processor = AutoProcessor.from_pretrained(model_id)

# Download and load the image

!pip install pillow
from PIL import Image
import requests
url = "https://files.catbox.moe/rykgsb.jpeg"
image = Image.open(requests.get(url, stream=True).raw)
def format_data(sample):
    return {"messages": [
                {
                    "role": "system",
                    "content": [{"type": "text", "text": system_message}],
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "image": sample["image"],
                        }
                    ],
                },
                {
                    "role": "assistant",
                    "content": [{"type": "text", "type": sample["label"]}],
                },
            ],
        }
dataset_id = "rajistics/indian_food_images"
dataset = load_dataset("rajistics/indian_food_images",split="test")
dataset = [format_data(sample) for sample in dataset]

print(dataset[345]["messages"])


