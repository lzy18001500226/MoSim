# Choosing Your Path: UFO² or UFO³ Galaxy?

Not sure which UFO framework to use? This guide will help you make the right choice based on your specific needs.

---

## 🗺️ Quick Decision Tree

Use this interactive flowchart to find the best solution for your use case:


```mermaid
graph TD
    Start[What are you trying to automate?] --> Q1{Involves multiple<br/>devices/platforms?}

    Q1 -->|Yes| Q2{Need parallel<br/>execution across<br/>devices?}
    Q1 -->|No| Q3{Complex multi-app<br/>workflow on Windows?}

    Q2 -->|Yes| Galaxy[✨ Use UFO³ Galaxy]
    Q2 -->|No, sequential| Q4{Can tasks run<br/>independently?}

    Q4 -->|Yes, independent| UFO2_Multi[Use UFO² on each device<br/>separately]
    Q4 -->|No, dependencies| Galaxy

    Q3 -->|Yes| UFO2[🪟 Use UFO²]
    Q3 -->|No, simple task| UFO2

    Q3 -->|Might scale later| Hybrid[Use UFO² now,<br/>Galaxy-ready setup]

    Galaxy --> GalaxyDoc[📖 See Galaxy Quick Start]
    UFO2 --> UFO2Doc[📖 See UFO² Quick Start]
    UFO2_Multi --> UFO2Doc
    Hybrid --> MigrationDoc[📖 See Migration Guide]

    style Galaxy fill:#fff9c4
    style UFO2 fill:#c8e6c9
    style UFO2_Multi fill:#c8e6c9
    style Hybrid fill:#e1bee7

    click GalaxyDoc "./getting_started/quick_start_galaxy.md"
    click UFO2Doc "./getting_started/quick_start_ufo2.md"
    click MigrationDoc "./getting_started/migration_ufo2_to_galaxy.md"
```

---

## 📊 Quick Comparison Matrix

| Dimension | UFO² Desktop AgentOS | UFO³ Galaxy |
|-----------|---------------------|-------------|
| **Target Scope** | Single Windows desktop | Multiple devices (Windows/Linux/macOS) |
| **Best For** | Simple local automation | Complex cross-device workflows |
| **Setup Complexity** | ⭐ Simple | ⭐⭐⭐ Moderate (requires device pool) |
| **Learning Curve** | ⭐⭐ Easy | ⭐⭐⭐⭐ Advanced |
| **Execution Model** | Sequential multi-app | Parallel DAG orchestration |
| **Network Required** | ❌ No | ✅ Yes (WebSocket between devices) |
| **Parallelism** | Within single device | Across multiple devices |
| **Fault Tolerance** | Retry on same device | Retry + task migration |
| **Typical Latency** | 10-30s (local) | 20-60s (includes orchestration) |
| **Ideal Task Count** | 1-5 steps | 5-20+ steps with dependencies |

**Quick Rule of Thumb:**
- **1 device + simple workflow** → UFO²
- **2+ devices OR complex dependencies** → Galaxy
- **Not sure?** → Start with UFO², migrate later ([Migration Guide](./getting_started/migration_ufo2_to_galaxy.md))

---

## 🎯 Scenario-Based Recommendations

### Scenario 1: Desktop Productivity Automation

**Task:** "Create a weekly report: extract data from Excel, generate charts in PowerPoint, send via Outlook"

**Recommendation:** ✅ **UFO²**

**Why:**
- All applications on one Windows desktop
- Sequential workflow (Excel → PowerPoint → Outlook)
- No cross-device dependencies

**Learn More:** [UFO² Overview](./ufo2/overview.md)

---

### Scenario 2: Development Workflow Automation

**Task:** "Clone repo on my laptop, build Docker image on GPU server, run tests on CI cluster, open results on my desktop"

**Recommendation:** ✅ **UFO³ Galaxy**

**Why:**
- Spans 3+ devices (laptop, GPU server, CI cluster, desktop)
- Sequential dependencies (clone → build → test → display)
- Requires device coordination and data transfer

**Learn More:** [Galaxy Overview](./galaxy/overview.md)

---

### Scenario 3: Batch Data Processing

**Task:** "Process 100 files: fetch from cloud, clean data, run ML model, save results"

**Recommendation:** **Depends on setup**

| Setup | Recommendation | Why |
|-------|---------------|-----|
| **Single powerful workstation** | ✅ UFO² | All processing on one machine, simpler |
| **Distributed cluster** | ✅ Galaxy | Parallel processing across nodes, faster |
| **Mix (local + cloud GPU)** | ✅ Galaxy | Heterogeneous resources |

**Learn More:**
- [UFO² for Single Device](./getting_started/quick_start_ufo2.md)
- [Galaxy for Distributed](./getting_started/quick_start_galaxy.md)

---

### Scenario 4: Cross-Platform Testing

**Task:** "Test web app on Windows Chrome, Linux Firefox, and macOS Safari"

**Recommendation:** ✅ **UFO³ Galaxy**

**Why:**
- Requires 3 different OS platforms
- Parallel execution saves time
- Centralized result aggregation

**Learn More:** [Galaxy Multi-Platform Support](./galaxy/overview.md#cross-device-collaboration)

---

### Scenario 5: File Management & Organization

**Task:** "Organize Downloads folder by file type, compress old files, upload to cloud"

**Recommendation:** ✅ **UFO²**

**Why:**
- Single-device local file operations
- No network dependencies
- Simple sequential workflow

**Learn More:** [UFO² Quick Start](./getting_started/quick_start_ufo2.md)

---

### Scenario 6: Multi-Stage Data Pipeline

**Task:** "Collect logs from 5 Linux servers, aggregate on central server, analyze, generate dashboard on Windows"

**Recommendation:** ✅ **UFO³ Galaxy**

**Why:**
- Multiple source devices (5 Linux servers)
- Parallel log collection (5x faster than sequential)
- Cross-platform (Linux → Windows)
- Complex dependency graph

**Learn More:** [Galaxy Task Constellation](./galaxy/constellation/overview.md)

---

### Scenario 7: Learning Agent Development

**Task:** "I'm new to agent development and want to learn by building simple automation"

**Recommendation:** ✅ **UFO²**

**Why:**
- Simpler architecture (easier to understand)
- Faster feedback loop (local execution)
- Comprehensive documentation and examples
- Can upgrade to Galaxy later

**Learn More:** [UFO² Quick Start](./getting_started/quick_start_ufo2.md)

---

### Scenario 8: Enterprise Workflow Integration

**Task:** "Integrate with existing CI/CD pipeline across dev laptops, build servers, and test farms"

**Recommendation:** ✅ **UFO³ Galaxy**

**Why:**
- Enterprise-scale device coordination
- Fault tolerance with automatic recovery
- Formal safety guarantees for correctness
- Supports heterogeneous infrastructure

**Learn More:** [Galaxy Architecture](./galaxy/overview.md#architecture)

---

## 🔀 Hybrid Approaches

You don't have to choose just one! Here are common hybrid patterns:

### Pattern 1: UFO² as Galaxy Device

**Setup:** Run UFO² as a Galaxy device (requires both server and client)

```bash
# Terminal 1: Start UFO² Server on Windows desktop
python -m ufo.server.app --port 5000

# Terminal 2: Start UFO² Client (connect to server)
python -m ufo.client.client --ws --ws-server ws://localhost:5000/ws --client-id my_windows_device --platform windows
```

**Benefits:**
- Keep UFO² for local Windows expertise
- Gain Galaxy's cross-device orchestration
- Best of both worlds

**Learn More:** [UFO² as Galaxy Device](./ufo2/as_galaxy_device.md)

---

### Pattern 2: Gradual Migration

**Strategy:** Start with UFO² for immediate needs, prepare for Galaxy expansion

**Phase 1:** Use UFO² standalone
```bash
python -m ufo --task "Your current task"
```

**Phase 2:** Make UFO² Galaxy-compatible
```yaml
# config/galaxy/devices.yaml (prepare in advance)
devices:
  - device_id: "my_windows"
    server_url: "ws://localhost:5000/ws"  # Where UFO client connects to UFO server
    os: "windows"
    capabilities: ["office", "web"]
```

**Phase 3:** Start UFO device agent and connect to Galaxy
```bash
# Terminal 1: Start UFO Server on your Windows machine
python -m ufo.server.app --port 5000

# Terminal 2: Start UFO Client (connects to UFO server above)
python -m ufo.client.client --ws --ws-server ws://localhost:5000/ws --client-id my_windows --platform windows

# Terminal 3: Start Galaxy (on control machine, can be same or different)
python -m galaxy --request "Cross-device workflow"
```

**Learn More:** [Migration Guide](./getting_started/migration_ufo2_to_galaxy.md)

---

### Pattern 3: Domain-Specific Split

**Strategy:** Use different frameworks for different workflow types

| Workflow Type | Framework | Example |
|--------------|-----------|---------|
| **Daily desktop tasks** | UFO² | Email processing, document creation |
| **Development workflows** | Galaxy | Code build → test → deploy |
| **Data processing** | Galaxy (if distributed) | Multi-node ML training |
| **Quick automation** | UFO² | One-off tasks |

**Learn More:** [When to Use Which](./getting_started/migration_ufo2_to_galaxy.md#when-to-use-which)

---

## 🚫 Common Misconceptions

### Misconception 1: "Galaxy is always better because it's newer"

**Reality:** UFO² is better for simple single-device tasks due to:
- Lower latency (no network overhead)
- Simpler setup and debugging
- Battle-tested stability

**Use Galaxy only when you actually need multi-device orchestration.**

---

### Misconception 2: "I need to rewrite everything to migrate to Galaxy"

**Reality:** UFO² can run as a Galaxy device with minimal changes:
```bash
# Terminal 1: Start UFO Server
python -m ufo.server.app --port 5000

# Terminal 2: Start UFO Client in WebSocket mode
python -m ufo.client.client --ws --ws-server ws://localhost:5000/ws --client-id my_device --platform windows
```

**Learn More:** [Migration Guide](./getting_started/migration_ufo2_to_galaxy.md#option-2-convert-ufo2-instance-to-galaxy-device)

---

### Misconception 3: "Galaxy can't run on a single device"

**Reality:** Galaxy works perfectly on one device if you need:
- DAG-based workflow planning
- Advanced monitoring and trajectory reports
- Preparation for future multi-device expansion

```yaml
# Single-device Galaxy setup
devices:
  - device_id: "localhost"
    server_url: "ws://localhost:5005/ws"
```

---

### Misconception 4: "UFO² is deprecated in favor of Galaxy"

**Reality:** UFO² is actively maintained and recommended for single-device use:
- More efficient for local tasks
- Simpler for beginners
- Core component when used as Galaxy device

**Both frameworks are complementary, not competing.**

---

## 🎓 Learning Paths

### For Beginners

**Week 1-2: Start with UFO²**
1. [UFO² Quick Start](./getting_started/quick_start_ufo2.md)
2. Build simple automation (file management, email, etc.)
3. Understand HostAgent/AppAgent architecture

**Week 3-4: Explore Advanced UFO²**
4. [Hybrid GUI-API Actions](./ufo2/core_features/hybrid_actions.md)
5. [MCP Server Integration](./mcp/overview.md)
6. [Customization & Learning](./ufo2/advanced_usage/customization.md)

**Week 5+: Graduate to Galaxy (if needed)**
7. [Migration Guide](./getting_started/migration_ufo2_to_galaxy.md)
8. [Galaxy Quick Start](./getting_started/quick_start_galaxy.md)
9. Build cross-device workflows

---

### For Experienced Developers

**Direct to Galaxy** if you already know you need multi-device:
1. [Galaxy Quick Start](./getting_started/quick_start_galaxy.md)
2. [Task Constellation Concepts](./galaxy/constellation/overview.md)
3. [ConstellationAgent Deep Dive](./galaxy/constellation_agent/overview.md)
4. [Performance Monitoring](./galaxy/evaluation/performance_metrics.md)

---

## 📋 Decision Checklist

Still unsure? Answer these questions:

**Q1: Does your workflow involve 2+ physical devices?**

- ✅ Yes → **Galaxy**
- ❌ No → Continue to Q2

**Q2: Do you need parallel execution across different machines?**

- ✅ Yes → **Galaxy**
- ❌ No → Continue to Q3

**Q3: Does your workflow have complex dependencies (DAG structure)?**

- ✅ Yes, complex DAG → **Galaxy**
- ❌ No, simple sequence → Continue to Q4

**Q4: Are you comfortable with distributed systems concepts?**

- ✅ Yes → **Galaxy** (if any of Q1-Q3 is yes)
- ❌ No → **UFO²** (learn basics first)

**Q5: Do you need cross-platform support (Windows + Linux)?**

- ✅ Yes → **Galaxy**
- ❌ No, Windows only → **UFO²**

---

**Result:**

- **3+ "Galaxy" answers** → Use Galaxy ([Quick Start](./getting_started/quick_start_galaxy.md))
- **Mostly "UFO²" answers** → Use UFO² ([Quick Start](./getting_started/quick_start_ufo2.md))
- **Mixed answers** → Start with UFO², keep Galaxy option open ([Migration Guide](./getting_started/migration_ufo2_to_galaxy.md))

---

## 🔗 Next Steps

### If you chose UFO²:
1. 📖 [UFO² Quick Start Guide](./getting_started/quick_start_ufo2.md)
2. 🎯 [UFO² Overview & Architecture](./ufo2/overview.md)
3. 🛠️ [Configuration Guide](./configuration/system/overview.md)

### If you chose Galaxy:
1. 📖 [Galaxy Quick Start Guide](./getting_started/quick_start_galaxy.md)
2. 🎯 [Galaxy Overview & Architecture](./galaxy/overview.md)
3. 🌟 [Task Constellation Concepts](./galaxy/constellation/overview.md)

### If you're still exploring:
1. 📊 [Detailed Comparison](./getting_started/migration_ufo2_to_galaxy.md#when-to-use-which)
2. 🎬 [Demo Video](https://www.youtube.com/watch?v=QT_OhygMVXU)
3. 📄 [Research Paper](https://arxiv.org/abs/2504.14603)

---

## 💡 Pro Tips

!!! tip "Start Simple"
    When in doubt, start with **UFO²**. It's easier to scale up to Galaxy later than to debug a complex Galaxy setup when you don't need it.

!!! tip "Hybrid is Valid"
    Don't feel locked into one choice. You can use **UFO² for local tasks** and **Galaxy for cross-device workflows** simultaneously.

!!! tip "Test Before Committing"
    Try both for a simple workflow to see which feels more natural for your use case:
    ```bash
    # UFO² test
    python -m ufo --task "Create test report"

    # Galaxy test
    python -m galaxy --request "Create test report"
    ```

!!! warning "Network Requirements"
    Galaxy requires **stable network connectivity** between devices. If your environment has network restrictions, UFO² might be more reliable.

---

## 🤝 Getting Help

- **Documentation:** [https://microsoft.github.io/UFO/](https://microsoft.github.io/UFO/)
- **GitHub Issues:** [https://github.com/microsoft/UFO/issues](https://github.com/microsoft/UFO/issues)
- **Discussions:** [https://github.com/microsoft/UFO/discussions](https://github.com/microsoft/UFO/discussions)

Still have questions? Check the [Migration FAQ](./getting_started/migration_ufo2_to_galaxy.md#getting-help) or open a discussion on GitHub!
