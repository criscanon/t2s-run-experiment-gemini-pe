# Function to classify SQLite errors
def classify_sqlite_error(error_message):
    
    # Check for the specific "No error." message
    if "No error." in error_message:
        return "No error."

    # Common syntax errors
    syntax_errors = [
        "syntax error",
        "near",
        "incomplete input"
    ]

    # Common semantic errors
    semantic_errors = [
        "no such table",
        "no such column",
        "datatype mismatch",
        "unique constraint failed",
        "foreign key constraint failed",
        "check constraint failed",
        "ambiguous column name"
    ]

    # Convert the error message to lowercase for comparison
    error_message = error_message.lower()

    # Check if the error is syntactic
    for syntax_error in syntax_errors:
        if syntax_error in error_message:
            return "Syntactic"

    # Check if the error is semantic
    for semantic_error in semantic_errors:
        if semantic_error in error_message:
            return "Semantic"

    # If the error type is not recognized
    return "Unknown"