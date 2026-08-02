from flask import Blueprint, request, jsonify, g
from app.models import db, Roadmap, RoadmapNode, RoadmapNodeResource, UserRoadmapProgress
from app.services.markdown_service import render_sanitized_html
from app.utils.decorators import require_auth, get_current_user

roadmap_bp = Blueprint('roadmap', __name__, url_prefix='/api/roadmaps')

def seed_default_cybersecurity_roadmap():
    existing = Roadmap.query.filter_by(slug='cyber-security').first()
    if existing:
        return existing

    roadmap = Roadmap(
        slug='cyber-security',
        title='Cybersecurity Learning Roadmap',
        description='Structured domain pathway from IT foundations to Red/Blue Team specialization and industry certifications.'
    )
    db.session.add(roadmap)
    db.session.flush()

    # Define curriculum node structure
    sections = [
        {
            'label': 'IT & Fundamentals',
            'layout_group': 'fundamentals',
            'nodes': [
                {
                    'label': 'Hardware & OS Fundamentals',
                    'node_type': 'topic',
                    'importance': 'recommended',
                    'description': '### Hardware & OS Fundamentals\n\nUnderstand physical computer architecture, motherboard buses, RAM, storage interfaces, peripherals, and OS-independent diagnostic workflows across Windows, Linux, and MacOS.\n\n- Computer Hardware Components & Buses\n- Connection Types & Interfaces\n- OS-Independent Troubleshooting\n- Popular Suites (iCloud, Google, MS Office)\n- CRUD Operations on Files & CLI',
                    'resources': [
                        {'title': 'CompTIA A+ Study Guide', 'url': 'https://www.comptia.org/certifications/a', 'resource_type': 'doc'},
                        {'title': 'Hardware Basics Overview', 'url': 'https://roadmap.sh/cyber-security', 'resource_type': 'article'}
                    ]
                },
                {
                    'label': 'Local & Wireless Technologies',
                    'node_type': 'topic',
                    'importance': 'recommended',
                    'description': '### Local & Wireless Technologies\n\nLearn how short-range and local wireless radio protocols transmit data, how handshakes occur, and how to identify vulnerability patterns in wireless access points.\n\n- WiFi (802.11 Standards)\n- Bluetooth Security & Pairing\n- NFC & RFID Mechanics\n- Infrared Communications',
                    'resources': [
                        {'title': 'Wireless Security Overview', 'url': 'https://www.wi-fi.org', 'resource_type': 'article'}
                    ]
                },
                {
                    'label': 'CTF Arenas & Platforms',
                    'node_type': 'topic',
                    'importance': 'alternative',
                    'description': '### CTF Platforms & Practice Arenas\n\nHands-on practice platforms designed to build offensive and defensive problem-solving skills through gamified challenge rooms and vulnerable machines.\n\n- HackTheBox Lab Navigation\n- TryHackMe Learning Paths\n- picoCTF Beginner Challenges\n- VulnHub Local VM Hacking',
                    'resources': [
                        {'title': 'HackTheBox', 'url': 'https://www.hackthebox.com', 'resource_type': 'doc'},
                        {'title': 'TryHackMe', 'url': 'https://tryhackme.com', 'resource_type': 'doc'}
                    ]
                },
                {
                    'label': 'Beginner Certifications Track',
                    'node_type': 'subtopic',
                    'importance': 'recommended',
                    'description': '### Beginner Certifications Track\n\nValidate core competency in hardware, Linux system administration, Cisco routing/switching, and foundational security controls.\n\n- CompTIA A+ (Core 1 & 2)\n- CompTIA Linux+ (XK0-005)\n- CompTIA Network+ (N10-008)\n- Cisco CCNA (200-301)\n- CompTIA Security+ (SY0-701)',
                    'resources': [
                        {'title': 'CompTIA Security+ Blueprint', 'url': 'https://www.comptia.org/certifications/security', 'resource_type': 'doc'}
                    ]
                }
            ]
        },
        {
            'label': 'Networking & Infrastructure',
            'layout_group': 'networking',
            'nodes': [
                {
                    'label': 'OSI Model & IP Subnetting',
                    'node_type': 'topic',
                    'importance': 'recommended',
                    'description': '### OSI Model & IP Subnetting\n\nMaster the 7 layers of the OSI model and packet encapsulation. Calculate subnets, CIDR notation, default gateways, and local loopback interfaces.\n\n- OSI 7-Layer Model & Encapsulation\n- IPv4 & IPv6 Addressing\n- CIDR & Subnet Masking\n- Public vs Private Ranges\n- Localhost & Loopback Mechanics',
                    'resources': [
                        {'title': 'OSI Model Guide', 'url': 'https://www.cloudflare.com/learning/network/what-is-the-osi-model/', 'resource_type': 'article'}
                    ]
                },
                {
                    'label': 'Network Services & Topologies',
                    'node_type': 'topic',
                    'importance': 'recommended',
                    'description': '### Network Services & Topologies\n\nUnderstand structural network layouts (Star, Mesh, Bus) and core services providing automated IP configuration (DHCP), domain resolution (DNS), and time synchronization (NTP).\n\n- DHCP & DNS Resolution\n- NTP & IPAM Services\n- Star, Mesh, Bus Topologies\n- Routers, Switches & VLANs\n- VPN Tunnels & WAN Connections',
                    'resources': [
                        {'title': 'DNS Mechanics Explained', 'url': 'https://howdns.works', 'resource_type': 'video'}
                    ]
                },
                {
                    'label': 'Virtualization & Hypervisors',
                    'node_type': 'topic',
                    'importance': 'alternative',
                    'description': '### Virtualization & Hypervisors\n\nLearn virtual machine provisioning, hypervisor abstractions, hardware passthrough, and sandbox creation on VMWare, Proxmox, and ESXi environments.\n\n- Type-1 Hypervisors (ESXi, Proxmox)\n- Type-2 Hypervisors (VirtualBox, VMWare Workstation)\n- Guest OS vs Host OS Isolation\n- Virtual Switch & NAT Networking',
                    'resources': [
                        {'title': 'Proxmox VE Documentation', 'url': 'https://pve.proxmox.com/pve-docs/', 'resource_type': 'doc'}
                    ]
                },
                {
                    'label': 'Network Diagnostic Tools & Auth',
                    'node_type': 'subtopic',
                    'importance': 'recommended',
                    'description': '### Network Diagnostic Tools & Auth Methodologies\n\nMaster CLI utilities for network diagnostics and traffic analysis alongside enterprise authentication protocols like Kerberos, Active Directory LDAP, SSO, and RADIUS.\n\n- Packet Captures (tcpdump, Wireshark)\n- Port Scanning & Routes (nmap, route)\n- Kerberos & LDAP Authentication\n- SSO & RADIUS Federation',
                    'resources': [
                        {'title': 'Wireshark User Guide', 'url': 'https://www.wireshark.org/docs/wsug_html_chunked/', 'resource_type': 'doc'}
                    ]
                }
            ]
        },
        {
            'label': 'Red Team (Offensive Security)',
            'layout_group': 'red_team',
            'nodes': [
                {
                    'label': 'Web Application Attacks & OWASP',
                    'node_type': 'topic',
                    'importance': 'recommended',
                    'description': '### Web Application Attacks & OWASP Top 10\n\nExploit critical web vulnerabilities listed in the OWASP Top 10. Intercept and tamper with requests using Burp Suite, perform blind/error-based SQL injection, and exploit stored/reflected XSS.\n\n- SQL Injection (SQLi)\n- Cross-Site Scripting (XSS)\n- Cross-Site Request Forgery (CSRF)\n- Directory Traversal & LFI/RFI\n- Burp Suite Pro Exploitation',
                    'resources': [
                        {'title': 'PortSwigger Web Security Academy', 'url': 'https://portswigger.net/web-security', 'resource_type': 'article'}
                    ]
                },
                {
                    'label': 'Privilege Escalation & Active Directory',
                    'node_type': 'topic',
                    'importance': 'recommended',
                    'description': '### Privilege Escalation & Active Directory Exploitation\n\nGain root or NT AUTHORITY\\SYSTEM access on compromised hosts and perform Active Directory domain takeovers using Kerberoasting, AS-REP Roasting, and BloodHound graphs.\n\n- SUID & Capabilities Exploitation\n- Windows Token & Service Hijacking\n- Kerberoasting & AS-REP Roasting\n- BloodHound LDAP Mapping\n- Pass-the-Hash & DCSync',
                    'resources': [
                        {'title': 'GTFOBins Linux Escalation', 'url': 'https://gtfobins.github.io', 'resource_type': 'doc'},
                        {'title': 'WADComs Active Directory Commands', 'url': 'https://wadcoms.github.io', 'resource_type': 'doc'}
                    ]
                },
                {
                    'label': 'Social Engineering & Attack Vectors',
                    'node_type': 'topic',
                    'importance': 'alternative',
                    'description': '### Social Engineering & Attack Vectors\n\nUnderstand human and protocol attack vectors: Phishing campaigns, Vishing, Man-in-the-Middle (MITM) ARP poisoning, Rogue Access Points, and low-level memory buffer overflows.\n\n- Phishing & Social Engineering\n- Man-In-The-Middle (MITM) Spoofing\n- Evil Twin & Rogue Access Points\n- Memory Leak & Buffer Overflow',
                    'resources': [
                        {'title': 'Social Engineering Framework', 'url': 'https://www.social-engineer.org', 'resource_type': 'article'}
                    ]
                },
                {
                    'label': 'Advanced Red Team Certifications',
                    'node_type': 'subtopic',
                    'importance': 'optional',
                    'description': '### Advanced Red Team Certifications\n\nValidate elite hands-on offensive capabilities through 24-hour practical labs and challenge networks.\n\n- Certified Ethical Hacker (CEH)\n- GIAC Penetration Tester (GPEN)\n- Offensive Security Certified Professional (OSCP)\n- CREST Registered Penetration Tester',
                    'resources': [
                        {'title': 'OffSec OSCP Course', 'url': 'https://www.offsec.com/courses/pen-200/', 'resource_type': 'doc'}
                    ]
                }
            ]
        },
        {
            'label': 'Blue Team (Defensive Security)',
            'layout_group': 'blue_team',
            'nodes': [
                {
                    'label': 'SIEM & SOC Analytics',
                    'node_type': 'topic',
                    'importance': 'recommended',
                    'description': '### SIEM & SOC Analytics (Splunk)\n\nSecurity Operations Center (SOC) analysts monitor enterprise networks 24/7. Learn to query Splunk, analyze Sysmon logs, create alert rules, and investigate suspicious activity.\n\n- Splunk Search Processing Language (SPL)\n- Windows Event Logs & Sysmon\n- Log Correlation & Alerting\n- Incident Triage & Severity Rating',
                    'resources': [
                        {'title': 'Splunk Fundamentals Training', 'url': 'https://www.splunk.com', 'resource_type': 'video'}
                    ]
                },
                {
                    'label': 'Digital Forensics & IR Tools',
                    'node_type': 'topic',
                    'importance': 'recommended',
                    'description': '### Digital Forensics & Incident Response (DFIR)\n\nMaster forensic data extraction and discovery tools for live memory analysis, disk imaging with FTK Imager, network packet dissection in Wireshark, and log filtering.\n\n- FTK Imager Disk Acquisition\n- Autopsy Digital Forensics Suite\n- RAM Memory Analysis (Volatility)\n- Wireshark & Hex Dissection',
                    'resources': [
                        {'title': 'Volatility Foundation', 'url': 'https://www.volatilityfoundation.org', 'resource_type': 'doc'}
                    ]
                },
                {
                    'label': 'Threat Intel & Sandboxing',
                    'node_type': 'topic',
                    'importance': 'alternative',
                    'description': '### Threat Intelligence & Sandbox Analysis\n\nAnalyze suspicious files, URLs, and domains using cloud sandbox environments (Any.run, Joe Sandbox), WHOIS records, and reputation APIs to classify APT threats.\n\n- VirusTotal Malware Scoring\n- Interactive Sandboxing (Any.run)\n- Joe Sandbox Behavioral Analysis\n- Domain & IP Reputation Lookup',
                    'resources': [
                        {'title': 'ANY.RUN Interactive Sandbox', 'url': 'https://any.run', 'resource_type': 'doc'}
                    ]
                },
                {
                    'label': 'Advanced Blue Team Certifications',
                    'node_type': 'subtopic',
                    'importance': 'optional',
                    'description': '### Advanced Blue Team Certifications\n\nValidate advanced defensive expertise in threat hunting, SOC operations, digital forensics, and enterprise incident response.\n\n- CompTIA Cybersecurity Analyst (CySA+)\n- GIAC Security Essentials (GSEC)\n- Blue Team Level 1 & 2 (BTL1/BTL2)\n- GIAC Certified Forensic Analyst (GCFA)',
                    'resources': [
                        {'title': 'Security Blue Team BTL1', 'url': 'https://www.securityblueteam.com', 'resource_type': 'doc'}
                    ]
                }
            ]
        },
        {
            'label': 'Cloud Security & DevSecOps',
            'layout_group': 'cloud',
            'nodes': [
                {
                    'label': 'Cloud Architecture & Security',
                    'node_type': 'topic',
                    'importance': 'recommended',
                    'description': '### Cloud Architecture & Infrastructure Security\n\nUnderstand cloud security architecture across AWS, Azure, and GCP. Audit IAM policies, secure S3 cloud storage buckets, configure Infrastructure as Code (Terraform), and protect serverless functions.\n\n- AWS, Azure & GCP Security Controls\n- Cloud Service Models (IaaS, PaaS, SaaS)\n- IAM Policy Auditing & Hardening\n- Infrastructure as Code (IaC) Scanning',
                    'resources': [
                        {'title': 'AWS Security Documentation', 'url': 'https://aws.amazon.com/security/', 'resource_type': 'doc'}
                    ]
                },
                {
                    'label': 'Security Scripting (Python / Go)',
                    'node_type': 'topic',
                    'importance': 'recommended',
                    'description': '### Security Scripting & Tooling\n\nDevelop security automation scripts, custom exploit modules, and log parsing tools using Python, Go, Bash, and PowerShell.\n\n- Python Security Scripting & Scapy\n- Go Network Tools & Concurrency\n- Bash Shell Automation\n- PowerShell Administration & Cmdlets',
                    'resources': [
                        {'title': 'Black Hat Python', 'url': 'https://nostarch.com/blackhatpython2e', 'resource_type': 'article'}
                    ]
                },
                {
                    'label': 'Executive Certifications (CISSP)',
                    'node_type': 'subtopic',
                    'importance': 'optional',
                    'description': '### Executive Leadership & Apex Certifications\n\nPrepare for enterprise leadership roles (CISO, Director of Security). Master security governance, risk assessment, legal regulatory compliance, and obtain the CISSP/CISM credentials.\n\n- CISSP 8 Security Domains\n- CISM Security Governance & Strategy\n- CISA Information Systems Auditing',
                    'resources': [
                        {'title': '(ISC)² CISSP Domain Guide', 'url': 'https://www.isc2.org/Certifications/CISSP', 'resource_type': 'doc'}
                    ]
                }
            ]
        }
    ]

    order_counter = 1
    for s_idx, sec_data in enumerate(sections):
        sec_header = RoadmapNode(
            roadmap_id=roadmap.id,
            parent_id=None,
            label=sec_data['label'],
            description_markdown=f"## {sec_data['label']}\n\nCore curriculum section for {sec_data['label']}.",
            node_type='section',
            importance='recommended',
            order_index=order_counter,
            layout_group=sec_data['layout_group']
        )
        db.session.add(sec_header)
        db.session.flush()
        order_counter += 1

        parent_node_id = sec_header.id
        for n_data in sec_data['nodes']:
            node = RoadmapNode(
                roadmap_id=roadmap.id,
                parent_id=parent_node_id,
                label=n_data['label'],
                description_markdown=n_data['description'],
                node_type=n_data['node_type'],
                importance=n_data['importance'],
                order_index=order_counter,
                layout_group=sec_data['layout_group']
            )
            db.session.add(node)
            db.session.flush()
            order_counter += 1

            for res_idx, r_data in enumerate(n_data.get('resources', [])):
                res = RoadmapNodeResource(
                    node_id=node.id,
                    title=r_data['title'],
                    url=r_data['url'],
                    resource_type=r_data['resource_type'],
                    order_index=res_idx + 1
                )
                db.session.add(res)
            
            # Connect topics sequentially inside section
            parent_node_id = node.id

    db.session.commit()
    return roadmap

@roadmap_bp.route('', methods=['GET'])
def list_roadmaps():
    seed_default_cybersecurity_roadmap()
    roadmaps = Roadmap.query.all()
    return jsonify([r.to_dict() for r in roadmaps]), 200

@roadmap_bp.route('/<slug>', methods=['GET'])
def get_roadmap(slug):
    roadmap = seed_default_cybersecurity_roadmap() if slug == 'cyber-security' else Roadmap.query.filter_by(slug=slug).first_or_404()

    # Public route (anonymous visitors can browse the roadmap), but if a real
    # session cookie is present we still resolve it to show personal progress.
    current_user, _ = get_current_user()
    user_status_map = {}
    if current_user:
        progress_entries = UserRoadmapProgress.query.filter_by(user_id=current_user.id).all()
        for entry in progress_entries:
            user_status_map[entry.node_id] = entry.status

    nodes = RoadmapNode.query.filter_by(roadmap_id=roadmap.id).order_by(RoadmapNode.order_index).all()
    nodes_data = [n.to_dict(user_status_map=user_status_map) for n in nodes]
    for nd in nodes_data:
        nd['description_html'] = render_sanitized_html(nd['description_markdown'])

    # Calculate overall progress percent for non-section nodes
    topic_subtopic_nodes = [n for n in nodes_data if n['node_type'] != 'section']
    total_count = len(topic_subtopic_nodes)
    done_count = sum(1 for n in topic_subtopic_nodes if n['user_status'] == 'done')
    progress_percent = round((done_count / total_count * 100), 1) if total_count > 0 else 0.0

    return jsonify({
        'roadmap': roadmap.to_dict(),
        'nodes': nodes_data,
        'progress_percent': progress_percent,
        'done_count': done_count,
        'total_count': total_count
    }), 200

@roadmap_bp.route('/nodes/<int:node_id>/progress', methods=['PATCH'])
@require_auth
def update_node_progress(node_id):
    current_user_id = g.current_user.id

    node = RoadmapNode.query.get_or_404(node_id)
    data = request.get_json() or {}
    new_status = data.get('status')
    if new_status not in ['not_started', 'in_progress', 'done']:
        return jsonify({'error': 'Invalid status'}), 400

    entry = UserRoadmapProgress.query.filter_by(user_id=current_user_id, node_id=node_id).first()
    if not entry:
        entry = UserRoadmapProgress(user_id=current_user_id, node_id=node_id, status=new_status)
        db.session.add(entry)
    else:
        entry.status = new_status

    db.session.commit()

    # Recompute overall completion for this user on this roadmap
    all_nodes = RoadmapNode.query.filter_by(roadmap_id=node.roadmap_id).all()
    user_status_map = {}
    for p in UserRoadmapProgress.query.filter_by(user_id=current_user_id).all():
        user_status_map[p.node_id] = p.status

    topic_subtopic_nodes = [n for n in all_nodes if n.node_type != 'section']
    total_count = len(topic_subtopic_nodes)
    done_count = sum(1 for n in topic_subtopic_nodes if user_status_map.get(n.id) == 'done')
    progress_percent = round((done_count / total_count * 100), 1) if total_count > 0 else 0.0

    node_dict = node.to_dict(user_status_map=user_status_map)
    node_dict['description_html'] = render_sanitized_html(node_dict['description_markdown'])

    return jsonify({
        'node': node_dict,
        'progress_percent': progress_percent,
        'done_count': done_count,
        'total_count': total_count
    }), 200
