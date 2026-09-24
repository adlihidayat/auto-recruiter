import os
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

def download_and_export():
    target_dir = os.getenv("ONNX_INJECTION_MODEL_DIR", "/app/assets/onnx_model")
    os.makedirs(target_dir, exist_ok=True)
    
    model_id = "deepset/deberta-v3-base-injection"
    print(f"Downloading {model_id} and exporting to {target_dir}...")
    
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForSequenceClassification.from_pretrained(model_id)
    
    # Generate dummy inputs for ONNX tracing
    dummy_inputs = tokenizer("This is a test of the injection system.", return_tensors="pt")
    input_names = list(dummy_inputs.keys())
    inputs = tuple(dummy_inputs.values())
    
    dynamic_axes = {name: {0: "batch_size", 1: "sequence_length"} for name in input_names}
    dynamic_axes["logits"] = {0: "batch_size"}
    
    onnx_path = os.path.join(target_dir, "model.onnx")
    
    # Export using native PyTorch ONNX exporter
    torch.onnx.export(
        model,
        inputs,
        onnx_path,
        input_names=input_names,
        output_names=["logits"],
        dynamic_axes=dynamic_axes,
        opset_version=14,
    )
    
    tokenizer.save_pretrained(target_dir)
    print("Download and native ONNX export complete.")

if __name__ == "__main__":
    download_and_export()
