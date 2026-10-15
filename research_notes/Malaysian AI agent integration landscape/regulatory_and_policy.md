# Malaysian Regulatory & Policy Landscape for an AI-Agent Business-Action Platform (as of 15 Oct 2026)

> Method note: All full-page fetches (WebFetch/curl) failed in this session (DNS/proxy errors) and the shared web-search budget ran out near the end. Every finding below is therefore based on search-engine summaries of the cited pages, not full-text reads. Primary documents (Gazette, pdp.gov.my, bnm.gov.my, hasil.gov.my, NAIO/AI Malaysia papers) should be checked before any legal reliance. Status tags used: **[ACT IN FORCE]**, **[ENACTED, NOT YET IN FORCE]**, **[GUIDELINE]** (regulator guidance; may be binding under the Act), **[POLICY]**, **[PROPOSAL/CONSULTATION]**, **[PRE-2025 — possibly stale]**.

## 1. PDPA: Personal Data Protection (Amendment) Act 2024, commencement, 2025–2026 JPDP guidelines, and what applies to a processor/intermediary platform

### Takeaway
All of the 2024 PDPA amendments have been in force since 1 June 2025. Data processors are now directly bound by the Security Principle. Processors that meet the volume or monitoring thresholds must appoint a DPO. Controllers must notify a breach within 72 hours (Commissioner) and 7 days (data subjects). Cross-border transfers now run on a list of legal bases plus a Transfer Impact Assessment (TIA), with no whitelist. In late April 2026, JPDP added guidelines on DPIA, Data Protection by Design and Automated Decision-Making & Profiling (ADMP). These bear directly on an agent platform: a DPIA is triggered by ADMP regardless of scale, and the ADMP guideline expects human oversight.

### Cited Findings
- **[ACT IN FORCE] Phased commencement.** The amendments came in three phases: a first tranche from **1 Jan 2025** ([Tay & Partners via Legal500](https://legal500.com/developments/thought-leadership/countdown-to-compliance-personal-data-protection-amendment-act-2024-in-force-starting-1-january-2025)), processor security duties, cross-border rules, revised definitions and higher penalties from **1 Apr 2025**, and DPO, breach notification and data portability from **1 Jun 2025** ([Baker McKenzie](https://insightplus.bakermckenzie.com/bm/data-technology/malaysia-personal-data-protection-amendment-act-2024-to-come-into-force); [DFDL](https://www.dfdl.com/insights/legal-and-tax-updates/malaysia-implementation-of-the-personal-data-protection-amendment-act-2024/); [HHQ final roundup](https://hhq.com.my/posts/full-implementation-of-the-personal-data-protection-amendment-act-2024-final-roundup/); [China Briefing](https://www.china-briefing.com/china-outbound-news/malaysia-tightens-data-protection-from-june-2025)). *Conflict:* firms disagree on whether the definitions and higher penalties took effect in the January or the April tranche.
- **Penalties.** The maximum PDPA fine is **RM1,000,000 per offence and/or up to 3 years' imprisonment** ([InCorp 2026 summary](https://malaysia.incorp.asia/?p=71808)).
- **[ACT IN FORCE] Processors.** Data processors are now directly subject to the Security Principle (PDPA s.9) ([Mayer Brown, Jul 2025](https://www.mayerbrown.com/en/insights/publications/2025/07/from-legislative-reform-to-practical-guidance-key-amendments-to-malaysias-pdpa-and-the-launch-of-cross-border-transfer-guidelines); [Chambers Data Protection 2026 – Malaysia](https://practiceguides.chambers.com/practice-guides/data-protection-privacy-2026/malaysia/trends-and-developments/O24504)).
- **[ACT IN FORCE + GUIDELINE] DPO (from 1 Jun 2025).**
  - Who must appoint: any organisation that processes personal data of **more than 20,000 data subjects**, or **sensitive personal data of more than 10,000**, or that engages in **regular and systematic monitoring**. This applies to **processors as well as controllers**.
  - Appointing a DPO does not discharge the organisation's own compliance duty.
  - Sources: [Christopher & Lee Ong](https://www.christopherleeong.com/viewpoints/launch-of-the-personal-data-protection-guidelines-for-mandatory-data-breach-notification-and-data-protection-officer-appointment/); [Shearn Delamore](https://www.shearndelamore.com/whats-new/publications/pdpa-malaysia-compliance-guide/); [OneAsia newsletter](https://oneasia.legal/en/wp-content/themes/standard_black_cmspro/img/March-Newsletter-PDPA.pdf).
  - The controller must notify the Commissioner of the appointment and publish a DPO contact email ([China Briefing](https://www.china-briefing.com/china-outbound-news/malaysia-tightens-data-protection-from-june-2025)).
- **[ACT IN FORCE + GUIDELINE, Feb 2025] Breach notification (from 1 Jun 2025).**
  - Trigger: the breach causes, or is likely to cause, significant harm.
  - To the Commissioner: "as soon as practicable" and **within 72 hours**. Phased notifications are allowed, and any delay must be justified and documented.
  - To affected data subjects: without unnecessary delay and **no later than 7 days after the initial notification to the Commissioner**.
  - Sources: [Christopher & Lee Ong](https://www.christopherleeong.com/viewpoints/launch-of-the-personal-data-protection-guidelines-for-mandatory-data-breach-notification-and-data-protection-officer-appointment/); [CMS](https://cms.law/en/sgp/legal-updates/new-guidelines-on-mandatory-breach-notifications-under-malaysia-s-personal-data-protection-act-2010); [HLC](https://www.hlc.com/en/publications/malaysia-imposes-data-breach-reporting-what-your-business-needs-to-know); [HHQ](https://hhq.com.my/posts/personal-data-breach-notification-in-malaysia-a-legal-guide-for-compliance/).
  - *Conflict:* sources differ on whether the 72-hour clock runs from the breach itself or from when it is detected. One practitioner notes that the 72-hour and 7-day limits sit in the guideline, not in the Act ([Securiti](https://securiti.ai/malaysia-data-protection-guidelines-dpo-appointment-and-breach-notification/)).
- **[ACT IN FORCE; guideline pending] Data portability (s.43A, from 1 Jun 2025).** Data subjects can ask for their data to go directly to another controller, subject to technical feasibility and format compatibility. The implementing guideline was expected in 2026 and was still unconfirmed as final ([Mayer Brown](https://www.mayerbrown.com/en/insights/publications/2025/07/from-legislative-reform-to-practical-guidance-key-amendments-to-malaysias-pdpa-and-the-launch-of-cross-border-transfer-guidelines); [Chambers 2026](https://practiceguides.chambers.com/practice-guides/data-protection-privacy-2026/malaysia/trends-and-developments/O24504)).
- **Planned guideline programme.** On 18 Nov 2024 the Commissioner said four guidelines (DPO, Data Breach Notification, Cross-border Transfer, Data Portability) plus a revised PDP Standard would come in early 2025, and three more in Q3 2025 ([Baker McKenzie](https://insightplus.bakermckenzie.com/bm/data-technology/malaysia-personal-data-protection-amendment-act-2024-to-come-into-force)).
- **[GUIDELINE] Cross-Border Personal Data Transfer Guideline (No. 03/2025), issued 29 Apr 2025.**
  - The s.129 whitelist is replaced by enumerated bases; a controller needs to satisfy only one of them.
  - Relying on "substantially similar law" or "adequate protection" requires a **Transfer Impact Assessment**.
  - BCRs, SCCs and approved certifications are recognised mechanisms.
  - Contractual precautions with the recipient count toward the s.129(3)(f) due-diligence exception.
  - Sources: [Rahmat Lim](https://www.rahmatlim.com/publication/articles/30646/new-guidelines-on-cross-border-personal-data-transfer); [Hogan Lovells](https://www.hoganlovells.com/en/publications/malaysias-groundbreaking-cross-border-data-transfer-guidelines-explained); [Nagashima](https://www.nagashima.com/en/publications/publication20250527-2/); [Mayer Brown](https://www.mayerbrown.com/en/insights/publications/2025/07/from-legislative-reform-to-practical-guidance-key-amendments-to-malaysias-pdpa-and-the-launch-of-cross-border-transfer-guidelines).
- **[GUIDELINE, 2026] Second tranche: DPIA, Data Protection by Design (DPbD), and ADMP v1.0.**
  - JPDP issued all three together on **~29–30 Apr 2026**, after a public consultation that ran **20 Mar – 19 May 2025** ([LexBlog, 29 Apr 2026](https://www.lexblog.com/2026/04/29/malaysia-jpdp-publishes-guidelines-on-dpia-privacy-by-design-and-automated-decision-making-and-profiling/); [Allen & Gledhill 2026](https://www.allenandgledhill.com/perspectives/publications/bulletins-malaysia/2026/pdp-commissioner-launches-guidelines-on-data-protection-impact-assessment-automated-decision-making-and-profiling-and-data-protection-by-design/); [Rajah & Tann](https://www.rajahtannasia.com/viewpoints/news-alert-issuance-of-new-guidelines-on-data-protection-impact-assessment-data-protection-by-design-and-automated-decision-making-and-profiling/); [Digital Policy Alert](https://digitalpolicyalert.org/event/39555-department-of-personal-data-protection-released-automated-decision-making-and-profiling-admp-guideline)).
  - The approach is risk-based and accountability-based, with **human oversight** to mitigate bias in automated decisions.
  - **ADMP is a qualitative DPIA trigger regardless of processing scale** ([InCorp summary](https://malaysia.incorp.asia/?p=71808)).
  - The 2025 consultation paper proposed volume thresholds of more than 10,000 data subjects for ADM and more than 20,000 for general processing ([CLO/Rajah & Tann consultation update, 8 Apr 2025](https://aitoolkit.rajahtannasia.com/wp-content/uploads/2025/04/250408-PDPA-Public-Consultation-Paper-Client-Update-CLOv02a-Clean_8April2025.pdf)). The final thresholds are unverified.
  - One summary describes DPbD as recommended best practice rather than mandatory ([InCorp](https://malaysia.incorp.asia/?p=71808)).
- **Contracts with processors.** Under the CBPDT guideline, a controller's contract with its processor should include clauses on how personal data is processed ([Mayer Brown](https://www.mayerbrown.com/en/insights/publications/2025/07/from-legislative-reform-to-practical-guidance-key-amendments-to-malaysias-pdpa-and-the-launch-of-cross-border-transfer-guidelines)).

### Inferences
- **Dual role.** For each business customer, the platform will usually be a **data processor**: it handles invoice counterparties, employee data for payroll or EPF actions, and customer records on the business's instructions. It is a **data controller** for its own user and account data, and for any data it uses for its own purposes, such as model fine-tuning, analytics or cross-customer benchmarking. Repurposing customer data turns the platform into a controller for that processing.
- **DPO is near-certain.** An agent platform serving many SMEs will almost certainly exceed 20,000 data subjects in aggregate. Continuous agent activity on business systems may also count as "regular and systematic monitoring".
- **Breach readiness.** The 72-hour and 7-day duties fall on the controller (the SME). The platform must contractually commit to near-immediate breach escalation so customers can meet them; a target of 24 hours or less is a sensible design goal.
- **Foreign model APIs.** Sending prompts containing personal data to foreign LLMs (US or EU hosted) is a cross-border transfer. It needs a s.129 basis: a TIA per destination, or SCCs with the model vendor. A Malaysian-hosted or sovereign model option (see Q4/Q8) reduces this burden.
- **Consequential agent actions.** Approving or rejecting counterparties, credit or payroll changes, or automatic e-invoice rejection or cancellation likely count as ADMP under the April 2026 guideline. Expect DPIAs, human-in-the-loop checkpoints and explanation or appeal channels to be expected practice.
- **Portability is a product opportunity.** Agents that pull or push data across controllers could be positioned as portability enablers once the guideline lands.

### Gaps
- No confirmation that the Data Portability guideline is final as of Oct 2026.
- Final DPIA thresholds and the binding status of DPbD in the April 2026 guidelines are unverified; the official JPDP texts were not read.
- Whether processors have an express statutory or guideline duty to notify controllers of breaches, and within what time, was not found. DPO residency and language requirements were also not confirmed.
- Whether the remaining "Q3 2025" guidelines were issued, and any 2026 amendments to the PDP Regulations, were not confirmed.

## 2. Cyber Security Act 2024 (Act 854): NCII sectors and CSSP licensing — does it touch agent middleware?

### Takeaway
The CSA 2024 binds only designated NCII entities and licensed cyber security service providers (CSSPs). An AI-agent middleware is neither, unless it is designated or sells SOC-monitoring or penetration-testing services. Customers in the 11 NCII sectors will, however, push CSA codes of practice, audits and 6-hour incident timelines down onto vendors through contracts.

### Cited Findings
- **[ACT IN FORCE] Commencement.** The CSA and its subsidiary regulations have been in force since **26 Aug 2024** ([Baker McKenzie](https://insightplus.bakermckenzie.com/bm/data-technology/asia-pacific-malaysia-cyber-security-act-2024-and-subsidiary-regulations-in-force-on-26-august-2024); [FMT](https://www.freemalaysiatoday.com/category/nation/2024/08/26/cyber-security-act-comes-into-effect)). [PRE-2025 — possibly stale]
- **11 NCII sectors:**
  1. government
  2. banking & finance
  3. transport
  4. defence & national security
  5. information, communication & digital
  6. healthcare
  7. water, sewerage & waste
  8. energy
  9. agriculture & plantation
  10. trade, industry & economy
  11. science, technology & innovation

  ([FMT](https://www.freemalaysiatoday.com/category/nation/2024/08/26/cyber-security-act-comes-into-effect)).
- **Designated NCII entities must:**
  - implement their sector code of practice;
  - conduct risk assessments (at least yearly) and audits (at least every 2 years);
  - give initial incident notification **within 6 hours** of becoming aware of the incident.

  Sources: [Mayer Brown, Dec 2024](https://www.mayerbrown.com/en/insights/publications/2024/12/malaysias-new-cyber-security-act-2024-a-summary-and-brief-comparative-analysis); [DNH](https://dnh.com.my/introduction-of-the-new-cyber-security-act-2024-csa-and-supporting-regulations/).
- **Sector leads, not NACSA, designate entities.** Sector leads designate NCII entities and prepare the sector codes ([Christopher & Lee Ong, Aug 2024](https://www.christopherleeong.com/wp-content/uploads/2024/08/2024-08_CLO-Cyber-Security-Act-2024-27-Aug-2024-v2.pdf)).
- **The NCII list is not public.** NACSA said it would reassess the 299 entities previously listed under NSC Directive No. 26; only the sector leads are published ([The Cyber Express](https://thecyberexpress.com/nacsa-revamps-cybersecurity-act-2024/)).
- **CSSP licensing covers only two prescribed services:** managed SOC monitoring and penetration testing. The licensing portal opened 1 Oct 2024, with a grace period to 31 Dec 2024 ([Baker McKenzie](https://insightplus.bakermckenzie.com/bm/data-technology/asia-pacific-malaysia-cyber-security-act-2024-and-subsidiary-regulations-in-force-on-26-august-2024)).
- **Cloud and data centres.** No 2026 information was found on designating cloud or data centre providers as NCII ([GRC Lens comparison 2026](https://www.grclens.net/blog/critical-infrastructure-cyber-laws-compared-apac-gulf)).

### Inferences
- The platform does not need a CSSP licence unless it bundles managed SOC or pen-testing.
- If the platform integrates deeply with banks, government agencies (LHDN, KWSP, SSM) or utilities, it may be in scope as a supplier. Expect clauses requiring support for 6-hour incident reporting, audit rights, and alignment with sector codes.
- Designation of an agent platform itself is unlikely but legally possible if a sector lead deems it critical, for example a dominant tax-submission intermediary. This is a low-probability, high-impact risk.

### Gaps
- No 2025–2026 amendments to the CSA, new regulations, or the published sector codes of practice were confirmed.
- Whether any "information, communication & digital" NCII designations cover SaaS or cloud intermediaries is unknown.

## 3. AI governance: AIGE (2024), NAIO → AI Malaysia Berhad, AI Governance Bill, National AI Action Plan 2026–2030, agentic AI guidance, sovereign AI (ILMU)

### Takeaway
Malaysia is moving from voluntary AI ethics (AIGE, 2024) to a binding, risk-tiered **AI Governance Bill**:
- 10 Jul 2026: NAIO consultation paper.
- 10 Sep 2026: draft declared complete.
- Target: tabling by Q1 2027 at the latest. The bill is **not enacted**.

The bill regulates "Developers" and "Deployers" and creates a Central AI Authority with sectoral leads and mandatory incident reporting. NAIO was institutionalised as **AI Malaysia Berhad** (announced 28 Jul 2026), which includes an AI safety institute (MY-AISafe). No standalone agentic-AI guidance exists. The National AI Action Plan 2026–2030 defines agentic AI as an emerging class.

### Cited Findings
- **[GUIDELINE, voluntary] AIGE and the 2024 frameworks.** FPF reviewed Malaysia's new data-protection and AI-ethics frameworks ([FPF](https://fpf.org/blog/malaysia-charts-its-digital-course-a-guide-to-the-new-frameworks-for-data-protection-and-ai-ethics/)). [PRE-2025 — possibly stale]
- **NAIO.** Cabinet approved NAIO on **28 Aug 2024** and it launched on **12 Dec 2024**. One source says 12 Nov 2024; most say 12 Dec ([regulations.ai](https://regulations.ai/regulations/RAI-MY-NA-NAIONXX-2024)).
- **Budget 2026** allocated **RM18.1m to NAIO** ([MDEC press release](https://www.mdec.my/media-release/news-press-release/402/belanjawan-madani-2026-a-%E2%80%98strategic-whole-of-nation-catalyst%E2%80%99-for-ai-nation-2030,-says-mdec); search summary).
- **[PROPOSAL] AI Governance Bill timeline.**
  - Late 2025: the Digital Minister said an AI legislative framework would go to Cabinet in **June 2026** ([Bernama](https://www.bernama.com/en/news.php?id=2494573); [Skrine, Dec 2025](http://www.skrine.com/insights/alerts/december-2025/malaysia-to-introduce-comprehensive-legal-framewor); [AmCham](https://amcham.com.my/malaysia-to-introduce-comprehensive-legal-framework-for-artificial-intelligence/)).
  - **10 Jul 2026:** NAIO released a Public Consultation Paper; feedback closed **31 Jul 2026** (some sources say 1 Aug) ([Baker McKenzie, Jul 2026](https://www.bakermckenzie.com/en/insight/publications/2026/07/malaysia-public-consultation-on-the-ai-governance-bill); [HLC](https://www.hlc.com/en/publications/malaysia-consults-on-ai-governance-bill); [MPC consultation portal](https://upc.mpc.gov.my/view-consultation/264); [dig.watch](https://dig.watch/updates/malaysia-ai-governance-bill-consultation)).
  - **10 Sep 2026:** Gobind Singh Deo said the draft is complete and will go to Cabinet, with tabling hoped for by **Q1 2027** at the latest ([AI Commission report, Sep 2026](https://aicommission.org/2026/09/digital-minister-says-malaysias-draft-ai-governance-bill-complete-hopes-to-table-it-by-q1-2027/); [Crypto Briefing](https://cryptobriefing.com/malaysia-first-ai-law-early-2027/); [Eversheds Sutherland](https://www.eversheds-sutherland.com/en/united-states/insights/ai-governance-bill-malaysias-next-step-towards-the-first-ai-rulebook)).
  - Cabinet approval was **not confirmed** in sources.
- **[PROPOSAL] AI Governance Bill structure** (per the consultation paper, [Baker McKenzie](https://www.bakermckenzie.com/en/insight/publications/2026/07/malaysia-public-consultation-on-the-ai-governance-bill); [ZICO Legal](https://www.ziclegal.com/resources/consultation-alert-public-consultation-on-malaysias-ai-governance-bill); [LPP Law submission](https://lpplaw.my/ai-governance-malaysia/); [Cyberpeace](https://cyberpeace.org/resources/blogs/malaysias-first-ai-law-is-coming-heres-whats-actually-in-it)):
  - Three harm-based tiers:
    - **Tier 1, unacceptable:** AI developed or deployed *with intent to cause harm*; prohibited outright.
    - **Tier 2:** AI with no intent to harm that *creates a risk of harm*. Summaries describe the obligations as risk assessment, documentation, internal controls, human oversight, monitoring and mitigation.
    - **Tier 3:** no foreseeable material harm.
  - Two regulated roles: **Developer** and **Deployer**.
  - A **Central AI Authority** with three functions: AI safety (risk framework, assessment supervision); investigation and enforcement (incidents); and enablement (guidance, **AI sandboxes**). It can appoint **Sectoral Leads** with delegated powers.
  - **Extraterritorial reach:** covers AI used in Malaysia from anywhere.
  - **Mandatory incident reporting.**
  - Penalty levels have not been published.
- **Enforcement first.** Gobind said the enforcement agencies and administrative structure must be in place before the law takes effect ([TechRepublic](https://www.techrepublic.com/article/news-ai-governance-bill-apac-malaysia/)).
- **[ESTABLISHED ENTITY] AI Malaysia Berhad.** Announced by the PM on **28 Jul 2026** as the national AI entity under the Ministry of Digital, replacing and institutionalising NAIO. Its remit extends from policy to coordinating implementation across the public sector and industry, and its six functions include the AI safety institute **MY-AISafe** (safety, evaluation, standards, technical assurance). An inaugural board was announced around 11 Sep 2026. Sources: [The Edge](https://theedgemalaysia.com/node/812301); [Skrine, Aug 2026](https://www.skrine.com/insights/alerts/august-2026/national-ai-office-institutionalised-as-ai-malaysi); [Lowyat](https://www.lowyat.net/2026/399891/govt-launches-ai-malaysia-berhad/); [Ministry of Digital](https://www.digital.gov.my/en-GB/siaran/AI-Malaysia-Pemacu-Utama-Menuju-Negara-AI-2030); [Malaysia-AI.my explainer](https://malaysia-ai.my/explainer-what-is-ai-malaysia-berhad/).
- **[POLICY] National AI Action Plan 2026–2030 ("AI Nation 2030").**
  - Content: 14 sector-application initiatives and 14 enabler initiatives (talent, innovation, infrastructure, governance, financing).
  - Targets: up to **+1.2 ppt GDP growth** attributable to AI, up to **300,000 AI-attributable jobs** (the fact sheet says 300k–500k), and **Top 10 in global AI indices** by 2030, with Top 20 as the 2028 interim marker.
  - The plan **defines agentic AI** as systems that "run tools in iterative loops to achieve goals" and names it among emerging forms lowering deployment barriers.
  - Sources: [NAIO Action Plan PDF (v. 29 Jul 2026)](https://strapi.naio.okie.my/uploads/AI_Nation_2030_National_AI_Action_Plan_2026_2030_Eng_V_290726_49cb382621.pdf); [AI Malaysia fact sheet](https://ai.gov.my/faq/national-ai-action-plan-2026-2030-fact-sheet/); [US-ASEAN](https://www.usasean.org/article/malaysia-accelerates-national-ai-agenda).
- **Related plan.** The Ministry of Digital launched an "MD2030 Action Plan" on 29 Jun 2026 ([MoD press release PDF](https://www.digital.gov.my/api/file/file/29062026_PRESS%20RELEASE_LAUNCH%20OF%20THE%20MD2030%20ACTION%20PLAN.pdf)); its content was not read.
- **Sovereign AI: ILMU and infrastructure.**
  - YTL AI Labs unveiled **ILMU** in **Aug 2025** as a homegrown LLM trained on Malaysian languages and context, positioned for government, education and SMEs. It runs alongside YTL's Kulai GB200 data centre ([YTL Power press release](https://www.ytlpowerinternational.com/press-releases/malaysia-accelerates-sovereign-ai-ambition-nvidia-and-ytl-brief-prime-minister-anwar-ibrahim-at-apec-summit/); [Malay Mail, 31 Oct 2025](https://www.malaymail.com/amp/news/malaysia/2025/10/31/nvidia-ytl-power-infrastructure-milestone-a-boost-for-malaysias-ai-push-says-anwar/196767); [ISIS Malaysia](https://www.isis.org.my/2025/10/27/owning-the-future-malaysias-sovereign-ai-cloud/)).
  - **Mar 2026:** YTL/Nvidia released "Ilmu-Nemo-30B", fine-tuned on Malaysian data, with a reported 23% MalayMMLU gain (per search summary of [Bernama](https://bernama.com/en//news.php?id=2535342); attribution to this exact URL unverified).
  - **Budget 2026:** RM2bn for an MCMC-led **Sovereign AI Cloud** ([Lowyat](https://www.lowyat.net/2025/369197/budget-2026-mcmc-sovereign-ai-cloud-rm2-billion-investment/)).
  - **15 Oct 2026:** Minister Fahmi Fadzil said the sovereign cloud will keep classified information beyond the reach of foreign laws ([Malay Mail](https://www.malaymail.com/news/malaysia/2026/10/15/malaysia-is-building-its-own-digital-cloud-to-safeguard-data-sovereignty-minister-says/239161)).
  - No evidence was found of government procurement mandates preferring ILMU.

### Inferences
- Under the draft bill, the platform would likely be a **Deployer**, and possibly a **Developer** of agent systems. The model vendor is the Developer of the foundation model. Agents filing tax, issuing e-invoices or moving money plausibly fall in **Tier 2**: no intent to harm, but a risk of financial or legal harm. Design now for risk assessment, documentation, human oversight, logging and incident reporting.
- Extraterritoriality means foreign agent frameworks used in Malaysia are caught too, so compliance becomes a market-entry barrier the platform can turn into a moat.
- The Central AI Authority's "AI sandbox" function and AI Malaysia Berhad's implementation remit are potential channels for a regulated pilot of agentic business actions.
- Offering a Malaysian-hosted or ILMU-compatible model option aligns with the sovereign-AI narrative and eases cross-border PDPA transfer issues. It is not legally required for private-sector data.

### Gaps
- AIGE details were not verified in this session. From background knowledge: MOSTI released AIGE on 20 Sep 2024 with 7 principles (fairness; reliability, safety & control; privacy & security; inclusiveness; transparency; accountability; human benefit), voluntary, with separate obligations for end users, policymakers and developers.
- Penalty levels, Tier 2 sub-categories (e.g., whether finance or tax uses are enumerated), treatment of general-purpose models and agentic systems, and the transition period of the AI Governance Bill are all unknown.
- No agentic-AI-specific guidance from NAIO, AI Malaysia, MOSTI or the Ministry of Digital was found.
- Whether Cabinet approved the bill after 10 Sep 2026 was not confirmed.

## 4. Financial regulation intersection: BNM (RMiT, outsourcing, e-KYC, customer information, AI discussion paper, sandbox/green lane, open finance) and SC AI guidance

### Takeaway
There is no binding BNM AI rulebook yet: the Aug 2025 Discussion Paper is exploratory and technology-neutral, and no follow-up exposure draft was found. For a platform serving financial institutions or touching payments, the binding layer is:
- **RMiT** (revised 28 Nov 2025): stricter third-party, SBOM and SLA rules, extended to large non-bank merchant acquirers;
- the **Outsourcing PD**: material cloud outsourcing needs BNM written approval;
- the **Technology Requirements PD for payment services regulatees** (effective 12 Mar 2027);
- the forthcoming **Open Finance** framework (ED Nov 2025), the natural legal rail for agents accessing bank data.

The **Green Lane** sandbox is open only to licensed institutions. The SC has a thin AI appendix in its GTRM and a 2026 masterplan priority on responsible AI.

### Cited Findings
- **[CONSULTATION] BNM Discussion Paper on AI in the Financial Sector.**
  - Issued **5 Aug 2025**; feedback closed **17 Oct 2025** ([BNM](https://www.bnm.gov.my/-/dp-aifs25); [Rajah & Tann](https://www.rajahtannasia.com/viewpoints/bank-negara-malaysia-issues-discussion-paper-on-artificial-intelligence-in-the-financial-sector-for-public-feedback/)).
  - BNM's 2024 survey: **71% of banks and 77% of insurers/takaful operators** ran at least one AI solution, up from 56% and 58% ([The Edge CEO Morning Brief](https://ceomorningbrief.theedgemalaysia.com/article/2025/1003/Home/3/765308); [TechWire Asia](https://techwireasia.com/2025/08/malaysia-ai-financial-regulation-framework-banking/)).
  - Risks flagged: model bias, data leakage, **over-reliance on third-party tools**, explainability.
  - Stance: technology-neutral, guided by parity, proportionality and neutrality ([NewsWav](https://newswav.com/article/bank-negara-is-regulating-ai-in-finance-what-does-this-mean-for-your-money-A2508_HiYVJ9)).
  - Emphasis on transparent, fair and explainable AI in credit, fraud and product recommendation ([RinggitPlus](https://ringgitplus.com/en/blog/bank-news/bank-negara-is-regulating-ai-in-finance-what-does-this-mean-for-your-money.html)).
  - No 2026 AI policy document or exposure draft was found.
- **[POLICY DOCUMENT IN FORCE] RMiT revised 28 Nov 2025** ([BNM](https://www.bnm.gov.my/-/pd-rmit-nov25); [PwC](https://www.pwc.com/my/en/assets/pdf/2025-updates-bnm-rmit-risk-management-in-technology.pdf); [SecurityScorecard white paper, Jul 2026](https://securityscorecard.com/wp-content/uploads/2026/07/SecurityScorecard-Whitepaper_Malaysia_MeetingBNMRMiT2025_July-2026.pdf)):
  - Extends coverage to **non-bank merchant acquirers and intermediary remittance institutions with more than 5% market share**.
  - Adds continuous third-party vendor monitoring, SBOM practices, and stricter SLA terms on incident disclosure and remediation.
  - PwC lists SLA renegotiation as an action due by Q2 2026.
  - Stand-in processing for least-substitutable services by 30 Sep 2027 (secondary source).
  - A BNM PDF labelled "pd-rmit-sep26" suggests a further **Sept 2026** revision, which could **not be confirmed** ([BNM PDF](https://www.bnm.gov.my/documents/20124/938039/pd-rmit-sep26.pdf)).
  - *Conflict:* one source says RMiT has no AI-specific obligations; another says the revision expressly brings AI into emerging-tech governance ([theleveragedyears](https://www.theleveragedyears.com/ai-regulation-news/malaysia-bnm-rmit-ai-ml-tech-risk-accountability-2026); [regulations.ai](https://regulations.ai/regulations/RAI-MY-NA-BNMDRXX-2023)).
- **Cloud under RMiT and the Outsourcing PD.**
  - RMiT defines third-party service providers to include cloud SaaS, PaaS and IaaS, with mandatory SLA terms.
  - Public cloud for critical systems requires prior engagement with BNM.
  - **Material cloud arrangements need BNM written approval under the 2019 Outsourcing PD** ([Chambers Global Practice Guide](https://gpg-pdf.chambers.com/view/731628805/226/)). [Outsourcing PD 2019 — possibly stale]
  - **RMiT contains no data residency requirement** ([Aqvantiq](https://aqvantiq.com/blog/malaysia-cloud-compliance-guide/)).
- **[POLICY DOCUMENT, ENACTED, NOT YET IN FORCE] Technology Requirements for Payment Services Regulatees.** Issued **12 Mar 2026**, effective **12 Mar 2027** ([Skrine, Apr 2026](http://www.skrine.com/insights/alerts/april-2026/bank-negara-issues-policy-document-on-technology-r)).
- **[EXPOSURE DRAFT] Open Finance.**
  - Issued **18 Nov 2025**; comments until **1 Mar 2026**. It sets requirements for consent-based sharing of customer information ([BNM ED PDF](https://www.bnm.gov.my/documents/20124/938039/ED_Open_Finance_2025.pdf); [HHQ](https://hhq.com.my/posts/open-finance-in-malaysia-bank-negara-malaysias-exposure-draft/)).
  - Mandatory for banks/DFIs with more than 100,000 customers, phased with those above 1,000,000 first; voluntary for smaller institutions.
  - Finalisation expected Q3–Q4 2026 and first mandatory phase from **1 Jan 2027** (secondary source: [iMoney](https://www.imoney.my/articles/bnm-open-finance-malaysia-2026)).
- **e-KYC.** The PD dates from June 2020; BNM FAQs are from Apr 2024; an exposure draft updating it exists, date unconfirmed ([Lexology/Skrine](https://www.lexology.com/library/detail.aspx?g=b80f3076-3dfc-4464-b1c6-bf3dfa2fb551); [BNM Payment Systems page](https://www.bnm.gov.my/payment-systems)). [PRE-2025 — possibly stale]
- **[POLICY DOCUMENT] Fintech Regulatory Sandbox.**
  - The PD of **29 Feb 2024** replaced the 2016 framework. It introduced the **Green Lane** for licensed FIs with strong risk management: a one-off capability assessment, then simplified registration of each new solution ([Skrine, Mar 2024](https://www.skrine.com/insights/alerts/march-2024/bank-negara-issues-new-fintech-sandbox-framework); [Fintech News MY](https://fintechnews.my/42303/innovation/bnms-new-sandbox-introduces-a-fast-lane-for-financial-institutions/)).
  - 2026 Green Lane applications ran **1–31 Jul 2026**, with testing capped at 20,000 customers over 12 months ([Business Today, 3 Jul 2026](https://www.businesstoday.com.my/2026/07/03/bank-negara-opens-application-for-fintech-regulatory-sandbox-green-lane/); [The Edge](https://theedgemalaysia.com/node/808976)).
- **Securities Commission.**
  - The **Guidelines on Technology Risk Management** (last revised Aug 2024) contain a short AI/ML appendix of four points, described as thin ([PKF Malaysia](https://www.pkfmalaysia.com/insights/2026-editions/securities-commission-s-artificial-intelligence-regulation/)).
  - The **Capital Market Masterplan 2026–2030** (launched ~Mar 2026) has a priority to "facilitate the development of a safe and responsible AI-enabled digital capital market ecosystem" ([SC CMP exec summary](https://www.sc.com.my/api/documentms/download.ashx?id=75f80f9b-4bcf-4ae1-8848-1a321bf8d321); [Skrine, Mar 2026](https://www.skrine.com/insights/alerts/march-2026/securities-commission-malaysia-launches-the-capita)).
  - A consultation (closed 31 Jul 2026) proposes **board oversight and disclosure of AI use by listed companies** ([theleveragedyears](https://www.theleveragedyears.com/ai-regulation-news/malaysia-sc-board-ai-oversight-disclosure-plc-2026)); secondary source, final rules unconfirmed.

### Inferences
- **Not itself regulated, but contractually bound.** An agent platform selling to SMEs is not a BNM regulatee merely by orchestrating payments through a customer's own bank channels. If a bank, insurer or large payment institution integrates it, or uses it for customers, the platform becomes a **third-party service provider** under RMiT/Outsourcing. Expect due diligence, SBOM requests, audit and access rights, exit and stand-in plans, incident SLAs, and possibly BNM approval where the arrangement is material.
- **Holding funds is the line.** Holding or transmitting customer funds itself, as opposed to instructing the customer's bank, would likely engage payment-system licensing (FSA 2013 / IFSA 2013 / PSA 2003). Design the agent to instruct, not custody.
- **Open finance is the right rail.** Once finalised (target phase 1 from 1 Jan 2027), the Open Finance framework is likely the legitimate path for agents to read bank data with consent instead of screen-scraping. Track third-party-provider eligibility.
- **Sandbox access needs a partner.** The Green Lane is for licensed FIs, so the platform would enter via a partner bank's Green Lane or the standard sandbox.

### Gaps
- No BNM AI policy or exposure draft after the Aug 2025 Discussion Paper was found. It is unknown whether the paper addresses agentic AI or AI-initiated transactions.
- The current text and date of the Management of Customer Information & Permitted Disclosures PD, and of the e-KYC ED, were not confirmed.
- Whether the Open Finance ED creates a registration or licensing route for non-bank third-party providers or AI agents, and whether payment initiation is in scope, was not confirmed (the search budget was exhausted).
- Whether an "RMiT Sep 2026" revision exists was not confirmed.
- No SC AI-specific guidance beyond the GTRM appendix and the CMP was found.

## 5. Tax intermediary rules: MyInvois "intermediary" role, ITA s.153 tax agents, e-invoice liability/penalties, current e-invoice scope

### Takeaway
A software platform can legally submit e-invoices **as a MyInvois "Intermediary"** once a director or owner appoints it in the MyInvois portal with granular permissions. No s.153 tax-agent approval is required for that role, and the **taxpayer stays liable** for content.

Preparing and lodging **income-tax returns or representing taxpayers** before LHDN is the domain of **s.153 approved tax agents**. A tax-filing agent therefore needs a licensed tax-agent partner or a taxpayer-self-submission design.

Mandatory e-invoicing scope has been cut sharply:
- turnover threshold raised to **RM3m effective 1 Sep 2026**;
- Phase 4 relaxation extended to **31 Dec 2027**;
- penalties under ITA s.120(1)(d) are **RM200–RM20,000 per offence**.

### Cited Findings
- **MyInvois intermediary mechanics.** Vendor guides consistently describe the following; this is secondary, so check the LHDN MyInvois user guide:
  - An intermediary is a third party formally appointed to submit e-invoices on a taxpayer's behalf, e.g. accounting firms or ERP/POS vendors.
  - The appointment is made in MyInvois under Taxpayer Profile → Representatives → **Add Intermediary**, entering the intermediary's TIN, BRN and name.
  - Permissions are granular toggles (submit, cancel, etc.) with **date-bounded validity (up to ~5 years)**.
  - **Only a company director** (or a sole proprietor registered as business owner in MyTax) can appoint.
  - The appointee needs a valid TIN and must submit via the portal or API.
  - **The business remains responsible for accuracy** of e-invoice content and records.
  - Sources: [AJobThing](https://www.ajobthing.com/resources/blog/how-appoint-intermideary-e-invoice-submission-myinvois); [ClearTax docs](https://docs.cleartax.in/product-help-and-support/for-large-businesses/cleartax-e-invoicing-malaysia/resources/add-cleartax-as-an-intermediary-on-myinvois-portal); [StoreHub](https://care.storehub.com/en/articles/9463916-set-up-e-invoice); [Access Group FAQ](https://www.theaccessgroup.com/media/wllcr3ts/faq_add-access-as-intermediary-in-myinvois.pdf); [Yezza](https://blog.yezza.com/how-to-access-the-malaysian-myinvois-portal-and-set-up-yezza-as-an-intermediary/).
- **Tax agents (ITA 1967 s.153).**
  - Only persons who are tax agents under s.153(3) may represent taxpayers for purposes of the Act. These are professional accountants approved by the Minister, or others approved on the DG of IRB's recommendation; applications go via the MyCukai portal ([MAICSA](https://www.maicsa.org.my/media/4334/students_recognition_tax.pdf); [HASiL – Profession as a Tax Agent](https://www.hasil.gov.my/en/tax-agent/profession-as-a-tax-agent/); [MAICSA tax agent licence](https://www.maicsa.org.my/resources/technical-research/tax-agent-license)).
  - Agents must quote their approval number in IRB correspondence ([MAICSA](https://www.maicsa.org.my/resources/technical-research/tax-agent-license)).
  - Staff of a tax agent may not consult HASiL officers without the taxpayer present ([HASiL](https://www.hasil.gov.my/en/tax-agent/consultation-with-hasil/)).
  - Secondary source: only approved agents can sign returns on clients' behalf, lodge objections, and represent in audits ([SSAM](https://www.ssam-group.com/blog/approved-tax-agent-malaysia/)).
- **e-Invoice threshold history.**
  - **6 Dec 2025:** Cabinet raised the mandatory threshold from RM500k to **RM1m** and cancelled the 5th wave ([BigSeller](https://alpha5.bigseller.pro/blog/articleDetails/4150/e-invoice-malaysia-update-2026.htm); [Airwallex](https://www.airwallex.com/en-my/blog/e-invoicing-exemption-malaysia-rm1-million)).
  - **30 Aug 2026:** the PM announced in his National Day address an increase to **RM3m, effective 1 Sep 2026** (Guideline **v4.8**). LHDN says more than **1.1m businesses** benefit, and stresses voluntary participation ([The Star, 30 Aug 2026](https://thestar.com.my/news/nation/2026/08/30/over-11-million-businesses-to-benefit-from-higher-e-invoicing-threshold-says-lhdn); [Malay Mail, 31 Aug 2026](https://www.malaymail.com/news/malaysia/2026/08/31/irb-stresses-voluntary-participation-as-government-lifts-einvoice-threshold-easing-compliance-for-msmes/233340); [Bernama Biz](https://www.bernamabiz.com/news.php?id=2601063); [LookupTax](https://lookuptax.com/tax-changes/malaysia/einvoice-exemption-threshold-3m-2026)).
  - The exemption is **disapplied** where a non-individual shareholder, holding company, or related company or JV has turnover of at least RM3m ([LookupTax](https://lookuptax.com/tax-changes/malaysia/einvoice-exemption-threshold-3m-2026); [3E CPA](https://www.3ecpa.com.my/resources/corporate-compliance-requirement/malaysia-e-invoice/)).
  - *Date conflict:* some sources date v4.8 to 30 Aug 2026; LHDN's statement says effective 1 Sep 2026.
- **Penalties and relaxation.**
  - Failure to issue an e-invoice is an offence under **ITA s.120(1)(d)**: **RM200–RM20,000 fine and/or up to 6 months' imprisonment**, potentially per non-compliant transaction. One source calls it strict liability ([Cleartax FAQ](https://www.cleartax.com/my/e-invoicing-faqs-malaysia); [QuickBooks MY](https://quickbooks.intuit.com/my/r/invoicing/irbm-e-invoice-guidelines-version-4/)).
  - The Interim Relaxation Period is "NOT a deferment". Phase 4 relaxation was **extended to 31 Dec 2027** ([RSM, Apr 2026](https://www.rsm.global/malaysia/sites/default/files/media/05%20Tax/Newsletter/PDF/202604%20-%20E-Invoicing.pdf)).
  - The rule requiring an individual e-invoice for transactions **above RM10,000** has applied since **1 Jan 2026** and is not relaxed ([Beancount, Sep 2026](https://beancount.io/blog/2026/09/16/malaysia-e-invoicing-phase-4-rm3m-exemption-rm10000-rule-guide)).
  - One source cites full enforcement from 1 Jan 2028 (unverified).
- **Voluntary adopters** can deduct up to **RM50,000 per YA** of qualifying e-invoice implementation costs, available **YA2024–YA2027** ([The Star, 30 Aug 2026](https://thestar.com.my/news/nation/2026/08/30/over-11-million-businesses-to-benefit-from-higher-e-invoicing-threshold-says-lhdn); search summary).
- **MyDigital ID and MyTax.**
  - LHDN accepted **MyDigital ID** as an SSO option for MyTax from **1 Jan 2025** ([Bernama](https://www.bernama.com/en/general/news.php?id=2522334)).
  - A 2024 report expected full integration by **1 Jan 2027** ([Lowyat, 2024](https://lowyat.net/2024/336335/lhdn-tnb-mydigital-id)). [PRE-2025 — possibly stale]
  - MyTax PINs can be obtained via selfie e-KYC (Feb 2026) ([Bernama](https://www.bernama.com/tv/news.php?id=2528818)).
  - No confirmation was found that MyDigital ID is mandatory for company representatives.

### Inferences
- **Shrinking mandate, unchanged rules for remaining users.** With the RM3m threshold, the *mandatory* e-invoice market shrinks to larger SMEs and group companies. Below RM3m, demand becomes voluntary, buyer-driven (large buyers want e-invoices for deductibility) and incentive-driven (RM50k deduction). The RM10k single-transaction rule still applies to those in scope.
- **The intermediary role is the legal anchor for agent e-invoice actions.** Agent actions should map one-to-one onto the permissions the director granted: submit, cancel, reject, with date bounds. Log every action against that appointment.
- **Liability allocation.** Because the taxpayer remains liable and penalties are per-transaction and possibly strict, the platform's terms must allocate liability for agent errors through indemnities, caps and insurance. Pre-submission validation and human approval for cancellations or credit notes reduce exposure.
- **Income-tax filing needs a different design.** For Form C/B/BE, CP204 or objections, either (a) partner with or employ approved s.153 tax agents who sign off, or (b) have the agent prepare drafts that the taxpayer submits under its own MyTax role. Representing taxpayers for reward without approval is likely a s.153 breach.

### Gaps
- The official LHDN MyInvois "Add/Manage Intermediary" guide and the e-Invoice Guideline v4.8 text were not read; whether LHDN imposes any certification of intermediaries or API "middleware" providers (e.g., an accredited-vendor list) was not confirmed.
- Whether MyTax has a non-tax-agent "representative" role for e-filing income-tax returns, and any LHDN API for e-filing by software vendors, were not found.
- Whether an intermediary can be personally liable under s.120 or other ITA provisions for erroneous e-invoices was not found.

## 6. Legal validity of agent-executed actions: Electronic Commerce Act 2006, Contracts Act 1950 agency, Digital Signature Act 1997, Consumer Protection (Electronic Trade Transactions) Regulations

### Takeaway
Malaysian law validates contracts formed by electronic messages (ECA 2006 s.7). Under **ECA s.17(2)(b)**, a message sent by an information processing system programmed by or for the originator to operate automatically is attributed to the originator. That is the strongest statutory hook for treating AI-agent actions as binding on the deploying business. The ECA has no express "electronic agent" provision; no amendment adding one was found; and no Malaysian case law applies Contracts Act agency principles to AI agents. The CPETT Regulations 2024 govern multi-vendor online marketplaces, not B2B agent middleware.

### Cited Findings
- **ECA s.7:** proposals, acceptances and revocations may be expressed by electronic message, and a contract is not invalid merely because an electronic message was used ([WIPO Lex – ECA 2006](https://www.wipo.int/wipolex/en/legislation/details/8179); [MyLaw](https://mylaw.my/legislation/akta-perdagangan-elektronik-2006)).
- **ECA s.17(2)(b):** a message sent by an information processing system programmed by or on behalf of the originator to operate automatically is deemed the originator's, as between originator and addressee ([ResearchGate – "Electronic Contracts, the Malaysian Perspective"](https://www.researchgate.net/publication/301554285_Electronic_Contracts_the_Malaysian_Perspective)). [PRE-2025 — possibly stale]
- **No e-agent provision.** Academic analysis concludes that an e-contract made by an e-agent is valid under ss.5, 7 and 17, but the Act "does not have any specific provision to recognize and validate e-agents" and should be amended ([ResearchGate](https://www.researchgate.net/publication/301554285_Electronic_Contracts_the_Malaysian_Perspective)).
- **No writing or signature requirement for simple contracts** under Malaysian law ([Allen & Gledhill](https://www.allenandgledhill.com/publication/articles/15066/my_restriction-of-movement-control-order-signing-contracts-electronically-during-trying-times)). [PRE-2025 — possibly stale]
- **Seals.** Where a law requires a seal, a **digital signature under the Digital Signature Act 1997** satisfies it for electronic messages, and the Minister may gazette other acceptable e-signatures ([Low & Partners](https://www.lowpartners.com/electronic-commerce-act-2006/)). Digital signatures give stronger signer-identity assurance than general e-signatures ([Mondaq](https://www.mondaq.com/new-technology/1420040/digital-signature-and-e-signature)).
- **General (non-Malaysian) 2026 commentary.** An AI agent rarely becomes a legal party; responsibility attaches to the organisation whose credentials and systems enabled the action, which must define the agent's limits of authority ([Zenodo white paper, 2026](https://zenodo.org/records/22730049)).
- **[REGULATIONS IN FORCE] Consumer Protection (Electronic Trade Transactions) Regulations 2024 (P.U.(A) 449/2024).**
  - In force **25 Dec 2024**, replacing the 2012 Regulations.
  - Cover multi-vendor online marketplaces, not single-vendor sites. Mandatory disclosures must be in Bahasa Malaysia; marketplaces have record-keeping and complaints duties.
  - Penalties: up to RM100k and/or 3 years for individuals, higher for repeat or corporate offences.
  - Sources: [Rödl & Partner](https://www.roedl.com/insights/newsflash-malaysia/2025_07/malaysia-consumer-protection-electronic-trade-transaction-regulations-2024); [OneAsia](https://oneasia.legal/en/wp-content/themes/standard_black_cmspro/img/EN_07-2025-CPETTR2024.pdf); [DNH](https://dnh.com.my/legal-updates-on-e-commerce-in-malaysia/).
  - *Conflict:* a seller blog says KPDN enforcement began 24 Jun 2025 ([BigSeller](https://www.bigseller.pro/blog/articleDetails/3364/malaysia-e-commerce-regulation-2025.htm)).
- **Dedicated e-commerce law.** KPDN is considering one ([The Vibes](https://www.thevibes.com/articles/news/111386/ministry-eyes-dedicated-e-commerce-law-to-enhance-digital-consumer-protection)).

### Inferences
- Under s.17(2)(b), an SME that configures the agent is very likely bound by what the agent sends: invoices, purchase orders, acceptances, submissions. The platform's main legal exposure is **contractual and tortious liability to the SME** when the agent acts outside instructions, not invalidity of the act.
- Mitigations:
  - explicit, scoped **mandates** (machine-readable authority limits), signed in-app;
  - per-action audit trails tying each message to the mandate;
  - human confirmation for high-value or irreversible acts;
  - clear ToS on error allocation.
- Where a statute requires a seal or a specific signature, or a government portal requires the individual's own login (MyTax, MyDigital ID), agents cannot replace the human or authorised representative. Use the portal's formal delegation (e.g., the MyInvois intermediary) rather than credential sharing.
- If the platform enables SMEs to sell to consumers through marketplace-like flows, CPETT 2024 disclosure duties (including Bahasa Malaysia) apply to listings the agent generates.

### Gaps
- No evidence was found of any Electronic Commerce (Amendment) Act or Digital Signature (Amendment) Act; this may reflect search limits.
- The ECA First Schedule exclusions were not verified. From background knowledge, they include powers of attorney, wills, trusts and negotiable instruments; if correct, an agent's *authority* cannot be granted by electronic power of attorney.
- No Malaysian judgment on automated or AI agents was found.
- What the "recent amendments" to CPETT 2024 changed was not confirmed.

## 7. Halal: legal basis, consultants, mandatory certification moves 2025–2026

### Takeaway
The legal basis for halal claims is the Trade Descriptions Act 2011 and its halal Orders (2011, amended 2024 and three times in 2026). JAKIM and the state religious councils (MAIN) certify. Certification is **voluntary** for domestic food premises and most products. Imported products may only be marked halal if certified by a JAKIM-recognised foreign body. Animal products are de facto mandatory. A draft mandatory-certification proposal for food premises has surfaced, but the government has repeatedly said it has no plans to enforce it. No rules on halal consultants were found.

### Cited Findings
- **The Orders.** The Trade Descriptions (Certification and Marking of Halal) Order 2011 is P.U.(A) 431/2011 ([ChemLinked database](https://food.chemlinked.com/database/view/5640)), with an Amendment Order 2024 ([ChemLinked](https://food.chemlinked.com/news/food-news/malaysia-issues-trade-descriptions-certification-and-marking-of-halal-amendment-order-2024)).
- **[ORDERS IN FORCE] 2026 amendments:**
  - **P.U.(A) 36/2026:** released 27 Jan, in force **30 Jan 2026**; amends the Second Schedule (foreign certification body names and logos) ([ChemLinked](https://food.chemlinked.com/database/view/6748)).
  - **(No. 2) Order:** in force **8 May 2026**.
  - **(No. 3) Order:** issued **20 Aug 2026**.
  - The No. 2 and No. 3 dates come from search summaries of ChemLinked pages ([ChemLinked foreign bodies list](https://food.chemlinked.com/expert-article/malaysias-list-of-recognized-foreign-halal-certification-bodies)).
- **Foreign bodies.** As of 30 Jan 2026, JAKIM recognises **94 foreign certification bodies across ~48 countries**. Imported products may only be described as halal if certified by a recognised body; imported meat and poultry plants also require JAKIM and DVS inspection ([Emerhub](https://emerhub.com/malaysia/jakim-recognized-foreign-halal-bodies/); [ChemLinked](https://food.chemlinked.com/expert-article/malaysias-list-of-recognized-foreign-halal-certification-bodies)).
- **Mandatory vs voluntary.**
  - Certification is mandatory for animal products (excluding pork) but not for other categories such as cosmetics ([Emerhub](https://emerhub.com/malaysia/how-to-get-halal-certificate-in-malaysia/)).
  - A parliamentary reply says applications "remain voluntary as they have been since … 1974"; Cabinet rejected mandatory certification for non-pork, non-alcohol eateries in 2024 ([FMT, Sep 2024](https://www.freemalaysiatoday.com/category/nation/2024/09/26/halal-certification-what-does-it-entail)). [PRE-2025 — possibly stale]
  - Kelantan's 2024 proposal to mandate certification raised federal–state legal issues ([Malay Mail, 31 Dec 2024](https://www.malaymail.com/news/malaysia/2024/12/31/council-vs-constitution-lawyers-explain-the-legal-tangle-behind-kelantans-proposal-to-mandate-halal-certs/161589)).
  - The religious affairs minister said a draft proposal to make halal certification mandatory for all food premises had been prepared for Cabinet; date unclear ([The Sun](https://thesun.my/local-news/halal-certification-report-to-be-presented-to-cabinet-this-wednesday-mohd-na-im-NC13006193)).
  - A later report: the government "has no plans to enforce halal cert for pork/alcohol-free restaurants" ([Daily Express, ~Jul 2026; date to verify](https://www.dailyexpress.com.my/news/245926/govt-has-no-plans-to-enforce-halal-cert-for-pork-alcohol-free-restaurants-says-na-im/)).
  - One low-authority source claims mandatory halal certification for imported F&B by 17 Oct 2026 (unverified). ChemLinked says enforcement for imported products was postponed to 2026 ([ChemLinked global halal](https://food.chemlinked.com/featured/global-halal-certification)).
- **Electronic certificates.** Malaysia launched electronic halal certificates ([ChemLinked Cosmetics](https://cosmetic.chemlinked.com/news/cosmetic-news/malaysia-launches-electronic-halal-certificates)); date not captured.
- **Enforcement.** KPDN enforces trade-description offences ([KPDN](https://www.kpdn.gov.my/en/submenu/enforcement-submenu/protecting-intellectual-property/trade-description)).

### Inferences
- An agent that drafts or files halal applications (MYeHALAL) or tracks certificate renewals has no specific licensing barrier on the evidence found. The key risk is an agent **generating or publishing halal claims or logos** in product listings or labels without valid certification, which is a TDA offence for the SME.
- Build hard guardrails: halal marks only where a valid JAKIM or recognised-foreign-body certificate is linked and unexpired.
- For importers, agent workflows should verify that a supplier's certifier is on the current JAKIM recognised list. The list changed three times in 2026.

### Gaps
- No source on JAKIM registration or regulation of **halal consultants** or consultancy firms was found.
- The 17 Oct 2026 imported-F&B mandatory date was not verified, and neither was the content of the 2026 No. 2 and No. 3 Orders.
- The status of any proposed standalone Halal Act was not found.

## 8. Online Safety Act 2025, CMA amendments, and data residency / cloud (Cloud First, MyGovCloud, sovereign cloud)

### Takeaway
The **Online Safety Act 2025 (Act 866)** has been in force since **1 Jan 2026** and applies to *licensed* application service providers (ASPs) and content application service providers (CASPs) under the CMA. It is largely irrelevant to a B2B agent middleware unless the platform hosts user-generated content as a licensed platform. Data residency is **not mandated by statute for private-sector or financial data**: RMiT has no residency rule. **Government classified data (Restricted/Confidential, NCII)** must stay onshore under the National Cloud Computing Policy and MyGovCloud@CFA procurement rules. A RM2bn MCMC sovereign AI cloud is being built.

### Cited Findings
- **[ACT IN FORCE] Online Safety Act 2025.**
  - Royal assent 6 May 2025; in force **1 Jan 2026**, together with the Online Safety (Form of Undertaking) Regulations 2025 (P.U.(A) 469/2025) ([Digital Policy Alert](https://digitalpolicyalert.org/event/36971-online-safety-bill-including-content-moderation-regulation-enters-into-force); [DPA – undertaking regs](https://digitalpolicyalert.org/event/36990-online-safety-form-of-undertaking-regulations-2025-enters-into-force); [DPA – royal assent](https://digitalpolicyalert.org/event/31888-adopted-online-safety-bill-including-content-moderation-regulation-was-signed-by-king)).
  - Applies to licensed ASPs and CASPs. Duties: mitigate 9 categories of harmful content; **CSAM and financial fraud are "priority harmful content"**; publish an Online Safety Plan; acknowledge user reports within one hour.
  - Creates an Online Safety Committee and an Appeal Tribunal ([Conventus Law](https://conventuslaw.com/report/malaysia-corporate-ma-update-the-online-safety-act-2025/)).
- **[POLICY] National Cloud Computing Policy (Ministry of Digital).**
  - Calls for sovereign cloud with reputable CSPs so critical data is "stored, processed, and accessed within national boundaries".
  - Four-tier data classification; the top tier (Confidential, including NCII data) is to be stored only in **sovereign cloud zones in Malaysia**.
  - Sources: [NCCP PDF](https://www.digital.gov.my/api/file/file/FINAL%20-%20MALAYSIA%E2%80%99S%20NATIONAL%20CLOUD%20COMPUTING%20POLICY%20(MNCCP).pdf); [MoD launch release](https://www.digital.gov.my/en-GB/siaran/Pelancaran-Dasar-Pengkomputeran-Awan-Negara-(NCCP)-Malaysia); [Aqvantiq](https://aqvantiq.com/blog/malaysia-cloud-compliance-guide/).
- **MyGovCloud@CFA.** Agencies handling **Restricted and Confidential** official information must limit market studies to providers offering **in-country data residency**. Private-sector residency constraints come mostly from contracts and sector policy, not statute ([Aqvantiq](https://aqvantiq.com/blog/malaysia-cloud-compliance-guide/)).
- **Sovereign AI cloud.** Budget 2026 allocated **RM2bn** for an MCMC-led Sovereign AI Cloud ([Lowyat](https://www.lowyat.net/2025/369197/budget-2026-mcmc-sovereign-ai-cloud-rm2-billion-investment/)). On **15 Oct 2026**, Fahmi Fadzil said it will keep classified data beyond the reach of foreign laws, managed by MCMC and the Communications Ministry ([Malay Mail](https://www.malaymail.com/news/malaysia/2026/10/15/malaysia-is-building-its-own-digital-cloud-to-safeguard-data-sovereignty-minister-says/239161); [OpenGov Asia](https://opengovasia.com/malaysia-plans-sovereign-cloud-to-protect-critical-data/?c=us)).
- **Data Sharing Act 2025.** Described as governing inter-agency government data exchange; secondary description only, sovereignty provisions not confirmed ([search summary; see Aqvantiq](https://aqvantiq.com/blog/malaysia-cloud-compliance-guide/)).

### Inferences
- For private SME data, hosting abroad is lawful subject to PDPA s.129 (Q1). Onshore hosting is nonetheless a selling point for banks (smoother BNM outsourcing approvals) and essential for any government-facing agent work.
- If agents touch government systems in ways that involve classified information (unlikely for LHDN/SSM taxpayer-facing APIs), only sovereign or in-country clouds qualify.
- The OSA becomes relevant only if the platform adds consumer-facing community or content features and meets ASP/CASP licensing criteria. Fraud as "priority harmful content" signals regulator focus on agent-enabled scams.

### Gaps
- The NCCP launch date, and whether the 2017 Cloud First policy or MAMPU-era public-sector cloud frameworks were formally replaced, were not confirmed.
- No details were found on 2025 CMA amendments (e.g., social media licensing thresholds); the search budget was exhausted.
- The Data Sharing Act 2025 text and commencement were not confirmed.

## 9. Tailwinds: grants, incentives, sandboxes and government AI-adoption targets for MSMEs (2025–2026), incl. Budget 2026 and Budget 2027

### Takeaway
Policy momentum is strongly pro-AI-adoption:
- **Budget 2026** (tabled 10 Oct 2025): RM5.9bn AI/digital, RM2bn sovereign AI cloud, a 50% additional deduction for SME AI and cyber training.
- **Budget 2027** (tabled **9 Oct 2026**): RM30m via MDEC for **4,000 MSMEs to adopt AI**, RM2:RM1 government co-investment through ECF/P2P for SME AI/robotics/digital until 2030, a 1-ppt SME tax cut, and AI subscriptions in lifestyle relief.

The flagship SME voucher (Geran Digital PMKS MADANI: 50% match, up to RM5k via MDEC-registered Digitalisation Partners) has uncertain 2026 status. AI Malaysia's plan targets Top-10 AI readiness by 2030; about **27% of businesses** reportedly use AI.

### Cited Findings
- **[BUDGET 2026, tabled 10 Oct 2025]** ([MDEC](https://www.mdec.my/media-release/news-press-release/402/belanjawan-madani-2026-a-%E2%80%98strategic-whole-of-nation-catalyst%E2%80%99-for-ai-nation-2030,-says-mdec); [MoD Budget 2026 release](https://www.digital.gov.my/en-GB/siaran/Peruntukan-Dalam-Belanjawan-Madani-2026-Akan-Merangsang-Transformasi-Digital-Malaysia); [The Vibes](https://www.thevibes.com/articles/news/113843/budget-2026-malaysia-bets-big-on-ai-and-homegrown-innovation); [Lowyat](https://www.lowyat.net/2025/369197/budget-2026-mcmc-sovereign-ai-cloud-rm2-billion-investment/)):
  - **RM5.9bn** for AI R&D, commercialisation and innovation;
  - **RM2bn** sovereign AI cloud (MCMC);
  - RM18.1m for NAIO;
  - **50% additional tax deduction for SMEs** on AI and cybersecurity training certified by NAIO/NAICI.
- **Unverified Budget 2026 items** (secondary sources): an **MDAG-AI** scheme reimbursing up to 70% of AI project cost, capped at RM2m ([Gotchaa Lab](https://gotchaa-lab.com/blog/2026-03-02-malaysia-ai-nation-budget-2026-business-guide)), and a Malaysia Digital Acceleration Grant of RM53m ([AITraining2u](https://www.aitraining2u.com/ai-adoption-incentives-malaysia-sme-2026.html)).
- **[BUDGET 2027, tabled 9 Oct 2026; Finance Bill not yet passed]** ([The Star, 11 Oct 2026](https://www.thestar.com.my/news/nation/2026/10/11/digital-ministry-pushes-ai-nation-goal-under-budget-2027); [OpenGov Asia](https://opengovasia.com/malaysia-budget-2027-advances-ai-adoption-and-digital-transformation/); [Digital News Asia](https://www.digitalnewsasia.com/digital-economy/budget-2027-malaysias-fifth-madani-budget-targets-200000-skilled-ai-professionals); [Microsoft Source Asia](https://news.microsoft.com/source/asia/features/microsoft-welcomes-budget-2027s-focus-on-accelerating-malaysias-ai-nation-ambition/); [Funding Societies](https://blog.fundingsocieties.com.my/budget-2027-malaysia/); [JW Tan](https://www.jwtan.co/blog/budget-2027)):
  - **RM30m via MDEC to help 4,000 MSMEs adopt AI and automate**;
  - training and certification for 5,000 AI professionals, under a headline target of 200,000 skilled AI professionals;
  - **RM2 of government co-investment for every RM1** raised by SMEs and mid-tier firms via ECF/P2P for robotics, AI and digital, until 2030;
  - SME tax rates cut by 1 ppt;
  - AI software and app subscriptions added to individual lifestyle relief from YA2027 (within the RM2,500 cap);
  - 100,000 free AI-app subscriptions for youth;
  - RM142m for NADI centres;
  - ACA for ICT reportedly extended to 2030 (single source);
  - a "RM7,500 matching grant per business" is reported by one source only and is **unconfirmed**.
- **Geran Digital PMKS MADANI (GDPM).**
  - Terms: **50% matching grant, up to RM5,000**, via BSN, through **MDEC-registered Digitalisation Partners**. Eligibility: at least 60% Malaysian-owned, operating at least 6 months, turnover at least RM50k ([BSN](https://www.bsn.com.my/page/GeranDigitalPMKSMadani?lang=ms-MY); [Gkash](https://gkash.com/mdec-digital-grant-madani/)).
  - The 2025 round **closed 5 Sep 2025**, and no 2026 round was confirmed ([BCL](https://main.bcl.my/msme-digital-grant/)). This conflicts with a blog saying it was still open in Aug 2026 ([Zenweb](https://zenweb.my/blog/sme-digitalisation-grant-digital-marketing/)).
- **e-Invoice incentive.** Deduction up to **RM50k per YA (YA2024–YA2027)** for voluntary e-invoice implementation costs ([The Star, 30 Aug 2026](https://thestar.com.my/news/nation/2026/08/30/over-11-million-businesses-to-benefit-from-higher-e-invoicing-threshold-says-lhdn)).
- **Adoption targets and statistics.** AI Nation 2030 targets: +1.2 ppt GDP, up to 300k AI jobs, Top 10 in global AI indices ([Action Plan PDF](https://strapi.naio.okie.my/uploads/AI_Nation_2030_National_AI_Action_Plan_2026_2030_Eng_V_290726_49cb382621.pdf); [fact sheet](https://ai.gov.my/faq/national-ai-action-plan-2026-2030-fact-sheet/)). Reported current adoption: AI use up 35% year on year, **~2.4m businesses (27%) using AI in some form** ([AI Malaysia fact sheet / US-ASEAN, per search summary](https://www.usasean.org/article/malaysia-accelerates-national-ai-agenda)).
- **Sandboxes.** The BNM Green Lane 2026 cohort (Q4). The Central AI Authority under the proposed AI Governance Bill is to operate **AI sandboxes** ([Baker McKenzie](https://www.bakermckenzie.com/en/insight/publications/2026/07/malaysia-public-consultation-on-the-ai-governance-bill)).

### Inferences
- **Grant-eligible vendor.** Registering as an **MDEC Digitalisation Partner** is the gateway to GDPM-type vouchers and probably to the Budget 2027 RM30m MSME AI adoption programme. Prioritise this.
- **Pitch: "grant-funded agent onboarding"**, combining the RM50k e-invoice deduction (voluntary adopters below RM3m), GDPM's 50% match, the SME training deduction (Budget 2026), and the Budget 2027 ECF/P2P co-investment for larger AI rollouts.
- **Market sizing.** The 27% AI-usage figure and the 4,000-MSME target show government willingness to subsidise adoption, but the programme scale is modest: RM30m is roughly RM7.5k per firm.

### Gaps
- No official confirmation of a 2026 GDPM round, or of Budget 2027 grant mechanics (application windows, eligible vendors, the RM7,500 figure).
- **MD (Malaysia Digital) status** incentives for an AI-agent platform company (tax rates, eligibility for AI and SaaS activities) were not researched; the search budget was exhausted.
- No official numeric MSME AI-adoption *target* was found, only the current 27% usage statistic and programme counts.

## 10. Cross-cutting: what all this means for an AI-agent business-action platform (obligations, licensing, risk summary)

### Takeaway
As of Oct 2026, **no licence is required simply to operate an AI-agent platform that executes business actions in Malaysia**. Formal authorisation is channel-specific:
- MyInvois intermediary appointment by the director;
- an s.153 tax agent for income-tax representation;
- a BNM licence only if the platform holds or moves funds itself;
- a CSSP licence only for SOC or pen-testing services.

The binding obligations today are PDPA (processor security, DPO, cross-border, DPIA/ADMP), contractual flow-downs from regulated customers (RMiT/Outsourcing, CSA NCII codes), and per-transaction tax liability borne by customers. The major pending change is the **AI Governance Bill** (tabling targeted by Q1 2027), which will likely make the platform a regulated "Deployer" with risk assessment, human-oversight and incident-reporting duties.

### Cited Findings
- No licensing regime specific to AI agents exists. The AI Governance Bill is still a proposal, with the draft complete as of 10 Sep 2026 ([AI Commission report](https://aicommission.org/2026/09/digital-minister-says-malaysias-draft-ai-governance-bill-complete-hopes-to-table-it-by-q1-2027/); [Baker McKenzie](https://www.bakermckenzie.com/en/insight/publications/2026/07/malaysia-public-consultation-on-the-ai-governance-bill)).
- The MyInvois intermediary appointment is the formal delegation for e-invoice actions; the taxpayer remains responsible ([AJobThing](https://www.ajobthing.com/resources/blog/how-appoint-intermideary-e-invoice-submission-myinvois)).
- Only s.153 tax agents may represent taxpayers under the ITA ([MAICSA](https://www.maicsa.org.my/media/4334/students_recognition_tax.pdf)).
- CSSP licensing is limited to SOC monitoring and penetration testing ([Baker McKenzie](https://insightplus.bakermckenzie.com/bm/data-technology/asia-pacific-malaysia-cyber-security-act-2024-and-subsidiary-regulations-in-force-on-26-august-2024)).
- Processors are directly bound by the PDPA Security Principle, and the DPO duty extends to processors ([Mayer Brown](https://www.mayerbrown.com/en/insights/publications/2025/07/from-legislative-reform-to-practical-guidance-key-amendments-to-malaysias-pdpa-and-the-launch-of-cross-border-transfer-guidelines); [Christopher & Lee Ong](https://www.christopherleeong.com/viewpoints/launch-of-the-personal-data-protection-guidelines-for-mandatory-data-breach-notification-and-data-protection-officer-appointment/)).
- Automated electronic messages are attributed to the originator ([ResearchGate on ECA s.17](https://www.researchgate.net/publication/301554285_Electronic_Contracts_the_Malaysian_Perspective)).

### Inferences
**Risk matrix (likelihood × impact, analyst judgement):**
1. **High: erroneous or unauthorised agent submissions.** Strict-liability, per-invoice penalties fall on the SME, which pushes liability back to the platform contractually. Mitigate with scoped mandates, pre-validation, human approval for irreversible actions, and immutable logs.
2. **High: PDPA cross-border transfers to foreign LLM providers.** Mitigate with TIAs, SCCs, and Malaysian-hosted model options.
3. **Medium-high: AI Governance Bill compliance from ~2027.** Expect Tier 2 obligations. Start a model and agent risk register, DPIA/ADMP alignment, and an incident-reporting playbook now.
4. **Medium: unlicensed tax representation.** Use a tax-agent partnership or a taxpayer-submits UX.
5. **Medium: regulated-customer flow-downs** (RMiT third-party rules, Outsourcing approvals, CSA NCII codes). Prepare SBOMs, audit rights, exit and stand-in plans, and 6-hour incident cooperation.
6. **Low-medium: payment licensing.** Avoid custody of funds; use the customer's own bank rails and the future Open Finance consent framework.
7. **Low: halal mislabelling by generative agents.** Add certificate-linked guardrails.

**Policy tailwinds to exploit:** the RM3m e-invoice threshold creates a voluntary and group-company segment; the RM50k e-invoice deduction; MDEC Digitalisation Partner status for GDPM and Budget 2027 AI-adoption money; AI Malaysia, MY-AISafe and Central AI Authority sandboxes; sovereign-AI alignment through onshore hosting or ILMU compatibility.

### Gaps
- A Malaysian practitioner analysis of liability allocation for AI-agent errors, and any regulator statement on agentic AI executing transactions, were not found.
- Primary-source verification is outstanding for: Guideline v4.8, the JPDP April 2026 guidelines, the NAIO consultation paper, the BNM Open Finance ED, and RMiT Nov 2025/Sep 2026.
