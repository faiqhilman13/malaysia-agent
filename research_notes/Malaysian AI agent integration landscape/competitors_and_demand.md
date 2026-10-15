# Competitors and Demand: Malaysian "One-Stop Agent Connectivity Hub" (as of 15 Oct 2026)

> **Method and reliability note (read first).** This session ran into two hard limits. (1) The shared web-search budget ran out after 3 searches. (2) The sandbox's egress policy blocked almost every domain: hasil.gov.my, smecorp.gov.my, dosm.gov.my, mdec.my, composio.dev, docs.stripe.com, zapier.com, pipedream.com, arcade.dev, glama.ai, mcp.so, smithery.ai, pulsemcp.com, dealstreetasia.com, vulcanpost.com, e27.co, techinasia.com, thestar.com.my, theedgemalaysia.com, jomeinvoice.my and gotchaa-lab.com all returned DNS failures or proxy 403s.
>
> Only **github.com** (web pages, not the API) and the **official MCP registry** (registry.modelcontextprotocol.io) could be fetched. As a result:
> - The **MCP-server inventory (Q1) is solid and was checked directly on 2026-10-15.**
> - Findings from the 3 web searches appear as "search-result summary" because the pages themselves could not be opened.
> - Everything else (startups, funding, global platform pricing, demand statistics, halal) appears **only under Gaps as "UNVERIFIED LEADS"**. These come from the analyst's background knowledge, which runs only to about mid-2026. Each lead lists a URL to check before anyone relies on it, and none should be cited as fact without that check.
> - The registry's `search` parameter matches **server names, not descriptions**. For example, `search=billplz` returned 0 results even though `malaysia-payments-mcp` describes itself as running on Billplz. Name-based counts therefore understate coverage.

## Q1. Existing MCP servers / agent tools for Malaysian services

### Takeaway
As of mid-October 2026 there are about 20 MCP servers for Malaysian services. **All of them are unofficial**, and all were built by individuals or small third parties. None comes from LHDN, PayNet, SSM, Billplz, Bukku, Shopee or Lazada. Most have 0–11 GitHub stars and were created between 2025 and 2026. Only about five can perform write actions (submit an e-invoice, take a payment, post accounting entries). The rest are read-only data lookups. One global "country-pack" publisher (Wishpool) bulk-published Malaysia invoice and payment servers in July 2026 alongside about 90 other countries, but the repos now return 404 and a directory listed the server as unhealthy. **The Malaysian layer is fragmented, thin and low-trust, so a credible, maintained and compliant hub would have no real incumbent today.**

### Cited Findings

**Transactional (write-capable) servers for Malaysian services**
- **techtemplemy/mcp-myinvois.** An open-source MyInvois toolkit with an MCP server, a Claude skill, a CLI and guides. It has **11 tools**: validate_tin, search_tin, get_supplier_profile, draft_invoice, prepare_ubl_submission, confirm_submission, get_submission, get_document, list_recent_documents, cancel_document and reject_document. Sandbox is the default and production is opt-in. Submission takes two steps, with a one-time confirm token that expires after 10 minutes. It runs over stdio with no telemetry. License WTFPL; **3 stars, 1 fork, 14 commits**; last updated about 5 Sep 2026. It is labelled "Unofficial · not affiliated with LHDN." — [GitHub](https://github.com/techtemplemy/mcp-myinvois); [GitHub search "myinvois mcp"](https://github.com/search?q=myinvois+mcp&type=repositories&s=updated&o=desc) (fetched 2026-10-15)
- **app.wishpool/malaysia-invoice-mcp v0.1.0.** Described as "Malaysia LHDN MyInvois: AI agents submit, query and cancel e-invoices, stateless BYO [bring-your-own credentials]." Published to the official registry on **2026-07-09**. — [MCP Registry search=malaysia](https://registry.modelcontextprotocol.io/v0/servers?search=malaysia&limit=100)
- **app.wishpool/malaysia-payments-mcp v0.1.0.** Described as "Malaysia payments for AI agents — FPX banking, DuitNow QR, cards via Billplz. Never holds funds." Published **2026-07-08**. — [MCP Registry search=malaysia](https://registry.modelcontextprotocol.io/v0/servers?search=malaysia&limit=100)
- **Wishpool is a mass "country-pack" publisher, not a Malaysia specialist.** The first page of results under the `app.wishpool` namespace lists **91 distinct servers**, almost all published between 8 and 10 July 2026:
  - **57 payment servers**, wrapping Stripe, Mollie, Mercado Pago, Paystack, Midtrans, PayMongo, Billplz, HitPay and others.
  - **24 e-invoice servers**, including India GST IRN, Mexico CFDI, Poland KSeF, Italy SdI and Peppol via Storecove.
  - **9 logistics servers**, including Indonesia via Biteship. There is **no Malaysia logistics server**.
  - **1 merchant-of-record server** for digital goods.

  The listing has a next-page cursor, so there are more. — [MCP Registry search=wishpool](https://registry.modelcontextprotocol.io/v0/servers?search=wishpool&limit=100)
- **The Wishpool code may no longer be live.** On 2026-10-15 the linked repo `github.com/junter1989k-ai/malaysia-payments-mcp` returned **HTTP 404**. The owner's GitHub profile shows only one unrelated public fork, with no name or company. — [GitHub repo (404)](https://github.com/junter1989k-ai/malaysia-payments-mcp); [GitHub profile](https://github.com/junter1989k-ai)
- **A Glama listing of the Wishpool MyInvois server showed "Status: Unhealthy" as of 2026-09-13.** It described the server as covering TIN validation, drafting, submission and document management. (Search-result summary; the page itself could not be opened.) — [Glama connector](https://glama.ai/mcp/connectors/app.wishpool/malaysia-invoice-mcp)
- **centry-digital/bukku.** An MCP server and CLI for **Bukku**, the Malaysian cloud accounting platform, published on npm as `@centry-digital/bukku-mcp` and `@centry-digital/bukku-cli`. The CLI covers invoices, contacts and products. It needs a Bukku API token and company subdomain. MIT licence; **7 stars, 3 forks, 181 commits**, which makes it the most actively developed Malaysian business MCP found. Nothing indicates it is official from Bukku. — [GitHub](https://github.com/centry-digital/bukku); [GitHub search "malaysia mcp"](https://github.com/search?q=malaysia+mcp&type=repositories&s=stars&o=desc)
- **mrslbt/xendit-mcp.** An unofficial Xendit MCP with **14 tools** covering balances, invoices, payment links, transactions and disbursements. Payout tools are disabled by default and use prepare/confirm steps. It claims coverage of ID, PH, TH, VN and **MY**, but the README says Malaysia behaviour is "not yet verified" because only IDR and PHP were sandbox-tested. MIT; 4 stars; 16 commits. Registry versions: 0.1.2 (2026-04-14), 0.2.0 (2026-06-22), 0.3.0 (2026-08-02). — [GitHub](https://github.com/mrslbt/xendit-mcp); [MCP Registry search=xendit](https://registry.modelcontextprotocol.io/v0/servers?search=xendit&limit=100)
- **thebuilderscollective/lazada-community-mcp.** Buyer-side grocery shopping on Lazada/RedMart through **browser automation, not the official API**, with 25 tools. Checkout sits behind a one-use approval token with a default S$300 ceiling, which suggests Singapore. MIT; 3 stars; 8 commits; "not official Lazada software." — [GitHub](https://github.com/thebuilderscollective/lazada-community-mcp)
- **chanoktrue/lazada-mcp.** Python, 1 star, updated Jul 2026. GitHub returned only 3 repos for "lazada mcp" in total. — [GitHub search "lazada mcp"](https://github.com/search?q=lazada+mcp&type=repositories&s=stars&o=desc)
- **dewatagiri/myinvois-helper.** Read-only tools: check_einvoice_obligation, draft_einvoice (with SST totals and a readiness checklist) and lookup_classification_code. Built as a "ChatGPT plugin for Malaysian e-Invoicing" (Apps SDK / MCP Apps). The README credits Mohamed Azman bin Mohamed Taufik (PintuNiaga). MIT; **0 stars**; 23 commits. — [GitHub](https://github.com/dewatagiri/myinvois-helper)
- **io.github.ANHQ280/myinvois-mcp v0.1.1.** Described as "Malaysian LHDN e-invoicing (MyInvois) compliance rules covering scope, validation, and change-diffs." Published 2026-06-17. Its linked repo `ANHQ280/myinvois-compliance-rules-feed` returned 404 on 2026-10-15. — [MCP Registry search=myinvois](https://registry.modelcontextprotocol.io/v0/servers?search=myinvois&limit=100)
- **Other e-invoice-adjacent tools.**
  - **einvoice-validators-mcp** (SamirChatwiti) validates MyInvois and several other countries' formats. It needs a RapidAPI key. (Search-result summary.) — [Glama](https://glama.ai/mcp/servers/SamirChatwiti/einvoice-validators-mcp)
  - **HengYpinn/myinvois-mcp-rag** is a Python RAG project with 3 stars, last updated 15 Jan 2026. — [GitHub search](https://github.com/search?q=myinvois+mcp&type=repositories&s=updated&o=desc)
  - **chanphil2002/myinvois-ai-mapper** is a Spring Boot and React app that uses Claude to map sales documents into MyInvois format. It is not an MCP server and calls itself a "walking skeleton." (Search-result summary.) — [GitHub](https://github.com/chanphil2002/myinvois-ai-mapper)
- **The official registry has no "lhdn" or "billplz" servers.** Searching for "lhdn" returned 0 and "billplz" returned 0, because the search is name-based. "lazada" also returned 0. — [Registry lhdn](https://registry.modelcontextprotocol.io/v0/servers?search=lhdn&limit=100); [Registry billplz](https://registry.modelcontextprotocol.io/v0/servers?search=billplz&limit=100); [Registry lazada](https://registry.modelcontextprotocol.io/v0/servers?search=lazada&limit=100)
- **GitHub has no "billplz mcp" repo.** The search returned 0 results. — [GitHub search](https://github.com/search?q=billplz+mcp&type=repositories)

**Read-only data and lookup servers for Malaysian services**
- **io.github.TheCompanyAtlas/malaysia-company-court v1.0.0.** Malaysian company search by name and **SSM number**, linked to court cases. It reports about **1.7 million companies, LLPs and Labuan entities** and about 26,000 court cases, exposed through 4 tools. Access is via Google OAuth at thecompanyatlas.com. It does not say whether the data comes from the SSM e-Info API or scraping. 0 stars, 1 commit. Published 2026-10-08. The same publisher also runs `singapore-acra`. — [GitHub](https://github.com/TheCompanyAtlas/malaysia-company-court-mcp); [MCP Registry](https://registry.modelcontextprotocol.io/v0/servers?search=malaysia&limit=100); [Registry search=singapore](https://registry.modelcontextprotocol.io/v0/servers?search=singapore&limit=100)
- **io.github.IndoTender/malaysia-court v1.0.0.** Searches Federal Court, Court of Appeal and High Court judgments. Published 2026-09-01. The same publisher runs `indonesia-regulatory` (BPOM, DGIP and Komdigi). — [MCP Registry](https://registry.modelcontextprotocol.io/v0/servers?search=malaysia&limit=100); [Registry search=indonesia](https://registry.modelcontextprotocol.io/v0/servers?search=indonesia&limit=100)
- **io.github.r3dz4r/malaysia-data-engine.** Read-only NPRA pharmaceutical records, with 5 tools. Published 2026-08-30. The same author maintains `r3dz4r/datapulse-my`, an "open-source trust and interoperability layer for Malaysian public data." — [MCP Registry](https://registry.modelcontextprotocol.io/v0/servers?search=malaysia&limit=100); [GitHub search](https://github.com/search?q=malaysia+mcp&type=repositories&s=stars&o=desc)
- **eu.ansvar/malaysian-law-mcp v1.0.1.** Full-text search of Malaysian statutes. Published 2026-02-22 and now **deprecated**, superseded by the authenticated paid "Ansvar Gateway." — [MCP Registry search=malaysian](https://registry.modelcontextprotocol.io/v0/servers?search=malaysian&limit=100)
- **data.gov.my servers.**
  - **faridyusof727/datagovmy-mcp** (Go) has **11 stars** and was last updated Jun 2025, which may be stale.
  - **hithereiamaliff/mcp-datagovmy** covers dataset catalogue and search, DOSM datasets, Parquet files, weather, flood and earthquake warnings, and GTFS transit. It offers a **free hosted endpoint** at `mcp.techmavie.digital/datagovmy/mcp` with no auth. MIT; 3 stars; 61 commits.

  Sources: [GitHub search](https://github.com/search?q=malaysia+mcp&type=repositories&s=stars&o=desc); [GitHub repo](https://github.com/hithereiamaliff/mcp-datagovmy)
- **Other read-only Malaysian servers on GitHub:**
  - hithereiamaliff/mcp-malaysiatransit: 4 stars; real-time bus and train data for 10+ cities.
  - Junhui20/malaysia-calendar-api: public holidays and school calendar.
  - ZhunHao/ktmb: rail data.
  - yting27/weather-my-mcp.

  The GitHub search "malaysia mcp" returned **53 repositories** in total, and the top 10 by stars range from 1 to 53 stars. — [GitHub search](https://github.com/search?q=malaysia+mcp&type=repositories&s=stars&o=desc)
- **ariffazil/arifOS (53 stars).** The top-starred "malaysia mcp" repo, but it is a generic "policy kernel for AI agents that judges actions before execution," not a Malaysian service connector. — [GitHub search](https://github.com/search?q=malaysia+mcp&type=repositories&s=stars&o=desc)
- **SeaMCP (Singapore-based; "Southeast Asia's data repository"; joined GitHub Sep 2026).**
  - **shopee-mcp** offers 5 market-research tools: search shops and products, get shop or product, and categories. It covers **MY, ID, TH, VN, PH, SG, TW and BR**.
  - It has a **free tier of 100 tool calls per month** with Google OAuth. The data source is not stated and appears to be its own database, not the Shopee Open Platform. 0 stars, 1 commit, and the source code is not in the repo.
  - It also publishes **grabfood-mcp** (restaurants, menus and prices) and idx-mcp.

  Sources: [SeaMCP org](https://github.com/SeaMCP); [shopee-mcp](https://github.com/SeaMCP/shopee-mcp); [Registry search=shopee](https://registry.modelcontextprotocol.io/v0/servers?search=shopee&limit=100); [Registry search=grab](https://registry.modelcontextprotocol.io/v0/servers?search=grab&limit=100)
- **Other Shopee servers in the registry target LatAm, not SEA:** codespar/mcp-shopee (Shopee LatAm Partner API v2, orders and products) and a Shopee Brasil scraper. — [Registry search=shopee](https://registry.modelcontextprotocol.io/v0/servers?search=shopee&limit=100)

**MyInvois developer ecosystem (non-MCP building blocks)**
- GitHub search "myinvois" returns **68 repos**. The top ones:

  | Repo | Stars | Notes |
  |---|---|---|
  | klsheng/myinvois-php-sdk | 103 | |
  | farhan-syah/myinvois-client | 51 | TypeScript |
  | farhan-syah/myinvois-gateway | 48 | JSON REST gateway with UBL translation |
  | amaseng/myinvois-open-sdk | 31 | Java |
  | ERPGulf/myinvois | 30 | ERPNext |
  | zahidaramai/MyInvoice-SDK-Middleware | 12 | Token mgmt, retry, dedup, polling |
  | deadboy18/myinvois-docs | — | Community docs, updated Oct 2026 |

  Sources: [GitHub search "myinvois"](https://github.com/search?q=myinvois&type=repositories&s=stars&o=desc)

### Inferences
- **No credible incumbent exists for a Malaysian agent hub.** Every Malaysian MCP found is unofficial, has 0–11 stars (excluding the generic arifOS), and is mostly a solo project. The most-starred Malaysian MyInvois code (103 stars) is a traditional SDK, not an agent interface.
- **The open-source MyInvois SDKs can be reused.** A startup could build on them (the TypeScript client and gateway, for example), so the hard part is not API plumbing. It is compliance logic, production certificates and digital signatures, consolidated-invoice rules, credential custody and liability.
- **Thin connectors are commoditizing quickly.** Wishpool shipped about 91 country connectors in roughly 3 days in July 2026, apparently the same unmaintained template, and some are already 404 or unhealthy. SeaMCP, TheCompanyAtlas/IndoTender and Ansvar (law) are taking a multi-country "data-pack" approach. **A hub that is only a wrapper will not be defensible.** Moats are more likely to come from reliability, verified production use, consent and credential management, audit trails, local-regulation depth and distribution.
- **Some Malaysian SME services have no MCP at all (the white space).** None of the following turned up in any search:
  - Payments: PayNet/DuitNow direct, FPX direct, toyyibPay, senangPay, iPay88/Fiuu, CHIP, Curlec.
  - Statutory and tax: SST (MySST), KWSP/EPF, PERKESO/SOCSO, HRDF, LHDN e-Filing/MyTax/stamp duty (e-Duti Setem), SSM registration and filing (as opposed to lookup).
  - Halal: JAKIM/MYeHALAL certification.
  - Marketplaces: Shopee, Lazada and TikTok Shop **seller-side** operations.
  - Logistics: Pos Malaysia, J&T, Ninja Van, Lalamove, EasyParcel.
  - Desktop accounting: AutoCount and SQL Account, which dominate SMEs.
- **Two of the most-starred Malaysia-related repos may be dormant.** datagovmy-mcp (11 stars) was last updated Jun 2025 and klsheng/myinvois-php-sdk shows "Jan 8".

### Gaps
- **The other MCP directories could not be searched.** glama.ai, mcp.so, smithery.ai and pulsemcp.com all failed DNS from the sandbox. Smithery and Glama may list hosted Malaysian servers that are absent from GitHub and the registry, and usage and install counts could not be obtained.
- **Some results pages were not checked.** GitHub search pages 2 and 3 of "malaysia mcp" (43 more repos) and "shopee mcp" hit HTTP 429 rate limits.
- **No adoption metrics** (downloads or calls) were found for any Malaysian MCP.
- **Wishpool's status is unknown.** It may be paused, private or abandoned (repos 404). wishpool.app also failed DNS from the sandbox, so its status cannot be inferred from that.

## Q2. Malaysian startups/companies building agentic AI or AI ops for SMEs (2025–2026) and funding

### Takeaway
**This question could not be researched properly this session.** The search budget ran out and every Malaysian tech-news and government domain was blocked. The verified evidence is thin: Malaysia was a "pocket of resilience" in SEA startup funding in Q1 2026, and GenAI and agentic deals gained ground. No search turned up a Malaysian startup that has publicly raised a 2026 round for an agentic "connectivity hub" positioning. The leads below need verification.

### Cited Findings
- DealStreetAsia's Q1 2026 SEA deal review is headlined "SE Asia startup funding stays thin in Q1 2026 even as agentic and GenAI gain ground." It reportedly names **Malaysia and AI-focused startups** as "pockets of resilience." (Search-result summary; the page was not fetched and is probably paywalled.) — [DealStreetAsia](https://www.dealstreetasia.com/stories/southeast-asia-deal-review-q1-2026-summary-481038)
- MDEC's **MDAG-AI grant** offers up to RM2 million per project. The guide says the 2026 window had not been announced as of its Mar 2026 date. (Search-result summary from a vendor blog.) — [Gotchaa Lab](https://gotchaa-lab.com/blog/2026-03-02-malaysia-ai-nation-budget-2026-business-guide)
- Tracxn reportedly puts total funding raised by Malaysian "AI companies" at about **US$19.2M**, with Gobi Partners and RISE as the most active investors. **Treat this with suspicion**: it looks implausibly low and probably reflects a narrow Tracxn category definition. (Search-result summary.) — [Tracxn](https://tracxn.com/d/artificial-intelligence/ai-startups-in-malaysia/__hVSSp7FF1uvnLIn7K53lSbzVrwTNBT3_PF67AJ6TRYQ)
- The one Malaysian SME-accounting agent integration verified this session is the **third-party** Bukku MCP by Centry Digital (see Q1). No evidence was found that **Bukku itself** has shipped an official MCP or agent API. — [GitHub](https://github.com/centry-digital/bukku)

### Inferences
- Malaysian accounting SaaS such as Bukku can be connected to agents today only through community wrappers. Several Malaysian SaaS vendors therefore look like **partners** (hub supplies distribution and agent access) rather than direct competitors. This is unconfirmed.

### Gaps
**UNVERIFIED LEADS** (from analyst background knowledge up to about mid-2026; not fetched this session; verify before use):
- **Ryt Bank** (YTL Digital Bank, a YTL and Sea Ltd JV) launched around Aug 2025 and marketed itself as Malaysia's first "AI-powered bank." Its in-app assistant "Ryt AI" is built on **ILMU**, the Malaysian LLM from **YTL AI Labs** (launched around Aug 2025). Check whether Ryt has opened SME or agentic APIs. Verify at ryt.com.my and ytlailabs.
- **Government AI programmes:**
  - The **National AI Office (NAIO)** under the Ministry of Digital (MyDIGITAL) was launched around Dec 2024.
  - Budget 2026 (tabled Oct 2025) contained AI and digital measures; check allocations for SME digitalisation and e-invoice grants.
  - MDEC has run AI-related programmes (Malaysia Digital, AI-related grants, an "AI Untuk Rakyat"-style public course was run with Intel).
  - "Malaysia AI Nexus": could not be verified as a programme name.

  Check mdec.my, digital.gov.my and the Budget 2026 speech.
- **MyEG** (super-app for government services). Check whether it has launched AI or agent features, and its e-invoice and blockchain (Zetrix) positioning.
- **Candidates for SME AI ops:** Bukku, Financio (AI bookkeeping), StoreHub (POS, F&B and retail), EasyStore (e-commerce), SQL Account and AutoCount (desktop accounting with e-invoice add-ons), plus WhatsApp-automation vendors (respond.io, which originated in Malaysia, WATI and SleekFlow). Check 2025–2026 agentic product announcements and funding on Vulcan Post, Digital News Asia, e27 and DealStreetAsia.
- **Aerodyne** (drone and DT3 data-AI) was flagged by a weak listicle source as an AI startup "to watch." It is not relevant to SME agent connectivity.
- **Not found: any Malaysian-founded startup explicitly positioning as an "agent connectivity / MCP hub" with disclosed funding.** This needs verification on Crunchbase, Tracxn and e27. If confirmed, it is an important white-space signal.

## Q3. E-invoicing API middleware players in Malaysia (most direct competitors for the tax piece)

### Takeaway
Malaysian e-invoice middleware is a crowded, fragmented market. Many local vendors sell per-invoice or monthly middleware, and custom ERP integration is expensive. **LHDN certifies no software**, so there is no certified-vendor moat. **None of the identified middleware vendors was seen offering an MCP or agent interface** (verified only through repository searches), so agent-native access is a gap they could close quickly.

### Cited Findings
- **Middleware pricing (search-result summaries; not fetched).** Figures vary widely and mostly come from vendor or vendor-affiliated blogs:
  - About **RM0.50–RM2.00 per validated invoice plus a monthly platform fee**. — [Jomeinvoice](https://jomeinvoice.my/myinvois-vs-api-integration-vs-e-invoicing-midldleware/)
  - Middleware at **RM100–2,500/month**, with yearly maintenance of **RM1,000–5,000** after the initial build (dated 2026-04-16). — [Gotchaa Lab](https://gotchaa-lab.com/blog/2026-04-16-lhdn-einvoice-integration-cost-malaysia)
  - Custom ERP and POS connectors "often land around **RM55,000–RM150,000**, excluding third-party licences" (Xantec). — [Xantec](https://xantec.com.my/software/e-invoicing/)
- **The MyInvois portal is free** for manual entry and batch uploads, which caps what low-volume SMEs will pay. (Search-result summary.) — [Jomeinvoice](https://jomeinvoice.my/myinvois-vs-api-integration-vs-e-invoicing-midldleware/)
- **"LHDN does not approve, certify or accredit any e-invoicing software."** MDEC accreditation applies only to **Peppol service providers**, which is a separate exchange framework. (Search-result summary.) — [Jomeinvoice](https://jomeinvoice.my/article/best-e-invoice-middleware-malaysia/)
- **Named middleware and e-invoice vendors seen in results:**
  - einvoice-online.my ("LHDN MyInvois Middleware"). — [einvoice-online.my](https://einvoice-online.my/)
  - Kiizen. — [Kiizen](https://www.kiizen.com.my/e-invoicing-solutions-in-malaysia/)
  - Xantec. — [Xantec](https://xantec.com.my/software/e-invoicing/)
  - Jomeinvoice, which publishes a "Top 7" middleware list. — [Jomeinvoice](https://jomeinvoice.my/article/best-e-invoice-middleware-malaysia/)
  - SQL Account's e-invoice module. — [SQL](https://www.sql.com.my/e-invoice/)
  - Orchida Tax. — [Orchida](https://orchidatax.com/malaysia-regulations/)
- **Open-source middleware is already available:**
  - farhan-syah/myinvois-gateway (48 stars): a JSON REST gateway with UBL translation.
  - zahidaramai/MyInvoice-SDK-Middleware (12 stars): token management, retry, dedup and a polling worker.

  — [GitHub search](https://github.com/search?q=myinvois&type=repositories&s=stars&o=desc)

### Inferences
- **The price anchor for a hub's e-invoice module is about RM0.50–2.00 per invoice or RM100–2,500 per month for middleware**, against a free portal for the smallest firms. A hub probably cannot charge a premium for e-invoicing alone. It has to bundle e-invoicing with payments reconciliation, accounting sync and compliance across many systems.
- Without certification, trust has to come from other signals, such as references, audit trails, uptime and insurance. **Incumbent middleware vendors already hold the customer relationships**, so they could add an MCP endpoint cheaply. Partnering with them, or white-labelling to them, may beat competing head-on.

### Gaps
- **The full vendor list could not be fetched**: the jomeinvoice "Top 7" and "Top 6" articles, plus the vendors' own pricing pages (DNS blocked). Traction figures (customers, invoices per month) for any middleware vendor were not obtained.
- **UNVERIFIED LEADS — other likely competitors** (verify via vendor sites):
  - Global and regional e-invoicing platforms that market MyInvois connectivity: Avalara, Sovos, Pagero (Thomson Reuters), Storecove, EDICOM, Comarch, SAP DRC, Oracle and Microsoft Dynamics partners.
  - Malaysian names: Bukku, AutoCount, SQL Account, Financio, Xero/QuickBooks add-ons, HiPOS/StoreHub POS e-invoice, and MyEG.
- **UNVERIFIED LEAD — e-invoice timeline.** Verify the current state at hasil.gov.my and in MOF statements; analyst memory may be out of date:
  - Phase 1: 1 Aug 2024 (revenue above RM100m).
  - Phase 2: 1 Jan 2025 (RM25m–100m).
  - Phase 3: 1 Jul 2025 (RM5m–25m).
  - Phase 4 (RM1m–5m): scheduled for 1 Jan 2026. The exemption threshold was raised to RM500k in mid-2025, then **RM1m** in late 2025, and there were reports of further deferral or relaxation of the smallest phases.
  - Penalties under s.120 of the Income Tax Act: RM200–RM20,000 or up to 6 months' imprisonment per offence.
  - A search snippet referenced an "RM1m Threshold, 55 Fields" guide at malaysia4u.com/einvoicing-guide (not fetched).

## Q4. SEA comparables and open-finance aggregators

### Takeaway
Elsewhere in SEA, the most direct analogues of a "country agent pack" in the MCP ecosystem are generic, small and unofficial. Examples: Wishpool's Indonesia, Philippines and Singapore payment servers; SeaMCP's multi-country marketplace data; Singapore ACRA lookups; and an Indonesian civic stack with 40 tools covering 11 portals. No SEA-wide "agent infrastructure" startup with official government or bank integrations was verifiable this session.

### Cited Findings
- **Singapore: 12 distinct servers in the registry.**
  - Wishpool singapore-payments (PayNow QR via HitPay).
  - ACRA/UEN company lookups by getzeroslide, sgpbusiness, sgpdirectory and TheCompanyAtlas/singapore-acra.
  - olano-ai/mcp-singapore (public data on transport, property, economy and weather).
  - pipeworx GeBIZ procurement and HSA products.
  - sg.propely (stamp duty and TDSR calculators).

  **No server for Singpass/Myinfo, SGFinDex or InvoiceNow was found.** — [Registry search=singapore](https://registry.modelcontextprotocol.io/v0/servers?search=singapore&limit=100)
- **Indonesia: 7 distinct servers.**
  - **suryast/indonesia-civic-stack**: "40 MCP tools for 11 Indonesian government portals — BPOM, BPJPH [the halal agency], AHU, OJK, BMKG+" (first published 2026-03-14).
  - Wishpool indonesia-payments (Midtrans: GoPay, QRIS, bank virtual accounts) and indonesia-logistics (Biteship).
  - IndoTender regulatory (BPOM, DGIP, Komdigi).
  - Economic-data and law servers.

  — [Registry search=indonesia](https://registry.modelcontextprotocol.io/v0/servers?search=indonesia&limit=100)
- **Philippines:** Wishpool philippines-payments-mcp, using PayMongo (GCash, Maya, cards). — [Registry search=wishpool](https://registry.modelcontextprotocol.io/v0/servers?search=wishpool&limit=100)
- **Peppol:** 3 distinct servers (peppolstatus, a Peppol/VIES validator by DouglasGouvea, and a pipeworx participant lookup). **None mentions Singapore InvoiceNow or Malaysia.** — [Registry search=peppol](https://registry.modelcontextprotocol.io/v0/servers?search=peppol&limit=100)
- **Xendit** (ID/PH/TH/VN/MY payments): only an unofficial community MCP (mrslbt) was found. — [GitHub](https://github.com/mrslbt/xendit-mcp)

### Inferences
- **indonesia-civic-stack is the closest SEA analogue** to a "government connectivity pack," and it includes BPJPH, Indonesia's halal agency. A Malaysian counterpart would cover JAKIM/MYeHALAL, SSM, LHDN, KWSP, PERKESO, NPRA and data.gov.my. **Halal is a credible differentiator** because Malaysia and Indonesia are the two leading halal-certification regimes.
- **Cross-border demand** ("SEA invoice + pay + ship" for agents) is served today only by thin multi-country wrappers. A Malaysian-founded hub that goes deep in MY first, then extends to ID, SG and TH through partners, would face no deep incumbent in the MCP layer.

### Gaps
**UNVERIFIED LEADS** (verify):
- **Singapore:**
  - APEX (API Exchange) for government APIs.
  - Singpass/Myinfo business APIs (Myinfo Business, Corppass).
  - SGFinDex (public-private financial data exchange).
  - InvoiceNow (Peppol): mandatory for newly incorporated companies that voluntarily register for GST from about Nov 2025, extending to all new voluntary GST registrants from about Apr 2026, per IRAS. Verify the dates at iras.gov.sg and imda.gov.sg.
- **Open-finance aggregators:**
  - **Brankas** (PH and ID open banking).
  - **Finverse** (HK and SEA aggregation; reported coverage of PH, SG, ID and MY banks).
  - **Ayoconnect** (Indonesia open-finance API; layoffs and a pivot reported in 2024).
  - **Brick** (Indonesia).

  Check whether any added MCP or agent toolkits in 2025–2026. Malaysia has no open-banking mandate comparable to the UK's (BNM's open-finance work is exploratory), and no direct bank-data aggregator MCP for Malaysia was found.
- **Payment toolkits:** Xendit and 2C2P official agent or MCP toolkits were not found via repository search. Check docs.xendit.co and the 2C2P developer portal.
- **SEA-wide "agent infra" startups:** none was verifiable. Search e27 and Tech in Asia.

## Q5. Global horizontal agent-integration platforms: Malaysian coverage and business model

### Takeaway
Of the horizontal platforms, only Pipedream's open-source catalog could be checked. It has a **Billplz app stub (auth only, no actions)** and a **Xendit integration with actions and sources**, but **no Shopee, Lazada, Bukku or toyyibPay**. Composio, Zapier, Merge, Arcade, Nango, Paragon and Klavis could not be checked from the sandbox. The evidence suggests the global platforms cover Malaysian services thinly or not at all, but each could add a connector cheaply once demand appears.

### Cited Findings
- **Pipedream components (open-source registry on GitHub; checked 2026-10-15):**
  - `components/billplz` exists, but contains only `billplz.app.mjs` and `package.json`, with **no actions or sources folders**. — [GitHub](https://github.com/PipedreamHQ/pipedream/tree/master/components/billplz)
  - `components/xendit` exists **with `actions`, `sources` and `common` folders**. — [GitHub](https://github.com/PipedreamHQ/pipedream/tree/master/components/xendit)
  - `components/shopee`, `components/lazada`, `components/bukku` and `components/toyyibpay` all return **404**. — [shopee](https://github.com/PipedreamHQ/pipedream/tree/master/components/shopee); [lazada](https://github.com/PipedreamHQ/pipedream/tree/master/components/lazada); [bukku](https://github.com/PipedreamHQ/pipedream/tree/master/components/bukku); [toyyibpay](https://github.com/PipedreamHQ/pipedream/tree/master/components/toyyibpay)

### Inferences
- **Global platforms are unlikely to build Malaysia-specific compliance depth soon.** That includes MyInvois signing and certificates, TIN validation, consolidated B2C invoices and the 72-hour cancellation window. Their economics favour high-volume Western SaaS. They could, however, **list a Malaysian partner's connector**, which is a plausible distribution channel for a local hub.
- A Pipedream app stub with no actions (Billplz) shows the typical pattern: authentication exists but agent-usable actions do not. The **long tail of SEA actions is the gap.**

### Gaps
**UNVERIFIED LEADS on business models and pricing.** All of the following could not be fetched and need checking at the vendor sites:
- **Composio:** hosted MCP and tool-calling platform with hundreds of toolkits and usage-based pricing. A Series A of about US$25M (Lightspeed) was reported around Jul 2025.
- **Zapier MCP:** exposes about 8,000 apps' actions to agents and bills against Zapier task quotas.
- **Pipedream Connect/MCP:** exposes its 2,500+ app catalog as MCP servers with per-user OAuth. Workday announced an agreement to acquire Pipedream around Nov 2025.
- **Merge Agent Handler:** launched around Oct 2025 as an agent tool and auth layer on top of Merge's unified APIs (HRIS, ATS, accounting).
- **Nango:** open-source integration and auth infrastructure.
- **Arcade.dev:** agent tool-calling with authorization; seed round in 2025.
- **Paragon ActionKit:** embedded agent actions for SaaS products.
- **Klavis AI:** YC, open-source MCP servers.

For each, check the pricing pages and whether any Malaysian app (Billplz, Bukku, Shopee seller, Lazada seller, MyInvois) appears in the catalog. A further check: does **Composio's** toolkit list include Xero, QuickBooks and Shopify (likely)? Those reach some Malaysian SMEs indirectly.

## Q6. Big platforms that could disintermediate

### Takeaway
None of the Malaysian anchor institutions or platforms has an **official** MCP server in the registry or on GitHub as of 2026-10-15: LHDN, PayNet, SSM, Bukku, Billplz, Shopee, Lazada, Grab, MyEG or TNG. Every Malaysian, Shopee, Lazada and GrabFood server found is third-party. Global platforms (Stripe, Xero, Intuit, Shopify) are widely believed to have shipped official MCP servers since 2025, but this could not be verified this session. The disintermediation risk is real but currently **latent in Malaysia**.

### Cited Findings
- The registry search for "malaysia" returns 6 servers from Wishpool, Ansvar, IndoTender, TheCompanyAtlas and r3dz4r. **None is from a Malaysian government body or Malaysian company.** — [Registry search=malaysia](https://registry.modelcontextprotocol.io/v0/servers?search=malaysia&limit=100)
- The registry's Shopee entries are a Singapore data aggregator (SeaMCP), a LatAm community package (codespar) and a Brazil scraper. **None is from Shopee/Sea.** — [Registry search=shopee](https://registry.modelcontextprotocol.io/v0/servers?search=shopee&limit=100)
- The only Grab-related registry server is SeaMCP's GrabFood data server, **not from Grab**. — [Registry search=grab](https://registry.modelcontextprotocol.io/v0/servers?search=grab&limit=100)

### Inferences
- **The biggest structural threats** would come from four directions:
  - **LHDN** publishing an official MyInvois MCP or "agent API," which would commoditize the e-invoice wrapper.
  - **PayNet** exposing DuitNow and FPX through an agentic-payments interface, alongside global agent-payment protocols.
  - **Shopee/Lazada/TikTok Shop** shipping official seller MCPs.
  - **Accounting SaaS** (Xero, QuickBooks, Bukku) adding MyInvois plus agent interfaces natively.

  For now, each anchor platform would only expose **its own** system. A cross-system "orchestration and compliance" layer, such as invoice in Bukku, then MyInvois, then DuitNow collection, then reconciliation, then Shopee payout, remains **distinctly hub-shaped**.

### Gaps
**UNVERIFIED LEADS** (verify on the vendors' docs and GitHub):
- **Stripe**: Agent Toolkit plus remote MCP at mcp.stripe.com (2025), and the Agentic Commerce Protocol with OpenAI (around Sep 2025). Stripe Malaysia supports FPX and GrabPay.
- **Xero**: official `XeroAPI/xero-mcp-server` (2025).
- **Intuit**: QuickBooks Online MCP server (2025).
- **Shopify**: Dev MCP and Storefront/Catalog MCP (2025).
- **Agent-payment protocols**: Google's Agent Payments Protocol (AP2, around Sep 2025), Visa Intelligent Commerce and Mastercard Agent Pay (2025).
- **Grab**: agentic or AI merchant tooling for GrabMerchant.
- **Shopee/Sea**: Sea is a partner in Ryt Bank.
- **MyEG and Touch 'n Go eWallet**: AI-assistant launches.
- **LHDN and PayNet**: no public statements on agent interfaces were found or verifiable.

## Q7. Demand signals (MSME counts, digital/AI adoption, e-invoice pain, halal)

### Takeaway
No demand statistics could be fetched from primary sources this session. SME Corp, DOSM, MDEC, the e-Conomy SEA site and HDC were all blocked. The verified demand signals are indirect: the size of the e-invoice middleware price band, and recent developer activity around MyInvois (68 repos). Quantified market-size figures must be filled from the leads below after verification.

### Cited Findings
- **Developer interest in MyInvois is substantial.** GitHub has 68 "myinvois" repositories, including SDKs in PHP, TypeScript, Java and B4X, an ERPNext app, community docs updated in Oct 2026, and an ERP that was updated "1 hour ago" when checked on 2026-10-15. — [GitHub search](https://github.com/search?q=myinvois&type=repositories&s=stars&o=desc)
- **Malaysian builders are publishing AI-agent tooling for e-invoicing** (a supply-side signal of perceived demand), dated Jan–Sep 2026:
  - a ChatGPT app (myinvois-helper);
  - an MCP plus Claude skill (techtemplemy);
  - a RAG assistant (HengYpinn);
  - an AI document mapper (chanphil2002).

  — [GitHub search "myinvois mcp"](https://github.com/search?q=myinvois+mcp&type=repositories&s=updated&o=desc); [myinvois-helper](https://github.com/dewatagiri/myinvois-helper); [myinvois-ai-mapper](https://github.com/chanphil2002/myinvois-ai-mapper)
- **Custom ERP/POS e-invoice integration costs RM55,000–150,000**, a pain point for mid-size firms. (Vendor search-result summary.) — [Xantec](https://xantec.com.my/software/e-invoicing/)

### Inferences
- E-invoicing has pushed tens of thousands of Malaysian businesses to integrate with a government API for the first time. That creates an installed base of "API-touched" SMEs and a natural wedge for agent-based automation. The exact count of in-scope taxpayers is a gap.

### Gaps
**UNVERIFIED LEADS (verify before citing):**
- **MSME counts**: DOSM's MSME Profile (Economic Census 2023, reference year 2022) reported about **1.10 million MSMEs (about 96.9% of business establishments)**. Most are micro-enterprises, and services make up the large majority (roughly 85%). MSMEs contribute about 38–39% of GDP and about 48% of employment. Verify the exact sector and size splits at dosm.gov.my and smecorp.gov.my ("SME Statistics" page).
- **Digital and AI adoption:**
  - SME Corp / MSME Insights surveys.
  - MDEC "Malaysia Digital" and digital-adoption reports.
  - e-Conomy SEA 2025 (Google, Temasek, Bain; released around Nov 2025) for Malaysia digital-economy GMV and AI-interest metrics.
  - Microsoft/LinkedIn Work Trend Index 2025 (Malaysia AI-use share).
  - AWS "Unlocking Malaysia's AI potential" studies (2024 and 2025 editions), which report the share of Malaysian businesses using AI, with SMEs lagging large firms.
  - BCG and Google AI-adoption SEA reports.

  None was fetched, so no figures can be given.
- **E-invoice compliance pain**: surveys by SME associations (SAMENTA, the Federation of Malaysian Manufacturers, ACCA/MIA) on e-invoice readiness and cost. Not fetched. The timeline and penalties are under Q3 Gaps.
- **Halal:**
  - **Export value**: HDC / MATRADE halal export figures (roughly RM50–60 billion a year in 2023–2024, by analyst recollection). HDC's Halal Industry Master Plan 2030 targets.
  - **Certified firms**: the number of JAKIM / state-JAIN halal-certified companies (roughly 8,000–10,000+, by analyst recollection).
  - **Pain points**: MYeHALAL application backlogs, renewal paperwork, ingredient-supplier traceability, and mutual recognition with Indonesia's BPJPH mandatory halal certification, which phases in from Oct 2024 to 2026.

  **All are unverified.** Verify at hdcglobal.com, halal.gov.my and matrade.gov.my.
- **The Startup Genome snippet is unreliable.** It claimed Budget 2026 "startup-related allocations" of about "$10.9 billion," which looks like a mis-summary or currency confusion and should not be used. — [Startup Genome](https://startupgenome.com/ecosystems/kuala-lumpur) (search summary only)

## Q8. What Malaysian SMEs pay for software today (price sensitivity) and preferred channels (WhatsApp)

### Takeaway
Only e-invoice-specific price points were found: a free MyInvois portal, RM0.50–2.00 per invoice, RM100–2,500 per month for middleware, and RM55k–150k for custom ERP/POS work. There are no verified figures for general SME SaaS spend or WhatsApp channel preference.

### Cited Findings
- See the Q3 pricing findings: the free portal, RM0.50–2.00 per validated invoice plus a monthly fee, RM100–2,500 per month for middleware, RM1,000–5,000 per year for maintenance, and RM55k–150k for custom connectors. — [Jomeinvoice](https://jomeinvoice.my/myinvois-vs-api-integration-vs-e-invoicing-midldleware/); [Gotchaa Lab](https://gotchaa-lab.com/blog/2026-04-16-lhdn-einvoice-integration-cost-malaysia); [Xantec](https://xantec.com.my/software/e-invoicing/) (search-result summaries)

### Inferences
- **A micro-SME (most of the base) will likely pay only tens of ringgit per month for any single tool.** The free government portal and the RM100/month floor for middleware set the anchor. A hub probably needs either **usage-based pricing** (per invoice or transaction) or monetization through **B2B2SME channels** (accounting SaaS, banks, payment gateways, POS vendors) rather than direct SME subscriptions.
- **The agent interface for micro-SMEs is likely to be chat**, such as WhatsApp or an AI assistant. A hub that exposes MCP for third-party agents **and** offers a WhatsApp front end would cover both developer and owner-operator channels. This is inferred, not verified.

### Gaps
**UNVERIFIED LEADS:**
- **Typical Malaysian SME SaaS prices**: Bukku, SQL Account, AutoCount, Financio, StoreHub and Xero Malaysia publish price lists (roughly RM30–RM300/month for accounting and POS tiers, by analyst recollection). Verify on their pricing pages.
- **Digitalisation grants that subsidise software**: the MDEC Digitalisation Grant, the Bank Simpanan Nasional (BSN) MADANI grants, and Budget 2025/2026 e-invoice-related grants and tax deductions. Verify on mdec.my and bsn.com.my.
- **WhatsApp channel preference**: penetration data (Meta, or the DataReportal/We Are Social "Digital 2026 Malaysia" report). WhatsApp Business adoption among Malaysian SMEs was not fetched.

## Q9. White space and where a Malaysian-founded startup could win (synthesis)

### Takeaway
The Malaysian agent-connectivity layer as of Oct 2026 is a **long tail of unofficial, low-traction, single-service wrappers** plus a few mass-produced global "country packs" of uncertain health. No official government or platform MCPs exist, and the global hubs cover Malaysian services thinly at best. A Malaysian-founded startup's best opening is a **trusted, compliance-grade, multi-service hub**: production MyInvois, DuitNow/FPX payments, SSM/LHDN/KWSP/SST statutory actions, marketplace seller ops and halal workflows. It should have consent and credential custody, human approval gates and audit logs, and be distributed through local SaaS, banks and associations.

### Cited Findings
- **The evidence base is the inventories in Q1, Q5 and Q6.**
  - Every Malaysian MCP found is unofficial with 0–11 stars (Q1).
  - Wishpool's Malaysian servers have 404 repos and an "Unhealthy" status (Q1).
  - Pipedream has a Billplz stub with no actions and no Shopee, Lazada, Bukku or toyyibPay (Q5).
  - The registry has no official Malaysian-institution servers (Q6).

  — [Registry search=malaysia](https://registry.modelcontextprotocol.io/v0/servers?search=malaysia&limit=100); [Pipedream billplz](https://github.com/PipedreamHQ/pipedream/tree/master/components/billplz); [Wishpool repo 404](https://github.com/junter1989k-ai/malaysia-payments-mcp)
- **Two existing design patterns are worth copying as baseline safety features:**
  - two-step submit with a time-limited confirm token, and sandbox by default (techtemplemy); — [GitHub](https://github.com/techtemplemy/mcp-myinvois)
  - payouts disabled by default with prepare/confirm steps (xendit-mcp). — [GitHub](https://github.com/mrslbt/xendit-mcp)
- **A precedent from a neighbouring country:** Indonesia already has a 40-tool civic stack covering 11 government portals, including halal agency BPJPH. — [Registry search=indonesia](https://registry.modelcontextprotocol.io/v0/servers?search=indonesia&limit=100)

### Inferences
**Where to win:**
1. **Depth over breadth in one country.** Production-grade MyInvois would need certificate signing, consolidated B2C invoices, self-billed invoices, the 72-hour cancel and reject flows, TIN validation and classification-code mapping. That is something the global wrappers (Wishpool, Composio and others) are unlikely to maintain.
2. **Statutory "action" servers nobody has built:** SST returns, KWSP/PERKESO/HRDF contributions, SSM annual returns, e-Duti Setem and MYeHALAL. Even if these start with assisted, human-in-the-loop portal workflows, they are white space.
3. **Payments plus reconciliation**: DuitNow QR, FPX and gateway aggregation (Billplz, toyyibPay, CHIP, iPay88/Fiuu, Curlec, Stripe MY), tied to e-invoice issuance and accounting sync (Bukku, SQL, AutoCount, Xero). Together this forms a closed "quote-to-cash-to-compliance" loop.
4. **Marketplace seller ops** on Shopee, Lazada and TikTok Shop: orders, payouts and e-invoices for marketplace sales. Today's MCPs are buyer-side or market-research only.
5. **A trust layer**: per-business consent, credential vaulting, spend and approval limits, audit trails, Bahasa Malaysia language support and local data residency. Policy-kernel projects such as arifOS show interest in this.
6. **Distribution**: partner with accounting and POS vendors and middleware firms, which have customers but no agent interface, and with banks such as Ryt or Maybank. Also list on the global hubs (Composio, Pipedream, Zapier) as the "Malaysia pack."

**Risks:**
- An LHDN, PayNet or platform launching official MCPs.
- Global hubs adding Malaysian connectors once demand is visible.
- Low SME willingness to pay, given a free government portal.
- Liability for incorrect tax submissions.
- Commoditization of thin wrappers, as Wishpool's 91 servers in about 3 days shows.

### Gaps
- Quantitative TAM and SAM could not be built this session because no primary demand data was reachable. The writer should treat all market-size numbers as **to be verified** (see Q7 and Q8 leads).
- Competitor funding and traction for Malaysian SME-AI startups could not be verified (Q2).
- Whether LHDN, PayNet, SSM, Shopee or Lazada have announced, rather than shipped, agent or MCP interfaces was not checked, because news sites were blocked.
