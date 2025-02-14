AZURE_CONNECTION_STRING = "<<connection_string>>"

SQLITE_QUEUE_PATH = "."

# Palavras proibidas para censura
FORBIDDEN_WORDS = ["palavrão1", "palavrão2"]

# Workflow
WORKFLOW_CONFIG = {
    "start": "filter_text",
    "filter_text": "sentiment_analysis",
    "sentiment_analysis": {
        "positive": "markdown_converter",
        "neutral": "markdown_converter",
        "negative": "spell_check"
    },
    "spell_check": "markdown_converter",
    "markdown_converter": "done"
}