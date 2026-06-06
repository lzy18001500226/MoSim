from pentestagent.playbooks.base_playbook import BasePlaybook, Phase


class THP3NetworkPlaybook(BasePlaybook):
    name = "thp3_network"
    description = "Network Compromise and Lateral Movement"
    mode = "crew"

    phases = [
        Phase(
            name="Initial Access",
            objective="Gain initial foothold on the network",
            techniques=[
                "Password spraying against external services",
                "Network protocol poisoning attacks",
                "Exploit public-facing vulnerabilities",
                "Phishing and social engineering",
            ],
        ),
        Phase(
            name="Enumeration & Privilege Escalation",
            objective="Map internal network and elevate privileges",
            techniques=[
                "Active Directory and domain enumeration",
                "Identify privilege escalation paths and misconfigurations",
                "Extract credentials from memory and files",
                "Enumerate users, groups, and permissions",
            ],
        ),
        Phase(
            name="Lateral Movement & Objectives",
            objective="Move through network to reach high-value targets",
            techniques=[
                "Lateral movement via remote services",
                "Pass-the-hash and pass-the-ticket attacks",
                "Access high-value targets and data repositories",
            ],
        ),
    ]
