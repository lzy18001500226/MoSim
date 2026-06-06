from pentestagent.playbooks.base_playbook import BasePlaybook, Phase


class THP3WebPlaybook(BasePlaybook):
    name = "thp3_web"
    description = "Web Application Exploitation"
    mode = "crew"

    phases = [
        Phase(
            name="Discovery",
            objective="Understand application attack surface",
            techniques=[
                "Identify web technologies and frameworks",
                "Content discovery and endpoint enumeration",
                "Parameter and input point identification",
                "Authentication and session mechanism analysis",
            ],
        ),
        Phase(
            name="Exploitation",
            objective="Identify and exploit web vulnerabilities",
            techniques=[
                "Injection attacks (SQL, NoSQL, Command, LDAP)",
                "Cross-Site Scripting (Reflected, Stored, DOM-based)",
                "Authentication and authorization bypass",
                "Server-Side Template Injection and SSTI",
                "Server-Side Request Forgery (SSRF)",
                "Insecure deserialization vulnerabilities",
                "XML External Entity (XXE) attacks",
                "File inclusion and path traversal",
            ],
        ),
    ]
