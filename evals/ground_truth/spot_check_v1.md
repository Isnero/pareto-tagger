# Spot check, v1 ground truth

Random seed: 67
Sample size: 30
Source: evals/ground_truth/v1.jsonl
Reviewer: ks

## Results

- Agree: 18
- Partial: 11
- Disagree: 1
- Contamination (separate category, filter 3 bypass): 1
- Per-ticket issue rate: 40% (12/30, includes contamination)

## Per-ticket notes

### ticket_id 5068

**Subject:** Assistance Required for Integration Errors

**Body:**

```text
The marketing firm faced several product integration issues, leading to interruptions in their digital marketing efforts. Likely cause: compatibility problems between software. Actions taken: restarted devices and updated software, but the issues remain unresolved.
```

**Priority:** high | **Queue:** Product Support | **Type:** Incident

**Current true_tags:** ['Disruption', 'Software']

**Verdict:** Partial

**Notes:** Could add also Integration tag, not huge but it was mentioned in description itself - tag wasn't there in original data so that's something I will add. Original: Bug, Disruption, Compatibility, Software, IT, Tech Support.

---

### ticket_id 7543

**Subject:** None

**Body:**

```text
Customer Support, I am reporting an issue with the digital tools provided to the marketing agency. The tools, including Coursera and Microsoft Word, are crashing intermittently. I suspect this may be due to recent software conflicts. Despite trying to reinstall and update the software, the problem persists. I have attempted troubleshooting on my own but have been unable to resolve it. I would greatly appreciate it if you could look into this matter and provide a solution as soon as possible. The frequent crashes are disrupting my work.
```

**Priority:** medium | **Queue:** IT Support | **Type:** Incident

**Current true_tags:** ['Crash', 'Performance', 'Software']

**Verdict:** Agree

**Notes:**

---

### ticket_id 50994

**Subject:** Problem with Ad Display

**Body:**

```text
Hello Customer Support, I hope this message finds you well. I am experiencing an issue with my digital ads not displaying as expected, and I am seeking your assistance to resolve it. Despite my efforts to check my campaign settings and the ad status, the ads remain undisplayed. I suspect this could be due to a glitch in the platform or an issue with my campaign setup. Your prompt attention to this matter would be greatly appreciated, and I would be grateful if you could look into it and offer a solution. Please inform me if any additional details are required from my end to help address this situation. I appreciate your swift action in this matter and look forward to your timely response. Thank you for your support. I have double-checked my campaign settings and ad status, but the ads are still not displaying properly.
```

**Priority:** high | **Queue:** Technical Support | **Type:** Incident

**Current true_tags:** ['Product']

**Verdict:** Agree

**Notes:**

---

### ticket_id 57875

**Subject:** Digital Campaign Metrics Integration Error Again Today

**Body:**

```text
Dear Support Team, I am facing difficulties with the synchronization of my digital campaign metrics. This issue might be attributed to an incorrect API integration or firewall problems. Despite my efforts to restart servers, validate API keys, and modify firewall settings, the issue remains unresolved. Kindly help me address this to ensure accurate campaign tracking. Thank you for your assistance.
```

**Priority:** low | **Queue:** Technical Support | **Type:** Problem

**Current true_tags:** ['Integration']

**Verdict:** Partial

**Notes:** Could add Network, orginally there was Firewall so can add rule to change firewall to network. Original tag list:
Technical,
Bug,
Integration,
API,
Firewall,
Server,
Account,
Resolution.

---

### ticket_id 51816

**Subject:** Problem with Sony Vegas Pro Integration

**Body:**

```text
Here is a concise description of the issue: Integration failure with Sony Vegas Pro 18. What happened: Syncing projects failed overnight. Possible reason: API key might have expired. Steps taken: Restarted system, verified API credentials. Please assist in resolving this issue promptly.
```

**Priority:** medium | **Queue:** Technical Support | **Type:** Problem

**Current true_tags:** ['Integration', 'Software', 'Product', 'Crash', 'Documentation']

**Verdict:** Agree

**Notes:**

---

### ticket_id 21163

**Subject:** Details on Integrating Evernote SaaS

**Body:**

```text
Could you provide more information on integrating the Evernote project management SaaS? This would significantly boost our team's productivity. Currently using the platform, we would like to know the steps required to connect Evernote. Thank you for your assistance. Looking forward to hearing back soon.
```

**Priority:** medium | **Queue:** IT Support | **Type:** Request

**Current true_tags:** ['Feature', 'Documentation']

**Verdict:** Agree

**Notes:**

---

### ticket_id 53515

**Subject:** Support Request for Missing Campaign Metrics

**Body:**

```text
Campaign performance data vanished unexpectedly likely due to integration glitches or misconfiguration. System restarts and log reviews were performed without resolution.
```

**Priority:** medium | **Queue:** Product Support | **Type:** Incident

**Current true_tags:** ['Integration', 'Performance']

**Verdict:** Agree

**Notes:**

---

### ticket_id 60230

**Subject:** Missing Project Data

**Body:**

```text
The project data has disappeared unexpectedly, likely because of a glitch in the recent update. I have already restarted Smart-Waage and verified the SQL connections, yet the problem still exists.
```

**Priority:** medium | **Queue:** Technical Support | **Type:** Incident

**Current true_tags:** ['Feature', 'Crash', 'Documentation']

**Verdict:** Partial

**Notes:** Feature is wrong

---

### ticket_id 22088

**Subject:** Support for Robot Mowers

**Body:**

```text
May I assist with your issue regarding robot mowers? Please share any details about the problems or error messages you're encountering. It would be helpful to discuss this further over a phone call at a convenient time for you to troubleshoot the robot mower.
```

**Priority:** low | **Queue:** Product Support | **Type:** Request

**Current true_tags:** ['Product', 'Feature']

**Verdict:** this should be contaminated

**Notes:** this should be contaminated

---

### ticket_id 15272

**Subject:** AR Brille Oracle Support

**Body:**

```text
Is it possible to provide comprehensive documentation on the AR-Brille compatibility with Oracle Database SaaS integration?
```

**Priority:** high | **Queue:** Technical Support | **Type:** Request

**Current true_tags:** ['Documentation', 'Feature']

**Verdict:** Agree

**Notes:**

---

### ticket_id 2826

**Subject:** Request for Support with Advanced Analytics

**Body:**

```text
Customer Support is seeking information about the advanced analytics tools offered by the firm to enhance investment strategies. They request comprehensive documentation, such as user manuals, tutorials, and webinars to assist with initial setup. Their main interest lies in understanding predictive modeling and portfolio optimization features. Furthermore, they are eager to see case studies or success stories that showcase how these analytics tools have improved investment results. They would appreciate any available resources that demonstrate the tools' effectiveness.
```

**Priority:** high | **Queue:** Technical Support | **Type:** Request

**Current true_tags:** ['Product', 'Documentation', 'Feature']

**Verdict:** Agree

**Notes:**

---

### ticket_id 12951

**Subject:** Problem with Digital Healthcare Tools

**Body:**

```text
An unexpected outage is impacting vital tools. Potential reasons could be network issues or system overload.
```

**Priority:** high | **Queue:** Service Outages and Maintenance | **Type:** Incident

**Current true_tags:** ['Network', 'Performance']

**Verdict:** Agree

**Notes:**

---

### ticket_id 22687

**Subject:** Request for Support in Revamping Marketing Strategy

**Body:**

```text
Customer Support, recently, our marketing initiatives have seen a decline, which has affected the growth of our brand visibility. This could be due to outdated digital strategies and ineffective product promotions. We have attempted to refine our social media campaigns and optimize ad placements, but the results have not been satisfactory. Our team has tried various approaches, including content creation and influencer partnerships, which have shown some increase in engagement and conversions. We are reaching out to seek guidance on how to revamp our marketing strategy to improve overall performance.
```

**Priority:** medium | **Queue:** Product Support | **Type:** Incident

**Current true_tags:** ['Sales']

**Verdict:** Agree

**Notes:**

---

### ticket_id 2374

**Subject:** Assistance with Digital Tools Enhancement

**Body:**

```text
Our customer support team is seeking help with updating and optimizing our digital tools software. We are a marketing agency aiming to improve our brand growth strategy implementation. We would be grateful for any guidance on how to effectively utilize the tools, along with recommendations for optimization. Please advise on any additional steps we should take. Thank you for your time and support.
```

**Priority:** medium | **Queue:** IT Support | **Type:** Change

**Current true_tags:** ['Product', 'Feature']

**Verdict:** Agree

**Notes:**

---

### ticket_id 10821

**Subject:** Support for Resolving Logitech Keyboard Integration Issues

**Body:**

```text
A marketing agency is facing integration problems with the Logitech K780 Keyboard when used with WooCommerce, encountering compatibility conflicts. Attempts to reset devices and update relevant applications have not resolved the issue. Assistance in resolving this problem is needed.
```

**Priority:** medium | **Queue:** Product Support | **Type:** Incident

**Current true_tags:** ['Performance', 'Product', 'Feature']

**Verdict:** Partial

**Notes:** Not sure about Feature, shouldn't be there.

---

### ticket_id 54486

**Subject:** Enhancing Brand Growth Through Digital Marketing Tools

**Body:**

```text
Hello Customer Support, I am contacting you to seek information on integrating new digital marketing tools to boost our brand growth, particularly in conjunction with our SAP ERP and Azure systems. Our organization aims to broaden its digital footprint and improve its marketing strategies. We think that aligning these systems will assist us in realizing this vision. Could you give us detailed insights into the implementation process and the advantages these tools can offer to our business? We would greatly value any advice or assistance you can provide. We are eagerly awaiting your response. Thank you for your time and help. We are looking forward to your prompt reply.
```

**Priority:** medium | **Queue:** IT Support | **Type:** Change

**Current true_tags:** ['Integration', 'Marketing']

**Verdict:** Agree

**Notes:**

---

### ticket_id 13266

**Subject:** Concern Regarding Marketing Campaign Efficiency

**Body:**

```text
Marketing campaigns are not achieving the anticipated increase in brand engagement due to inadequate targeting and ineffective use of digital channels. Despite adjusting ad budgets and testing various content, the results have not met our expectations.
```

**Priority:** medium | **Queue:** Product Support | **Type:** Incident

**Current true_tags:** ['Sales', 'Marketing', 'Performance']

**Verdict:** Partial

**Notes:** Performance should be locked to IT systems only.

---

### ticket_id 8242

**Subject:** Marketing Problem

**Body:**

```text
The digital marketing campaign resulted in inconsistent brand messaging across various platforms, which might be due to coordination issues within the team. Several strategy adjustments and internal reviews have been attempted to resolve the issue, but it still persists. Assistance is needed to identify the root cause and implement a solution to ensure consistent brand messaging.
```

**Priority:** low | **Queue:** Technical Support | **Type:** Problem

**Current true_tags:** ['Marketing']

**Verdict:** Agree

**Notes:**

---

### ticket_id 5900

**Subject:** None

**Body:**

```text
A financial organization encountered system performance issues. These slowdowns may be due to software conflicts or hardware limitations.
```

**Priority:** high | **Queue:** Technical Support | **Type:** Incident

**Current true_tags:** ['Performance', 'Hardware']

**Verdict:** Partial

**Notes:** Could add software maybe? Add rule to match software conflict with software general tag. Original tags:
Performance,
Hardware,
Software Conflict.

---

### ticket_id 60365

**Subject:** Problem: Project Data Loss During Nighttime Update

**Body:**

```text
I am writing to report an issue where my project data has mysteriously disappeared overnight. The data was intact when I left for the day, but upon returning the next morning, it was no longer there. I have already tried rebooting the system, reviewing the logs, and ensuring all settings are correct, but the issue remains unresolved. I believe this could be due to a synchronization problem or a software glitch. I kindly request your assistance in resolving this issue as soon as possible.
```

**Priority:** low | **Queue:** Technical Support | **Type:** Incident

**Current true_tags:** ['Crash', 'Documentation']

**Verdict:** Partial

**Notes:** Could add Software or even Product, but not much data to back it up. Original tags:
Technical,
Bug,
Crash,
Resolution,
Documentation.

---

### ticket_id 25268

**Subject:** Exploring Integration Options for TensorFlow SaaS Project

**Body:**

```text
Seeking to understand the integration options available for the TensorFlow SaaS project. Could you provide detailed information on this? I would greatly appreciate any details you can offer about the integration process, its potential benefits, and any challenges involved. Thank you for your assistance with this matter.
```

**Priority:** medium | **Queue:** Product Support | **Type:** Request

**Current true_tags:** ['Feature', 'Documentation']

**Verdict:** Agree

**Notes:**

---

### ticket_id 18817

**Subject:** Inquiry About Scalable SaaS Features

**Body:**

```text
Can you provide an overview of the scalable SaaS features and their benefits for project management?
```

**Priority:** high | **Queue:** Technical Support | **Type:** Request

**Current true_tags:** ['Feature', 'Documentation', 'Sales']

**Verdict:** Partial

**Notes:** Is sales really for project management? I mean it could be I'm just not sure.

---

### ticket_id 49936

**Subject:** Medical Data Breach Noted

**Body:**

```text
Hello Customer Support,

I am in touch to inform you about a medical data breach that has been identified in our system. This breach occurred due to unauthorized access, which is documented in our system. Potential reasons for this breach might include inadequate firewall settings and an outdated Apache Hadoop version.

We have attempted to address the issue by restarting the servers, running a Kaspersky scan, and reviewing the Docker logs, but the problem continues to persist.

I would be grateful if you could investigate this and offer a solution as soon as possible.

Thank you for your attention and assistance.
Sincerely, [Your Name]
```

**Priority:** high | **Queue:** Technical Support | **Type:** Incident

**Current true_tags:** ['Security', 'Crash', 'Documentation']

**Verdict:** Partial

**Notes:** DOcumentation wrong, not asking for anything explicitly only mentioned that breach was documented. Original tags:
Security,
Breach,
Outage,
Maintenance,
Crash,
Documentation,
Resolution,
Incident,

---

### ticket_id 994

**Subject:** Crash Problem with Analytics Platform

**Body:**

```text
The data analytics platform experienced a crash during investment optimization tasks, potentially due to errors from the recent software update. Restarting the system and clearing the cache did not resolve the issue. Despite following troubleshooting procedures, the platform remains unusable. This situation raises concerns about its impact on making well-informed investment decisions. We would appreciate it if you could investigate this matter urgently and provide a solution or workaround to restore the platform's functionality promptly. Please keep us informed.
```

**Priority:** high | **Queue:** IT Support | **Type:** Incident

**Current true_tags:** ['Crash', 'Performance']

**Verdict:** Partial

**Notes:** Performance shouldn't be there as it's not working, clearly stated platform remains unusable. Should be Disruption but that's newly added tag by me. Could add Product because i imagine this platform is self developed.

---

### ticket_id 49757

**Subject:** None

**Body:**

```text
The process of data encryption has unexpectedly stopped functioning, which might be due to a potential software defect. After rebooting the encryption server, the problem still exists. I require your support to fix this issue.
```

**Priority:** high | **Queue:** IT Support | **Type:** Incident

**Current true_tags:** ['Security', 'Crash']

**Verdict:** Agree

**Notes:**

---

### ticket_id 10957

**Subject:** Strategies for Enhancing Shopify Brand Growth

**Body:**

```text
Enhance Shopify brand growth through digital strategies such as SEO and social media marketing.
```

**Priority:** high | **Queue:** IT Support | **Type:** Request

**Current true_tags:** ['Sales', 'Feature']

**Verdict:** Agree

**Notes:**

---

### ticket_id 10507

**Subject:** Concerns About Brand Expansion

**Body:**

```text
The marketing firm is experiencing a decline in brand growth through various digital strategies. This may be due to the use of outdated tools and ineffective campaigns. So far, we have analyzed our current strategies, gathered team feedback, and examined competitor activities. However, we need expert help to identify the root cause and implement corrective measures. We would appreciate guidance on the latest tools and trends in digital marketing. Additionally, we need assistance in creating
```

**Priority:** medium | **Queue:** Product Support | **Type:** Incident

**Current true_tags:** ['Sales', 'Marketing', 'Product', 'Feature']

**Verdict:** Agree

**Notes:**

---

### ticket_id 45599

**Subject:** Problem with the Dashboard

**Body:**

```text
Dear Customer Support, I am experiencing issues with the dashboard that have led to random crashes, which have significantly disrupted my workflow. Upon investigation, I discovered that the problem arises from incompatible library versions. Despite attempting to resolve it by updating dependencies and clearing the cache, the issue continues. I would be very grateful if you could look into this and provide guidance on how to fix it. Please inform me if you need any additional details from me. Thank you for your attention and assistance. I am looking forward to your response.
```

**Priority:** high | **Queue:** Technical Support | **Type:** Problem

**Current true_tags:** ['Crash', 'Disruption', 'Documentation']

**Verdict:** Agree

**Notes:**

---

### ticket_id 358

**Subject:** Critical Service Downtime

**Body:**

```text
Dear Customer Support Team,

I am writing to urgently seek immediate help due to ongoing service interruptions that are severely affecting essential healthcare infrastructure. These disruptions are impacting multiple crucial systems, such as medical device integration, telemedicine services, and compliance monitoring tools. The outages are creating serious difficulties in maintaining secure operations and providing vital patient care.

The services reliant on medical devices are essential for patient monitoring and treatment.
```

**Priority:** high | **Queue:** Service Outages and Maintenance | **Type:** Change

**Current true_tags:** ['Disruption', 'Hardware', 'Security']

**Verdict:** Agree

**Notes:**

---

### ticket_id 54785

**Subject:** Inquiry on System Requirements for Optimal Performance Today

**Body:**

```text
Hello Customer Support, I am writing to ask about the system requirements for the optimal performance of your project management SaaS platform. Could you kindly share with me the detailed hardware and software specifications needed? Specifically, I am interested in the recommended operating system, processor speed, memory, and any other pertinent details. This information will assist me in ensuring that my system meets the necessary standards and operates the platform efficiently. I appreciate your time and help with this. Thanks for your support, and I am eagerly awaiting your response.
```

**Priority:** high | **Queue:** Technical Support | **Type:** Request

**Current true_tags:** ['Product', 'Performance', 'Hardware', 'Software']

**Verdict:** Partial

**Notes:** Not sure about Hardware and Software, this could be restricted to not working only not as asking for performance boost. But i'm not sure if that's worth. It still touch this areas so could be full agree.

---
