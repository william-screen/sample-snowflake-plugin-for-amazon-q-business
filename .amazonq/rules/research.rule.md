# Research

## Purpose
This rule ensures thorough research using the FETCH tool with Google search before moving to another issue or giving up on a problem.

## Instructions
- MUST use FETCH tool with Google search to find answers before declaring something impossible or moving to another issue (ID: GOOGLE_SEARCH_FIRST)
- ALWAYS search for "site:docs.aws.amazon.com [your query]" for AWS-specific documentation (ID: AWS_DOCS_SEARCH)
- MUST search for "site:github.com [package name] examples" for code examples and usage patterns (ID: GITHUB_EXAMPLES_SEARCH)
- ALWAYS search for "[error message] solution" when encountering build or runtime errors (ID: ERROR_SOLUTION_SEARCH)
- MUST search for "[package name] typescript interface" when dealing with TypeScript type errors (ID: TYPESCRIPT_INTERFACE_SEARCH)
- NEVER move to another issue without first researching the current problem thoroughly (ID: NO_ISSUE_SWITCHING)
- ALWAYS provide the Google search URL used in your research for transparency (ID: SHOW_SEARCH_URL)
- MUST try at least 3 different search queries before considering a problem unsolvable (ID: MULTIPLE_SEARCH_ATTEMPTS)
- NEVER simplify or remove functionality as a first step - ALWAYS research existing solutions on GitHub first (ID: NO_SIMPLIFY_FIRST)
- MUST search "site:github.com [library name] [specific feature]" to find working examples before modifying code (ID: GITHUB_SOLUTION_FIRST)

## Priority
Critical

## Error Handling
- If FETCH tool fails, try alternative search terms and retry
- If Google search returns no results, try searching Stack Overflow or official documentation sites
- If research doesn't solve the problem, document what was searched and why it didn't work
- Never abandon a problem without exhaustive research using multiple search strategies
- Never simplify code without first finding examples of the correct implementation
