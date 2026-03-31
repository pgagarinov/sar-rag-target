"""MLX-based embedding function for Apple Silicon, with sentence-transformers fallback."""

from typing import Protocol


class EmbeddingFunction(Protocol):
    def __call__(self, input: list[str]) -> list[list[float]]: ...


class MLXEmbeddingFunction:
    """Embedding function using MLX for Apple Silicon GPU acceleration.

    Uses all-MiniLM-L6-v2 (4-bit quantized) via mlx-embeddings.
    Clears Metal cache after each call to prevent memory accumulation.
    """

    def __init__(self, model_name: str = "mlx-community/all-MiniLM-L6-v2-4bit"):
        from mlx_embeddings.utils import load
        self._model, self._tokenizer = load(model_name)

    def __call__(self, input: list[str]) -> list[list[float]]:
        import mlx.core as mx
        inputs = self._tokenizer(
            list(input), return_tensors="mlx",
            padding=True, truncation=True, max_length=512,
        )
        outputs = self._model(**inputs)
        mx.eval(outputs.text_embeds)
        result = outputs.text_embeds.tolist()

        # Release MLX tensors and Metal GPU cache to prevent accumulation
        del inputs, outputs
        mx.clear_cache()

        return result


def get_embedding_function() -> EmbeddingFunction:
    """Get the best available embedding function.

    Uses MLX on Apple Silicon, falls back to sentence-transformers on other platforms.
    """
    try:
        return MLXEmbeddingFunction()
    except (ImportError, RuntimeError):
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer("all-MiniLM-L6-v2")
        return lambda input: model.encode(input).tolist()
