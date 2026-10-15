# Malaysian Government & Statutory-Body APIs for AI-Agent Business Task Execution (state as of mid-October 2026)

> Research method note (read first): Research done 15 Oct 2026. The research tool could not open most Malaysian government and news sites directly (DNS/proxy failures for hasil.gov.my, sdk.myinvois.hasil.gov.my, thestar.com.my, bdo.my, etc.). So the findings below come from (a) web-search result summaries of those pages, (b) the npm registry, and (c) raw GitHub files. Source (c) includes a community mirror of the official MyInvois SDK docs (deadboy18/myinvois-docs, "last verified August 2026"), which was read directly. The shared web-search budget ran out before the SSM BizTrust, bank host-to-host statutory payments, MyEG/JPJ API and SSM e-Info API queries could run. Those appear as gaps. Each claim carries a date. Anything dated before 2025 is marked **[PRE-2025, possibly stale]**.

---

## Summary inventory: which systems expose APIs, and how does a third-party platform get access?

### Takeaway
LHDN MyInvois is the only Malaysian government system with a well-documented, public, write-capable REST API. It has an explicit "intermediary / on-behalf-of" model, which makes it the natural first target for an agent platform. The other systems fall into three groups:
- **Read-only open data APIs:** data.gov.my / OpenDOSM.
- **Licensed-intermediary-only data access:** SSM company data through four appointed service providers; customs declarations through licensed customs agents over the Dagang Net National Single Window.
- **Portal / file-upload only, with no public API found:** MySST, e-PCB Plus, e-Duti Setem, KWSP e-Caruman, PERKESO ASSIST, HRD Corp eTRiS, SSM MBRS, JAKIM MYeHALAL, and local-council licensing.

MyDigital ID, MyGDX and PADU are government-side platforms with no published private-sector developer onboarding as of Oct 2026.

### Cited Findings
Inventory matrix. "Verified" means the claim comes from an official page or doc mirror; otherwise the source type is stated.

| System (operator) | Public/partner API? | How access is obtained | Auth model | Sandbox | Actions possible | Status / roadmap (dated) |
|---|---|---|---|---|---|---|
| **MyInvois e-Invoice (LHDN/IRBM)** | **Yes, public REST API** ([SDK e-Invoice APIs](https://sdk.myinvois.hasil.gov.my/einvoicingapi)) | Taxpayer registers its ERP in the MyInvois portal and gets a Client ID/Secret. An intermediary logs in "on behalf of" a taxpayer once the taxpayer grants it permissions ([Login as Intermediary](https://sdk.myinvois.hasil.gov.my/api/08-login-as-intermediary-system/)) | OAuth 2.0 client-credentials at `/connect/token`, plus an `onbehalfof` header (TIN, or TIN:ROB) for intermediaries ([official doc via mirror](https://github.com/deadboy18/myinvois-docs/blob/main/02-platform-api/02-login-intermediary.md)) | Yes: `preprod-api.myinvois.hasil.gov.my` ([mirror README](https://github.com/deadboy18/myinvois-docs)) | **Write:** submit, cancel, reject, bulk cancel (new Sept 2026). **Read:** validate TIN, search TIN, QR-code lookup, get/search documents, notifications | All 4 phases live. Exemption threshold raised to RM3m (General Guideline v4.8, 30 Aug 2026). Relaxation for Phase 4 runs to 31 Dec 2027 (see Q1) |
| **MDEC Peppol (MY Peppol Authority)** | Yes, via accredited Peppol Access Points | Become an MDEC-accredited Peppol Service Provider (OpenPeppol membership plus MDEC/IRBM security requirements) ([ClearTax list](https://www.cleartax.com/my/en/top-e-invoicing-solution-provider-malaysia)) | Peppol AS4 / SMP (standard) | n/a | Send/receive e-invoices; route to MyInvois | Voluntary ([OpenPeppol](https://peppol.org/learn-more/country-profiles/malaysia/)) |
| **MyTax / e-PCB Plus (LHDN)** | No public API found | Employer or representative portal login; payroll software produces a .txt file for upload ([BrioHR](https://support.briohr.com/knowledge/e-pcb-plus-for-mtd-submissions-and-payments)) | MyTax login (human) | No | Upload MTD/PCB file, then pay | e-PCB Plus mandatory. e-Data PCB, e-PCB and e-CP39 being deactivated (vendor sources) |
| **e-Duti Setem (LHDN, on MyTax)** | No API found | MyTax login. Each user needs a TIN ([KPMG US TNF, Dec 2025](https://kpmg.com/us/en/taxnewsflash/news/2025/12/tnf-malaysia-stamp-assessment-and-payment-system-replaced-by-e-duti-setem-starting-january-1-2026.html)) | Portal | No | Self-assess, declare, pay stamp duty | Replaced STAMPS from 1 Jan 2026. Self-assessment regime |
| **MySST (JKDM/RMCD)** | No API found ([MySST guides](https://mysst.customs.gov.my/SystemGuides)) | Portal registration | Portal | No | Register, file SST-02, pay; public registration-status lookup | Live |
| **SMK / NSW (Dagang Net, myTRADELINK) and uCustoms (JKDM)** | EDI/NSW messaging for licensed parties. No open API found | Only JKDM-licensed customs agents file declarations ([DNE Forwarding 2026](https://dnelogistics.com.my/customs-clearance-malaysia-guide.html)) | Dagang Net subscription | Unknown | K1/K2/K8/K9 declarations, permits (ePermit), manifests | SMK still running K1/K2/K9 as of Jan 2026. uCustoms rolling out station by station (forwarder source) |
| **SSM company data (MyDATA-SSM, e-Info, SSM Search, SAFEDATA)** | **Partner API only**, via appointed service providers | Contract with one of four appointed SSM data service providers (e.g., Infomina gave CTOS API access, Jun 2025) ([The Star](https://www.thestar.com.my/business/business-news/2025/06/20/ctos-infomina-pact-for-ssm-data-access)) | Provider-specific | Unknown | Read: company/business profiles, certified copies | No SSM developer portal ([Business Data Guide, Sep 2026](https://www.businessdataguide.com/blog/jurisdictions/malaysia-company-search-guide)) |
| **SSM MBRS 2.0 (XBRL filing)** | No API ([Fareez Law](https://fareezlaw.com/mbrs/)) | mTool desktop app plus mPortal upload | Portal | No | File XBRL financial statements | XBRL AFS mandatory for all companies from 1 Jun 2025 (law-firm source) |
| **KWSP/EPF i-Akaun (Majikan) e-Caruman** | No public API found | Employer i-Akaun. CSV/TXT format must be approved by EPF ([EPF FAQ 2017](https://secure.kwsp.gov.my/e-caruman/download/SOALAN_LAZIM_e-Caruman_EN_as_at_19052017.pdf)) | Portal | No | Upload contribution file (Form A), pay | Since 1 Jan 2026 EPF no longer posts statements; employers download from i-Akaun ([KWSP](https://www.kwsp.gov.my/en/w/announcement/enotices-available-on-iakaun-employer)) |
| **PERKESO ASSIST / ASSIST 2.0 (SOCSO + EIS)** | No API found. Combined text-file upload | Employer portal | Portal | No | Upload combined SOCSO+EIS text file, pay | ASSIST 2.0 (planned 30 Jun 2026) postponed to a date to be announced ([HR Online](https://www.humanresourcesonline.net/socso-revised-contribution-rates-for-june-july-2026-not-yet-reflected-in-e-payroll-as-system-undergoes-enhancements)) |
| **HRD Corp eTRiS** | No API found | Employer login with MyCoID ([PayrollPanda](https://www.payrollpanda.my/help/how-and-when-to-make-hrdf-levy-payments/)) | Portal | No | Levy e-slip (Form 2), payment, training claims | Live |
| **JAKIM MYeHALAL / Verify Halal** | No public developer API found | Public portal lookup; Verify Halal app (built by Serunai Commerce) | n/a | No | Read: certificate status lookup. Write: applications via portal | MYeHALAL 2.0 with AI screening announced May 2026 ([Malay Mail](https://www.malaymail.com/news/malaysia/2026/05/23/jakim-to-harness-ai-in-myehalal-20-promises-faster-halal-certification-approvals/221058)) |
| **MyDigital ID (MyDigital ID Sdn Bhd)** | Relying-party integration exists, but **no public onboarding terms** ([Didit, 5 Oct 2026](https://didit.me/blog/mydigital-id-integration/)) | Bilateral onboarding/MoU. Banks are in a BNM/MOF sandbox | Not published (OIDC not confirmed) | Bank sandbox phases | Login/identity verification | 12m users, 114 govt services (30 Jun 2026) |
| **MyGDX (JDN)** | Yes, but **government-agency only** | Agency subscription through the MyGDX API catalogue ([MyGDX](https://mygdx.gov.my/ms/landing-page/theme?theme=third-theme&uuid=+&year=)) | Not published | Unknown | Inter-agency data verification | MyGDX 2.0 launched 10 Feb 2026 |
| **PADU (DOSM/Ministry of Economy)** | No (govt-only) | Govt agencies only. "We will not open Padu to the private sector" (Apr 2026) | n/a | n/a | n/a | Adding analytics for agencies from May 2026 |
| **data.gov.my / OpenDOSM (JDN/DOSM)** | **Yes, open REST API** ([developer.data.gov.my](https://developer.data.gov.my/)) | Open. Optional token by email to dataterbuka@jdn.gov.my ([auth](https://developer.data.gov.my/authentication)) | None, or `Authorization: Token <t>` | n/a | Read-only statistics/open data | Live. 4 req/min default ([rate limit](https://developer.data.gov.my/rate-limit)) |
| **MyGOV Malaysia app (Ministry of Digital)** | No third-party API. Citizen super-app | MyDigital ID login | n/a | n/a | 52 services from 19 agencies (Jul 2026). In-app agentic AI in beta since Aug 2026 | See Q6 |
| **Local councils (PBT) business licences** | No API found. Per-council portals (e.g., MBPJ eLesen) plus federal ePBT portal | Council portal accounts | Portal | No | Apply/renew licences | Renewal cycles run per council |
| **MyEG (commercial e-government concessionaire)** | No Malaysian developer API found (MYEG Philippines markets a payment-gateway API) | n/a | n/a | n/a | Consumer app: road tax, summons, SSM data, MyDigital ID | App updated 6 Oct 2026 |

### Inferences
- For a third-party agent platform, the only "submit on behalf of a business" API that is legally and technically sanctioned today is MyInvois, through the intermediary login. Everything else (payroll statutory filings, SST, stamp duty, SSM filings, council licences) needs one of two approaches. The first is file generation plus a human (or browser-automation) upload into a portal under the business's own credentials. The second is going through a licensed intermediary (customs agent, SSM data provider, Peppol AP).
- Browser automation of portals carries risk: credential custody, portal ToS, and SSM's reported anti-scraping terms. This is an inference; I did not read the portal ToS directly.
- Regulators are not converging on public APIs for SMEs. Instead they are moving toward: (1) the government's own super-app (MyGOV) with its own agentic AI, (2) MyDigital ID as the identity layer, and (3) government-internal data exchange (MyGDX). Private agent platforms may end up competing with or complementing MyGOV's agent rather than plugging into it.

### Gaps
- No official API catalogue for private-sector access to any agency other than LHDN MyInvois and data.gov.my was found.
- The search budget ran out before I could check: SSM e-Info's advertised "API integration" terms, MyEG B2B APIs, JPJ APIs for insurers/road-tax agents, bank host-to-host statutory payment files, and SSM BizTrust.

---

## Q1. LHDN MyInvois e-invoicing: API capabilities, intermediary model, mandate timeline/thresholds, consolidated rules, Peppol, adoption, pain points; and other LHDN APIs

### Takeaway
MyInvois has a mature REST API (OAuth2 client-credentials, UBL 2.1 XML/JSON, XAdES signing in document v1.1). It supports a first-class intermediary ("onbehalfof") model and covers submit, cancel, reject, TIN validate/search, QR lookup and document search. Bulk cancellation was added in Sept 2026, and TIN+BRN combination validation in Aug 2026.

The mandate has changed four times:
1. The exemption threshold went from RM150k to RM500k, then to RM1m (announced Dec 2025, which also cancelled Phase 5).
2. It then went to RM3m under General Guideline v4.8 (30 Aug 2026).
3. The Phase 4 penalty-relaxation period now runs to 31 Dec 2027, with enforcement from 1 Jan 2028.

About 268,000 businesses and ~1.9 billion submissions had been recorded as of 1 Oct 2026. No other LHDN service (MyTax, e-PCB Plus, e-Duti Setem, e-Filing, CP204) has a public API that I could find.

### Cited Findings

**API surface (official SDK; verified via official pages and the Aug-2026 community mirror)**
- Platform APIs: Login as Taxpayer System, Login as Intermediary System, Get All Document Types, Get Document Type, Get Document Type Version, Get Notifications — [MyInvois SDK Platform API (mirror of sdk.myinvois.hasil.gov.my/api/)](https://github.com/deadboy18/myinvois-docs/blob/main/02-platform-api/README.md)
- e-Invoice APIs: Validate Taxpayer's TIN, Submit Documents, Cancel Document, Reject Document, Get Recent Documents (last 31 days only), Get Submission, Get Document, Get Document Details, Search Documents, Search Taxpayer's TIN, Taxpayer's QR Code. The QR Code API "search[es] and retrieve[s] the information for a specific Taxpayer based on the Base64 formatted string obtained from scanning the respective QR code" — [SDK e-Invoice APIs](https://sdk.myinvois.hasil.gov.my/einvoicingapi); [mirror](https://github.com/deadboy18/myinvois-docs/blob/main/03-einvoice-api/README.md)
- Search TIN signature: `GET /api/v1.0/taxpayer/search/tin?idType=&idValue=&taxpayerName=&fileType=`, 60 RPM — [SDK: Search Taxpayer TIN](https://sdk.myinvois.hasil.gov.my/einvoicingapi/10-search-taxpayer-tin/)
- Auth: "solution leverages OAuth 2.0 client credentials flow" via `POST /connect/token` on the identity service. Tokens expire per `expires_in`, and the community mirror says the default is 60 min — [Login as Intermediary System (official)](https://sdk.myinvois.hasil.gov.my/api/08-login-as-intermediary-system/); [mirror pitfalls page](https://github.com/deadboy18/myinvois-docs/blob/main/12-cookbook/05-common-pitfalls.md)
- **Intermediary model:** "When trying to login as intermediary, add an extra header parameter… `onbehalfof`… TIN of the taxpayer the intermediary is representing" (e.g., `C25845632020` or `IG12345678912:201901234567` for TIN:ROB). "Permissions that are granted by the taxpayer will be applied on the intermediary's profile and this will control the functionalities that they will be able to execute on behalf of the taxpayer" — [SDK Login as Intermediary (via mirror)](https://github.com/deadboy18/myinvois-docs/blob/main/02-platform-api/02-login-intermediary.md)
- An intermediary can only access documents it submitted on behalf of a taxpayer (third-party guide summarising SDK) — [ClearTax: Login as Intermediary API](https://www.cleartax.com/my/en/login-intermediary-system-api)
- Rate limits per Client ID: Login 12 RPM (both), Submit 100, Get Submission 300, Cancel 12, Reject 12, Get Document 60, Get Document Details 125, Get Recent Documents 12, Search Documents 12, Search TIN 60, QR Code 60. 429 responses carry `Retry-After`. The sandbox has lower limits (effective 28 Apr 2025) and 3 months of data retention — [SDK Integration Practices](https://sdk.myinvois.hasil.gov.my/integration-practices/); [mirror rate-limits page](https://github.com/deadboy18/myinvois-docs/blob/main/12-cookbook/04-rate-limits.md)
- Environments: prod `api.myinvois.hasil.gov.my`, sandbox `preprod-api.myinvois.hasil.gov.my`. Sandbox and prod credentials are separate (you register the ERP in each portal) — [mirror README](https://github.com/deadboy18/myinvois-docs); [pitfalls](https://github.com/deadboy18/myinvois-docs/blob/main/12-cookbook/05-common-pitfalls.md)
- Sandbox access originally required emailing LHDN for a Client ID/Secret with TIN, BRN, company name, email and ERP name. Pilot access started 10 Apr 2024 and general access 22 Apr 2024 **[PRE-2025, possibly stale; today ERP registration is self-service in the portal per the mirror]** — [Bernama](https://www.bernama.com/en/general/news.php?id=2287230); [The Sun](https://thesun.my/local_news/lhdn-myinvois-sandbox-test-environment-now-accessible-LB12319301)
- Production API opened 24 May 2024 **[PRE-2025]** — [Malay Mail](https://www.malaymail.com/news/malaysia/2024/05/24/irb-myinvois-system-production-environment-via-application-programming-interface-opened-companies-can-issue-e-invoices/136308)
- Digital certificates for signing (doc v1.1) come from MCMC-licensed CAs: Pos Digicert, MSC Trustgate, Rafftech, TM Applied Business — [mirror README](https://github.com/deadboy18/myinvois-docs)

**2026 API changes (official release notes, as summarised by search)**
- 12 Jun 2026: the Validate TIN API will check TIN+BRN combinations from 1 Aug 2026 — [SDK Release Notes](https://sdk.myinvois.hasil.gov.my/release-notes/); [VATupdate 14 Jun 2026](https://www.vatupdate.com/2026/06/14/myinvois-sdk-1-0-adds-tin-brn-validation-from-august-2026/)
- 8 Jul 2026: new document versions SVDP 1.2 (unsigned) and SVDP 1.3 (signed), usable only for the Special Voluntary Disclosure Programme (to 31 Dec 2027) — [SDK Release Notes](https://sdk.myinvois.hasil.gov.my/release-notes/); [VATupdate 9 Jul 2026](https://www.vatupdate.com/2026/07/09/myinvois-sdk-1-0-svdp-document-versions-and-tin-brn-validation-from-august-2026/)
- 6 Aug 2026: monetary amount fields get a 26-digit max length — [SDK Release Notes](https://sdk.myinvois.hasil.gov.my/release-notes/)
- 21 Sep 2026: **Bulk Cancellation** and **Get Bulk Cancellation Status** endpoints; a classification-code filter on Search Documents; an optional version parameter on Get Document/Details; validator error reference pages. Sandbox from 25 Sep 2026, **production 24 Oct 2026** — [SDK Release Notes](https://sdk.myinvois.hasil.gov.my/release-notes/)
- Scientific notation is no longer accepted in amounts, and State Code 17 is restricted to consolidated/foreign transactions (secondary source; exact dates not confirmed) — [Fiscal Solutions](https://www.fiscal-requirements.com/news/5637)

**Mandate timeline & thresholds**
- Phases: 1 Aug 2024 (>RM100m), 1 Jan 2025 (RM25m–100m), 1 Jul 2025 (RM5m–25m), 1 Jan 2026 (up to RM5m). Turnover is based on FY2022 audited accounts or YA2022 return — [mirror: implementation timeline, citing General Guideline v4.7/v4.8](https://github.com/deadboy18/myinvois-docs/blob/main/12-cookbook/10-implementation-timeline.md)
- Dec 2025: exemption threshold raised from RM500,000 to RM1 million. The planned final phase for sub-RM500k businesses (Phase 5) was cancelled and the 1 Jan 2026 date unchanged — [VATupdate 17 Dec 2025](https://www.vatupdate.com/2025/12/17/malaysia-raises-e-invoicing-exemption-threshold-to-rm1-million-cancels-final-implementation-phase/); [Info-Tech](https://www.info-tech.com.my/blog/malaysia-new-e-invoice-guidelines/)
- 30 Aug 2026: General Guideline v4.8 raised the exemption from RM1m to **RM3m** (§1.6.1(e)). It includes a related-party carve-out (§1.6.10): no exemption if a non-individual shareholder, holding/related company or JV has revenue ≥RM3m. Sole proprietorships under the same person are aggregated — [JomeInvoice v4.8](https://jomeinvoice.my/article/lhdn-e-invoice-general-guideline-v4-8-rm3-million-exemption/); [VATupdate 8 Sep 2026](https://www.vatupdate.com/2026/09/08/malaysia-raises-e-invoice-exemption-threshold-to-myr-3-million/); [Kalyx](https://www.kalyxconsultants.com.my/post/malaysia-e-invoice-2026-latest-implementation-timeline). **Conflict:** one source gives the effective date as 1 Sep 2026, and others tie it to the 30 Aug publication. One source said LHDN had issued no media release/FAQ at the time. A consultant page dated 4 Sep 2026 claims RM3m with businesses below RM3m "implementing from 1 July 2026", which conflicts with the exemption reading — [SME Advisor](https://sme-advisor.com/einvoice-consultant)
- New businesses: those that started 2023–2025 with turnover ≥RM3m are mandatory from 1 Jul 2026. Those starting 2026 onward are mandatory from 1 Jul 2026 or commencement, whichever is later (if first-year revenue <RM3m, from 1 Jan of the second year after crossing RM3m) — [mirror timeline](https://github.com/deadboy18/myinvois-docs/blob/main/12-cookbook/10-implementation-timeline.md)
- Relaxation (penalty grace): originally 6 months, then extended to 12 months. In April 2026 (Specific Guideline v4.7, reportedly announced by PM Anwar on ~20 Apr 2026 as part of SME relief), the Phase 4 relaxation was extended to **31 Dec 2027**, with full enforcement from **1 Jan 2028** — [BDO latest updates](https://www.bdo.my/en-gb/sites/e-invoicing-latest-updates); [JomeInvoice: Phase 4 extended to 2028](https://jomeinvoice.my/article/e-invoice-phase-4-extension-malaysia-2028/); [BDO guide (Sep 2026)](https://www.bdo.my/en-gb/insights/featured-insights/guide-to-e-invoicing-in-malaysia). A ClearTax page states both 31 Dec 2026 and 31 Dec 2027 (internally inconsistent) — [ClearTax phases](https://www.cleartax.com/my/en/different-phases-implementation-timelines-einvoicing-malaysia)
- During relaxation, a taxpayer may decline individual e-invoice requests from buyers (Specific Guideline v4.9 per a secondary guide) — [JomeInvoice FAQs](https://jomeinvoice.my/article/latest-malaysia-e-invoicing-faqs/)
- **Special Voluntary Disclosure Programme (SVDP):** 7 Jul 2026 – 31 Dec 2027. Penalty-free catch-up for missed or non-compliant e-invoices using SVDP 1.2/1.3 versions. Consolidated catch-up must be month by month. It does not cover fraud or wilful default — [mirror timeline, citing Specific Guideline v4.8 §17](https://github.com/deadboy18/myinvois-docs/blob/main/12-cookbook/10-implementation-timeline.md); [The Star 2 Oct 2026](https://www.thestar.com.my/news/nation/2026/10/02/special-lhdn-disclosure-opportunities)

**Consolidated e-invoice rules**
- From 1 Jan 2026, any single transaction above **RM10,000** needs its own e-invoice and cannot go into a consolidated e-invoice. This applies even during the relaxation period — [Storecove](https://storecove.com/blog/en/navigating-malaysias-e-invoicing-mandate-the-latest-lhdn-rules-timelines-and-compliance-strategies); [mhub](https://mhub.my/post/progress-claims-above-rm10000-need-their-own-e-invoice)
- Consolidated e-invoices are otherwise permitted. The issuance-date-to-submission window is 72h. The supplier cancel window and buyer reject window are both 72h post-validation, after which adjustments need credit/debit/refund notes — [mirror pitfalls](https://github.com/deadboy18/myinvois-docs/blob/main/12-cookbook/05-common-pitfalls.md)
- Self-billed e-invoices for foreign vendors use generic TIN `EI00000000030` and doc type 11 (community MCP README) — [npm: mcp-myinvois](https://www.npmjs.com/package/mcp-myinvois)

**Peppol**
- MDEC is the Malaysian Peppol Authority and runs a centralised Malaysian SMP. Peppol is voluntary. IRBM recognises submission via a Peppol Service Provider as one option — [OpenPeppol Malaysia profile](https://peppol.org/learn-more/country-profiles/malaysia/)
- 58 MDEC-accredited Peppol Service Providers as of 29 May 2026 (vendor-reported). Accreditation needs OpenPeppol membership, MDEC spec compliance, and IRBM security controls (MFA, encryption at rest/in transit) — [ClearTax provider list](https://www.cleartax.com/my/en/top-e-invoicing-solution-provider-malaysia)
- Named APs: SESAMi ([SESAMi](https://sesami.com/peppol-my/)), EDICOM ([EDICOM](https://edicomgroup.com/electronic-invoicing/malaysia)), ClearTax. Not all EU Peppol providers are accredited in MY — [Besitec](https://besitec.com/peppol-malaysia-e-invoicing-my-pint-en/)

**Adoption**
- 1 Oct 2026 (LHDN CEO): **268,000+ businesses** have implemented e-invoicing, with **~1.9 billion** e-invoices submitted for validation — [The Star, 1 Oct 2026](https://www.thestar.com.my/news/nation/2026/10/01/over-268000-businesses-adopt-e-invoicing-as-nearly-19-billion-submissions-validated-says-lhdn)
- Earlier: 203,949 taxpayers and >1bn e-invoices (Mar 2026); 225,604 taxpayers and 1.299bn (Apr 2026) — [VATupdate briefing Jul 2026](https://www.vatupdate.com/2026/07/29/briefing-document-comprehensive-overview-of-e-invoicing-compliance-in-malaysia/); Microsoft cites >1.3bn processed and an Azure cloud-first build — [Microsoft Source Asia](https://news.microsoft.com/source/asia/features/how-lhdnm-is-modernizing-malaysias-tax-system-to-be-scalable-secure-and-cloud-first/)
- LHDN (May 2026) told individuals to obtain e-invoices to support tax-relief claims — [FMT 9 May 2026](https://www.freemalaysiatoday.com/category/nation/2026/05/09/get-e-invoices-when-filing-tax-relief-claims-says-lhdn)

**Known API pain points (documented)**
- TIN formatting is the #1 cause of HTTP 400. Individual TIN prefix is now `IG` (replacing OG/SG). Non-individual TINs need leading zeros stripped and a trailing 0. Sole-proprietor IG+BRN works only with the "Business Owner" MyTax role — [mirror pitfalls](https://github.com/deadboy18/myinvois-docs/blob/main/12-cookbook/05-common-pitfalls.md)
- Using prod credentials in sandbox gives 403. Re-logging-in per call triggers throttling (12 RPM). Using Get Recent/Search Documents for status polling causes 429s. Timestamps must be UTC with `Z`. API-submitted e-invoices cannot be printed from the MyInvois Portal. The UBL-JSON `"_"` wrapper quirk. v1.0 (no signature) vs v1.1 (signature, recommended) — [mirror pitfalls](https://github.com/deadboy18/myinvois-docs/blob/main/12-cookbook/05-common-pitfalls.md); [mirror rate limits](https://github.com/deadboy18/myinvois-docs/blob/main/12-cookbook/04-rate-limits.md)
- LHDN does not publish a complete list of `CF###` validation rules. XAdES signature errors DS300–DS338 come from a PosDigicert guide — [mirror README](https://github.com/deadboy18/myinvois-docs)
- Vendor bug example (2026): SQL Accounting fixed a "Test Validate" bug that could push e-invoices into sandbox wrongly, and a bug accepting cancellations/rejections without a reason — [SQL Account changelog](https://docs.sql.com.my/sqlacc/changelog/5.2026.1069.892)
- Account-setup traps: registering under a *personal* MyTax profile instead of the company, and clock-skew rejections (per a community MCP README) — [npm: mcp-myinvois](https://www.npmjs.com/package/mcp-myinvois)

**Other LHDN systems**
- **e-PCB Plus (MTD/PCB):** mandatory for employer MTD submission. The older e-Data PCB, e-PCB and e-CP39 are being deactivated. Payroll software generates a .txt that is uploaded via MyTax > ezHasil > e-PCB Plus > e-Data PCB ("Upload Data, Check and Pay"). Records without employee TINs are rejected. Employers paying via a bank payroll application need not register (vendor sources) — [BrioHR](https://support.briohr.com/knowledge/e-pcb-plus-for-mtd-submissions-and-payments); [Pandahrms](https://pandahrms.com/e-pcb-plus-is-live-simplify-e-data-pcb-submissions-effortlessly-with-pandahrms/); [Kakitangan](https://blog.kakitangan.com/lhdns-early-announcement-transition-to-e-pcb-plus-system-mytax/)
- **Stamp duty:** the STAMPS portal was closed after 31 Dec 2025. e-Duti Setem on MyTax has been mandatory since 1 Jan 2026 (opened 15 Dec 2025). Duty is self-assessed by the duty payer or appointed agent. A TIN is required — [KPMG US TNF](https://kpmg.com/us/en/taxnewsflash/news/2025/12/tnf-malaysia-stamp-assessment-and-payment-system-replaced-by-e-duti-setem-starting-january-1-2026.html); [KPMG MY](https://kpmg.com/my/en/home/insights/2025/12/stamp-duty-in-malaysia-are-you-ready-for-the-self-assessment-era.html). LHDN waives penalties for qualifying BNDS errors on submissions 1 Jan–31 Dec 2026 — [RinggitPlus](https://ringgitplus.com/en/blog/personal-finance-news/lhdn-waives-penalties-during-first-year-of-self-assessment-e-stamp-duty-system.html)

### Inferences
- An agent platform can lawfully act as a MyInvois **intermediary**. The taxpayer (business) assigns the intermediary in MyTax/MyInvois and grants permissions, and the platform then logs in with its own Client ID/Secret plus `onbehalfof`. This is the cleanest delegated-authority model in Malaysian government IT.
- Moving the threshold to RM3m (Aug 2026) shrinks the mandatory SME market for e-invoicing. Many micro-SMEs are now exempt or voluntary, and Phase 4 enforcement only begins 2028. Demand for "agent does my e-invoicing" among sub-RM3m firms will be driven by buyer pressure (B2B buyers need e-invoices for tax deductibility, and individuals for tax relief), not by penalties.
- Bulk Cancellation (prod 24 Oct 2026) and TIN+BRN validation (Aug 2026) suggest LHDN is actively evolving the API. An agent platform needs continuous SDK monitoring.
- Because LHDN does not publish a full rules list, a "validate before submit" agent tool cannot be complete. Sandbox round-trips remain necessary.

### Gaps
- Could not open LHDN's own v4.8 guideline PDF or press release to confirm the exact RM3m effective date (30 Aug vs 1 Sep 2026) or whether LHDN issued a media statement.
- No official statement found on whether LHDN plans to make Peppol mandatory or to retire API document v1.0.
- Penalty quantum for non-issuance (commonly cited as s.120 ITA fines) was not verified in this pass.
- No public API found for MyTax e-Filing (Form C/B/BE), CP204 instalment estimates, e-PCB Plus, e-Duti Setem, or tax-agent bulk filing. These appear portal-only, but that is an absence-of-evidence finding.
- No independent outage history for MyInvois was found (no status page located).

---

## Q2. Royal Malaysian Customs (JKDM/RMCD): MySST, uCustoms, MyCIEDS, National Single Window / Dagang Net / myTRADELINK

### Takeaway
None of JKDM's systems has a published third-party API. MySST is a portal (registration, SST-02 returns, payment, public registration lookup). Customs declarations (K1/K2/K8/K9) are filed only by JKDM-licensed customs agents. Some still go through the legacy SMK via Dagang Net's National Single Window (myTRADELINK), while uCustoms, announced in 2014, is still being rolled out. An agent platform would need to partner with a licensed customs agent or forwarder, or with Dagang Net.

### Cited Findings
- MySST (mysst.customs.gov.my) is the RMCD portal for registration, returns and payment. It publishes system guides, the SST-02 form and its filling guide, and a user manual for online return and payment — [MySST System Guides](https://mysst.customs.gov.my/SystemGuides); [MySST SST Forms](https://mysst.customs.gov.my/sstforms)
- A public SST registration-status lookup returns business name, effective date and status (third-party description) — [Commenda: SST verification](https://www.commenda.io/blog/malaysia-sst-verification)
- No official MySST API or developer documentation was found. Third-party compliance vendors (e.g., Commenda) offer SST services. Auto-populated SST-02 from e-invoices is speculation in a non-official guide, not an announced feature — [Malaysia4U SST guide](https://malaysia4u.com/sst-guide); [HitPay SST guide](https://hitpayapp.com/blog/sst-malaysia)
- SST filing is bi-monthly. Registration is due within 30 days of crossing RM500,000 taxable turnover (some newly added sectors reportedly have an RM1m threshold; sources conflict) — [HitPay](https://hitpayapp.com/blog/sst-malaysia); [Malaysia4U](https://malaysia4u.com/sst-guide)
- System status conflict, 2026: some forwarders say "all customs declarations… through uCustoms." DNE Forwarding cites a Dagang Net Jan 2026 maintenance notice showing K1, K2 and K9 still running on **SMK** via NSW/myTRADELINK, with uCustoms as "the long-announced successor" — [DNE: customs clearance guide 2026](https://dnelogistics.com.my/customs-clearance-malaysia-guide.html); [DNE: register as importer 2026](https://dnelogistics.com.my/register-as-importer-malaysia.html); [Malaysia4U import/export](https://malaysia4u.com/import-export-guide)
- RMCD grants access to the declaration system only to licensed customs agents (forwarder source) — [DNE](https://dnelogistics.com.my/customs-clearance-malaysia-guide.html). uCustoms has a forwarder appointment/re-appointment process — [Globalior](https://www.globalior.com/malaysia-ucustoms-appointing-re-appointing-forwarders/)
- uCustoms was planned to replace SMK from 1 Jan 2016. In 2019 it was still "in progress" as a single-window end-to-end system for permits, STA permits, certificates of origin and duty payments **[PRE-2025, stale]** — [Conventus Law 2019](https://conventuslaw.com/report/malaysia-malaysia-implementation-of-the-ucustoms/)
- Dagang Net operates Malaysia's National Single Window (since 1989). Its 2026 notices include RMCD's temporary postponement of "Agent Code Z" validation for freight forwarders in manifest (Customs Form No. 4) submissions, and agent codes restricted to the state of issuance for House B/L (dated 29 Sep 2026 on the site, but date consistency is uncertain) — [Dagang Net](https://www.dagangnet.com/); ePermit notices (Jun/Mar 2026) — [Dagang Net ePermit](https://epermit.dagangnet.com.my/)
- The NSW contract was extended 1 Sep 2024 – 31 Aug 2025 (no later extension found) — [DNeX Aug 2024](https://www.dnex.com.my/2024/dnex-receives-contract-extension-for-national-single-window-for-trade-facilitation-2/). DNeX planned a trader monthly fee and super-app from Jan 2024 **[PRE-2025, possibly stale]** — [The Edge](https://theedgemalaysia.com/node/685391)

### Inferences
- For customs, the realistic integration paths are a partnership with a licensed customs agent or forwarder, or Dagang Net messaging. Customs-agent licensing makes direct agent-platform filing infeasible without a licensed entity.
- SST compliance automation would likely mean computing returns from accounting/e-invoice data and handing a prepared SST-02 to the business (or its agent) for portal submission.

### Gaps
- MyCIEDS: no information found in this pass.
- No official 2026 uCustoms rollout status (which stations or declaration types are live) was found. Dagang Net NSW EDI/API technical specs and contract status after Aug 2025 are unknown.
- Whether MySST accepts any bulk or tax-agent channel is unknown.

---

## Q3. SSM (Companies Commission): MBRS, e-Info, company search/verification APIs, BizTrust, reseller access

### Takeaway
SSM itself publishes no developer API or key programme. Company data reaches third parties only through four SSM-appointed data service providers (portals: e-Info, MYDATA-SSM, SSM Search, SAFEDATA). Some of these resell API access: Infomina gave CTOS direct API access in June 2025, and e-Info advertises "API integration". Statutory filing via MBRS 2.0 (XBRL) has no API; files are prepared in the mTool desktop app and uploaded to mPortal.

### Cited Findings
- SSM lists its authorised company-information access points as the e-Info, MYDATA-SSM, SSM Search and SAFEDATA portals, each run by a service provider appointed by SSM. Fees follow the Companies Regulations 2017 schedule (Reg. 8) — [SSM Corporate Info](https://www.ssm.com.my/Pages/Product/Corporate-Info.aspx)
- Infomina Berhad is "one of only four authorized SSM data service providers". On 19 Jun 2025 it agreed to give CTOS Digital direct API access to SSM data through its search platform and aims to do similar deals in fintech and corporate services — [The Star 20 Jun 2025](https://www.thestar.com.my/business/business-news/2025/06/20/ctos-infomina-pact-for-ssm-data-access); [Malaysia SME](https://www.malaysiasme.com.my/infomina-partners-with-ctos-digital-to-deliver-real-time-ssm-data-access/); [The Edge](https://theedgemalaysia.com/node/759661)
- SSM e-Info describes itself as the "official and authorised" portal and advertises API integration for real-time SSM data retrieval and auto-population (terms not reviewed) — [SSM e-Info](https://www.ssm-einfo.my/)
- **Conflict:** Business Data Guide (updated 2 Sep 2026) says "no public API is available for MyDATA-SSM", that SSM has no developer portal, API key programme or bulk data licence, and that SSM terms prohibit automated scraping without written authorisation — [Business Data Guide](https://www.businessdataguide.com/blog/jurisdictions/malaysia-company-search-guide). The two are reconcilable: APIs exist at the service-provider level, not from SSM.
- MyEG offers MYDATA-SSM company search; MYDATA is SSM's appointed technology and service provider — [MyEG SSM service](https://www.myeg.com.my/services/ssm); original launch ~2019 **[PRE-2025]** — [Digital News Asia](https://www.digitalnewsasia.com/business/myeg-launches-mydata-ssm-services)
- Indicative fees (third-party): RM10 per profile, RM20 per digital certified copy — [Business Data Guide](https://www.businessdataguide.com/blog/jurisdictions/malaysia-company-search-guide)
- MBRS 2.0 went live 25 Sep 2024. XBRL audited financial statements are mandatory for all companies from 1 Jun 2025. "SSM does not provide an official API for integration or automation of accounting software with mTool 2.1". Files are prepared in mTool and uploaded, signed, paid and lodged via mPortal — [Fareez Law MBRS](https://fareezlaw.com/mbrs/); [SSM MBRS 2.0 overview PDF](https://www.ssm.com.my/Pages/Publication/PDF%20Files/AD%202024%20-%20Overview%20of%20MBRS%20v2.pdf); [mbrs.com.my mPortal guide](https://www.mbrs.com.my/mportal-mbrs-portal/). mTool v2.2 was reportedly current in early 2026 — [Xberra Tagger](https://xberratagger.my/how-to-file-xbrl-ssm-malaysia)

### Inferences
- For KYB (know-your-business) verification inside an agent workflow, contract with an SSM-authorised provider (Infomina, MYDATA/MyEG, the e-Info operator) or a bureau that resells them (CTOS, possibly Experian). Each lookup costs a statutory fee.
- Write actions (annual returns, director changes, MBRS lodgement) appear to be portal-only (MyCoID/ezBiz/mPortal). Agent automation would be document preparation plus human submission, or partnering with company secretarial firms.

### Gaps
- SSM BizTrust: not researched (search budget exhausted). No information.
- Identities of all four authorised providers, and Experian's access route, were not confirmed.
- No information found on any SSM API for ezBiz/MyCoID filings (annual return, change of particulars).

---

## Q4. Payroll statutory submissions: KWSP/EPF, PERKESO/SOCSO (ASSIST, EIS), HRD Corp, LHDN PCB/MTD

### Takeaway
None of the four payroll statutory bodies publishes a third-party API. All run on employer-portal logins plus file uploads in agency-approved formats:
- **EPF:** CSV/TXT through i-Akaun Majikan.
- **PERKESO:** a combined SOCSO+EIS text file through ASSIST. ASSIST 2.0 was postponed from 30 Jun 2026.
- **LHDN:** a .txt file through e-PCB Plus.
- **HRD Corp:** an eTRiS e-slip.

Payroll software vendors generate the files, and the employer uploads and pays.

### Cited Findings
- EPF e-Caruman: employers submit contributions and Form A via i-Akaun, either as preprinted/blank Form A, CSV upload, or EPFORMA.TXT/EPFORMA2.TXT. "For CSV or TXT files, employers must get approval of the format from EPF." **[2017 FAQ, possibly stale]** — [EPF e-Caruman FAQ (2017)](https://secure.kwsp.gov.my/e-caruman/download/SOALAN_LAZIM_e-Caruman_EN_as_at_19052017.pdf)
- Current flow (vendor help): log in with the employer EPF number, go to Contribution Payment > Submit Contributions, then upload TXT/CSV. The contribution month is payroll month +1 — [PayrollPanda](https://www.payrollpanda.my/help/how-to-submit-the-epf-csv-file-through-i-akaun/)
- From 1 Jan 2026, EPF stopped posting/emailing notices and contribution statements to employers. Employers download them from i-Akaun (Employer) — [KWSP announcement](https://www.kwsp.gov.my/en/w/announcement/enotices-available-on-iakaun-employer)
- PERKESO: a combined employee contribution text file covering SOCSO (Act 4) and EIS (Act 800), for ASSIST 2.0, "implementation planned from June 2026", uploaded via the portal — [PERKESO Text File Format FAQ](https://perkeso.gov.my/images/lindung/lindung-24-jam/FAQ_TextFileFormat_EN.pdf)
- The ASSIST 2.0 rollout scheduled for 30 Jun 2026 was **postponed** to a date to be announced, so employers continue on the existing ASSIST. Revised Jun–Jul 2026 contribution rates were not reflected in e-Payroll — [HR Online](https://www.humanresourcesonline.net/socso-revised-contribution-rates-for-june-july-2026-not-yet-reflected-in-e-payroll-as-system-undergoes-enhancements). **Conflict:** an HR vendor FAQ claims combined-file submission via ASSIST 2.0 is mandatory from 1 Oct 2026 (unverified) — [OmniHR](https://www.omnihr.co/faqs/what-is-changing-with-malaysias-socso-submissions-from-october-2026)
- Existing ASSIST combined SOCSO+EIS upload steps (2022 vendor guide) **[PRE-2025, possibly stale]** — [BrioHR](https://support.briohr.com/knowledge/how-to-upload-socso-eis-combined-text-files-to-perkeso-assist-portal)
- HRD Corp levy: log in to eTRiS with MyCoID, go to the Form 2 e-slip (headcount and wages), then online payment via bank. Due by the 15th of the following month, with late interest of 10% p.a. (sources differ) — [PayrollPanda](https://www.payrollpanda.my/help/how-and-when-to-make-hrdf-levy-payments/); [Malaysia4U HRD Corp](https://malaysia4u.com/hrd-corp-guide). HRD Corp's support centre covers claims and e-disbursement — [HRD Corp support](https://supportcentre.hrdcorp.gov.my/portal/en/kb/articles/hrd-corp-claimable-course-claim-tp)
- LHDN e-PCB Plus: see Q1. It is file-upload only and mandatory, with legacy channels deactivated — [BrioHR](https://support.briohr.com/knowledge/e-pcb-plus-for-mtd-submissions-and-payments)
- Community MCP for *calculations only* (no submission): `@havahr/mcp-calculators` (Jul 2026) covers EPF, SOCSO, EIS, PCB, HRD Corp levy, overtime and Employment Act coverage. Its README says "No auth… no network calls… estimates only" — [npm: @havahr/mcp-calculators](https://www.npmjs.com/package/@havahr/mcp-calculators)

### Inferences
- An agent can compute payroll and generate the agency-format files (EPF CSV/TXT, PERKESO combined text, e-PCB Plus .txt, HRD Corp figures). The submit-and-pay step stays with the employer's portal session or bank payroll channel.
- The PERKESO ASSIST 2.0 file-format change is in flux (postponed). An agent platform should build to the PERKESO FAQ spec but keep the legacy format available.

### Gaps
- Bank host-to-host statutory payment channels (Maybank2u Biz, CIMB BizChannel and others that bundle EPF/SOCSO/EIS/PCB/zakat) were not researched (search budget exhausted). These are probably the most automatable route, but that is unverified.
- No current (2025–2026) official EPF file-format spec was located.
- No info on any EPF or PERKESO API pilot for payroll vendors.

---

## Q5. JAKIM halal: MYeHALAL / SPHM, MyHALALINGREDIENTS, verification APIs, 2025–2026 developments

### Takeaway
There is no public halal-verification API. Verification works through the MYeHALAL public lookup and the JAKIM-endorsed Verify Halal app, which is built by a private firm (Serunai Commerce) on MYeHALAL records. Since 5 May 2025 all SPHM applications are fully electronic, with QR-coded PDF certificates. In May 2026 JAKIM announced MYeHALAL 2.0, which uses AI to screen applications against the MyHALALINGREDIENTS database "within the next few months". Go-live was not confirmed as of Oct 2026.

### Cited Findings
- Effective 5 May 2025, all Malaysian Halal Certification (SPHM) applications are processed electronically. Certificates are issued as PDFs with unique QR codes for real-time verification — [OneKeyBiz guide](https://onekeybiz.com/insights/jakim-halal-certification-malaysia-foreign-company-2025-2026.html); [Halal Times](https://www.halaltimes.com/malaysias-halal-certification-goes-fully-digital/)
- 23 May 2026: JAKIM DG Sirajuddin Suhaimee said AI will be used in **MYeHALAL 2.0**, supported by the MyHALALINGREDIENTS database, "within the next few months", to review each application. JAKIM also introduced a whitelist for companies with strong compliance records — [Malay Mail](https://www.malaymail.com/news/malaysia/2026/05/23/jakim-to-harness-ai-in-myehalal-20-promises-faster-halal-certification-approvals/221058); [FMT](https://www.freemalaysiatoday.com/category/nation/2026/05/23/jakim-to-use-ai-to-speed-up-halal-certification-process); [Lowyat](https://www.lowyat.net/2026/393661/jakim-ai-myehalal/)
- Verify Halal is a JAKIM-endorsed app that scans barcodes/QR codes. It is built by Serunai Commerce (Play Store id `com.serunai.verifyhalal`) and reportedly connects to MYeHALAL records — [Google Play](https://play.google.com/store/apps/details?id=com.serunai.verifyhalal&hl=en); [Verify Halal](https://verifyhalal.com/). Coverage figures for foreign certification bodies conflict (30+, ~60, 94)
- The public MYeHALAL lookup (myehalal.halal.gov.my) reportedly works without login (secondary) — [HalalKetak](https://halalketak.com/panduan/my-e-halal/)
- An end-to-end certification timeline of 3–6 months is reported. Pharmaceutical categories face halal transitional deadlines around Oct 2026 (secondary) — [OneKeyBiz](https://onekeybiz.com/insights/jakim-halal-certification-malaysia-foreign-company-2025-2026.html)

### Inferences
- An agent could do read-only halal checks by scanning certificate QR codes or querying the public MYeHALAL lookup. Bulk or programmatic access would likely require a commercial arrangement like Serunai's, or scraping (with ToS risk).
- Application preparation (document assembly, ingredient pre-screening against MyHALALINGREDIENTS) is the most plausible agent value-add. Submission stays portal-based.

### Gaps
- No evidence of a JAKIM developer API or data-sharing agreement terms. Serunai's access model is unknown.
- MYeHALAL 2.0 go-live status as of Oct 2026 and the HDC (Halal Development Corporation) digital initiatives for 2025–2026 were not found.

---

## Q6. MyDigital ID, PADU, MyGovUC, MyGDX, data.gov.my/OpenDOSM, and GovTech / "API-first" initiatives

### Takeaway
- **MyDigital ID** is scaling fast: about 12m users and 114 government services integrated as of 30 Jun 2026, with 19 state apps live and 28 in development. Private-sector integration is happening through bilateral MoUs and a regulator-supervised bank sandbox (18 banks in Phase 2), plus telcos. There are still no public relying-party onboarding terms, attribute list, fee schedule or digital-signature spec (as of 5 Oct 2026), and the protocol is not published.
- **MyGDX 2.0** (launched 10 Feb 2026) is the government-internal API exchange: 81 agencies, 49 systems, more than 184m transactions.
- **PADU** is explicitly closed to the private sector.
- **data.gov.my / OpenDOSM** is the only open, keyless government API (read-only).
- **MyGOV Malaysia** (52 services, 19 agencies, 2.9m users) has had its own in-app agentic-AI beta since August 2026.

### Cited Findings
**MyDigital ID**
- As of 30 Jun 2026: ~12 million registered users; 114 government online services integrated (as of 25 Jun 2026); 16 million identity transactions; at least 19 state government apps integrated with 28 more in development (DPM Zahid, written parliamentary reply) — [Malay Mail 8 Jul 2026](https://www.malaymail.com/news/malaysia/2026/07/08/dpm-zahid-12-million-malaysians-have-signed-up-for-mydigital-id-as-of-june-30-with-114-govt-services-integrated/226817); [The Star 8 Jul 2026](https://www.thestar.com.my/news/nation/2026/07/08/mydigital-id-expands-to-state-level-government-systems-hits-12-million-users-says-zahid)
- Target: 17 million accounts by end-2026 — [Bernama](https://www.bernama.com/en/news.php?id=2523289)
- May 2026: MyDigital ID added 29 partners and is integrated across more than 100 public and private applications, with more than 11m users — [Biometric Update May 2026](https://www.biometricupdate.com/202605/malaysias-mydigital-id-adds-29-partners-as-adoption-grows)
- Banks: Phase 1 sandbox (15 banks, concluded Jun 2025, 6 integrated). Phase 2: 18 banks; as of Jan 2026, 10 integrating and 2 had completed technical onboarding. Phase 2 was due to end Mar 2026, with nationwide rollout only after readiness and security compliance — [Malay Mail 23 Jan 2026](https://www.malaymail.com/news/malaysia/2026/01/23/finance-ministry-eighteen-banks-join-phase-2-sandbox-for-mydigital-id-rollout/206423); [Biometric Update Jan 2026](https://www.biometricupdate.com/202601/malaysia-is-testing-mydigital-id-integration-with-18-banks). On 12 Feb 2026 MoUs were signed with 15 banks and fintechs — [Didit](https://didit.me/blog/mydigital-id-integration/)
- Telcos: verification integration has begun with all mobile operators (SIM-misuse/scam control) (Dec 2025) — [Biometric Update Dec 2025](https://www.biometricupdate.com/202512/malaysia-begins-mydigital-id-verification-integration-for-all-mobile-operators)
- As of 5 Oct 2026, a vendor review found "no public onboarding terms, attribute list or price list for businesses". The operator mentions a "MyDigital ID Certificate" but does not describe signing; signature format and legal effect are unpublished — [Didit, Oct 2026](https://didit.me/blog/mydigital-id-integration/)
- The government is mulling legislation to make registration mandatory — [The Edge](https://theedgemalaysia.com/node/763374); analysis "when optional starts to look unavoidable" (Sep 2026) — [Biometric Update Sep 2026](https://www.biometricupdate.com/202609/malaysia-and-mydigital-id-when-optional-starts-to-look-unavoidable). Integration across financial services, healthcare and telecoms is planned from 2026 — [Technave](https://technave.com/gadget/MyDigital-ID-will-integrate-government-and-private-services-in-2026-45154.html); [The Star Dec 2025](https://www.thestar.com.my/news/nation/2025/12/13/prepare-for-mydigital-id-integration)

**MyGDX (Malaysian Government Central Data Exchange)**
- PPDSA (Public Sector Data Digitalisation Policy) and the MyGDX expansion launched 10 Feb 2026. MyGDX 2.0 is ready, and new data subscription requests use the new platform. At that point: 81 agencies (51 data providers, 23 consumers), 49 integrated systems, >23m API transactions (datasets include passport verification and vehicle/licence info) — [Ministry of Digital media release 10 Feb 2026](https://www.digital.gov.my/api/file/file/10022026_SIARAN%20MEDIA_REVOLUSI%20DIGITAL%20SEKTOR%20AWAM%20PPDSA%20DAN%20MYGDX%20PEMACU%20TRANSFORMASI%20RAKYAT.pdf); [JDN DG speech](https://www.jdn.gov.my/wp-content/uploads/2026/03/TEKS-UCAPAN-KP-PELUNCURAN-PPDSA-DAN-MYGDX-10-FEB-2026-1.pdf)
- More than 184 million transactions, and more than 1m verification requests/hour at peak (university admissions) — [GovInsider (~mid-2026)](https://govinsider.asia/intl-en/article/data-exchange-is-breaking-down-siloes-in-malaysias-digital-government)
- The MyGDX portal has an API catalogue and Open API subscription documents (Jul 2026). Some entries are restricted to specific agencies — [MyGDX portal](https://mygdx.gov.my/ms/landing-page/theme?theme=third-theme&uuid=+&year=)

**PADU**
- Apr 2026, Economy Minister Akmal Nasrullah: "We will not open Padu to the private sector." There are no plans to commercialise it. Analytics for agencies were added from May 2026, and it serves 26 agencies — [RinggitPlus](https://ringgitplus.com/en/blog/personal-finance-news/padu-is-moving-beyond-data-verification-into-policy-analysis.html); [Bernama](https://bernama.com/en/news.php?id=2546955)

**data.gov.my / OpenDOSM**
- Open API for Data Catalogue, OpenDOSM, Weather and GTFS Static/Realtime: 4 requests/min default, with 429 on excess — [developer.data.gov.my rate limit](https://developer.data.gov.my/rate-limit)
- No token needed. A higher-limit token can be requested by emailing dataterbuka@jdn.gov.my (case by case), then used as `Authorization: Token <token>` — [developer.data.gov.my authentication](https://developer.data.gov.my/authentication)

**GovTech / MyGOV / agentic AI**
- GovTech: first phase launched 2025, with "full implementation of GovTech" 2026–2030 (Digital Minister Gobind Singh Deo) — [The Star Feb 2025](https://www.thestar.com.my/tech/tech-news/2025/02/05/gobind-govtech-initiative-to-launch-in-q1-this-year-to-be-implementated-from-2026-to-2030); single-gateway framing — [The Edge](https://theedgemalaysia.com/node/769249). A World Bank report (Jul 2026, prepared with the Ministry of Digital) assesses GovTech progress — [World Bank](https://www.worldbank.org/en/country/malaysia/publication/building-malaysia-s-future-government-unlocking-public-sector-productivity-with-govtech)
- MyGOV Malaysia: beta Aug 2025 with 34 services. Citizens otherwise face 288 apps from 125 agencies — [SoyaCincau Aug 2025](https://soyacincau.com/2025/08/20/mygov-app-beta-malaysia-one-stop-govt-services-hub/). As of Jul 2026: 2.9m users, 52 services, 19 agencies. Login via MyDigital ID. Built "100% in-house" — [Ministry of Digital](https://www.digital.gov.my/en-GB/siaran/MyGOV-Malaysia-Melangkah-Ke-Era-Baharu-Dengan-Agentic-AI). On 7 Oct 2026 it covered driving licences, road tax, JPJ summons, passports, clinic appointments and STR — [Malay Mail 7 Oct 2026](https://www.malaymail.com/news/malaysia/2026/10/07/fahmi-mygov-malaysia-consolidates-government-services-into-one-app/237987)
- **Agentic AI in MyGOV:** announced 8 Aug 2026 and in beta since early Aug 2026. Example flow: check an outstanding police fine, then pay it, with actions subject to user authorisation and following the Public Sector AI Adoption Guidelines — [The Star 8 Aug 2026](https://www.thestar.com.my/news/nation/2026/08/08/mygov-gets-ai-agent-to-make-government-services-easier-says-gobind); [OpenGov Asia](https://opengovasia.com/malaysia-digital-ministry-integrates-agentic-ai-into-mygov-platform/); [Entrepreneur APAC](https://apac.entrepreneur.com/?p=9762)

### Inferences
- The government is building agentic capability *inside* its own channel (MyGOV), backed by MyDigital ID and MyGDX. A third-party agent platform's "act on behalf of a business" story would most plausibly rely on MyDigital ID for user/director authentication once private relying-party onboarding is formalised, but that is not available on published terms today.
- Because MyGDX and PADU are government-only, third parties cannot use them for KYB/KYC. Commercial routes (SSM providers, CTOS, bank e-KYC) remain necessary.

### Gaps
- MyDigital ID technical protocol (OIDC/SAML), relying-party eligibility, fees and digital-signature capability: not published (as of Oct 2026 per Didit). I could not confirm OIDC.
- MyGovUC was not researched. It is understood to be civil-service unified communications and probably irrelevant to business APIs, but that is unverified.
- No evidence of a formal government "API-first" policy document or a private-sector API gateway beyond data.gov.my was found.

---

## Q7. Local councils (business licensing), JPJ, and MyEG as a commercial gateway

### Takeaway
Business licensing is fragmented across councils (PBTs). Each runs its own portal (e.g., MBPJ eLesen), alongside a federal ePBT portal, and no licensing API was found. JPJ services reach citizens through MyGOV and MyEG, but no third-party JPJ API was found. MyEG is a consumer and concessionaire channel (road tax, summons, SSM MYDATA, MyDigital ID). No Malaysian MyEG developer API was found; MYEG Philippines markets a payment-gateway API.

### Cited Findings
- Most PBTs have their own online portals. A federal "Portal ePBT Online" offers online licence applications across PBTs — [MyGovernment: Portal ePBT Online](https://www.malaysia.gov.my/my/my-initiative/sistem-penyampaian-perkhidmatan-awam-dan-kerajaan-tempatan/local-e-government/portal-epbt-online)
- Renewal windows for 2026 licences were per council: MBJB 1 Oct–31 Dec 2025; MBS 1 Nov 2025–31 Jan 2026 (late penalty 10–50%); MPKS instant online renewal — [MBJB](https://www.mbjb.gov.my/ms/pembaharuanlesen2026); [MBS](https://www.mbs.gov.my/en/mbs/media-centre/announcement/2026-license-renewal); [MPKS](https://www.mpks.gov.my/ms/node/2095)
- MBPJ uses an eLesen portal with account registration (consultancy source) — [ApplyLesenPBT](https://applylesenpbt.com.my/blog/selangor-pbt-license/)
- MyGOV app (Oct 2026) includes driving licence, road tax and JPJ summons checks — [Malay Mail 7 Oct 2026](https://www.malaymail.com/news/malaysia/2026/10/07/fahmi-mygov-malaysia-consolidates-government-services-into-one-app/237987). MyGDX shares vehicle and licence information among agencies — [Ministry of Digital release](https://www.digital.gov.my/api/file/file/10022026_SIARAN%20MEDIA_REVOLUSI%20DIGITAL%20SEKTOR%20AWAM%20PPDSA%20DAN%20MYGDX%20PEMACU%20TRANSFORMASI%20RAKYAT.pdf)
- MyEG app (updated 6 Oct 2026): renew road tax, pay summons, MyDigital ID — [Google Play: MyEG](https://play.google.com/store/apps/details?id=mf.myeg.com.eservicemobile&hl=en_US). MyEG's anchor services are Road Transport, Immigration and Royal Malaysian Customs — [Macro Ops](https://macro-ops.com/my-e-g-services-myeg-a-high-margin-digital-government-solutions-provider/)
- MYEG Philippines offers a payment-gateway API to clients and partners (Philippines, not Malaysia) — [MYEG PH](https://myeg.ph/services/payment-gateway)

### Inferences
- Council licensing automation would require per-council browser automation or form preparation. No standard exists across roughly 150 PBTs (the count is approximate and was not verified here).
- MyEG is better treated as a potential B2B partner, given its concessions with JPJ, Immigration and SSM data, than as an open API. Any partnership terms are unknown.

### Gaps
- JPJ APIs for insurers and road-tax agents (e.g., the insurer–JPJ link for road tax renewal) were not researched; the search budget was exhausted.
- No MyEG B2B or API offering in Malaysia was found. DBKL's current licensing system was not identified.

---

## Q8. Official or community MCP servers for these systems

### Takeaway
There are **no official MCP servers** from any Malaysian agency, and none in Claude's connector registry (checked 15 Oct 2026). Community MCP servers exist for:
- MyInvois: one live-API server that can submit, plus one rules/validation-only server.
- data.gov.my / OpenDOSM: at least five servers.
- BNM Open API.
- Payroll statutory calculations (calculation only).

I found no MCP server for SSM, KWSP, PERKESO, HRD Corp, JKDM/MySST, JAKIM or MyDigital ID.

### Cited Findings
- **mcp-myinvois** (techtemplemy) is unofficial. v1.1.0 was published 5 Sep 2026 (first 12 Jul 2026). Its tools include `search_tin`, `validate_tin`, `draft_invoice` → `confirm_submission` (a two-step submit with a one-time token, enforced in code), `list_recent_documents`, `get_document`, `get_submission`, and `cancel_document` (72-hour window), plus self-billed invoices for foreign vendors. It defaults to sandbox. It ships SKILL.md files that use browser-use/Playwright to walk users through MyTax/MyInvois ERP registration and API-key capture. Credentials are stored locally in `~/.myinvois.env` — [npm: mcp-myinvois](https://www.npmjs.com/package/mcp-myinvois); [GitHub: techtemplemy/mcp-myinvois](https://github.com/techtemplemy/mcp-myinvois); [LobeHub listing](https://lobehub.com/mcp/techtemplemy-e-invoice-malaysia-mcp)
- **myinvois-mcp** (ANHQ280) is v0.1.1 (17 Jun 2026). Four tools: `check_einvoice_scope`, `get_einvoice_field_rules`, `validate_einvoice` (stateless) and `get_einvoice_changes`. It wraps a hosted rules feed, needs no API key and does **not** submit to LHDN — [npm: myinvois-mcp](https://www.npmjs.com/package/myinvois-mcp); [GitHub: ANHQ280/myinvois-compliance-rules-feed](https://github.com/ANHQ280/myinvois-compliance-rules-feed); [mcp.so #myinvois tag](https://mcp.so/tags/myinvois)
- data.gov.my MCP servers:
  - **hithereiamaliff/mcp-datagovmy**: 31 tools, remote endpoint, Smithery package — [GitHub](https://github.com/hithereiamaliff/mcp-datagovmy); [Glama](https://glama.ai/mcp/servers/@hithereiamaliff/mcp-datagovmy)
  - **faridyusof727/datagovmy-mcp** (Go) — [GitHub](https://github.com/faridyusof727/datagovmy-mcp)
  - **manfye/data-dosm-mcp-nodejs** (npm `datagovmy-mcp-server`, Jul 2025) — [GitHub](https://github.com/manfye/data-dosm-mcp-nodejs); [PulseMCP](https://www.pulsemcp.com/servers/manfye-datagovmy)
  - **@lightyoruichi/datagovmy-mcp** (Dec 2025) — [npm](https://www.npmjs.com/package/@lightyoruichi/datagovmy-mcp)
  - **@pipeworx/mcp-opendosm-my** (Sep 2026) — [npm](https://www.npmjs.com/package/@pipeworx/mcp-opendosm-my)
- **@pipeworx/mcp-bnm-my** (25 Sep 2026): Bank Negara Malaysia Open API MCP, keyless — [npm](https://www.npmjs.com/package/@pipeworx/mcp-bnm-my)
- **@havahr/mcp-calculators** (Jul 2026): EPF/SOCSO/EIS/PCB/HRD levy calculators only, no network calls — [npm](https://www.npmjs.com/package/@havahr/mcp-calculators)
- Adjacent non-MCP automation:
  - n8n node `n8n-nodes-lhdn-einvoice` (Jul 2025) — [npm](https://www.npmjs.com/package/n8n-nodes-lhdn-einvoice)
  - Multiple community MyInvois SDKs: `@ibnumalik/myinvois` v4.0.0 (Aug 2026), `@ripwords/myinvois-client` (Jul 2026), `myinvois-client` (Oct 2025), `@lazuar/lhdn-sdk` (Jun 2026), PyPI `myinvois` (Beta, intermediary support), PHP `klsheng/myinvois-php-sdk` — [npm: @ibnumalik/myinvois](https://www.npmjs.com/package/@ibnumalik/myinvois); [npm: @ripwords/myinvois-client](https://www.npmjs.com/package/@ripwords/myinvois-client); [PyPI: myinvois](https://pypi.org/project/myinvois/); [Packagist: klsheng/myinvois-php-sdk](https://root.packagist.org/packages/klsheng/myinvois-php-sdk)
  - The deadboy18/myinvois-docs repo ships a Claude Skill that audits the live SDK portal for changes — [GitHub: deadboy18/myinvois-docs](https://github.com/deadboy18/myinvois-docs)
- The Claude MCP connector registry search (15 Oct 2026) for "Malaysia / MyInvois / LHDN e-invoice / e-invoicing / Malaysia open data" returned no Malaysian connectors (direct tool check, no URL).

### Inferences
- The MyInvois MCP space is nascent: one hobby/indie submit-capable server about three months old, and one rules server. A production-grade MyInvois MCP supporting **multi-tenant intermediary login** (`onbehalfof`), bulk cancel and SVDP versions does not appear to exist yet. That is a whitespace opportunity.
- techtemplemy's approach (browser automation to obtain API keys, then API for submission) shows the hybrid pattern most Malaysian agent integrations will need: APIs where they exist, and browser automation or human-in-the-loop for portal-only steps.

### Gaps
- GitHub-wide search was unavailable (API blocked), so smaller or private MCP repos (e.g., on Smithery or the official MCP registry) beyond npm and search results may exist. No server for SSM, KWSP, PERKESO, HRD Corp, MySST, JAKIM or MyDigital ID was found.
- An "mcpmarket mygov-1" listing appeared in search results but its content was not verified.
