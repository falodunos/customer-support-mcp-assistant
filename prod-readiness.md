## production-readiness features:

1. Configuration & secrets
.env.example
Strict environment validation
No secrets in GitHub
Separate local/staging/production configs
2. Input validation
Validate customer_id
Validate order_id
Validate empty/unsafe questions
Limit question length
3. Tool safety
Allowlist tool names
Validate tool arguments against schema
Block unknown tool calls
Limit max tools per request
Prevent repeated/looping tool calls
4. Error handling
Graceful MCP server failure response
Graceful LLM failure response
User-friendly error messages
Internal error logging
5. Timeout control
Timeout for MCP tool discovery
Timeout for MCP tool execution
Timeout for LLM calls
Overall request timeout
6. Retry policy
Retry transient MCP failures
Retry transient LLM/API failures
Use bounded retries only
Avoid retrying invalid requests
7. Logging
Structured logs
Log request lifecycle
Log selected tools
Log MCP execution status
Log errors without exposing secrets
8. Observability
Request IDs
Tool execution duration
LLM response duration
Success/failure metrics
Basic health endpoint or status page
9. Security
Do not expose raw secrets
Avoid logging sensitive customer data
Add basic auth or protected access for demo app
Sanitize displayed tool outputs
Restrict CORS if you later expose an API
10. Guardrails
Prompt-injection warning in planner prompt
Planner must only use discovered tools
Final answer must only use MCP tool results
Reject unsupported actions
Human escalation path
11. Reliability
Start MCP server consistently
Handle missing MCP tools
Handle malformed tool responses
Handle empty tool results
Add fallback message when no tool is relevant
12. Testing
Unit tests for tool planner parsing
Unit tests for MCP client validation
Unit tests for service orchestration
Mock LLM responses
Mock MCP tool responses
13. Deployment readiness
README.md
Render build/start commands
.gitignore
pyproject.toml
uv.lock
Environment variable checklist
Smoke test instructions
14. UX polish
Loading spinner
Clear error messages
Show selected MCP tools
Show tool outputs in expandable sections
Sidebar with sample IDs
Clear business problem statement on the app page
15. Documentation
Architecture diagram
MCP flow explanation
Tool catalogue
Local setup guide
Deployment guide
Video/demo script

---
# For your assessment, the highest-impact features to implement are:
1. input validation
2. tool discovery + dynamic execution
3. tool allowlist / unknown-tool blocking
4. timeouts
5. retries
6. structured logging
7. graceful error handling
8. clean README + deployment guide