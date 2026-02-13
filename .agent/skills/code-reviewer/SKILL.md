---
name: code-reviewer
description: expert code review and optimization assistant. Use this skill to review code for efficiency, readability, security, and best practices. It provides actionable feedback and optimized code snippets.
---

# Code Reviewer Skill

This skill provides expert code review and optimization capabilities.

## When to Use

Use this skill when:
- You have written code and want to ensure it is efficient and follows best practices.
- You want to identify potential bugs or security vulnerabilities.
- You need to optimize existing code for better performance.
- You want to improve the readability and maintainability of code.

## Workflow

1.  **Analyze the Code**: Read the code carefully to understand its functionality and logic.
2.  **Identify Issues**: Look for:
    -   **Inefficiencies**: O(n^2) loops where O(n) is possible, redundant calculations, memory leaks.
    -   **Anti-patterns**: Global variables, magic numbers, lack of error handling.
    -   **Security Risks**: SQL injection, XSS, unvalidated input.
    -   **Style Violations**: Inconsistent naming, poor formatting (though linters handle this, you can spot logical style issues).
3.  **Provide Feedback**:
    -   Be specific and constructive.
    -   Explain *why* a change is recommended.
    -   Rate the severity of the issue (Critical, Major, Minor).
4.  **Optimize**:
    -   Provide refactored code snippets that address the identified issues.
    -   Ensure the optimized code maintains the original functionality (unless the functionality itself was buggy).

## Guidelines

-   **Performance First**: Prioritize algorithmic efficiency and resource usage.
-   **Readability Matters**: Clean code is easier to maintain and less prone to bugs.
-   **Security is Paramount**: Never overlook potential security holes.
-   **Context Aware**: Consider the specific constraints and environment of the project (e.g., embedded system vs. cloud server).

## Example Usage

**Request:** "Review this Python function for efficiency."

**Response:**
"The function uses a nested loop to find duplicates, resulting in O(n^2) complexity.
**Recommendation:** Use a set to track seen elements for O(n) complexity.
**Optimized Code:**
```python
def find_duplicates(items):
    seen = set()
    duplicates = []
    for item in items:
        if item in seen:
            duplicates.append(item)
        else:
            seen.add(item)
    return duplicates
```"
