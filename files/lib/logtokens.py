"""
Simple library to show token usage.
Usage:
    logTokens (completion, source, model), where:
        completion = object returned by OpenAPI,
        source = the function which was invoking the prompt (for statistical purposes),
        model = model name to estimate the price
"""

def logTokens(completion, source, model):
    pricing = {
        "gpt-4o": {
            "input": 250,
            "output": 1000
        },
        "gpt-4o-2024-08-06": {
            "input": 250,
            "output": 1000
        },
        "gpt-4o-2024-05-13": {
            "input": 500,
            "output": 1500
        },
        "gpt-4o-mini": {
            "input": 15,
            "output": 60
        },
        "gpt-4o-mini-2024-07-18": {
            "input": 15,
            "output": 60
        },
        "o1-preview": {
            "input": 1500,
            "output": 6000
        },
        "o1-preview-2024-09-12": {
            "input": 1500,
            "output": 6000
        },
        "o1-mini": {
            "input": 300,
            "output": 1200
        },
        "o1-mini-2024-09-12": {
            "input": 300,
            "output": 1200
        }
    }
    input_tokens = completion.usage.prompt_tokens
    output_tokens = completion.usage.completion_tokens
    input_pricing = pricing[model]["input"] if model in pricing else 0
    output_pricing = pricing[model]["output"] if model in pricing else 0
    input_tokens = completion.usage.prompt_tokens
    output_tokens = completion.usage.completion_tokens
    input_price = input_tokens * input_pricing / 1000000
    output_price = output_tokens * output_pricing / 1000000
    print (f".... prompt from \"{source}\" used {input_tokens} (in) + {output_tokens} (out) tokens for {input_price:.4f} + {output_price:.4f} = {(input_price+output_price):.4f} cents.")
