"""
Simple library to show token usage.
Usage:
    tokens = UsedTokens (False)  # Creates tokens logging object; quiet=False makes it print each usage immediately
    tokens.log (completion, model, source="")  # 
        completion = object returned by OpenAPI,
        source = the function which was invoking the prompt (for statistical purposes),
        model = model name to estimate the price
"""

class UsedTokens:
    quiet = True
    total_in_tokens = 0
    total_out_tokens = 0
    total_in_price = 0
    total_out_price = 0
    def __init__(self, quiet=True):
        self.quiet=quiet
    # Pricing contains information about input and output price in cents per 1M tokens
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
    def log(self, completion, source=""):
        in_tokens = completion.usage.prompt_tokens
        out_tokens = completion.usage.completion_tokens
        self.total_in_tokens += in_tokens
        self.total_out_tokens += out_tokens
        model = completion.model
        in_pricing = self.pricing[model]["input"] if model in self.pricing else 0
        out_pricing = self.pricing[model]["output"] if model in self.pricing else 0
        in_price = in_tokens * in_pricing / 1000000
        out_price = out_tokens * out_pricing / 1000000
        self.total_in_price += in_price
        self.total_out_price += out_price
        if not self.quiet:
            print (f".... prompt from \"{source}\" used {in_tokens} (in) + {out_tokens} (out) tokens for {in_price:.4f} + {out_price:.4f} = {(in_price+out_price):.4f} cents.")
    def print(self):
        in_tokens = self.total_in_tokens
        out_tokens = self.total_out_tokens
        in_price = self.total_in_price
        out_price = self.total_out_price
        print (f"\nThe program used total {in_tokens} (in) + {out_tokens} (out) tokens for {in_price:.4f} + {out_price:.4f} = {(in_price+out_price):.4f} cents.")
    def cost(self):
        return self.total_in_price + self.total_out_price
