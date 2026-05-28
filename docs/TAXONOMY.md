# Taxonomy

13-tag closed taxonomy for multi-label classification. Tags below are the only valid prediction targets. Anything outside this list is a hallucination and should be retried.

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

- "We need to improve our security posture" with no specific incident: Security plus Documentation (they likely want guidance)
- Security audit request: Security plus Documentation
- Password reset issue: not Security alone, this is usually Software or Product depending on the system

---

### Performance

Use when an IT system or software application runs but slowly, lags, or has degraded responsiveness. The system is up but not working as expected.
Does NOT apply to business-metric performance such as marketing campaign performance, conversion rates, sales pipeline performance, or brand engagement. Those are Marketing or Sales depending on context.

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

Use when the ticket asks for documentation, guides, references, explanations, or how-to information.

**Example tickets:**

> Subject: Support Request for Integrating DataRobot with SaaS Project Management Platform
> Body: Could you provide detailed information on the integration process, including necessary documentation, APIs, and deployment steps?

Tags: Documentation, Integration

> Subject: Seeking Guidance on Securing Medical Data Across Products and Services
> Body: I am in need of guidance on securing medical data across various products and services. Could you provide information on practices and protocols?

Tags: Documentation, Security

**Edge cases:**

- "Where can I find the API docs": Documentation
- "Your docs are wrong about X": Documentation (still about docs, even if it is a complaint)
- "I read the docs and the system still does not work": probably not Documentation, focus on the actual problem

**Negative clause (added v2):**
> Documentation applies only when the ticket explicitly requests guides, references, API docs, tutorials, or how-to information. It does NOT apply to closing boilerplate such as "let me know if you need more details," "I can provide further information," or "please advise on next steps." That phrasing is a politeness convention, not a documentation request. A ticket reporting a login failure or a sync error that ends with "let me know if you need more info" is not a Documentation ticket.

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

This taxonomy is v1, locked at the start of the project. Changes require:

1. New entry in `evals/ground_truth/CHANGELOG.md`
2. New ground truth file `evals/ground_truth/v2.jsonl`
3. New CI threshold calibration after re-running baseline measurements
4. Updated worked examples in this document

The taxonomy is part of the eval contract. Silent changes to taxonomy without corresponding ground truth and threshold changes break the comparability of historical eval runs.
