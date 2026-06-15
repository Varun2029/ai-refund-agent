# Fraud Detection & Prevention Policy

**Effective Date:** January 1, 2025  
**Last Updated:** June 1, 2025  
**Policy ID:** POL-FRAUD-001  
**Version:** 2.4

---

## 1. Purpose

This policy defines the rules, indicators, and procedures used to detect, assess, and mitigate fraudulent refund and return activity on the ShopSmart Inc. platform. All automated agents and human support staff must follow these guidelines when processing refund requests.

---

## 2. Fraud Score Framework

Every refund request is assigned a **fraud score** (0–100) calculated by the automated fraud-detection agent. The score aggregates multiple risk signals into a single actionable metric.

### 2.1 Score Thresholds & Actions

| Score Range | Risk Level | Action |
|---|---|---|
| 0–30 | **Low** | Auto-approve if policy conditions are met. No additional verification required. |
| 31–60 | **Medium** | Process with standard review. Agent should verify order details and customer history. Flag for monitoring. |
| 61–80 | **High** | Place refund on hold. Require additional verification (photo evidence, receipt confirmation). Escalate to Team Lead within 2 hours. |
| 81–100 | **Critical** | Block refund immediately. Escalate to Fraud Investigation Team. Suspend account pending review. Do not communicate fraud suspicion to the customer directly. |

---

## 3. High-Risk Indicators

The following signals contribute to the fraud score. Each indicator has an associated weight.

### 3.1 Refund Frequency Indicators

| Indicator | Weight | Description |
|---|---|---|
| More than 3 refund requests in 30 days | +25 points | Pattern of serial returns |
| More than 5 refund requests in 90 days | +30 points | Chronic return behaviour |
| More than 2 refund requests in 7 days | +35 points | Rapid-fire refund attempts |
| Refund-to-purchase ratio > 50% (lifetime) | +20 points | Customer returns more than they keep |

### 3.2 Amount-Based Indicators

| Indicator | Weight | Description |
|---|---|---|
| Refund amount > 80% of order value | +20 points | Near-total refund on a multi-item order |
| Single refund > $500 | +15 points | High-value refund request |
| Single refund > $1,000 | +25 points | Very high-value refund request |
| Cumulative refunds > $2,000 in 90 days | +30 points | Significant cumulative refund volume |

### 3.3 Account-Based Indicators

| Indicator | Weight | Description |
|---|---|---|
| Account age < 30 days | +20 points | New accounts are higher risk |
| Account age < 7 days | +30 points | Very new account — elevated risk |
| No previous successful orders | +15 points | First order immediately requesting refund |
| Multiple addresses on file (> 3) | +10 points | Potential proxy shipping |
| Recent account-detail changes (< 48 hrs before refund) | +15 points | Email or address changed just before request |

### 3.4 Behavioural Indicators

| Indicator | Weight | Description |
|---|---|---|
| Customer claims "item not received" but tracking shows delivered | +30 points | Contradicts carrier data |
| Different reason given for same order across multiple contacts | +25 points | Inconsistent story |
| Customer requests refund within 1 hour of delivery | +10 points | Suspiciously fast claim |
| Customer refuses to provide photo evidence when requested | +15 points | Lack of cooperation |
| Customer demands manager immediately | +5 points | Mild escalation pressure |
| Bulk purchase of high-resale-value items followed by refund | +25 points | Potential wardrobing / resale fraud |

### 3.5 Payment & Device Indicators

| Indicator | Weight | Description |
|---|---|---|
| Order paid with a prepaid / virtual card | +10 points | Harder to trace |
| Multiple orders from same IP with different accounts | +20 points | Potential multi-account fraud |
| VPN or proxy detected on purchase or refund request | +10 points | IP masking |
| Chargeback history on the account | +30 points | Prior disputed payments |

---

## 4. Score Calculation Rules

1. **Additive scoring:** All applicable indicator weights are summed.
2. **Cap at 100:** The maximum fraud score is 100.
3. **Floor at 0:** The minimum fraud score is 0.
4. **Decay:** Indicators older than 180 days receive a **50% weight reduction**. Indicators older than 365 days are excluded.
5. **Positive history bonus:** Customers with more than 10 successful orders and zero prior refund issues receive a **−15 point adjustment** (minimum 0).

---

## 5. Pattern Detection Rules

Beyond individual indicators, the system monitors for broader fraud patterns:

### 5.1 Ring Detection

If **3 or more accounts** share two or more of the following attributes, flag the group for investigation:

- Same shipping address
- Same payment method (last 4 digits)
- Same IP address or device fingerprint
- Same phone number

### 5.2 Velocity Checks

| Pattern | Trigger |
|---|---|
| Same customer, same item refunded twice | Automatic hold + manual review |
| Same address receives > 5 refunded orders in 60 days | Account cluster investigation |
| Refund requested before order has shipped | Auto-approve cancellation, flag if frequent |

### 5.3 Seasonal Spikes

During high-volume periods (Black Friday, Cyber Monday, holiday season), the following adjustments apply:

- All thresholds are reduced by **10 points** (i.e., medium starts at 21, high at 51, critical at 71).
- Manual review capacity is doubled.
- Auto-approve is disabled for orders over $200.

---

## 6. Escalation Procedures

### 6.1 Escalation Matrix

| Fraud Score | Escalation Target | Response SLA |
|---|---|---|
| 31–60 | Senior Support Agent | Review within 4 hours |
| 61–80 | Team Lead | Review within 2 hours |
| 81–90 | Fraud Investigation Team | Review within 1 hour |
| 91–100 | Fraud Manager + Legal | Immediate review |

### 6.2 Investigation Steps

When a case is escalated, the investigator must:

1. Review complete order and refund history for the account.
2. Cross-reference shipping address against known fraud databases.
3. Verify tracking information with the carrier.
4. Request photo evidence from the customer (if applicable).
5. Check for account-cluster patterns (Section 5.1).
6. Document findings in the case management system.
7. Make a determination: **Approve**, **Partial Approve**, **Deny**, or **Suspend Account**.

---

## 7. Customer Communication Guidelines

- **Never** use the word "fraud" or accuse the customer of dishonesty.
- Use neutral language: "additional verification required", "routine security review".
- If a refund is denied due to fraud indicators, state: *"Based on our review, this request does not meet our refund policy requirements."*
- Offer the customer the right to appeal through a formal review process.
- All communications are logged and auditable.

---

## 8. Account Actions

| Action | Trigger | Reversible? |
|---|---|---|
| **Monitoring** | Score 31–60 | Automatic after 90 days clean |
| **Restricted** | Score 61–80 confirmed twice | Manager review required |
| **Suspended** | Score 81+ or confirmed fraud | VP-level approval to reinstate |
| **Banned** | Confirmed repeat fraud, legal action | Permanent (legal review only) |

---

## 9. Reporting & Audit

- All fraud scores and decisions are logged with timestamps and agent IDs.
- Weekly fraud summary reports are generated for management.
- Monthly trend analysis identifies emerging fraud patterns.
- Quarterly audits verify policy compliance and false-positive rates.
- Target false-positive rate: **< 5%** of flagged transactions.

---

## 10. Data Retention

- Fraud assessment data is retained for **3 years** from the date of the transaction.
- Account ban records are retained **indefinitely**.
- All data handling complies with applicable privacy regulations (GDPR, CCPA).

---

*This policy is reviewed quarterly by the Fraud Prevention and Risk Management teams. Amendments require approval from the VP of Operations.*
