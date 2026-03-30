"""MLX-based embedding function for ChromaDB on Apple Silicon."""

from chromadb.api.types import Documents, EmbeddingFunction, Embeddings


class MLXEmbeddingFunction(EmbeddingFunction[Documents]):
    """Embedding function using MLX for Apple Silicon GPU acceleration.

    Uses all-MiniLM-L6-v2 (4-bit quantized) via mlx-embeddings.
    ~90x faster than ChromaDB's default ONNX CPU embeddings on Apple Silicon.
    """

    def __init__(self, model_name: str = "mlx-community/all-MiniLM-L6-v2-4bit"):
        from mlx_embeddings.utils import load
        self._model, self._tokenizer = load(model_name)

    def __call__(self, input: Documents) -> Embeddings:
        import mlx.core as mx
        inputs = self._tokenizer(
            list(input), return_tensors="mlx",
            padding=True, truncation=True, max_length=512,
        )
        outputs = self._model(**inputs)
        mx.eval(outputs.text_embeds)
        return outputs.text_embeds.tolist()


def get_embedding_function() -> EmbeddingFunction:
    """Get the best available embedding function.

    Uses MLX on Apple Silicon, falls back to ChromaDB's default ONNX on other platforms.
    """
    try:
        return MLXEmbeddingFunction()
    except (ImportError, RuntimeError):
        # MLX not available (Linux, non-ARM Mac) — use ChromaDB default
        from chromadb.utils.embedding_functions import ONNXMiniLM_L6_V2
        return ONNXMiniLM_L6_V2()
