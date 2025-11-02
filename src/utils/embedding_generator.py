import torch
from sentence_transformers import SentenceTransformer

# Determine if GPU is available and set the device
device = 'cuda' if torch.cuda.is_available() else 'cpu'
print(f"Using device: {device}")

# Load the pre-trained sentence transformer model
# 'all-MiniLM-L6-v2' is a good general-purpose model
model = SentenceTransformer('all-MiniLM-L6-v2', device=device)

def generate_embeddings(texts):
    """
    Generates sentence embeddings for a given text or list of texts.

    Args:
        texts (str or list[str]): The text or list of texts to encode.

    Returns:
        numpy.ndarray: A 2D numpy array of embeddings, where each row corresponds
                       to the embedding of a text.
    """
    if isinstance(texts, str):
        texts = [texts]

    # Encode the texts to get embeddings
    embeddings = model.encode(texts, convert_to_tensor=False) # convert_to_tensor=False returns numpy array

    return embeddings

