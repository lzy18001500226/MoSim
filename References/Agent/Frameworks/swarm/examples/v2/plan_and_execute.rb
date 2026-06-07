#!/usr/bin/env ruby
# frozen_string_literal: true

require "swarm_sdk"

# Example: Plan and Execute Pattern
# Two nodes, one agent - first node plans, second node executes the plan

swarm = SwarmSDK.build do
  name("Plan and Execute")

  # Define a single agent that will be used in both nodes
  agent(:assistant) do
    description("A versatile assistant that can plan and execute tasks")
    provider(:openai)
    model("gpt-5")
    coding_agent(false)

    system_prompt(<<~PROMPT)
      You are a helpful assistant who can both plan and execute tasks.

      When planning, you should:
      - Break down the task into clear, actionable steps
      - Identify any dependencies or prerequisites
      - Consider potential challenges

      When executing, you should:
      - Follow the plan carefully
      - Use available tools effectively
      - Report on progress and completion
    PROMPT

    # Give the assistant tools for execution
    disable_default_tools(true)
  end

  # Node 1: Planning stage
  # The agent receives the original input and creates a plan
  node(:planning) do
    # Use the assistant agent in planning mode (fresh context)
    agent(:assistant)

    # Transform input for planning
    #
    # NOTE: Input/output blocks are automatically converted to lambdas,
    # which means you can use `return` safely for early exits!
    #
    # Example of using return for conditional skip:
    # return ctx.skip_execution(content: "cached result") if cached
    input do |ctx|
      <<~INPUT
        Please create a detailed plan for the following task:

        #{ctx.original_prompt}

        Your plan should:
        1. Break down the task into specific steps
        2. Identify what needs to be done first
        3. List any tools or resources needed
        4. Be clear and actionable

        Output your plan in a structured format.
      INPUT
    end

    # Transform output to extract key information
    output do |ctx|
      # Save the plan to a file for reference
      File.write("plan.txt", ctx.content)

      # Pass the plan to the next node
      <<~OUTPUT
        PLAN CREATED:
        #{ctx.content}

        Now execute this plan step by step.
      OUTPUT
    end
  end

  # Node 2: Execution stage
  # The agent receives the plan and executes it
  node(:implementation) do
    # Depends on planning node
    depends_on(:planning)

    # Use the assistant agent in execution mode (fresh context)
    agent(:assistant)

    # Transform input to provide context from planning
    input do |ctx|
      plan = ctx.all_results[:planning].content

      <<~INPUT
        You previously created the following plan:

        #{plan}

        Now execute this plan. Use the available tools (Write, Edit, Bash) to complete each step.
        Report on what you accomplished.
      INPUT
    end

    # Output transformer for final results
    output do |ctx|
      <<~OUTPUT
        EXECUTION COMPLETE

        #{ctx.content}

        Plan reference: #{File.exist?("plan.txt") ? "Saved in plan.txt" : "Not saved"}
      OUTPUT
    end
  end

  # Set the starting node
  start_node(:planning)
end

# Execute the swarm
if __FILE__ == $PROGRAM_NAME
  # Example task
  task = "Create a simple Ruby script that reads a CSV file and outputs a summary"

  puts "Starting Plan and Execute swarm..."
  puts "Task: #{task}"
  puts "\n" + "=" * 80 + "\n"

  result = swarm.execute(task) do |log|
    # Optional: Log events as they happen
    case log[:type]
    when "node_start"
      puts "\n🔵 Starting node: #{log[:node]}"
    when "node_complete"
      puts "✅ Completed node: #{log[:node]} (#{log[:duration].round(2)}s)"
    when "tool_call"
      puts "  🔧 Tool: #{log[:tool]}"
    end
  end

  puts "\n" + "=" * 80 + "\n"

  if result.success?
    puts "✅ Swarm execution successful!\n\n"
    puts result.content
    puts "\n" + "-" * 80
    puts "Stats:"
    puts "  Duration: #{result.duration.round(2)}s"
    puts "  Total cost: $#{result.total_cost.round(4)}"
    puts "  Total tokens: #{result.total_tokens}"
    puts "  Agents involved: #{result.agents_involved.join(", ")}"
  else
    puts "❌ Swarm execution failed!"
    puts "Error: #{result.error.message}"
    puts result.error.backtrace.first(5).join("\n")
  end
end
