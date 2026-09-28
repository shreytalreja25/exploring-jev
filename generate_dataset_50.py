import json
import os

emails = [
    # --- 1-10 (First Scale) ---
    {
        "id": "EML-001",
        "from": "sarah.jenkins@growthpartners.io",
        "to": "campaigns@company.com",
        "cc": "cmo@company.com",
        "subject": "Q4 Product Launch Ad Creatives & Omnichannel Campaign Assets",
        "body": "Hi team, we've finalized the creative deck, billboard copies, and social paid ad spend allocations for the upcoming Q4 rollout. Please review the attached Figma mocks and let us know if we have sign-off to begin A/B testing on Meta and TikTok.",
        "ground_truth": "Marketing"
    },
    {
        "id": "EML-002",
        "from": "david.vance@apexlogistics.com",
        "to": "inbound-sales@company.com",
        "cc": "procurement@apexlogistics.com",
        "subject": "Inquiry: Enterprise License Tier & Volume Pricing for 500 Seats",
        "body": "Hello, Apex Logistics is evaluating enterprise software solutions for 500 active seats across North America. We would like to schedule a product demo and discuss volume discounting, multi-year contracts, and onboarding timelines with your account executive.",
        "ground_truth": "Sales"
    },
    {
        "id": "EML-003",
        "from": "billing-ops@cloudhost-provider.net",
        "to": "accounts-payable@company.com",
        "cc": "finance-approvals@company.com",
        "subject": "Overdue Notice: Invoice #INV-2026-9941 - Wire Remittance Required",
        "body": "Dear Accounts Payable, this is an automated reminder that invoice #INV-2026-9941 for $14,250.00 is 15 days past due. Please transmit remittance advice or ACH transaction receipt to accounts@cloudhost-provider.net to avoid suspension of cluster resources.",
        "ground_truth": "Finance"
    },
    {
        "id": "EML-004",
        "from": "claire.reynolds@company.com",
        "to": "people-ops@company.com",
        "cc": "mark.stevens@company.com",
        "subject": "Internal Transfer Request: Senior Engineer Transfer to Core Platform Team",
        "body": "Hi HR Team, following my mid-year performance review with my manager Mark, I am officially submitting my application for the open Senior Software Engineer role on the Core Infrastructure team. Could you please send over the transfer guidelines and compensation band adjustments?",
        "ground_truth": "Human Resources"
    },
    {
        "id": "EML-005",
        "from": "ops-monitoring@datacenter-west.org",
        "to": "support@company.com",
        "cc": "incident-response@company.com",
        "subject": "CRITICAL INCIDENT: 504 Gateway Timeout Errors on API Gateway /v1/chat",
        "body": "High severity alert: Our production edge reverse proxy is recording sustained 504 Gateway Timeouts across US-West nodes. Downstream worker processes are failing health checks and crashing under socket connection backpressure. Immediate engineering triage required.",
        "ground_truth": "Technical Support"
    },
    {
        "id": "EML-006",
        "from": "events@global-tech-summit.com",
        "to": "marketing-leads@company.com",
        "cc": "press@company.com",
        "subject": "Invitation: Keynote Sponsorship & Brand Expo Booth at AI World 2026",
        "body": "Dear Marketing Director, we would love to feature your company as a Tier-1 Diamond Sponsor at AI World Summit 2026 in San Francisco. The sponsorship package includes prime exhibit booth positioning, brand logo placement across 50,000 attendees, and a 20-minute mainstage keynote.",
        "ground_truth": "Marketing"
    },
    {
        "id": "EML-007",
        "from": "rachel.zhao@fintech-ventures.co",
        "to": "sales@company.com",
        "cc": "legal@fintech-ventures.co",
        "subject": "RFP Response & Master Services Agreement (MSA) Redlines for Renewal",
        "body": "Hi Sales Team, our executive board has approved proceeding with the renewal. Attached is our legal counsel's marked-up MSA with revisions to Section 8 regarding data residency and indemnification clauses. Can we hop on a call tomorrow at 2 PM ET to finalize the contract?",
        "ground_truth": "Sales"
    },
    {
        "id": "EML-008",
        "from": "travel-desk@company.com",
        "to": "marcus.brooks@company.com",
        "cc": "payroll-audit@company.com",
        "subject": "Expense Report Rejection: Missing Itemized VAT Receipts for London Trip #EX-4412",
        "body": "Marcus, your recent expense submission for the Q3 London business trip has been flagged by corporate audit. The hotel folio and train receipts lack itemized VAT breakdowns required under our financial compliance policy. Please upload the receipts to Concur by Friday.",
        "ground_truth": "Finance"
    },
    {
        "id": "EML-009",
        "from": "benefits@company.com",
        "to": "all-employees@company.com",
        "cc": "hr-leadership@company.com",
        "subject": "Annual Open Enrollment 2026: Health Benefits, Dental & 401(k) Matching",
        "body": "Hello Everyone, our annual Open Enrollment window opens Monday, October 5th. All eligible full-time employees must log into the HR portal to select their medical, dental, and vision benefit tiers, and review employer 401(k) matching contributions for fiscal year 2027.",
        "ground_truth": "Human Resources"
    },
    {
        "id": "EML-010",
        "from": "alex.m@developer-community.io",
        "to": "helpdesk@company.com",
        "cc": "dev-support@company.com",
        "subject": "Bug Report: Python SDK v1.2.3 HMAC Webhook Verification Fails on Windows",
        "body": "Hello Support, while integrating your official Python SDK on Windows 11, the `verify_webhook_signature` function consistently throws an InvalidSignatureError due to CRLF newline handling in byte comparison. Linux and macOS work fine. Sample code and reproduction logs attached.",
        "ground_truth": "Technical Support"
    },

    # --- 11-20 (Scale 20) ---
    {
        "id": "EML-011",
        "from": "newsletter@saas-benchmarks.net",
        "to": "growth@company.com",
        "cc": "content@company.com",
        "subject": "Featured Placement: Inbound SEO & Guest Editorial Collaboration",
        "body": "Hi Growth Team, we'd like to syndicate your latest whitepaper on AI decision systems in our weekly enterprise newsletter reaching 120,000 engineering leaders. Please send over tracking UTM links and author headshots.",
        "ground_truth": "Marketing"
    },
    {
        "id": "EML-012",
        "from": "tomas.k@nordic-retail.se",
        "to": "inbound-sales@company.com",
        "cc": "purchasing@nordic-retail.se",
        "subject": "Demo Request: Point-of-Sale Real-Time Decision Gateway",
        "body": "Hello, Nordic Retail operates 400 department stores across Scandinavia. We are seeking a unified decision API for our checkout routing. We would like an intro call with an enterprise AE this Thursday.",
        "ground_truth": "Sales"
    },
    {
        "id": "EML-013",
        "from": "tax-compliance@deloitte-audit.com",
        "to": "cfo@company.com",
        "cc": "accounting@company.com",
        "subject": "FY2026 Form 1099-MISC & Foreign Entity Withholding Audit",
        "body": "Dear Finance Department, in preparation for the upcoming fiscal audit, please provide general ledger reconciliation sheets and W-8BEN certifications for all non-resident international contractors paid during Q2.",
        "ground_truth": "Finance"
    },
    {
        "id": "EML-014",
        "from": "talent-acquisition@company.com",
        "to": "hiring-managers@company.com",
        "cc": "head-of-people@company.com",
        "subject": "Q4 Engineering Headcount Approvals & Visa Sponsorship Guidelines",
        "body": "Team, please review the finalized H1-B visa cap lottery policies and compensation bands for international hires joining the Austin and London offices before scheduling final interview loops.",
        "ground_truth": "Human Resources"
    },
    {
        "id": "EML-015",
        "from": "datadog-alerts@company.com",
        "to": "oncall-infra@company.com",
        "cc": "tier3-support@company.com",
        "subject": "[P1 Incident] Redis Cluster Node Failover & High Memory Eviction Rates",
        "body": "Alert triggered: Cluster node redis-prod-04 has exceeded 95% maxmemory threshold. Keyspace evictions are causing latency spikes of 450ms across downstream cache lookups. On-call engineer please acknowledge.",
        "ground_truth": "Technical Support"
    },
    {
        "id": "EML-016",
        "from": "agency-lead@viralmedia.co",
        "to": "marketing@company.com",
        "cc": "brand@company.com",
        "subject": "YouTube Influencer Sponsorship Contract & Tracking Pixels",
        "body": "Hi, we have signed the three targeted tech YouTubers for our November product blitz. Please supply the coupon promo codes and dedicated conversion tracking pixel URLs by Wednesday so they can insert ad reads into next week's videos.",
        "ground_truth": "Marketing"
    },
    {
        "id": "EML-017",
        "from": "steven.wong@singapore-airlines.sg",
        "to": "sales@company.com",
        "cc": "procurement@singapore-airlines.sg",
        "subject": "Enterprise Procurement: Vendor Security Questionnaire & RFQ",
        "body": "Dear Enterprise Sales, our procurement department is reviewing your enterprise proposal for APAC deployment. Attached is our 120-question SOC2/ISO27001 vendor risk assessment. Please return with signature to proceed to price quotes.",
        "ground_truth": "Sales"
    },
    {
        "id": "EML-018",
        "from": "stripe-billing@stripe.com",
        "to": "finance@company.com",
        "cc": "treasury@company.com",
        "subject": "Stripe Payout Failure: Bank Account Verification Required (ACH #TR-881)",
        "body": "Notification: Your scheduled daily merchant payout of $48,320.19 could not be routed to JPMorgan Chase account ending in 4102. Please update corporate entity KYC documentation in the Stripe Dashboard.",
        "ground_truth": "Finance"
    },
    {
        "id": "EML-019",
        "from": "wellness-program@company.com",
        "to": "all-staff@company.com",
        "cc": "people-ops@company.com",
        "subject": "Employee Assistance Program (EAP) & Mental Health Stipends",
        "body": "Hi All, we are pleased to announce the launch of our expanded employee wellbeing initiative. Every employee is now entitled to a $500 annual mental health and fitness reimbursement through our benefits portal.",
        "ground_truth": "Human Resources"
    },
    {
        "id": "EML-020",
        "from": "security-bot@github.com",
        "to": "security-alerts@company.com",
        "cc": "dev-support@company.com",
        "subject": "Dependabot Alert: High Severity RCE in package 'aiohttp' < 3.10.11",
        "body": "Dependabot detected a vulnerability in requirements.txt: CVE-2026-4198 allows remote attackers to bypass HTTP header validations. Please review pull request #402 to bump dependencies and deploy to staging.",
        "ground_truth": "Technical Support"
    },

    # --- 21-30 (Scale 30) ---
    {
        "id": "EML-021",
        "from": "press-release@techcrunch-wire.com",
        "to": "communications@company.com",
        "cc": "cmo@company.com",
        "subject": "Media Query: Interview Request with CEO regarding Series B Announcement",
        "body": "Hello, I am a reporter with TechCrunch covering enterprise AI infrastructure. We'd love to schedule a 15-minute briefing with your executive team ahead of your Series B press release embargo lift on Tuesday.",
        "ground_truth": "Marketing"
    },
    {
        "id": "EML-022",
        "from": "elena.rostova@berlin-health.de",
        "to": "sales-eu@company.com",
        "cc": "hospital-it@berlin-health.de",
        "subject": "Pilot License Agreement: GDPR-Compliant Hospital Decision Engine",
        "body": "Dear Sales Team, our hospital board has approved a 3-month proof of concept trial for 25 oncology clinics. Please prepare the EU DPA (Data Processing Addendum) and initial invoice for the pilot setup fee.",
        "ground_truth": "Sales"
    },
    {
        "id": "EML-023",
        "from": "payroll@adp-systems.com",
        "to": "payroll-admin@company.com",
        "cc": "finance-controllers@company.com",
        "subject": "Monthly Payroll Tax Remittance Summary & State Unemployment Withholdings",
        "body": "Attached is the reconciled federal and multi-state employer tax liability schedule for payroll cycle ending September 30. Total automated direct debit from your operating account is $218,449.12.",
        "ground_truth": "Finance"
    },
    {
        "id": "EML-024",
        "from": "workplace-ops@company.com",
        "to": "nyc-office@company.com",
        "cc": "hr@company.com",
        "subject": "New York Office Return-to-Work Guidelines & Desk Booking System",
        "body": "Team, starting October 1st, our hybrid workplace policy requires all local staff to register in Envoy 24 hours prior to entering the Manhattan headquarters. Keycard badge access will be synced with your vaccination records.",
        "ground_truth": "Human Resources"
    },
    {
        "id": "EML-025",
        "from": "sre-alerts@pagerduty.com",
        "to": "infra-team@company.com",
        "cc": "support-leads@company.com",
        "subject": "[CRITICAL] PostgreSQL Replication Lag Exceeds 10GB on Read Replica 2",
        "body": "WAL sender process on master db-primary-01 has dropped connection to db-replica-02. Streaming replication has stalled and read traffic is encountering stale reads. SRE intervention needed immediately.",
        "ground_truth": "Technical Support"
    },
    {
        "id": "EML-026",
        "from": "creative-studio@designworks.io",
        "to": "brand-team@company.com",
        "cc": "cmo@company.com",
        "subject": "Final Brand Identity Guidelines & SVG Icon System Delivery",
        "body": "Hi Marketing, attached is the comprehensive brand book detailing primary/secondary HEX color tokens, typography scales, and social media templates for Twitter, LinkedIn, and Instagram.",
        "ground_truth": "Marketing"
    },
    {
        "id": "EML-027",
        "from": "purchasing@tokyo-automotive.jp",
        "to": "sales-apac@company.com",
        "cc": "procurement@tokyo-automotive.jp",
        "subject": "Quote Request: Multi-Cloud Automated Routing for 10,000 Connected Vehicles",
        "body": "Hello, we are finalizing supplier selection for our telematics fleet backend. Please provide pricing tiers for 10M decisions/month, including 99.99% SLA commitment and dedicated technical account management.",
        "ground_truth": "Sales"
    },
    {
        "id": "EML-028",
        "from": "corporate-card@amex.com",
        "to": "accounting@company.com",
        "cc": "finance-director@company.com",
        "subject": "Monthly Corporate American Express Statement Balance: $78,419.03",
        "body": "Your American Express Corporate Card billing period has closed. Autopay is scheduled for October 12th. Please review employee cardholder itemized statements in the Amex Corporate Portal.",
        "ground_truth": "Finance"
    },
    {
        "id": "EML-029",
        "from": "ethics-hotline@company.com",
        "to": "hr-leadership@company.com",
        "cc": "chief-people-officer@company.com",
        "subject": "Confidential Grievance Submission: Workplace Harassment Inquiry",
        "body": "CONFIDENTIAL: A formal anonymous workplace conduct grievance #CASE-2026-081 has been filed through the ethics intake portal regarding management behavior. Please assign an investigator.",
        "ground_truth": "Human Resources"
    },
    {
        "id": "EML-030",
        "from": "dev@customer-app.io",
        "to": "api-support@company.com",
        "cc": "tech-triage@company.com",
        "subject": "Issue: WebSocket Connection Drops after 60s Idle Timeout on EU Node",
        "body": "Hi Support, our production real-time dashboard experiences frequent disconnection errors (Code 1006) on wss://eu.api.company.com. Can you check keep-alive heartbeat configs on your Cloudflare edge?",
        "ground_truth": "Technical Support"
    },

    # --- 31-40 (Scale 40) ---
    {
        "id": "EML-031",
        "from": "sem@adwords-consulting.com",
        "to": "digital-marketing@company.com",
        "cc": "growth@company.com",
        "subject": "Google Ads Performance Audit: 35% ROAS Improvement in Enterprise Campaigns",
        "body": "Hi Marketing Team, we completed negative keyword pruning and landing page conversion rate optimization for your high-intent 'enterprise decision model' keywords. Average CPC dropped by $4.20.",
        "ground_truth": "Marketing"
    },
    {
        "id": "EML-032",
        "from": "contract-negotiator@defense-contractors.gov",
        "to": "sales@company.com",
        "cc": "legal@company.com",
        "subject": "FedRAMP Moderate Compliance Confirmation & Sole-Source RFP",
        "body": "Gentlemen, our agency is preparing a sole-source procurement award under FAR Part 15. Please confirm that your system is hosted in an authorized GovCloud enclave with FedRAMP High certification.",
        "ground_truth": "Sales"
    },
    {
        "id": "EML-033",
        "from": "treasury-desk@silicon-valley-bank.com",
        "to": "treasury@company.com",
        "cc": "finance@company.com",
        "subject": "Commercial Money Market Yield & Overnight Sweep Confirmation",
        "body": "Treasury confirmation: $5,000,000 USD has been allocated to 30-day Treasury Bills at an annualized yield of 4.85%. Sweep transaction record #SWP-9092 is available in your commercial portal.",
        "ground_truth": "Finance"
    },
    {
        "id": "EML-034",
        "from": "performance-reviews@cultureamp.com",
        "to": "all-managers@company.com",
        "cc": "hr@company.com",
        "subject": "Reminder: 360-Degree Peer Feedback Deadline Tomorrow 5 PM",
        "body": "Managers, please ensure all direct reports complete peer reviews and self-evaluations for the H2 2026 performance cycle before calibration committees convene next Monday.",
        "ground_truth": "Human Resources"
    },
    {
        "id": "EML-035",
        "from": "cert-manager@letsencrypt.org",
        "to": "devops@company.com",
        "cc": "support@company.com",
        "subject": "URGENT: TLS/SSL Certificate for *.company.com Expires in 48 Hours",
        "body": "Automated alert: ACME automated renewal challenge for domain api.company.com failed DNS-01 verification. If not resolved before October 1st, public API clients will receive SEC_ERROR_EXPIRED_CERTIFICATE.",
        "ground_truth": "Technical Support"
    },
    {
        "id": "EML-036",
        "from": "podcast-host@ai-frontiers.fm",
        "to": "pr@company.com",
        "cc": "marketing@company.com",
        "subject": "Podcast Guest Invitation: Deep Dive on Decision AI vs Generative LLMs",
        "body": "Hello, we host the AI Frontiers podcast with 250k monthly downloads. We would love to interview your VP of Product on the economics of System-One decision models for episode 84.",
        "ground_truth": "Marketing"
    },
    {
        "id": "EML-037",
        "from": "lead-broker@cloud-procure.io",
        "to": "sales-director@company.com",
        "cc": "enterprise-sales@company.com",
        "subject": "Warm Inbound Introduction: Fortune 100 Insurance Carrier Looking for Fast Routing",
        "body": "Hi, I have a qualified enterprise lead with Zurich Insurance evaluating automated claims routing platforms. Budget is approved for $300k ACV. Can you connect them with an enterprise representative?",
        "ground_truth": "Sales"
    },
    {
        "id": "EML-038",
        "from": "audit-partner@kpmg.com",
        "to": "controller@company.com",
        "cc": "cfo@company.com",
        "subject": "Interim Revenue Recognition Audit: ASC 606 Multi-Year Subscription Amortization",
        "body": "Dear Controller, please provide the deferred revenue waterfall schedule and contract milestone verification logs for top 20 enterprise SaaS contracts signed in Q1 and Q2.",
        "ground_truth": "Finance"
    },
    {
        "id": "EML-039",
        "from": "maternity-support@company.com",
        "to": "jessica.tan@company.com",
        "cc": "hr-benefits@company.com",
        "subject": "Parental Leave Approval & FMLA Benefit Schedule: Oct 2026 - Jan 2027",
        "body": "Jessica, your formal request for 16 weeks of paid parental leave has been approved by People Operations. Attached is your wage continuation schedule and transition plan.",
        "ground_truth": "Human Resources"
    },
    {
        "id": "EML-040",
        "from": "github-actions@company.com",
        "to": "release-engineering@company.com",
        "cc": "dev-support@company.com",
        "subject": "Build Failure in Pipeline #9021: Docker Image Vulnerability Scan Blocked Merge",
        "body": "Trivy scan reported 2 CRITICAL CVEs in base image python:3.11-alpine (libcrypto3 buffer overflow). Merge to main has been blocked by branch protection rules. Urgent developer remediation required.",
        "ground_truth": "Technical Support"
    },

    # --- 41-50 (Scale 50) ---
    {
        "id": "EML-041",
        "from": "seo-monitoring@ahrefs-alerts.com",
        "to": "marketing-leads@company.com",
        "cc": "seo@company.com",
        "subject": "Keyword Alert: Company Moved to #1 Position on Google for 'System One Decision AI'",
        "body": "Great news! Your blog post on Tokenomics and Decision Models has reached Rank #1 globally for high-volume search term 'System One Decision AI', generating a 42% lift in organic signups.",
        "ground_truth": "Marketing"
    },
    {
        "id": "EML-042",
        "from": "coo@fintech-neobank.br",
        "to": "sales-latam@company.com",
        "cc": "finance@fintech-neobank.br",
        "subject": "Contract Renewal & Multi-Region Expansion: 20 Million Monthly Decisions",
        "body": "Hello Sales, our transaction volume in Brazil and Mexico has doubled. We want to expand our existing annual contract to include our Santiago and Bogota payment hubs. Please send pricing addendum.",
        "ground_truth": "Sales"
    },
    {
        "id": "EML-043",
        "from": "fixed-assets@accounting-solutions.com",
        "to": "finance@company.com",
        "cc": "it-procurement@company.com",
        "subject": "Q3 CapEx Asset Depreciation Schedule: GPU Cluster & Server Hardware",
        "body": "Please find attached the MACRS 5-year depreciation calculation for the 64 NVIDIA H100 GPU compute servers acquired in July. The depreciation write-off for Q3 totals $312,500.",
        "ground_truth": "Finance"
    },
    {
        "id": "EML-044",
        "from": "immigration-counsel@fragomen.com",
        "to": "hr@company.com",
        "cc": "hiring@company.com",
        "subject": "USCIS Form I-797 Approval Notice for O-1A Alien of Extraordinary Ability",
        "body": "People Ops, we are pleased to inform you that USCIS has approved the O-1A nonimmigrant visa petition for Dr. Aris Thorne. Original approval notices will arrive via courier tomorrow.",
        "ground_truth": "Human Resources"
    },
    {
        "id": "EML-045",
        "from": "security-incident@cloudflare-soc.com",
        "to": "noc@company.com",
        "cc": "support@company.com",
        "subject": "DDoS Mitigation Notice: 45 Million Packet/Sec SYN Flood Mitigated on Edge",
        "body": "Cloudflare Magic Transit has automatically mitigated an volumetric L4 SYN flood targeting origin IP 198.51.100.22. Edge routing rules successfully absorbed 99.8% of attack packets with zero downtime.",
        "ground_truth": "Technical Support"
    },
    {
        "id": "EML-046",
        "from": "partnerships@producthunt.com",
        "to": "marketing@company.com",
        "cc": "growth@company.com",
        "subject": "Product Hunt #1 Product of the Day Badge & Featured Newsletter Inclusion",
        "body": "Congratulations! Your launch of TypeSafe Jev Decision Integration has been voted the #1 Product of the Day. Attached are your official digital badges, embed widgets, and certificate.",
        "ground_truth": "Marketing"
    },
    {
        "id": "EML-047",
        "from": "chief-architect@tier1-telecom.com",
        "to": "enterprise-sales@company.com",
        "cc": "procurement@tier1-telecom.com",
        "subject": "Competitive Evaluation: Final Selection between Jev vs In-House Bert Classifier",
        "body": "Dear Sales Team, our engineering committee has finished internal benchmarks. Your hosted decision model demonstrated superior calibration on edge cases. We are ready to draft the formal agreement.",
        "ground_truth": "Sales"
    },
    {
        "id": "EML-048",
        "from": "compliance@irs-automated.gov",
        "to": "tax-department@company.com",
        "cc": "cfo@company.com",
        "subject": "Notice of Acceptance: Federal Corporate Tax Return Form 1120 Accepted",
        "body": "This electronic receipt confirms that your Form 1120 U.S. Corporation Income Tax Return for tax period ending December 31, 2025 has been accepted by the Internal Revenue Service.",
        "ground_truth": "Finance"
    },
    {
        "id": "EML-049",
        "from": "compensation-committee@company.com",
        "to": "board-of-directors@company.com",
        "cc": "head-of-hr@company.com",
        "subject": "Annual Executive Equity Refresh & Employee Stock Purchase Plan (ESPP) Allocation",
        "body": "Board Members, attached is the proposed 2027 equity refresh pool, stock option grant distribution, and ESPP participation summary for review ahead of the quarterly governance meeting.",
        "ground_truth": "Human Resources"
    },
    {
        "id": "EML-050",
        "from": "client-engineer@enterprise-client.de",
        "to": "support@company.com",
        "cc": "tier2-support@company.com",
        "subject": "Kafka Consumer Lag Surge: Partition 14 Rebalance Stalled on Event Stream",
        "body": "Hello Support, our downstream Kafka consumer group 'invoice-triage-workers' has stopped committing offsets on partition 14 after a broker restart. Latency is accumulating at 1,200 events/minute.",
        "ground_truth": "Technical Support"
    }
]

out_path = os.path.join(os.path.dirname(__file__), "emails_dataset_50.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(emails, f, indent=2)

print(f"Successfully generated 50 emails dataset at: {out_path}")
