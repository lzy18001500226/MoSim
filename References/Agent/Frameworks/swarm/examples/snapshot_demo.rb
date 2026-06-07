#!/usr/bin/env ruby
# frozen_string_literal: true

# Demo of SwarmSDK Snapshot/Restore functionality
#
# This example demonstrates:
# 1. Creating a swarm and executing tasks
# 2. Creating a snapshot object
# 3. Saving snapshot to file
# 4. Loading snapshot from file
# 5. Restoring into a new swarm instance

require "bundler/setup"
require "swarm_sdk"

# Set dummy API key for demo (agents won't actually call LLM)
ENV["OPENAI_API_KEY"] = "test-key"

puts "=== SwarmSDK Snapshot/Restore Demo ===\n\n"

# Create a simple swarm
puts "1. Creating swarm..."
swarm = SwarmSDK.build do
  name("Demo Team")
  lead(:assistant)

  agent(:assistant) do
    provider("openai")
    model("claude-haiku-4-5")
    base_url("https://api.example.com/v1")
    description("Helpful assistant")
    system_prompt("You are a helpful assistant")
    tools(:Think)
  end
end

puts "   ✓ Swarm created\n\n"

# Execute a task (simulated with direct message for demo)
puts "2. Adding conversation history..."
# Simulate a conversation by accessing the agent and adding messages manually
assistant_agent = swarm.agent(:assistant)
assistant_agent.messages << RubyLLM::Message.new(
  role: :user,
  content: "Hello! Can you help me with Ruby development?",
)
assistant_agent.messages << RubyLLM::Message.new(
  role: :assistant,
  content: "Of course! I'd be happy to help with Ruby development. What do you need?",
)

puts "   ✓ Conversation history added (#{assistant_agent.messages.size} messages)\n\n"

# Create snapshot
puts "3. Creating snapshot..."
snapshot = swarm.snapshot

puts "   ✓ Snapshot created"
puts "   - Type: #{snapshot.type}"
puts "   - Version: #{snapshot.version}"
puts "   - Created at: #{snapshot.snapshot_at}"
puts "   - Agents: #{snapshot.agent_names.join(", ")}\n\n"

# Save to file
puts "4. Saving snapshot to file..."
snapshot_path = "/tmp/swarm_demo_snapshot.json"
snapshot.write_to_file(snapshot_path)

puts "   ✓ Snapshot saved to: #{snapshot_path}\n\n"

# Create a new swarm (same config)
puts "5. Creating new swarm instance (simulating new process)..."
swarm2 = SwarmSDK.build do
  name("Demo Team")
  lead(:assistant)

  agent(:assistant) do
    provider("openai")
    model("claude-haiku-4-5")
    base_url("https://api.example.com/v1")
    description("Helpful assistant")
    system_prompt("You are a helpful assistant")
    tools(:Think)
  end
end

puts "   ✓ New swarm created (conversation is empty)\n\n"

# Load snapshot from file
puts "6. Loading snapshot from file..."
loaded_snapshot = SwarmSDK::Snapshot.from_file(snapshot_path)

puts "   ✓ Snapshot loaded\n\n"

# Restore into new swarm
puts "7. Restoring conversation state..."
result = swarm2.restore(loaded_snapshot)

if result.success?
  puts "   ✓ Restore successful!"
  puts "   - All agents restored\n\n"
else
  puts "   ⚠ Partial restore"
  puts "   - #{result.summary}\n\n"
end

# Verify restoration
puts "8. Verifying restoration..."
assistant2 = swarm2.agent(:assistant)
puts "   ✓ Agent has #{assistant2.messages.size} messages (should be 3)"
assistant2.messages.each_with_index do |msg, i|
  content_preview = msg.content.to_s[0..50]
  puts "   - Message #{i + 1} [#{msg.role}]: #{content_preview}..."
end
puts

# Cleanup
File.delete(snapshot_path) if File.exist?(snapshot_path)
puts "=== Demo Complete ===\n"
