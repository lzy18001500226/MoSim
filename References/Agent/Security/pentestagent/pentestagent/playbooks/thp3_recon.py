from pentestagent.playbooks.base_playbook import BasePlaybook, Phase


class THP3ReconPlaybook(BasePlaybook):
    name = "thp3_recon"
    description = "Red Team Reconnaissance"
    mode = "crew"

    phases = [
        Phase(
            name="Passive Reconnaissance",
            objective="Gather information without direct interaction",
            techniques=[
                "OSINT and public infrastructure identification",
                "Subdomain and DNS enumeration",
                "Cloud infrastructure scanning and misconfiguration checks",
                "Code repository search for exposed credentials",
                "Social media and email harvesting",
            ],
        ),
        Phase(
            name="Active Reconnaissance",
            objective="Interact with target to map attack surface",
            techniques=[
                "Port scanning and service version detection",
                "Web technology identification and fingerprinting",
                "Service banner grabbing and enumeration",
                "SSL/TLS certificate analysis",
            ],
        ),
    ]
