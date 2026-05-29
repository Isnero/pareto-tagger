# Taxonomy

12-tag closed taxonomy for multi-label classification. Tags below are the only valid prediction targets. Anything outside this list is a hallucination and should be retried.

For data noise stats and how this taxonomy was derived, see `docs/DATASET.md`. For the prediction prompt and Pydantic schema, see `docs/PROMPT_VERSIONING.md`.

## Quick reference

| Tag | Use when... |
| ----- | ------------- |
| Security | The ticket reports unauthorized access, breaches, vulnerabilities, or data exposure |
| Performance | The system runs but slowly, lags, or has degraded responsiveness |
| Disruption | A service is interrupted but not necessarily fully down. Includes outages, slowdowns severe enough to halt work, and partial unavailability |
| Crash | A specific application or system stopped running, errored out, or became unresponsive |
| Network | Connectivity issues, firewall problems, API rate limits, routing problems |
| Documentation | The ticket explicitly asks for docs, guides, references, or how-to information. Not closing boilerplate |
| Feature | The ticket requests new capability, enhancement of existing capability, or feature integration |
| Hardware | Physical equipment is failing or needs attention. Servers, devices, peripherals, networking gear |
| Software | A specific software product or version is causing the issue. Use when the body names software (SAP, Excel, JIRA, etc.) and ties the issue to that software |
| Product | A specific product the company sells or supports has an issue. Distinct from Software in that Product refers to the customer's relationship with what the company offers |
| Integration | Connecting two systems, APIs, or platforms. Anything about plugging X into Y |
| Marketing | Marketing and sales topics: strategy, campaign performance, brand growth, advertising, lead generation, conversion tracking, sales tools, CRM |

## Tag definitions and examples

### Security

Use when the ticket describes unauthorized access, attempted breaches, vulnerabilities, or data exposure concerns.

**Example tickets:**

> Subject: Required Assistance for Security Issues
> Body: A healthcare provider has encountered unauthorized access attempts on medical data. Initial actions taken involved updating firewall settings and reviewing user access logs.

Tags: Security, Network

> Subject: Security Access Issue Identified
> Body: An unauthorized access attempt has been detected in the healthcare system, which could potentially expose sensitive medical data.

Tags: Security

**Edge cases:**

- "We need to improve our security posture" with no specific incident: Security (they likely want guidance)
- Security audit request: Security
- Password reset issue: not Security alone, this is usually Software or Product depending on the system

---

### Performance

Use when an IT system or software application runs but slowly, lags, or has degraded responsiveness. The system is up but not working as expected.
Does NOT apply to business-metric performance such as marketing campaign performance, conversion rates, sales pipeline performance, or brand engagement. Those are Marketing.

**Example tickets:**

> Subject: Microservices Deployment Issue
> Body: I am writing to report an incident involving delays in deploying microservices within our cloud-native SaaS platform. Since the issue started, I have observed unpredictable lag times that significantly hinder the deployment process.

Tags: Performance, Disruption

> Subject: Problem with Marketing Agency System
> Body: Experiencing a slowdown in the reporting system, which is believed to be caused by recent digital marketing strategies deployed by the agency.

Tags: Performance, Marketing

**Negative example (do NOT tag as Performance):**

> Subject: Marketing Campaigns Not Performing Well
> Body: Our marketing campaigns are not performing as expected.

Tags: Marketing (not Performance). "Performing" here refers to business outcomes, not system responsiveness.

**Distinction from Crash and Disruption:**

- Performance: slow but working
- Crash: stopped running entirely or threw fatal errors
- Disruption: service is interrupted, can include both Performance and Crash, or partial unavailability

**Edge case:** "App is slow then crashes" gets both Performance and Crash.

---

### Disruption

Use when a service is interrupted, fully or partially. Includes outages, severe slowdowns that halt work, and unplanned unavailability.

This is the broadest tag for "service is broken right now". Outage was dropped from the taxonomy because it nests inside Disruption (every outage is a disruption but not vice versa). Use Disruption.

**Example tickets:**

> Subject: System Interruptions
> Body: I am submitting a report regarding multiple system service disruptions that are currently interfering with project operations and client interactions.

Tags: Disruption, Performance

> Subject: Concern Regarding Interruption in Project Management Tool
> Body: Faced a major disruption in the project management tool due to server overload.

Tags: Disruption, Performance

**Edge cases:**

- Planned maintenance window: not a Disruption (planned is not a problem to report)
- Login slow but works: Performance, not Disruption
- Login fails for some users: Disruption (partial unavailability)

---

### Crash

Use when a specific application or system stopped running, errored out, or became unresponsive in a way that prevents use.

**Example tickets:**

> Subject: System Crash in Data Analytics Platform
> Body: The data analytics system has experienced a failure. Attempts to reboot and install patches were unsuccessful.

Tags: Crash, Disruption, Software

> Subject: Frequent Website Crashes Require Urgent Attention
> Body: Please address this issue immediately

Tags: Crash, Disruption

**Distinction from Disruption:**

- Crash describes the failure mode (stopped, errored)
- Disruption describes the impact (service interrupted)
- Both apply when an application crash is causing service interruption

---

### Network

Use for connectivity issues, firewall problems, API rate limits, routing problems, anything between systems that should be talking but isn't.

**Example tickets:**

> Subject: Issue with Data Synchronization Process in Smartsheet TYPO3
> Body: The error message indicates that an error occurred during the synchronization process. This might be due to API rate limits being exceeded.

Tags: Network, Integration

> Subject: Concern about Unauthorized Access Attempts on Medical Data
> Body: Despite implementing firewall adjustments and updating software, issues still persist.

Tags: Security, Network

**Edge cases:**

- "Cannot connect to internal database": likely Network, possibly Software depending on detail
- Cloud service unreachable: Network plus Disruption
- Slow API responses: Performance, not Network (Network is for connectivity failures, not speed)

---

### Documentation

Used for a request for a written document, reference, specification, or set of requirements. Explicitly exclude requests for advice, recommendations, or best practices, those are Feature or map to the underlying problem.

**Example tickets:**

> Subject: Support Request for Integrating DataRobot with SaaS Project Management Platform
> Body: Could you provide detailed information on the integration process, including necessary documentation, APIs, and deployment steps?

Tags: Documentation, Integration

> Subject: System Requirements for Project Management SaaS
> Body: I require details about the system requirements for your project management software... operating system compatibility, browser support, and any necessary hardware or software configurations?

Tags: Software, Hardware, Documentation

**Edge cases:**

- "Where can I find the API docs": Documentation
- "Your docs are wrong about X": Documentation (still about docs, even if it is a complaint)
- "I read the docs and the system still does not work": probably not Documentation, focus on the actual problem

**Negative clause:**
> Documentation applies only when the customer asks for a written artifact: a guide, reference, API doc, tutorial, specification, or system requirements. It does NOT apply when the customer reports a malfunction and asks for help fixing it, even when they use phrases like "provide detailed steps," "guidance on how to fix," "a resolution," or "recommendations to resolve." A request to fix a broken thing is the underlying problem tag (Crash, Performance, Network, etc.), not Documentation. The test: would satisfying this ticket mean handing over a document, or doing technical work? If technical work, not Documentation.

**Negative example tickets:**

> Subject: Connection problems with QuickBooks Online
> Body: ...After restarting the router and verifying the network settings, the issue still exists. We have gone through the API documentation.

Tags: Network, Performance (NOT Documentation. "API documentation" here is a step already taken, not a request.)

> Subject: Investment optimization output discrepancy
> Body: ...Could you please provide a guide or solution to help us resolve this issue?

Tags: Performance, Feature (NOT Documentation. "Guide or solution to resolve" is a fix request, not a document request.)

---

### Feature

Use for requests for new capability, enhancement of existing capability, or feature additions.

**Example tickets:**

> Subject: Request for Enhancement in Salesforce CRM Data Analytics Tools Integration
> Body: I would like to see advanced features such as automated data tracking and customizable reports.

Tags: Feature, Integration, Marketing

> Subject: Optimization of Investment Data Analytics Workflow
> Body: Need to integrate tools such as Nuendo, Plex, and Google Cloud for improved efficiency.

Tags: Feature, Integration

**Distinction from Documentation:**

- Documentation: "tell me how to use what exists"
- Feature: "build me something new"

---

### Hardware

Use when physical equipment is failing or needs attention. Servers, devices, peripherals, networking gear, RAID controllers, printers.

**Example tickets:**

> Subject: Multiple Equipment Failures Affecting Operations
> Body: I am urgently reporting a series of severe outages impacting several key devices critical to our operations. The affected devices include network switches, core routers, and storage arrays.

Tags: Hardware, Disruption

> Subject: Problem with Investment Data
> Body: A financial organization is facing sporadic connectivity problems that are affecting their investment data analysis. The issue might be due to conflicting software or hardware.

Tags: Hardware, Network, Performance

**Edge cases:**

- "Software running on the printer is broken": Software, not Hardware (the issue is in the software, the printer is just where it runs)
- "Printer is not turning on": Hardware
- "Printer is printing wrong colors": Hardware

---

### Software

Use when a specific software product or version is causing the issue. Best when the body names the software and ties the issue to that software.

**Example tickets:**

> Subject: Problem with CRM Software Update
> Body: Faced interruptions with the CRM project management tools after the latest software update.

Tags: Software, Disruption

> Subject: Reported Problem with Dashboard Loading
> Body: The dashboard has failed to load, and we believe it could be due to a recent MySQL update that is not compatible.

Tags: Software, Crash

**Distinction from Product:**

- Software: a tool the company uses (SAP, JIRA, Excel, MySQL)
- Product: something the company sells or maintains as their offering

---

### Product

Use when the issue concerns a specific product the company sells, maintains, or supports as their offering.

**Example tickets:**

> Subject: Problems with Product Integration and Connection
> Body: I am currently facing difficulties with the connectivity of the product I recently acquired. Despite adhering to the installation guidelines, the device does not establish a proper connection.

Tags: Product, Network, Integration

> Subject: Support for Digital Strategies in Schoology
> Body: Is it possible to offer insights into effective digital strategies for promoting the Schoology product?

Tags: Product, Marketing

**Edge cases:**

- The line between Product and Software is blurry. When in doubt, ask: is this about a tool the customer uses internally (Software), or about something the customer is positioned as buyer or owner of (Product)?

---

### Integration

Use for connecting two systems, APIs, or platforms. Anything about plugging X into Y.

**Example tickets:**

> Subject: Support Request: Guidance on Integrating Smart-Thermometer with Express.js 4.17
> Body: I require help in integrating a Smart-Thermometer with Express.js 4.17. Could you recommend digital strategies to enhance this integration?

Tags: Integration, Documentation

> Subject: Concerns with Software Integration Tools
> Body: I am reporting an issue with the integration of software tools, including the Smart-Küchengeräte malware protection applications.

Tags: Integration, Software, Security

**Edge cases:**

- "Two systems used to talk and now they don't": Integration plus Disruption
- "I want to connect A to B": Integration plus Feature

---

### Marketing

Use for marketing and sales topics: brand strategy, campaign performance, brand growth, advertising, digital strategy, lead generation, conversion tracking, sales tools, and CRM operations.

This tag was originally split into Marketing and Sales. They were merged in taxonomy v2 because the source labels did not draw the boundary consistently. The same intake template appeared tagged Sales on one ticket and Marketing on a near-identical other, so the distinction was unlearnable. One tag now covers both.

**Example tickets:**

> Subject: Improve Digital Strategy for Brand Expansion
> Body: I am reaching out to request an update on our digital strategy tools and approaches aimed at boosting brand growth.

Tags: Marketing, Feature

> Subject: Marketing Campaigns Not Performing Well
> Body: Our marketing campaigns are not performing as expected. Despite attempts to adjust ad spending and update materials, the results have not improved.

Tags: Marketing

> Subject: Challenges in Lead Generation Tracking
> Body: Facing difficulties with lead generation conversion tracking across various digital platforms.

Tags: Marketing, Integration

> Subject: Inquiry About Data Analytics Solutions for Investment Strategies Optimization
> Body: Seeking information on data analytics solutions

Tags: Marketing, Documentation

**Note on "performing":**

"Campaign not performing" or "low conversion rate" is Marketing, not Performance. Performance covers system responsiveness only. Business-outcome language belongs here.

**Why this tag covers sales-adjacent content:**

The dataset's IT support queues include a meaningful chunk of sales and marketing tickets. Either real businesses route this content to IT support, or the synthetic data generator does not separate it cleanly. Dropping the tag entirely would leave around 550 tickets with no valid tag at all (see `docs/DATASET.md` for the zero-tag analysis). It is retained as a single merged category.

---

## Edge case decisions

Some judgment calls worth recording so future-me does not relitigate them.

**Disruption vs Outage.** Outage was in the original taxonomy. Dropped because every outage is also a disruption. Keeping both forced the model to learn an arbitrary distinction the labels did not consistently make. Disruption is the kept tag. If a ticket clearly describes total unavailability, still Disruption.

**Sales and Marketing.** Merged into a single Marketing tag in v2. They were separate in v1, but the source labels did not distinguish them consistently, so the boundary was unlearnable. See the Marketing section and CHANGELOG v2.

**Bug.** Dropped. The original Bug tag was applied to software defects, marketing strategy failures, security incidents, and basically anything that did not work. No consistent semantic. Software, Crash, and Disruption cover the actual cases.

**IT, Tech Support, Technical.** All three dropped. After the IT-queue filter, they appear on roughly half of all tickets and add no information beyond the queue field itself.

**Workflow tags (Resolution, Recovery, Investigation, Fix, Communication, Assistance, Guidance).** All dropped. They describe what the support team should do, not what the customer reported. Some appear in customer text ("I tried rebooting") but inconsistently. The trade-off is losing some classification signal in exchange for predictability.

**Long-tail tags (Elasticsearch, Dashboard, RAID-Controller, Database).** Below 0.5% frequency individually. Not enough data per tag to compute meaningful F1. Documented as iteration backlog (add when real data is available).

## Versioning

Current taxonomy version: v3 (12 tags).

Taxonomy version tracks the ground truth version. They move together. A change to tag definitions, tag membership, or labeling rules bumps both, because the taxonomy is the contract the ground truth labels are scored against. They are not independent counters.

### Version history

- v1: 13 tags, locked at project start. Sales and Marketing separate.
- v2: Sales folded into Marketing. 12 tags. Reflected in evals/ground_truth/v2.jsonl. Reason: source labels did not separate the two consistently, the boundary was unlearnable. See CHANGELOG.
- v3: Documentation definition tightened. Tag membership unchanged at 12. Excludes fix-requests and advice-requests that the v1 and v2 labels misfiled as Documentation. Ground truth regeneration pending (evals/ground_truth/v3.jsonl), requires a Documentation-strip rewrite rule in data/load_dataset.py. See CHANGELOG.

### Changing the taxonomy requires

1. New entry in evals/ground_truth/CHANGELOG.md stating what changed and why
2. New ground truth file evals/ground_truth/vN.jsonl, prior versions immutable once tagged
3. Matching update to the TagEnum in apps/api/src/api/ai/schemas.py and to data/taxonomy.yaml, in the same commit, so the enum and the taxonomy never disagree
4. New CI threshold calibration after re-running baselines, since per-tag floors are tied to the tag set
5. Updated worked examples in this document

A silent taxonomy change without the matching ground truth, enum, and threshold updates breaks the comparability of historical eval runs. Do not edit a locked vN.jsonl in place.