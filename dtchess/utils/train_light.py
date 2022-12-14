import torch as t
import datasets
from torch.utils.data import DataLoader
from dtchess.models.gpt import create_model
from dtchess.utils.utils import cuda_stats

device = "cuda" if t.cuda.is_available() else "cpu"


def prep():
    model, tokeniser = create_model("gpt2")
    dataset = datasets.load_dataset(
        "inwaves/dtchess-standard", streaming=True, split="train"
    )

    input_ids = dataset.map(
        lambda seq: tokeniser(
            seq["text"],
            padding="max_length",
            max_length=model.transformer.wpe.num_embeddings,
            truncation=True,
            return_tensors="pt",
        ),
        batched=True,
    )
    train_dl = DataLoader(input_ids, batch_size=8)

    return train_dl, tokeniser, model


def one_fwd_pass(train_dl, tokeniser, model):
    print(f"CUDA stats before fwd pass: {cuda_stats()}")
    one_batch = next(iter(train_dl))["input_ids"].squeeze().to(device)

    with t.inference_mode():
        logits = model(one_batch).logits
        print(f"CUDA stats after fwd pass: {cuda_stats()}")

    # del logits
    # t.cuda.empty_cache()
    print(f"CUDA stats after deleting outputs: {cuda_stats()}")


if __name__ == "__main__":
    one_fwd_pass(*prep())
