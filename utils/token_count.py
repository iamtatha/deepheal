import tiktoken

def count_tokens(text: str, model: str = "gpt-4o-mini") -> int:
    # Load the tokenizer for the model
    encoding = tiktoken.encoding_for_model(model)
    # Encode text into tokens
    tokens = encoding.encode(text)
    return len(tokens)