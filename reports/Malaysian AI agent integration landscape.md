# Win Malaysia's agent layer through MyInvois depth

As of October 2026, exactly one Malaysian government system lets a third party act for a business under a sanctioned delegation model. That system is LHDN's MyInvois e-invoicing API: a company director appoints an "intermediary", which then logs in with its own credentials plus an `onbehalfof` header. Almost everything else a "one-stop center" needs falls into three groups. Some systems are portal-and-file-upload only: EPF, SOCSO/EIS, PCB, HRD Corp, SST, stamp duty, SSM filings and council licences. Some are open only to licensed intermediaries: SSM data, customs declarations and PayNet's DuitNow rails. The rest are reachable only through commercial programmes such as payment gateways, marketplace developer approval and accounting APIs. No Malaysian agency, bank or platform ships an official MCP server. The roughly 20 Malaysian community servers are unofficial and have little traction, and thin API wrappers are becoming a commodity fast. An agent platform needs no licence to operate, but three hard lines apply: it must not hold funds, must not represent taxpayers on income tax without an approved tax agent, and must act through formal delegation rather than shared logins. Data-protection (PDPA) duties for processors already apply, and an AI Governance Bill is due to be tabled by Q1 2027. The current repository cannot carry this business. It is a single-user demo whose only real integration has never run live, whose approval gate can be bypassed, which has no multi-tenancy or remote MCP, and whose test suite starts failing on 16 October 2026. **The recommendation is to keep the idea, narrow the scope and rebuild the code.** Ship a compliance-grade, multi-tenant MyInvois layer (remote MCP plus REST) to bookkeeping firms and SME software builders. Then extend it to quote-to-cash and marketplace seller operations, park the halal module and discard the fake test-data integrations. One caveat on evidence: the research team ran out of search budget and could not open most Malaysian primary sources. SME demand figures, competitor pricing and startup funding are therefore marked as unverified wherever they appear.

## Only MyInvois offers sanctioned write access today

What a third party can reach falls into four tiers. The first is one government API that allows writes under formal delegation. The second is a handful of open or partner-only read APIs. The third is regulated rails reachable only through licensed partners. The fourth is commercial platforms that require developer approval. The tier matters more than the count, because each one forces a different product shape. Respectively, those shapes are: direct API automation; contracted data resale; execution routed through a partner; and preparing documents for a human to submit.

### MyInvois is mature, free and built for intermediaries

MyInvois has a public REST API. It covers submit, cancel, reject, TIN validation and search, QR lookup, and document retrieval and search ([MyInvois SDK](https://sdk.myinvois.hasil.gov.my/einvoicingapi)). Authentication uses OAuth 2.0 client credentials. An intermediary adds an `onbehalfof` header with the taxpayer's TIN, and "permissions that are granted by the taxpayer will be applied on the intermediary's profile" ([SDK: Login as Intermediary](https://sdk.myinvois.hasil.gov.my/api/08-login-as-intermediary-system/); [official doc mirror](https://github.com/deadboy18/myinvois-docs/blob/main/02-platform-api/02-login-intermediary.md)). The appointment is made in the MyInvois portal. **Only a company director, or a sole proprietor registered as business owner, can make it.** Permissions are switched on individually, and the appointment can last up to about five years ([AJobThing](https://www.ajobthing.com/resources/blog/how-appoint-intermideary-e-invoice-submission-myinvois)). Uptake is large: **268,000+ businesses and about 1.9 billion e-invoices** as of 1 October 2026 ([The Star](https://www.thestar.com.my/news/nation/2026/10/01/over-268000-businesses-adopt-e-invoicing-as-nearly-19-billion-submissions-validated-says-lhdn)).

LHDN keeps changing the API. TIN+BRN combination checks started on 1 August 2026 ([VATupdate](https://www.vatupdate.com/2026/06/14/myinvois-sdk-1-0-adds-tin-brn-validation-from-august-2026/)). Special document versions for the Special Voluntary Disclosure Programme (SVDP) arrived in July 2026. **Bulk cancellation reaches production on 24 October 2026** ([SDK release notes](https://sdk.myinvois.hasil.gov.my/release-notes/)). Rate limits apply per Client ID: **login 12 requests per minute**, submit 100, get-submission 300, cancel 12, reject 12 and search-documents 12. A 429 response carries `Retry-After` ([SDK integration practices](https://sdk.myinvois.hasil.gov.my/integration-practices/)).

Two of these details shape any hub. First, tokens last about 60 minutes and login is capped at 12 per minute per Client ID. An intermediary serving many businesses therefore has to cache one token per taxpayer. On that arithmetic, one Client ID can issue at most about 720 taxpayer tokens an hour; this is an inference that has not been checked with LHDN. Second, an intermediary can see only the documents it submitted itself ([ClearTax](https://www.cleartax.com/my/en/login-intermediary-system-api)). Reconciling a client's past e-invoices must therefore start from the client's own ledger, not from MyInvois.

LHDN publishes no complete list of its validation rules. Version 1.1 documents need an XAdES digital signature using a certificate from an MCMC-licensed certificate authority such as Pos Digicert or MSC Trustgate ([mirror README](https://github.com/deadboy18/myinvois-docs)). The documented pitfalls are TIN formatting, throttling from repeated logins, UTC timestamps and quirks in the UBL-JSON format ([mirror: common pitfalls](https://github.com/deadboy18/myinvois-docs/blob/main/12-cookbook/05-common-pitfalls.md)). Handling them is exactly the work a thin wrapper skips.

### Every other government system is read-only, partner-only or portal-only

Outside MyInvois, data.gov.my/OpenDOSM is the only open government API. It is read-only, with a default limit of **4 requests per minute** ([developer.data.gov.my](https://developer.data.gov.my/rate-limit)).

- **SSM company registry.** SSM publishes no developer API. Company data comes through four appointed service providers. One of them, Infomina, gave the credit bureau CTOS direct API access in June 2025 ([The Star](https://www.thestar.com.my/business/business-news/2025/06/20/ctos-infomina-pact-for-ssm-data-access)). Statutory fees run at about RM10 per company profile ([Business Data Guide](https://www.businessdataguide.com/blog/jurisdictions/malaysia-company-search-guide)). Annual financial-statement filing through SSM's MBRS system has no API ([Fareez Law](https://fareezlaw.com/mbrs/)).
- **Payroll bodies.** All four statutory bodies run employer portals that accept files in their own formats ([BrioHR](https://support.briohr.com/knowledge/e-pcb-plus-for-mtd-submissions-and-payments); [PayrollPanda](https://www.payrollpanda.my/help/how-to-submit-the-epf-csv-file-through-i-akaun/)):
  - EPF takes CSV/TXT files.
  - PERKESO takes a combined SOCSO+EIS text file.
  - LHDN's e-PCB Plus takes a text file.
  - HRD Corp uses an e-slip in its eTRiS portal.
- **PERKESO's ASSIST 2.0.** It was planned for 30 June 2026 and then postponed indefinitely ([HR Online](https://www.humanresourcesonline.net/socso-revised-contribution-rates-for-june-july-2026-not-yet-reflected-in-e-payroll-as-system-undergoes-enhancements)). One HR vendor claims combined submission becomes mandatory from 1 October 2026 ([OmniHR](https://www.omnihr.co/faqs/what-is-changing-with-malaysias-socso-submissions-from-october-2026)). The postponement is the better-sourced reading.
- **Customs.** MySST (sales and service tax) and e-Duti Setem (stamp duty) are portals. Customs declarations go only through customs agents licensed by JKDM ([DNE Forwarding](https://dnelogistics.com.my/customs-clearance-malaysia-guide.html)).
- **Halal.** JAKIM has no halal-verification API. In May 2026 it announced AI screening in MYeHALAL 2.0, with no confirmed go-live date ([Malay Mail](https://www.malaymail.com/news/malaysia/2026/05/23/jakim-to-harness-ai-in-myehalal-20-promises-faster-halal-certification-approvals/221058)).
- **Digital identity and government data.** MyDigital ID has about 12 million users. As of 5 October 2026 it still had **no public onboarding terms, attribute list or price list** for businesses that want to use it as a login ([Didit](https://didit.me/blog/mydigital-id-integration/)). MyGDX, the government data exchange, is for agencies only. PADU, the central population database, is explicitly closed to the private sector ([RinggitPlus](https://ringgitplus.com/en/blog/personal-finance-news/padu-is-moving-beyond-data-verification-into-policy-analysis.html)).

The most telling signal came in August 2026. The Ministry of Digital added its own agentic-AI assistant to the MyGOV citizen app ([The Star](https://www.thestar.com.my/news/nation/2026/08/08/mygov-gets-ai-agent-to-make-government-services-easier-says-gobind)). The state is building its own agent for citizens rather than opening APIs to others. That pushes a private hub toward serving businesses. The search budget ran out before the team could research SSM BizTrust, MyEG's business access, JPJ's links with insurers, or bank host-to-host files for statutory payments.

### Payments run through licensed partners; open finance arrives in 2027–2028

PayNet's developer portal offers a free sandbox ([PayNet Developer](https://developer.paynet.my/home)). Connecting directly, however, is limited to merchant acquirers and e-money issuers licensed by Bank Negara Malaysia (BNM). Non-bank acquirers must also show **at least 1 million transactions a year** ([PayNet KB](https://knowledgebase.paynet.my/hc/en-us/articles/51138284421017-Direct-Participation-Register-Your-Company)). A startup therefore reaches DuitNow through payment gateways. Several gateways offer collection APIs with webhooks, plus payouts over DuitNow Transfer:

- Billplz's Payment Order ([Billplz](https://support.billplz-sandbox.com/guide/payment-order-overview))
- CHIP Send, at RM1 per transfer ([CHIP pricing](https://www.chip-in.asia/pricing))
- Xendit payouts ([Xendit](https://docs.xendit.co/docs/overview-payouts-coverage))

None of the gateways surveyed yet offers DuitNow Request (request-to-pay) or AutoDebit. Curlec launched DuitNow Pay checkout in August 2026 and lists recurring payments as arriving "once PayNet releases them" ([Fintech News Malaysia](https://fintechnews.my/60499/payments-remittance-malaysia/razorpay-curlec-duitnow-pay/)). Stripe Malaysia supports FPX and GrabPay. Whether it supports DuitNow QR natively is disputed, and its Agentic Commerce Suite excludes Malaysia ([Stripe docs](https://docs.stripe.com/agentic-commerce/for-sellers)).

BNM published an Open Finance exposure draft on 18 November 2025. It covers consent-based sharing of account data, not starting payments. Rollout begins in phases from 2027 ([Fintech News Malaysia](https://fintechnews.my/54091/regtech-fintech-regulation-malaysia/malaysia-open-finance/)). Obligations for third parties that consume the data start in 2028 at the earliest, and SME account data comes in a later phase ([HHQ](https://hhq.com.my/posts/open-finance-in-malaysia-bank-negara-malaysias-exposure-draft/)). Among banks, only CIMB documents a corporate API gateway, and the pages found are on its Singapore site ([CIMB](https://www.cimb.com.sg/en/business/solutions-products/cash-management/channels-cimb/api-gateway-cimb.html)).

Agentic payments in Malaysia are led by the card networks. Mastercard ran the country's first authenticated agentic transaction with CIMB and RHB on 4 March 2026 ([Mastercard](https://www.mastercard.com/news/ap/en/newsroom/press-releases/en/2026/mastercard-conducts-first-live-agentic-transaction-in-malaysia-with-cimb-and-rhb-pilot/)). Visa launched "Agentic Ready" with Malaysian card-issuing banks on 30 April 2026 ([Fintech News Malaysia](https://fintechnews.my/58246/payments-remittance-malaysia/visa-agentic-ready-malaysia/)). Both are pilots for issuing banks, not products a developer can use. The payment volume underneath is real. PayNet processed **8.44 billion transactions in 2025** ([PayNet](https://paynet.my/about-us/media-centre/press-release/8-44-billion-transactions-processed-in-2025-as-digital-payments-become-malaysians-preferred-way-to-pay.html)), and DuitNow QR doubled to 3 billion ([TNGlobal](https://technode.global/2026/05/05/malaysias-duitnow-qr-more-than-doubled-in-2025-to-three-billion-transactions/)). Businesses face a growing pile of small receipts to match against invoices.

### Commercial platforms require approval but are reachable

Shopee, Lazada and TikTok Shop all run mature developer platforms, but you need approval to use them. The steps are:

1. Register as a software vendor or as a seller building its own integration.
2. Pass review. One integrator puts Shopee's review at about three working days.
3. Get OAuth authorisation from each shop ([Qiscus](https://documentation.qiscus.com/app-center/shopee); [Jentic on Lazada](https://jentic.com/apis/open.lazada.com/lazada)).

TikTok Shop forces a further review after 25 seller authorisations, which any multi-tenant hub will hit ([MintMCP](https://www.mintmcp.com/docs/tiktok-shop-mcp-setup)). GrabFood and foodpanda work only with approved partners, and foodpanda requires an NDA ([foodpanda](https://integration.foodpanda.com/en/documentation/)). EasyParcel ([developer portal](https://developer.easyparcel.com/)) and Lalamove ([docs](https://developers.lalamove.com/v2/index.html)) are self-serve and have sandboxes.

In accounting, Xero, QuickBooks and Zoho Books each have an official MCP server ([Xero](https://github.com/XeroAPI/xero-mcp-server); [Zoho](https://www.zoho.com/uk/books/help/mcp/zoho-books-mcp.html)). Their Malaysian features are thin:

- Xero's payroll tools work only for organisations in New Zealand and the UK.
- Xero's MyInvois flow still needs manual steps ([Xero product ideas](https://productideas.xero.com/forums/967115-invoices-quotes/suggestions/51559088-feature-request-default-myinvois-recipient-email)).
- QuickBooks points users to third-party apps for e-invoicing ([Intuit community](https://quickbooks.intuit.com/community/other-questions-88/qbo-e-invoicing-feature-for-malaysia-180122)).

Most local accounting software in use (SQL Account, AutoCount) is desktop-first. AutoCount's cloud API needs a client program running on the customer's own PC ([AutoCount wiki](https://wiki.autocountsoft.com/wiki/Introduction_to_AOTG_API)). Bukku, by contrast, offers a per-company token API ([npm](https://www.npmjs.com/package/bukku-client)) and already submits to MyInvois itself ([Bukku](https://bukku.my/lhdn-e-invoice-compliant-cloud-accounting-software-malaysia)). WhatsApp's Cloud API is self-serve. In Malaysia it costs about **US$0.014 per utility message and US$0.086 per marketing message** ([SleekFlow](https://sleekflow.io/en-us/blog/whatsapp-business-price)). That makes it a cheap channel for sending approval requests to owners outside the AI chat.

| System | Programmatic access for a third party | Condition of access | Realistic agent action today |
|---|---|---|---|
| LHDN MyInvois | Public REST API with sandbox | Director appoints platform as intermediary; platform's own Client ID | Validate TIN/BRN, submit, track, cancel/reject within 72h, bulk cancel |
| data.gov.my / OpenDOSM | Open REST | None; token on request for higher limits | Read statistics |
| SSM company data | Partner API via 4 appointed providers or CTOS | Commercial contract; ~RM10 per profile | Verify a business (KYB) |
| EPF, PERKESO, e-PCB Plus, HRD Corp | None (file upload) | Employer's own portal login | Compute and generate files; a human uploads and pays |
| MySST, e-Duti Setem, MBRS, councils | None (portal) | Business's own login | Prepare documents for a human to submit |
| Customs (SMK/uCustoms via Dagang Net) | EDI for licensed agents | JKDM customs-agent licence | Partner with a forwarder |
| JAKIM MYeHALAL | None | Public lookup only | Prepare dossiers, track certificates |
| MyDigital ID, MyGDX, PADU | No published private onboarding | Bilateral agreement or government-only | None today |
| PayNet DuitNow | Sandbox open; production for participants only | BNM-licensed acquirer or e-money issuer; ≥1M transactions/yr for non-bank acquirers | Only via gateways |
| Gateways (Billplz, CHIP, Xendit, HitPay, Curlec) | REST + webhooks | Merchant account per business | Payment links/QR, status, refunds; payouts from pre-funded balance |
| Bank data (open finance) | Not yet | Phased from 2027; data consumers 2028 or later | Ingest statement files meanwhile |
| Shopee / Lazada / TikTok Shop | Developer platforms requiring approval | Vendor approval plus OAuth per shop | Orders, stock, logistics, finance reads |
| EasyParcel / Lalamove | Open, with sandbox | Developer account, prepaid credit | Rates, bookings, labels, tracking |
| Xero / QuickBooks / Zoho Books | Open, with official MCP | OAuth per organisation | Read/write the ledger (Malaysian features thin) |
| Bukku / AutoCount / SQL Account | Token / local bridge / no public API | Per-company token; client on customer's PC | Ledger sync (Bukku easiest) |
| WhatsApp Cloud API | Open (Meta) or via a reseller | Business verification; per-message fees | Notifications, approvals |

### MCP coverage is unofficial, thin and short-lived

Searching the official MCP registry for "malaysia" returns six servers. None comes from a Malaysian institution or company ([MCP Registry](https://registry.modelcontextprotocol.io/v0/servers?search=malaysia&limit=100)). The servers that can write anything are listed below.

| Server | What it does | Status signal |
|---|---|---|
| techtemplemy/mcp-myinvois | 11 MyInvois tools; submission needs a second confirm step with a one-time token; defaults to sandbox | 3 stars, last updated Sep 2026 ([GitHub](https://github.com/techtemplemy/mcp-myinvois)) |
| Wishpool malaysia-invoice / malaysia-payments | MyInvois submission; FPX/DuitNow via Billplz | Two of 91 servers published 8–10 Jul 2026; repo now 404 ([Registry](https://registry.modelcontextprotocol.io/v0/servers?search=wishpool&limit=100); [GitHub](https://github.com/junter1989k-ai/malaysia-payments-mcp)) |
| centry-digital/bukku | Bukku invoices, contacts, products | Most active (181 commits); not from Bukku ([GitHub](https://github.com/centry-digital/bukku)) |
| mrslbt/xendit-mcp | Invoices; payouts off by default | Malaysia support "not yet verified" ([GitHub](https://github.com/mrslbt/xendit-mcp)) |
| ANHQ280 myinvois-mcp | Rules and validation only; cannot submit | Linked repo 404 ([npm](https://www.npmjs.com/package/myinvois-mcp)) |
| TheCompanyAtlas malaysia-company-court | 1.7M companies by SSM number, plus court cases | Data source undisclosed ([GitHub](https://github.com/TheCompanyAtlas/malaysia-company-court-mcp)) |
| mcp-datagovmy and four other servers | data.gov.my / OpenDOSM | Free hosted endpoint ([GitHub](https://github.com/hithereiamaliff/mcp-datagovmy)) |
| @havahr/mcp-calculators | EPF/SOCSO/EIS/PCB/HRD levy calculations | Makes no network calls ([npm](https://www.npmjs.com/package/@havahr/mcp-calculators)) |

No MCP server exists for MySST, KWSP, PERKESO, HRD Corp, SSM filing, JAKIM, seller-side marketplace operations, Malaysian couriers, AutoCount or SQL Account. The basic code for calling MyInvois is not scarce either. A GitHub search for "myinvois" returns 68 repositories, including software development kits (SDKs) with up to 103 stars and an open-source JSON gateway that translates to UBL ([GitHub search](https://github.com/search?q=myinvois&type=repositories&s=stars&o=desc)).

## Regulation permits agents but draws three hard lines

No licence exists specifically for AI agents. Authorisation depends on the channel: an intermediary appointment for e-invoices, an approved tax agent for income-tax representation, and a BNM licence only if the platform itself holds or moves money. Three lines follow from this, and each one translates directly into product design.

**The first line is money.** Under the Financial Services Act 2013, issuing e-money needs approval (s.11) and merchant acquiring needs registration (s.17). BNM tells applicants to judge for themselves whether their model falls under the acquiring definition ([BNM](https://www.bnm.gov.my/application-for-approval-and-registration)). A layer that never holds funds, never signs merchants up to accept payments and never moves money across borders plausibly falls outside these categories. That is an inference, though, since BNM offers no published safe harbour, so get a written legal opinion. Claude's connector directory separately bans connectors that "transfer money, cryptocurrency, or other financial assets" ([Claude docs](https://claude.com/docs/connectors/building/review-criteria)). BNM licensing, PayNet's participation thresholds and directory policy all point the same way: the agent prepares a payment, and the business's own gateway or bank moves the money.

**The second line is tax representation.** Acting as a MyInvois intermediary needs no tax-agent approval, and the taxpayer stays liable for what the e-invoice says ([AJobThing](https://www.ajobthing.com/resources/blog/how-appoint-intermideary-e-invoice-submission-myinvois)). Representing taxpayers under the Income Tax Act, by contrast, is reserved for tax agents approved under s.153 ([HASiL](https://www.hasil.gov.my/en/tax-agent/profession-as-a-tax-agent/); [MAICSA](https://www.maicsa.org.my/resources/technical-research/tax-agent-license)). Any work on income-tax returns or instalment estimates therefore needs either a licensed tax-agent partner or a design where the taxpayer submits.

**The third line is formal delegation, which also decides who carries liability.** Section 17(2)(b) of the Electronic Commerce Act 2006 treats a message sent by an automated system as sent by the business that set it up ([ResearchGate](https://www.researchgate.net/publication/301554285_Electronic_Contracts_the_Malaysian_Perspective)). The business is therefore bound by what its agent sends. Failing to issue an e-invoice is an offence under ITA s.120(1)(d), carrying **RM200–RM20,000 and/or up to six months' imprisonment**, potentially for each transaction ([ClearTax FAQ](https://www.cleartax.com/my/e-invoicing-faqs-malaysia)). Under contract, that liability flows back to whoever ran the agent. The required features follow:

- scoped mandates stating what the agent may do;
- a prepare-then-confirm flow for each action;
- approvals the agent cannot fake;
- append-only logs;
- liability caps and insurance.

Some portals require an individual's own login, such as MyTax and MyDigital ID. An agent cannot stand in for that person, and logging in with someone else's credentials or by browser automation carries risks under the portal's terms and over custody of those credentials.

The data-protection (PDPA) amendments have been fully in force since 1 June 2025 ([HHQ](https://hhq.com.my/posts/full-implementation-of-the-personal-data-protection-amendment-act-2024-final-roundup/)). They apply to the platform in five ways:

- **Security.** Data processors are now directly bound by the Security Principle ([Mayer Brown](https://www.mayerbrown.com/en/insights/publications/2025/07/from-legislative-reform-to-practical-guidance-key-amendments-to-malaysias-pdpa-and-the-launch-of-cross-border-transfer-guidelines)).
- **Data Protection Officer.** A DPO is required above 20,000 data subjects, and this applies to processors too ([Christopher & Lee Ong](https://www.christopherleeong.com/viewpoints/launch-of-the-personal-data-protection-guidelines-for-mandatory-data-breach-notification-and-data-protection-officer-appointment/)).
- **Breach notification.** Controllers have 72 hours to notify the Commissioner and 7 days to notify affected people, so the platform must escalate breaches to its customers within hours.
- **Cross-border transfers.** Each transfer needs one of the listed legal bases, plus a transfer impact assessment where adequacy is relied on ([Rahmat Lim](https://www.rahmatlim.com/publication/articles/30646/new-guidelines-on-cross-border-personal-data-transfer)).
- **Automated decisions.** The April 2026 guideline on Automated Decision-Making and Profiling expects human oversight ([LexBlog](https://www.lexblog.com/2026/04/29/malaysia-jpdp-publishes-guidelines-on-dpia-privacy-by-design-and-automated-decision-making-and-profiling/)). It requires a data protection impact assessment (DPIA) for such decisions **regardless of scale** ([InCorp](https://malaysia.incorp.asia/?p=71808)). Automatically cancelling or rejecting invoices fits squarely.

Fines reach RM1 million per offence. One point is easy to miss. In an MCP setup, tool results go to whichever AI client the business chose, and that client is usually hosted abroad. Keeping personal data out of tool outputs is therefore a compliance control, not just tidiness.

The AI Governance Bill would create three risk tiers, regulate "Developers" and "Deployers", and set up a Central AI Authority. That authority would run sandboxes, require incident reporting and have reach beyond Malaysia's borders ([Baker McKenzie](https://www.bakermckenzie.com/en/insight/publications/2026/07/malaysia-public-consultation-on-the-ai-governance-bill)). The draft was declared complete on 10 September 2026, with tabling hoped for by Q1 2027 ([AI Commission](https://aicommission.org/2026/09/digital-minister-says-malaysias-draft-ai-governance-bill-complete-hopes-to-table-it-by-q1-2027/)). Agents that file tax or move money plausibly fall in the middle tier, which brings duties to assess risk, keep documentation and ensure human oversight. AI Malaysia Berhad has replaced the National AI Office as the implementing body ([Skrine](https://www.skrine.com/insights/alerts/august-2026/national-ai-office-institutionalised-as-ai-malaysi)).

Banks and payment firms will also pass their own regulatory obligations down to the platform through contracts. These include BNM's revised technology-risk rules (RMiT) and its outsourcing rules. They also include BNM's technology requirements for payment firms, effective 12 March 2027 ([Skrine](http://www.skrine.com/insights/alerts/april-2026/bank-negara-issues-policy-document-on-technology-r)). For halal, the Trade Descriptions Orders were amended three times in 2026, and JAKIM recognises 94 foreign certification bodies ([Emerhub](https://emerhub.com/malaysia/jakim-recognized-foreign-halal-bodies/)). Any agent that writes product listings must refuse to add halal claims that are not backed by a valid certificate.

### The e-invoice mandate shrank while the rules for those still in scope tightened

The research notes disagree on several mandate facts. The table gives the best-supported reading of each.

| Question | Conflicting claims | Best-supported reading |
|---|---|---|
| Exemption threshold | RM1m (Cabinet, Dec 2025) vs RM3m (Aug 2026) | **RM3m**, announced in the Prime Minister's National Day address with an LHDN statement; General Guideline v4.8 ([The Star](https://thestar.com.my/news/nation/2026/08/30/over-11-million-businesses-to-benefit-from-higher-e-invoicing-threshold-says-lhdn); [Malay Mail](https://www.malaymail.com/news/malaysia/2026/08/31/irb-stresses-voluntary-participation-as-government-lifts-einvoice-threshold-easing-compliance-for-msmes/233340)). The RM1m figure in some notes and vendor pages predates August 2026 ([VATupdate, Dec 2025](https://www.vatupdate.com/2025/12/17/malaysia-raises-e-invoicing-exemption-threshold-to-rm1-million-cancels-final-implementation-phase/)) |
| RM3m effective date | 30 Aug 2026 (publication) vs 1 Sep 2026 | **1 Sep 2026**, per LHDN's statement. One consultant page's "from 1 July 2026" contradicts the exemption ([SME Advisor](https://sme-advisor.com/einvoice-consultant)) |
| End of Phase 4 penalty relaxation | 30 Jun or 31 Dec 2026 (ClearTax, internally inconsistent) vs 31 Dec 2027 | **31 Dec 2027** ([RSM, Apr 2026](https://www.rsm.global/malaysia/sites/default/files/media/05%20Tax/Newsletter/PDF/202604%20-%20E-Invoicing.pdf); [BDO](https://www.bdo.my/en-gb/sites/e-invoicing-latest-updates)), with full enforcement from 1 Jan 2028 (fewer sources) |
| Who is now in Phase 4 | RM1m–5m vs RM3m–5m | **RM3m–5m**, plus groups caught by the related-party carve-out: no exemption if a corporate shareholder or related company turns over ≥RM3m ([LookupTax](https://lookuptax.com/tax-changes/malaysia/einvoice-exemption-threshold-3m-2026)) |
| How to get sandbox access | Email sdkmyinvois@hasil.gov.my vs self-service registration in the portal | Both routes are documented ([SDK FAQ](https://sdk.myinvois.hasil.gov.my/faq); [mirror](https://github.com/deadboy18/myinvois-docs)). Try the portal first |

LHDN says **more than 1.1 million businesses** gain from the RM3 million threshold, and it now stresses that participation is voluntary ([Malay Mail](https://www.malaymail.com/news/malaysia/2026/08/31/irb-stresses-voluntary-participation-as-government-lifts-einvoice-threshold-easing-compliance-for-msmes/233340)). Set against 268,000 businesses already using MyInvois, the compulsory market is now mostly firms above RM3 million and group companies. The rules for those still in scope have nonetheless tightened, and several deadlines create urgency:

- **The RM10,000 rule.** Since 1 January 2026, any single transaction above RM10,000 needs its own e-invoice, even during the relaxation period ([Beancount](https://beancount.io/blog/2026/09/16/malaysia-e-invoicing-phase-4-rm3m-exemption-rm10000-rule-guide)).
- **The Special Voluntary Disclosure Programme.** It runs from 7 July 2026 to 31 December 2027 and allows **penalty-free catch-up on missed or faulty e-invoices** using dedicated document versions, month by month for consolidated catch-up ([The Star](https://www.thestar.com.my/news/nation/2026/10/02/special-lhdn-disclosure-opportunities); [mirror timeline](https://github.com/deadboy18/myinvois-docs/blob/main/12-cookbook/10-implementation-timeline.md)).
- **Buyer pull.** LHDN has told individuals to collect e-invoices to support tax-relief claims ([FMT](https://www.freemalaysiatoday.com/category/nation/2026/05/09/get-e-invoices-when-filing-tax-relief-claims-says-lhdn)).
- **A tax deduction for voluntary adopters.** Businesses that adopt voluntarily can deduct up to **RM50,000 of implementation costs per year of assessment through YA2027** ([The Star](https://thestar.com.my/news/nation/2026/08/30/over-11-million-businesses-to-benefit-from-higher-e-invoicing-threshold-says-lhdn)).

The other lesson is volatility. The exemption threshold went from RM500,000 to RM1 million in December 2025 and then to RM3 million in August 2026, while the Phase 4 grace period was extended twice. Any product tied to the mandate has to treat regulatory change as a standing cost.

### Tailwinds are real but small and arrive late

Budget 2027 was tabled on 9 October 2026. It gives **RM30 million through MDEC to help 4,000 MSMEs adopt AI**, which works out to roughly RM7,500 per firm. It also adds government co-investment of RM2 for every RM1 that SMEs raise through equity crowdfunding or peer-to-peer financing for AI and digital projects, through 2030 ([The Star](https://www.thestar.com.my/news/nation/2026/10/11/digital-ministry-pushes-ai-nation-goal-under-budget-2027)). The Finance Bill has not passed, and the programme details are unconfirmed. The main SME digital grant (Geran Digital PMKS MADANI) pays 50% up to RM5,000, delivered through MDEC-registered Digitalisation Partners. It has no confirmed 2026 round ([BSN](https://www.bsn.com.my/page/GeranDigitalPMKSMadani?lang=ms-MY); [BCL](https://main.bcl.my/msme-digital-grant/)).

The National AI Action Plan 2026–2030 explicitly defines agentic AI ([AI Nation 2030 plan](https://strapi.naio.okie.my/uploads/AI_Nation_2030_National_AI_Action_Plan_2026_2030_Eng_V_290726_49cb382621.pdf)). The widely quoted adoption figure, "27% of businesses, about 2.4 million, use AI" ([US-ASEAN](https://www.usasean.org/article/malaysia-accelerates-national-ai-agenda)), implies about 8.9 million businesses in total. That is far above any business count elsewhere in the evidence, so treat it as a soft signal. No verified SME counts or SME software-spend figures were obtainable.

The larger tailwinds come later. Open finance arrives in 2027–2028. MyDigital ID has no published terms for businesses to use it. Card-network agent payments are still pilots for issuing banks. All three matter for a 2027–2028 roadmap and should be planned for, but none can be built on today.

## Thin wrappers are becoming a commodity; deep compliance work is unclaimed

The competition falls into five groups, and none of them occupies the position this project should take.

**Global integration platforms** compete on breadth, and they are well funded:

- Arcade raised a **US$60 million Series A in June 2026**, bringing total funding to US$72 million, and pitches itself as "the secure action layer behind every production AI agent" ([BusinessWire](https://www.businesswire.com/news/home/20260615229631/en/Arcade-Raises-$60M-to-Become-the-Secure-Action-Layer-Behind-Every-Production-AI-Agent)).
- Composio advertises 1,000+ apps at a reported ~US$0.0003 per tool call after a US$29 plan. That price comes from a secondary source and is unverified ([Scalekit](https://www.scalekit.com/blog/composio-alternatives)).
- Nango lists 7,000+ tools ([Nango](https://nango.dev/blog/composio-vs-nango/)).
- Workday bought Pipedream ([Zapier](https://zapier.com/blog/pipedream-vs-zapier/)).

Their Malaysian coverage is thin. Pipedream's Billplz component handles login only and has no actions, and it has no Shopee, Lazada, Bukku or toyyibPay components at all ([GitHub](https://github.com/PipedreamHQ/pipedream/tree/master/components/billplz)). Composio's, Zapier's and Arcade's catalogues could not be checked.

**Mass "country-pack" publishers** show how quickly thin connectors decay. Wishpool published 91 servers across dozens of countries in three days in July 2026. Its Malaysian payments repository now returns 404, and a directory listed its MyInvois server as unhealthy. A connector anyone can generate in an afternoon has a shelf life of weeks.

**Local community projects** show that basic MyInvois access is now commodity code. techtemplemy's server already enforces a one-time confirmation token in code, which is the safeguard this repository's approval layer fails to deliver (see the next section).

**Local e-invoice middleware vendors** hold the customer relationships. Examples include einvoice-online.my, Kiizen, Xantec, Orchida and SQL's own module. Pricing reported in search summaries, and unverified, runs at **RM0.50–2.00 per validated invoice plus a monthly fee**, or **RM100–2,500 per month**. Custom ERP connectors reportedly cost **RM55,000–150,000** ([Jomeinvoice](https://jomeinvoice.my/myinvois-vs-api-integration-vs-e-invoicing-midldleware/); [Gotchaa Lab](https://gotchaa-lab.com/blog/2026-04-16-lhdn-einvoice-integration-cost-malaysia); [Xantec](https://xantec.com.my/software/e-invoicing/)). "LHDN does not approve, certify or accredit any e-invoicing software" ([Jomeinvoice](https://jomeinvoice.my/article/best-e-invoice-middleware-malaysia/)), so no vendor has a certification moat. None was seen offering an MCP interface, and any of them could add one cheaply. That makes them partners or white-label customers as much as rivals.

**Incumbents with their own MCP servers** are the last group. Xero, QuickBooks, Zoho, Stripe and PayPal all have official servers, and one curated list counts 280+ vendor-built servers ([VoltAgent](https://github.com/VoltAgent/official-mcp-servers)). Three latent threats remain: LHDN, Shopee or Bukku shipping their own MCP, and the government's MyGOV agent.

No Malaysian startup positioned as an agent-connectivity hub with disclosed funding was found. Tracxn's figure of US$19.2 million raised by all Malaysian AI companies looks implausibly low ([Tracxn](https://tracxn.com/d/artificial-intelligence/ai-startups-in-malaysia/__hVSSp7FF1uvnLIn7K53lSbzVrwTNBT3_PF67AJ6TRYQ)). Both points are unverified.

The open space is depth rather than breadth. Nothing found anywhere covers the following:

- **A production-grade MyInvois service for many clients.** It would generate UBL documents, sign them, cache a token per taxpayer, handle bulk cancellation, the disclosure-programme document versions and the RM10,000 rule, and keep an audit trail.
- **Seller-side marketplace operations.** Today's Shopee and Lazada MCP servers are buyer-side or market-research tools.
- **Payments tied to invoices.** A loop running from gateway collections to automatic matching against e-invoices to accounting sync.
- **Preparing statutory files** for EPF, PERKESO and e-PCB Plus.
- **A trust layer.** Consent records, a credential vault, approvals, audit, PDPA-grade handling, Bahasa Malaysia support and an option to host in Malaysia.
- **Bridges to the desktop accounting software** most SMEs actually run.

Indonesia shows the pattern can travel: a 40-tool civic stack already covers 11 government portals, including the halal agency BPJPH ([MCP Registry](https://registry.modelcontextprotocol.io/v0/servers?search=indonesia&limit=100)).

Directory rules decide how the product is framed. Claude's directory requires that a connector "call your own first-party APIs, or APIs you legitimately proxy", with the server's domain matching the service. It asks whether a proxied API is used "with permission" ([Claude docs: Submit](https://claude.com/docs/connectors/building/submission)). It also requires every tool to carry a title and a read-only or destructive flag, and it rejects catch-all tools ([Claude docs: Review criteria](https://claude.com/docs/connectors/building/review-criteria)). A "Malaysia hub" that simply passes through other companies' APIs therefore struggles with both directories and incumbents.

The framing that holds is a first-party compliance API. Its own work (normalising invoices, generating UBL, validating, signing, approvals and audit) is the product, and MyInvois sits behind it under each taxpayer's appointment. ChatGPT's directory lets an app target specific countries ([OpenAI](https://openai.com/index/developers-can-now-submit-apps-to-chatgpt/)). Microsoft Copilot Studio accepts only tools served over Streamable HTTP ([Babybots](https://www.babybots.ai/guides/connect-copilot-studio-agents-mcp-2026)).

Precedent points the same way. Thomson Reuters paid about US$800 million for Pagero, an e-invoicing network valued for its compliance coverage across many countries ([Accountancy Age](https://accountancyage.com/2024/02/27/thomson-reuters-buys-pagero-in-800-million-deal/?amp=1)). Regional compliance depth gets bought. Charging per tool call does not survive horizontal pricing near US$0.0003 a call, so price per completed regulated outcome instead.

## The repository is a demo: keep the idea, rebuild the code

The audit treats the repository as primary evidence. Tests pass 22/22 in 0.74 seconds on Python 3.13, and the last code commit was in May 2026. It finds a well-documented, single-user local demo.

### Only a fraction of the integrations are real

The 45 actions are exposed identically through the CLI, REST and stdio MCP (`src/malaysia_agent_ops/service.py:39-85`). Only eleven provider actions make live HTTP calls, seven for MyInvois and four for CIDB, and every test mocks them. The roadmap still lists "P4 live sandbox workflow" as Next (`docs/roadmap-and-phases.md:198`). CIDB calls `/internal/...` paths on a portal backend using a bearer token pasted by hand (`providers.py:231,245,264,283`), not a documented API. Several "integrations" are made-up test data (fixtures):

- SSM lookups use five fake companies (`fixtures.py:4-50`).
- The halal directory holds three fake certificates (`fixtures.py:53-78`).
- DuitNow requests are an invented `duitnow://sandbox/request/...` URI, not a real DuitNow QR code (`service.py:2389-2398`).
- Sandbox invoice validation rejects any TIN outside the five fixtures (`service.py:2331-2336`), so no real business can use it.

### The MyInvois adapter has correct plumbing but none of the hard parts

It contains about 150 lines of correct plumbing: the token request, the `onbehalfof` header, and the document-type, TIN, submission and cancel endpoints (`providers.py:99-206`). The hard 80% is missing:

- No UBL generation; the invoice model lacks most of the ~55 mandatory fields (`service.py:2377-2386`).
- No signing code.
- No document hashing.
- No token cache: it logs in again on every call (`service.py:2753-2785`), against a limit of 12 logins per minute.
- No rate limiting.
- Status mapping reads only the first document of a submission (`service.py:2738-2751`).
- An operator-precedence bug stores the invoice number as "unknown" whenever every document is rejected (`service.py:2585`).

### The approval gate fails in practice

The pitch rests on approvals, and the probe broke them in five ways:

1. **The agent can approve itself.** Identity is self-asserted: passing `identity.verified: true` is enough (`service.py:429`). `approvals.approve` is a tool the same agent can call, and the skill tells it to (`skill/SKILL.md:39,74`).
2. **One approval covers any payload.** Approvals are matched by action name only (`service.py:2416`). One approval authorised two different real submissions in the probe.
3. **Low-level bypass.** Declaring `provider: "sandbox"` on the low-level tool runs a real submission with no approval (`service.py:2517-2520`).
4. **Cancel bypass.** A real cancellation without `provider: "real"` matches no approval policy (`service.py:2462-2463`).
5. **Self-marked payments.** The agent can mark its own invoices paid by replaying the payment event the system suggests.

### Security is open by default

- The HTTP server has no authentication.
- `Access-Control-Allow-Origin: *` (`server.py:154`) lets any web page drive approvals on the local API.
- The payment webhook secret is loaded but never checked (`config.py:104`).
- Secrets travel as tool arguments, and the MyInvois bearer token is returned to the model (`service.py:2141`).
- Raw request payloads are stored in plaintext (`service.py:255-271`).
- There are no tenants, users or vault; a single global configuration holds one set of credentials (`config.py:24-37`).
- There is no idempotency: the same invoice submitted twice produces two submissions (`db.py:75-94`).
- There is no audit log, despite the docs' claim that "every action, transition, and exception is recorded" (`docs/purpose-and-architecture.md:139`).

### The MCP layer cannot reach hosted clients

The MCP server is about 290 lines of hand-written stdio JSON-RPC. It always advertises protocol version 2025-11-25 (`mcp_server.py:11`), while the current revision is 2026-07-28 ([MCP blog](https://blog.modelcontextprotocol.io/posts/2026-07-28-release-candidate/)). Its other defects:

- 40 of the 45 tools have no input schema.
- Several safety flags are wrong (`mcp_server.py:161-181`). `invoices.status` changes state but is marked read-only, and the legally binding submit is marked non-destructive. This matters because Claude runs read-only tools without asking for confirmation ([Claude docs](https://claude.com/docs/connectors/building/review-criteria)).
- Dotted tool names break the function-name rules of Anthropic and OpenAI.
- The server crashes on any unexpected exception, and it replies to notifications, which the spec forbids.
- With no Streamable HTTP or OAuth, it cannot become a Claude.ai or ChatGPT connector.

### The halal module is thin, the tests expire and the docs overclaim

The halal precheck is 679 lines with 15 rules that cite only two sources. A rule passes if any document of the declared kind exists, and the files themselves are never opened. Its "OCR" compares against hand-written JSON labelled `glm-ocr` (`examples/ocr/barakah/supplier-a-coconut-cert.json:3`). The certificate in `examples/barakah-curry-paste.dossier.json:118` expires on 2026-10-15, so the assertions at `tests/test_end_to_end.py:282` and `:364` **fail from 16 October 2026**. The docs claim "Live MyInvois integration" (`docs/purpose-and-architecture.md:151`) and "Live sandbox tested" (`docs/index.html:1078`), neither of which is true.

### Why the defects matter now

Each defect lines up with a legal exposure from the previous section:

- **The approval gate.** The self-approving gate conflicts with the human-oversight expectation in the automated-decision guideline.
- **Plaintext secrets.** These conflict with the PDPA Security Principle that now binds processors.
- **The bypasses.** A bypassable submit creates exactly the per-transaction liability that the Electronic Commerce Act attributes to the SME.

| Decision | What | Why |
|---|---|---|
| **Keep (concepts)** | Response envelope with `status`/`next_action`/`blocking_reason` (`service.py:160-178`); approval rules keyed to policy; "block honestly, never fake a submission"; the halal evidence-class register | Good agent-UX design and good trust principles; competitors lack the envelope |
| **Keep (as reference)** | MyInvois endpoint and header map (`providers.py:66-213`); test scenarios as acceptance specs | Saves days of SDK reading |
| **Park** | `halal_precheck.py` plus its JSON rules | Only `cli.py:10` imports it, so it is easy to lift. No halal API exists, its sourcing is thin, and JAKIM's own AI screening may absorb pre-screening |
| **Discard** | Hand-written MCP server, `server.py`, `db.py`, fake-data providers (SSM, halal directory, DuitNow, trade), the CIDB adapter, ~1,000 lines of halal CRUD, the synchronous workflow runner, the dashboards and videos | Retrofitting multi-tenancy, OAuth, remote MCP, a vault, signing and idempotency costs more than rebuilding |

On the three options, the evidence is clear. **Continuing as is fails**: the code cannot serve a second business, cannot reach hosted AI clients and cannot be trusted to gate a legally binding action. **Pivoting everything is right for the code but wrong for the idea.** The landscape confirms the original thesis: Malaysia-specific actions, honest blocking, approvals keyed to policy, and responses built for agents. The audit estimates 2–4 days for MCP transport and auth and about a week to type the tools, with multi-tenancy as the real cost. The answer is to **narrow the scope and rebuild the code**: freeze the repository as a `v0-reference` tag and start a clean build.

## Ninety days to a paid, multi-tenant MyInvois product

### Position as the mandate and compliance layer, sold through intermediaries

Hold off on the "one-stop center" label until it is earned, and avoid competing head-on with Arcade's generic "action layer" pitch. Position the product as **the compliance-grade way for any AI agent to issue, fix and reconcile Malaysian e-invoices for a business**: acting under the director's MyInvois appointment, with a human approval and a tamper-evident audit trail. The product needs two surfaces on one core: a remote MCP server for Claude, ChatGPT and Copilot, and a REST API for software vendors. Its value is its own work (normalising invoices, generating UBL, checking TIN+BRN, applying consolidation and RM10,000 logic, signing, approvals, audit, status tracking). That satisfies the directory rule on first-party APIs and is exactly what free wrappers skip.

The first buyers should not be micro-SMEs. They have a free portal, most are now exempt below RM3 million, and their willingness to pay is low. Three groups fit better:

- **Bookkeeping and accounting firms** that already act for many SMEs. Each client appoints the firm's platform once. The intermediary model is built for one-to-many, and LHDN's login limit per Client ID rewards a shared token cache.
- **SME software builders without a MyInvois-plus-agent capability.** Point-of-sale (POS) systems in the Loyverse mould, marketplace seller tools, and agencies building agents can use it white-labelled.
- **Firms above RM3 million on Xero or QuickBooks**, whose MyInvois flows are clumsy.

Each group has a deadline that creates urgency: the disclosure programme ends on 31 December 2027, the RM10,000 rule already applies, Phase 4 enforcement starts in 2028, and the RM50,000 deduction runs through YA2027. Demand from every one of these segments is **unverified**, which is why the plan opens with interviews.

### The wedge: about a dozen workflow-level tools

The wedge is around a dozen tools built around real workflows rather than raw endpoints. In the order an agent uses them:

1. **Check a counterparty** (TIN+BRN validation and search).
2. **Draft an e-invoice.** This read-only step normalises the data, validates it and returns a preview plus a confirmation handle.
3. **Submit,** which requires that handle and an approval the agent cannot grant itself.
4. **Track status** through Get Submission. Do not poll the 12-per-minute search endpoints.
5. **Correct or reverse.** This covers cancel and reject within the 72-hour window, bulk cancel, and credit, debit and refund notes.
6. **Handle special cases.** Build monthly consolidated B2C invoices with an automatic RM10,000 carve-out, and issue self-billed invoices to foreign vendors.
7. **Plan disclosure-programme catch-up** from the client's ledger.
8. **Request approvals and export the audit trail.**

| Order | Integration | Access path | Why |
|---|---|---|---|
| 1 | MyInvois preprod, then production, as intermediary | Register the system in the preprod portal (email LHDN as fallback); directors appoint the platform | The only sanctioned write API; the wedge |
| 2 | Signing certificate from Pos Digicert or MSC Trustgate | Commercial purchase | Signed v1.1 documents; protects against v1.0 being retired |
| 3 | Out-of-band approvals: a web page opened through MCP's URL-mode prompt, plus WhatsApp utility templates | Meta business verification | Owners approve where they already are; ~US$0.014 per message |
| 4 | One gateway: Billplz or CHIP (collections plus webhooks; payouts off) | Merchant account in each business's name | Closes the invoice-to-payment loop without holding funds |
| 5 | Bukku API and Xero API | Per-company token; OAuth | Source of invoices and target for reconciliation |
| 6 | Shopee, TikTok Shop and Lazada developer approval, plus EasyParcel | **File the developer applications in month one** because review takes time | Consolidated e-invoices for marketplace sales; shipping |
| Later | SSM data via Infomina/CTOS; EPF, PERKESO and e-PCB file preparation; halal precheck; open finance; MyDigital ID | Contracts, file preparation, 2027+ rails | Only after paying customers |

### The technical rebuild plan

Week figures below are estimates built from the audit's effort numbers, not measured.

| Phase | Build | Exit criterion |
|---|---|---|
| 0 (week 0–1) | Tag the repo `v0-reference`; inject a clock into the date-dependent tests; remove the "Live" overclaims and absolute paths. Start preprod registration, a certificate quote, marketplace developer applications and an MDEC Digitalisation Partner enquiry. Run 15–20 customer interviews | 3 design partners committed |
| 1 (weeks 1–3) | **Foundation:** Python with the official MCP SDK; Postgres with migrations; an external OAuth 2.1 identity provider. Data model for tenants, users, taxpayers and intermediary appointments (permissions, validity dates). Encrypted credential vault; append-only audit log; idempotency keys on every write. Approvals bound to a hash of the payload, single-use, time-limited and granted by a separately authenticated human | Every bypass from the audit is a passing regression test |
| 2 (weeks 3–8) | **MyInvois depth:** invoice model with all mandatory fields, converted to UBL 2.1 JSON; v1.0 documents first, then signed v1.1. Per-taxpayer token cache and a rate limiter that honours `Retry-After`. Status mapping for multi-document submissions; cancel, reject and bulk cancel. Consolidated invoices with the RM10,000 guard; self-billed invoices; credit, debit and refund notes; disclosure-programme document versions. Nightly round-trip tests against preprod | Full lifecycle passes in preprod for every document type |
| 3 (weeks 8–10) | **Remote MCP:** Streamable HTTP built on the stateless 2026-07-28 spec, with a fallback for older clients. Standard OAuth metadata and client registration (CIMD, with DCR as fallback). Typed tools with underscore names and correct safety flags. Approvals through URL-mode prompts; SKILL.md playbooks; REST on the same core | Listed in Claude's directory and in ChatGPT for Malaysia; works in Copilot Studio |
| 4 (weeks 10–13) | **Production with design partners:** option to host in Malaysia; DPIA; DPO; terms of service with liability caps; professional indemnity insurance quote | ≥1 paying customer; zero unapproved destructive actions in the audit log |
| 5 (months 4–9) | **Quote-to-cash:** gateway webhooks (signed and de-duplicated), automatic matching of payments to invoices, Bukku/Xero sync. Then marketplaces and EasyParcel | Payment-to-invoice match rate; a second revenue line |

Several principles run through every phase:

- **Backward compatibility.** Build to the stateless 2026-07-28 spec, but keep older clients working. A mid-2026 compatibility check found only **2 of 22** clients and SDKs supported the new revision ([Hidekazu Konishi](https://hidekazu-konishi.com/entry/which_mcp_clients_a_remote_mcp_server_lets_in.html)).
- **No agent-callable approval.** Never expose an approval tool the agent can call; approvals happen out of band.
- **Secrets stay out of the model.** Never accept secrets as tool arguments or return them in results.
- **Minimal personal data in results.** Keep personal data out of tool outputs, because those outputs often go to AI clients hosted abroad.
- **Separate read and write tools.** Pin tool descriptions too: injection and tool-poisoning attacks are now well documented ([OWASP MCP Top 10](https://github.com/OWASP/www-project-mcp-top-10)).
- **Watch the MyInvois SDK.** The community docs repository ships a skill that audits the SDK for changes ([deadboy18/myinvois-docs](https://github.com/deadboy18/myinvois-docs)). Run it on a schedule, because LHDN changed the API at least four times in 2026.

### Pricing, distribution and the day-90 decision gate

Pricing hypotheses to test are a **fee per validated document, benchmarked against the RM0.50–2.00 middleware band**, plus a **monthly fee per client TIN** for firms and **white-label endpoint fees** for software vendors. For distribution:

- Register as an MDEC Digitalisation Partner to reach grant-funded buyers.
- List in Claude's directory, where new connectors are listed automatically as "Community", and in ChatGPT, targeted at Malaysia.
- Offer Copilot Studio support for Microsoft 365-heavy firms.

The day-90 gate decides what happens next:

- **Continue** if at least three design partners are submitting production e-invoices under appointments, at least one is paying, and no destructive action ran unapproved.
- **Pivot to white-label infrastructure** for middleware and software vendors if accounting firms won't pay but vendors will.
- **Switch the wedge** to marketplace seller operations if neither group pays. That means consolidated e-invoices plus payout reconciliation for Shopee and TikTok Shop sellers.

### Risks and open questions to validate

| Risk or question | Why it matters | Validate or mitigate |
|---|---|---|
| Willingness to pay (firms, vendors) is unverified | No primary demand or SME-spend data was reachable; the free portal sets the price ceiling | 15–20 interviews and 3 letters of intent by week 4; verify DOSM/SME Corp counts |
| Scaling as an intermediary | 12 logins per minute per Client ID caps how many taxpayers stay active; it is unknown whether LHDN allows several Client IDs | Ask the SDK team; load-test preprod |
| Signing model | Unknown whether v1.0 (unsigned) will be retired, and whether the intermediary's certificate or each taxpayer's certificate signs | Ask LHDN, Pos Digicert and MSC Trustgate before Phase 2 |
| Directory acceptance | The rules on "legitimately proxy" and "money transfer" are untested; it is unclear whether creating a payment link counts as a transfer | Email mcp-review@anthropic.com before building payment tools; confirm ChatGPT is available in Malaysia |
| Per-transaction liability | Strict penalties fall on the SME and flow back to the platform under contract | Liability caps, professional indemnity cover, and an opinion from Malaysian counsel |
| Payment licensing | No safe harbour for orchestration-only platforms | Legal opinion; use gateway partner programmes; never hold funds |
| PDPA and AI Governance Bill duties | DPO, DPIA, transfer assessments now; middle-tier AI duties likely from 2027 | Keep a risk register and an incident playbook from day one |
| Incumbents building their own | LHDN, Bukku, SQL or middleware vendors ship an MCP | Offer them the white-label endpoint first; win on depth |
| Policy churn | Threshold and grace period changed repeatedly in 2025–2026; the API changed at least 4 times in 2026 | Scheduled SDK audits; treat rule changes as product updates |
| Unverified inputs | Middleware pricing, Composio and Nango pricing, startup funding, WhatsApp rates (copied from a reseller's table), Visa/Mastercard details (mostly secondary) and the ASSIST 2.0 date all rest on secondary or search-summary sources | Check each against the primary page before it drives a decision |

## Conclusion

Malaysia's agent economy is being built on delegation primitives, not open APIs. Today that means the MyInvois intermediary appointment. Tomorrow it means open-finance consent, MyDigital ID logins and card-network agent tokens. The scarce asset is therefore not connectors, which anyone can generate and which decay within weeks. It is a trustworthy **mandate ledger**: who authorised which agent to do what, for which business, until when, and with whose approval. Building that core once, with MyInvois as its first and only sanctioned write target, turns "one-stop center" from "one place that proxies everything" into "one place that holds the authority and the audit trail". When 2027–2028 brings new rails, they plug into that core.

The timing is unusually clear. The disclosure programme runs to the end of 2027, Phase 4 enforcement begins in 2028, and the AI Governance Bill and open finance both start in 2027. A founder who has a production intermediary with clean audit trails by mid-2027 becomes the natural partner, white-label supplier or acquisition target for incumbents that need Malaysian depth they will not build themselves. The repository's lasting contribution is its principles: block honestly, never fake a submission, and tell the agent what to do next. Those principles were right, but the code does not yet enforce them, and the rebuild is where they become real.
