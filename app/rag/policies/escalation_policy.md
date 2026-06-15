# Escalation & Resolution Policy

**Effective Date:** January 1, 2025  
**Last Updated:** June 1, 2025  
**Policy ID:** POL-ESCAL-001  
**Version:** 2.1

---

## 1. Purpose

This policy defines when, how, and to whom customer-support cases should be escalated. It ensures consistent handling, timely resolution, and appropriate authority for every case that cannot be resolved at the first contact level.

---

## 2. Escalation Triggers

A case **must** be escalated when any of the following conditions are met:

### 2.1 Fraud-Related Triggers

| Trigger | Escalation Level |
|---|---|
| Fraud score > 75 | Team Lead (immediate) |
| Fraud score > 90 | Fraud Investigation Team (immediate) |
| Confirmed chargeback on the account | Fraud Investigation Team |
| Suspected account-cluster fraud (≥ 3 linked accounts) | Fraud Manager |

### 2.2 Policy-Related Triggers

| Trigger | Escalation Level |
|---|---|
| Refund request outside the standard return window (30+ days) | Senior Agent |
| Request to refund a non-refundable item category | Team Lead |
| Conflicting policies apply to the same order | Team Lead |
| Customer requests exception to published policy | Team Lead |
| Refund value exceeds $500 | Team Lead |
| Refund value exceeds $1,000 | Manager |

### 2.3 Customer-Related Triggers

| Trigger | Escalation Level |
|---|---|
| Customer explicitly requests a manager or supervisor | Team Lead (within 5 minutes) |
| Customer expresses extreme dissatisfaction (3rd contact on same issue) | Team Lead |
| Customer threatens legal action | Manager + Legal |
| Customer threatens social-media escalation | Manager |
| VIP / loyalty-tier customer (Gold, Platinum) dissatisfied | Team Lead (priority handling) |
| Accessibility or language-barrier issues unresolvable by agent | Specialised Support Team |

### 2.4 Technical Triggers

| Trigger | Escalation Level |
|---|---|
| System unable to process refund (payment-gateway error) | Technical Support Team |
| Order data inconsistency (missing records, duplicate entries) | Technical Support Team |
| Agent system timeout or failure during processing | Technical Support Team |

---

## 3. Priority Levels

Every escalated case is assigned a priority level that determines response and resolution SLAs.

### 3.1 Priority Definitions

| Priority | Definition | Examples |
|---|---|---|
| **P1 — Critical** | Immediate business or customer impact. Potential legal, financial, or reputational risk. | Confirmed fraud, legal threats, data breach, media escalation |
| **P2 — High** | Significant customer impact requiring prompt resolution. Unresolved after multiple contacts. | Fraud score > 75, refund > $1,000, VIP complaints, 3+ contacts on same issue |
| **P3 — Medium** | Requires additional expertise or authority beyond front-line agent. | Policy exceptions, refund outside window, non-refundable item requests |
| **P4 — Low** | Informational escalation or minor issue requiring documentation. | Process clarification, minor policy questions, non-urgent feedback |

### 3.2 SLA Timelines

| Priority | First Response | Resolution Target | Maximum Time to Close |
|---|---|---|---|
| P1 — Critical | 15 minutes | 2 hours | 24 hours |
| P2 — High | 1 hour | 4 hours | 48 hours |
| P3 — Medium | 4 hours | 24 hours | 5 business days |
| P4 — Low | 8 hours | 48 hours | 10 business days |

> **Note:** SLA timers run during **business hours** (Monday–Friday, 9:00 AM–6:00 PM local time) for P3 and P4. P1 and P2 SLAs run **24/7**.

### 3.3 SLA Breach Procedure

If an SLA is at risk of being breached:

1. The system sends an automatic alert at **75% of the SLA window**.
2. At **90% of the SLA window**, the case is automatically re-escalated one level up.
3. Any SLA breach is logged and included in the weekly operations report.
4. Repeated SLA breaches trigger a process-improvement review.

---

## 4. Escalation Hierarchy

```
Level 0: AI Agent (automated handling)
   │
   ├── Level 1: Senior Support Agent
   │      └── Authorised to: approve refunds up to $200, issue goodwill credits up to $25
   │
   ├── Level 2: Team Lead
   │      └── Authorised to: approve refunds up to $500, issue goodwill credits up to $50, override standard policy
   │
   ├── Level 3: Support Manager
   │      └── Authorised to: approve refunds up to $2,000, issue goodwill credits up to $200, account actions
   │
   ├── Level 4: Director of Customer Operations
   │      └── Authorised to: approve any refund amount, account bans, policy exceptions
   │
   └── Level 5: VP of Operations / Legal
          └── Authorised to: handle legal threats, regulatory matters, PR-sensitive cases
```

---

## 5. Manager Review Procedures

When a case reaches Level 2 (Team Lead) or above:

### 5.1 Required Review Steps

1. **Case Summary Review:** Read all prior agent notes, customer communications, and system logs.
2. **Policy Check:** Verify which policies apply and confirm the agent's initial assessment.
3. **Customer History Analysis:** Review the customer's complete order, return, and contact history.
4. **Fraud Assessment:** Check the fraud score and any flagged indicators.
5. **Decision:** Choose one of the following resolution paths (see Section 6).
6. **Documentation:** Record the decision rationale in the case-management system.
7. **Customer Communication:** Inform the customer of the decision within the SLA window.

### 5.2 Documentation Requirements

Every escalated case must include:

- Original agent's case notes
- Reason for escalation (with specific trigger)
- All supporting evidence (screenshots, tracking data, customer correspondence)
- Manager's decision and rationale
- Follow-up actions required
- Date and time of resolution

---

## 6. Resolution Options

Escalation reviewers have the following resolution options:

| Resolution | Description | Authority Level |
|---|---|---|
| **Full Refund** | 100% refund to original payment method | Level 1+ (within their limit) |
| **Partial Refund** | Percentage refund per partial-refund schedule | Level 1+ |
| **Store Credit** | Refund issued as store credit (with optional bonus) | Level 1+ |
| **Goodwill Credit** | Additional credit beyond refund as customer-retention gesture | Level 1: $25 / Level 2: $50 / Level 3: $200 |
| **Replacement** | Ship replacement item at no cost | Level 1+ |
| **Exchange** | Process return and ship alternative item | Level 1+ |
| **Policy Exception** | Override standard policy for this specific case | Level 2+ |
| **Deny with Explanation** | Deny the request with clear policy-based reasoning | Level 1+ |
| **Account Action** | Restrict, suspend, or ban account | Level 3+ |
| **Legal Referral** | Refer to Legal department | Level 4+ |

---

## 7. Communication Templates

### 7.1 Escalation Acknowledgement (to Customer)

> "Thank you for your patience, [Customer Name]. I've escalated your case to our specialist team for a thorough review. You can expect to hear from us within [SLA timeframe]. Your case reference is [CASE-ID]."

### 7.2 Resolution — Approved

> "Great news, [Customer Name]. After reviewing your case, we've approved [resolution type]. [Details of the resolution]. You should see this reflected in your account within [timeframe]. Is there anything else I can help you with?"

### 7.3 Resolution — Denied

> "Thank you for your patience while we reviewed your request, [Customer Name]. After a thorough review, we're unable to process this request as it falls outside our [specific policy]. However, we'd like to offer [alternative — e.g., store credit, discount on next purchase]. If you'd like to discuss this further, you may request a formal review through our Customer Advocacy team."

---

## 8. Automated Agent Escalation Rules

When the AI agent determines escalation is necessary, it must:

1. **Inform the customer** that the case is being escalated.
2. **Provide the case reference number.**
3. **Set the correct priority level** based on the triggers in Section 2.
4. **Transfer all context** (conversation history, order details, fraud score) to the escalation queue.
5. **Not attempt further resolution** after escalation — hand off cleanly.
6. **Log the escalation reason** with the specific trigger that was activated.

---

## 9. Quality Assurance

- **10% of all escalated cases** are randomly audited monthly.
- Audits check for: correct escalation trigger identification, SLA compliance, appropriate resolution, documentation completeness.
- Agent performance on escalations is included in quarterly reviews.
- Customer satisfaction scores (CSAT) for escalated cases are tracked separately and compared against non-escalated cases.

---

## 10. Continuous Improvement

- Escalation trends are reviewed weekly by the operations team.
- Common escalation reasons are analysed to identify training opportunities.
- Policy gaps that cause frequent escalations are flagged for quarterly policy review.
- The AI agent's escalation accuracy is reviewed monthly — false escalations should be < 10%.

---

*This policy is reviewed quarterly by the Customer Operations and Risk Management teams. Changes require Manager-level or above approval.*
