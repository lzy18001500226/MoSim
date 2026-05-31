task_id: COAGENT-MINILOOP-04
conversation_title: MoSim｜候选测试闭环
role: candidate_visible_worker_repair
working_directory: /mnt/c/Users/HP/Desktop/MoSim
result_file: Results/coagent_miniloop/COAGENT-MINILOOP-04/worker_result_packet.json

Objective:
Repair the candidate result packet so it satisfies the existing CoAgent result
router schema.

Instructions:
1. Edit only:
   Results/coagent_miniloop/COAGENT-MINILOOP-04/worker_result_packet.json
2. Add a top-level `summary` field with a short Chinese summary.
3. Keep the existing task_id, status, owner, evidence, forbidden action flags,
   and next_recommended_action.
4. Do not run Git, MCP, or any broad file scan.
5. Stop after writing the repaired JSON.
