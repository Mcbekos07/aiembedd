# Token Budgeting

## Budget model
`global_max_context`
- `reserved_output_budget`
- `reserved_system_prompt_budget`
- `reserved_tool_action_budget`
= `available_retrieval_budget`

## Modes
- quick_diagnosis
- deep_build_fix
- runtime_analysis
- refactor_task
- architecture_task

## Packing priority
1. task_instruction
2. critical_log
3. code_fragment
4. active_memory
5. warm_memory
6. git_history

## Truncation policies
- trim low-rank/lower-priority fragments first
- compact history and warm memory blocks
- keep file path + snippet for large code fragments
- never send full raw logs by default
