#!/bin/bash
# Agor Process Cleanup Script
# Kills orphaned Node/tsx/Vite processes

echo "🧹 Cleaning up Agor processes..."

# Kill orphaned Vite processes (not in current terminal)
ORPHANED_VITE=$(ps aux | grep 'vite/bin/vite' | grep -v grep | grep '??' | awk '{print $2}')
if [ -n "$ORPHANED_VITE" ]; then
  echo "Found orphaned Vite processes: $ORPHANED_VITE"
  echo "$ORPHANED_VITE" | xargs kill 2>/dev/null
  echo "✓ Killed orphaned Vite processes"
fi

# Kill orphaned tsx processes (PPID=1)
ORPHANED_TSX=$(ps -ef | grep 'tsx watch' | grep -v grep | awk '$3==1 {print $2}')
if [ -n "$ORPHANED_TSX" ]; then
  echo "Found orphaned tsx processes: $ORPHANED_TSX"
  echo "$ORPHANED_TSX" | xargs kill 2>/dev/null
  echo "✓ Killed orphaned tsx processes"
fi

# Kill orphaned tsup processes (PPID=1)
ORPHANED_TSUP=$(ps -ef | grep 'tsup.*watch' | grep -v grep | awk '$3==1 {print $2}')
if [ -n "$ORPHANED_TSUP" ]; then
  echo "Found orphaned tsup processes: $ORPHANED_TSUP"
  echo "$ORPHANED_TSUP" | xargs kill 2>/dev/null
  echo "✓ Killed orphaned tsup processes"
fi

# Kill processes on specific ports if stuck
for PORT in 3030 5173 6006; do
  PID=$(lsof -ti:$PORT 2>/dev/null)
  if [ -n "$PID" ]; then
    echo "Found process on port $PORT: $PID"
    kill $PID 2>/dev/null
    echo "✓ Killed process on port $PORT"
  fi
done

echo "✅ Cleanup complete!"
