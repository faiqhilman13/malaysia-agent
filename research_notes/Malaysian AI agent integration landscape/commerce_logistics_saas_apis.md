# Private-sector SaaS & platform APIs used by Malaysian SMEs: commerce, logistics, accounting, HR, POS, messaging, telco, e-signature, credit, e-invoicing (state as of Oct 2026)

Research date: 2026-10-15. Method: web search plus targeted fetches. Many vendor developer portals (open.shopee.com, developer.grab.com, mdec.my, sdk.myinvois.hasil.gov.my, cleartax.com, jomeinvoice.my) could not be fetched from this environment (DNS or fetch blocked), so some claims rest on search-result snippets and third-party integration guides. These are flagged. "Claude connector directory" means a live lookup of the official Claude/Anthropic MCP connector registry made on 2026-10-15 with the SearchMcpRegistry tool. That registry has no public URL to cite, and it is noted wherever used.

Access-model legend used below: **OPEN** = self-serve developer signup/keys; **GATED** = developer account needs approval/review; **PARTNER** = NDA, contract or account-manager provisioning; **NONE** = no public API found.

---

## Q1. Marketplaces, social commerce and food delivery (Shopee, Lazada, TikTok Shop, GrabFood/GrabMart, foodpanda, ShopeeFood)

### Takeaway
All three big marketplaces have mature REST "open platforms" covering orders, products, logistics and finance. Access is gated: you register as a seller in-house developer or as an ISV, the marketplace approves you, and each shop must grant OAuth authorization. None of the three ships an official seller-side MCP server as of Oct 2026. The MCP servers that exist are community or third-party ones. The only TikTok MCP is for **Ads**, not Shop. Food-delivery merchant APIs (GrabFood, foodpanda) are partner-only and integrate through POS/aggregator partners. I found no public ShopeeFood Malaysia API.

### Cited Findings
**Market importance**
- Shopee leads in all six SEA markets studied and is "strongest in Vietnam, Malaysia, Singapore". TikTok Shop is "the most notable mover", gaining share in Malaysia. This is a secondary LinkedIn analysis of 2025 data, so treat it as indicative only — [LinkedIn analysis](https://th.linkedin.com/in/sanantachai)
- ECDB's Malaysia electronics e-commerce ranking (2025) puts Shopee #1, TikTok Shop #2 and Lazada #3. In toys, TikTok Shop ranks #1. ECDB's currency units look inconsistent, so do not use its absolute values — [ECDB electronics MY](https://ecdb.com/resources/sample-data/market/my/electronics)
- Regionally, Shopee, Lazada and TikTok Shop (incl. Tokopedia) took >98.8% of SEA platform GMV, which was US$157.6B in 2025. TikTok Shop plus Tokopedia GMV was 65.7% of Shopee's in 2025. These are SEA figures, not Malaysia-only — [DealStreetAsia on Momentum Works 2025](https://www.dealstreetasia.com/stories/momentum-works-report-2025-479044)
- I found no authoritative Malaysia-only 2025 GMV share split (see Gaps).

**Shopee Open Platform (open.shopee.com): GATED**
- There are two developer groups: (a) software service providers/ISVs building apps for sellers, and (b) sellers with in-house dev capability connecting their own systems — [Rollout guide](https://rollout.com/integration-guides/shopee/api-essentials)
- Flow: create a console account, pick a country and the "Shopee Seller" account type, and Shopee verifies the account. When creating an app, choose App Category "Seller In House System". One integrator says Shopee processes seller applications in about 3 working days — [Qiscus docs](https://documentation.qiscus.com/app-center/shopee)
- After approval you get a Partner ID and Partner Key. Test credentials work in the sandbox only — [API2Cart](https://api2cart.com/how-to-connect-shopee-to-api2cart); [Rutter docs](https://docs.rutter.com/platforms/commerce/shopee)
- Open API features are "available to all Shopee Managed Sellers, Independent Service Vendors or third-party system providers such as ERP" — [Ginee MY](https://ginee.com/my/insights/shopee-partner-platform/)
- Community MCP servers built on Open Platform v2:
  - A Vietnamese-built server with 15 tools: get_shop_info, get_item_list, add_item, update_price, update_stock, get_order_list — [PulseMCP listing](https://www.pulsemcp.com/servers/nguyenducshuy-shopee)
  - A listing-automation server with OAuth2, product create and image upload — [LobeHub](https://lobehub.com/mcp/datdtpl-maker-shopee-mcp-server)
  - An "agentic" server — [Glama](https://glama.ai/mcp/servers/PedroGuilhermeSilv/mcp-shopee)
  - An affiliate-search connector for SG/ID — [Glama SeaMCP](https://glama.ai/mcp/connectors/io.github.SeaMCP/shopee)
  - Most of these are unvalidated and have low star counts. **None is Shopee-official.**
- The Claude connector directory had no Shopee entry on 2026-10-15 (SearchMcpRegistry lookup; no public URL).

**Lazada Open Platform (open.lazada.com): GATED (app key + per-seller authorization)**
- The REST API covers product/category catalog, order processing, logistics and shipping labels, and finance/payout reconciliation. Auth is an app key/secret plus a per-seller token from seller authorization, with HMAC-SHA256 request signing (the "TOP" scheme). The Affiliate API is separate — [Jentic summary](https://jentic.com/apis/open.lazada.com/lazada)
- The community PHP SDK supports the VN, SG, MY, TH, PH and ID regions — [Packagist ecomphp/lazada-php](https://packagist.org/packages/ecomphp/lazada-php)
- Third-party MCP: Unified.to offers a Lazada integration plus MCP server (Beta) with write actions. Jentic publishes a read-only OpenAPI spec — [Unified.to](https://unified.to/integrations/lazada); [Jentic](https://jentic.com/apis/open.lazada.com/lazada)
- I found **no official Lazada MCP server**. The Claude directory had no Lazada entry.

**TikTok Shop Partner Center (partner.tiktokshop.com): GATED**
- Non-US markets, including MY, use partner.tiktokshop.com. Sellers register as "seller developers". Agencies and ISVs register as "app developers", which requires company details and a registration review — [MintMCP setup doc](https://www.mintmcp.com/docs/tiktok-shop-mcp-setup)
- Apps are market-specific: one app per market. A "Custom" app skips the public listing review, but review is still required for the Connector category or after 25 seller authorizations. Market and seller type cannot be changed after creation — [MintMCP](https://www.mintmcp.com/docs/tiktok-shop-mcp-setup)
- MY seller eligibility:
  - Individuals: aged 18+, Malaysian citizen, MyKad, and a matching bank account
  - Corporates: business registered in Malaysia, plus licence or registration certificate
  - [WorldFirst MY](https://www.worldfirst.com/my/blog/e-commerce-online-sellers/tiktok-shop-seller-malaysia/)
- MCP:
  - TikTok announced a **TikTok Ads MCP server** and "Agentic Hub" at TikTok World (May 2026) — [Digiday](https://digiday.com/marketing/tiktok-launches-mcp-server-to-let-ai-agents-run-campaigns/); [TikTok Ads help](https://ads.tiktok.com/help/article/about-tiktok-for-business-agentic-hub-and-mcp-server?lang=ro-RO)
  - Its GA status is disputed. One late-June 2026 guide said it was not yet generally available — [Soku.ai](https://soku.ai/blog/tiktok-ads-mcp-guide)
  - I found no official **TikTok Shop seller** MCP.
  - The Claude connector directory lists "AfterShip Channels for TikTok Shop", a third-party connector with tools such as get-orders, get-product-listings and get-products (SearchMcpRegistry lookup, 2026-10-15). MintMCP also offers a hosted TikTok Shop MCP that is read-only by default — [MintMCP](https://www.mintmcp.com/docs/tiktok-shop-mcp-setup)

**GrabFood / GrabMart: PARTNER**
- Grab publishes official GrabFood partner SDKs:
  - OAuth2 at api.grab.com; partner endpoints under partner-api.grab.com/grabfood
  - Endpoints to accept/reject orders (POST /partner/v1/order/prepare), list orders, mark orders ready, cancel orders and trace menus
  - Webhook models for menu sync and integration status
  - [grab/grabfood-api-sdk-go](https://github.com/grab/grabfood-api-sdk-go); [grab/grabfood-api-sdk-java](https://github.com/grab/grabfood-api-sdk-java)
- Merchants connect through approved POS integration partners rather than a direct developer signup. Examples are Eats365 and Klikit (vendor content) — [Eats365 support](https://support.eats365pos.com/integrations/integrate-grabfood-with-the-eats365-pos); [Klikit MY](https://klikit.io/en/learn/grabfood-pos-integration-malaysia)
- developer.grab.com could not be fetched, so GrabExpress and GrabMart specifics are unverified.

**foodpanda (Delivery Hero): PARTNER**
- Delivery Hero POS Middleware APIs manage orders, menus and stores. Access needs username/password credentials, a signed NDA and a go-ahead from a foodpanda contact — [integration.foodpanda.com docs](https://integration.foodpanda.com/en/documentation/)
- Plugin contract: POST for incoming orders, PUT for status (secondary) — [Jentic](https://jentic.com/apis/deliveryhero-pos-plugin-api)
- A community Laravel package (OmniConnect), updated Oct 2026, implements both directions — [Packagist](https://packagist.org/packages/nosh/omniconnect)

**ShopeeFood: NONE public (MY)**
- I found no public Malaysia API. A Philippines vendor guide describes merchants generating credentials in the ShopeeFood dashboard — [Klikit PH](https://klikit.io/en/learn/shopeefood-integration-philippines)
- StoreHub markets food-delivery integrations including foodpanda, ShopeeFood, Otter and Orderlina — [StoreHub](https://storehub.com/?p=15976)

### Inferences
- A hub cannot get "instant" marketplace access for a merchant. It must register once as an ISV/app developer on each of Shopee, Lazada and TikTok Shop (per market), pass review, and then run an OAuth authorization per shop. ISV status is the scalable model because it covers multiple sellers with one app. TikTok's 25-authorization review trigger means any multi-tenant hub will face review.
- No marketplace has an official MCP, so this is the clearest white space for a Malaysian hub: wrap Shopee, Lazada and TikTok Shop order, stock, logistics and chat APIs as MCP tools. Community servers prove demand but are unvetted. Unified.to and AfterShip are early commercial competitors.
- Food delivery will need to piggy-back on certified POS middleware (Klikit, Eats365, StoreHub, Otter) rather than direct API access, given NDA and partner gating.

### Gaps
- open.shopee.com, open.lazada.com and partner.tiktokshop.com primary docs were not fetchable. Exact API module lists, chat API (Shopee SellerChat) permissions and rate limits are unverified.
- No Malaysia-only GMV share figures were found. Check the Momentum Works "Ecommerce in SEA 2026" report or Statista directly.
- Whether Shopee or Lazada have announced their own AI-agent or MCP programs in 2026: none found in searches.
- GrabExpress (on-demand delivery API) and GrabMart: developer.grab.com could not be reached, so access model and sandbox are not verified.

---

## Q2. Logistics carriers and aggregators (Pos Malaysia, J&T, Ninja Van, DHL eCommerce MY, City-Link, Lalamove, Grab Express; EasyParcel, Delyva, Parcel Asia, Tracking.my)

### Takeaway
Self-serve, sandboxed APIs exist at the aggregator layer (EasyParcel) and from Lalamove. Carrier-direct APIs are mostly gated or account-based: Ninja Van needs review, Pos Laju issues credentials from its dashboard, and J&T's Open API is used mostly via ERP/marketplace integrations. No Malaysian carrier or aggregator has an official MCP server. The shipping MCP servers that exist (Easyship, Shippo) are from global players.

### Cited Findings
**EasyParcel (MY aggregator): OPEN, with sandbox**
- Flow: log into a developer account, register an app (name and URL), then get OAuth client credentials. The API covers courier rate comparison, shipment creation, order management, tracking and label generation — [developer.easyparcel.com](https://developer.easyparcel.com/)
- The sandbox ("Demo Environment") simulates transactions without touching your wallet or booking couriers. It needs demo credit, uses the same endpoints with a different base URL, and comes from SG help-centre documentation — [EasyParcel help](https://helpcentre-sg.easyparcel.com/support/solutions/articles/9000268835-does-easyparcel-s-api-have-a-sandbox-environment-)
- The MY site offers an "Individual API" and a "Marketplace API" for multi-seller platforms — [EasyParcel MY API landing](https://easyparcel.com/my/apilanding/)
- MCP: none found — [search returned only Easyship, Shippo and EasyPost](https://easyship.com/blog/easyship-mcp-server)

**Delyva (MY aggregator / MatDespatch): OPEN-ish, via account API key**
- Delyva says it connects to e-commerce, ERP and marketplace systems through APIs and plugins — [WordCamp MY 2025 sponsor page](https://malaysia.wordcamp.org/2025/a-big-thank-you-to-delyva-our-bronze-sponsor/)
- Credentials (Company ID, User ID, Customer ID, API key) come from the customer web app under Settings > API Integrations. Webhook status updates cover preparing, collected, start-delivery, delivered and failed — [DelyvaX WP plugin](https://wordpress.org/plugins/delyvax/); [EasyStore help](https://support.easystore.co/en/article/connect-with-delyva-malaysia-1svmya3/)
- I found no public API reference.

**Lalamove (on-demand): OPEN, with sandbox**
- Separate sandbox (rest.sandbox.lalamove.com) and production keys are issued via partnerportal.lalamove.com. Auth is HMAC-signed with an API key and secret — [Lalamove developer docs](https://developers.lalamove.com/v2/index.html)
- Production keys require topping up real credit. Malaysia is a supported market — [Lalamove MY API solutions](https://www.lalamove.com/en-my/business/api-solutions)
- Requests are market-segmented by header. A community package defaults to the 'MY' market — [Packagist laraditz/courier-lalamove](https://packagist.org/packages/laraditz/courier-lalamove)

**Ninja Van: GATED**
- OAuth 2.0. Access is granted through a review process, and a Malaysia developer support contact is listed — [Ninja Van API docs](https://api-docs.ninjavan.co/)
- Tracking is also available via AfterShip with no Ninja Van account — [AfterShip](https://www.aftership.com/carriers/ninjavan-my/api)

**J&T Express MY: GATED/PARTNER**
- A community Laravel package for the "J&T Express Malaysia Open API" covers order create/query/cancel, AWB label printing, tracking, batch operations and tracking webhooks (updated Dec 2025) — [Packagist aiarmada/jnt](https://packagist.org/packages/aiarmada/jnt)
- J&T is described as a favourite of online sellers because of its integration with Shopee, Lazada and TikTok Shop — [ParcelDaily](https://parceldaily.com/blog/best-courier-service-in-malaysia/)
- Official J&T developer docs were not found.

**Pos Malaysia / Pos Laju: account-based credentials**
- In the Pos Laju dashboard, Integration > Add Store generates a Client ID and Client Secret. This comes from a third-party seller-tool tutorial — [BigSeller help](https://help.bigseller.pro/en_US/detailPage/3/1/9163/content)
- Third-party integrators (ClickPost) expose Pos Malaysia label, tracking, cancel and EDD APIs — [ClickPost](https://www.clickpost.ai/carrier-integration/malaysia-post-ems-pos-laju)
- I found no public Pos Malaysia developer portal.

**City-Link Express**
- City-Link lists an "E-Commerce Integration" service and an online shipment creator, but no public API documentation — [City-Link services](https://www.citylinkexpress.com/our-services/)

**Global shipping MCP servers (benchmarks)**
- Easyship launched a cross-border shipping MCP server with 25 tools: rates, labels, address validation, tracking, pickups, customs and duty calculation — [Easyship blog](https://easyship.com/blog/easyship-mcp-server)
- Shippo has an MCP server — [Shippo docs](https://docs.goshippo.com/docs/guides_general/mcpserver)

### Inferences
- The fastest coverage path for a hub is aggregator-first. EasyParcel's Marketplace API (multi-seller, OAuth, sandbox) plus Lalamove for same-day delivery would cover most SME parcel and on-demand needs without negotiating with each carrier. Direct carrier APIs (J&T, Ninja Van, Pos Laju) matter mainly for higher-volume shippers with their own contracts.
- Tracking-only needs can be met cheaply via global tracking APIs (AfterShip, TrackingMore, Ship24), which already cover MY carriers.
- An EasyParcel or Delyva MCP wrapper is unclaimed territory.

### Gaps
- DHL eCommerce Malaysia, Grab Express, Parcel Asia and Tracking.my APIs: no information found in searches.
- J&T and Pos Malaysia official developer documentation, sandbox availability and access criteria were not confirmed from primary sources.
- I found no courier market-share data for Malaysia.

---

## Q3. Accounting software (SQL Account, AutoCount, Bukku, Financio, Biztory, Million, UBS, Xero, QuickBooks, Zoho Books, MYOB/Deskera): APIs, MyInvois and MCP

### Takeaway
The installed base is dominated by local desktop-first products (SQL Account, AutoCount, UBS). These have weak or bridged APIs. AutoCount's AOTG cloud API needs a local client on the customer's PC. Local cloud players such as Bukku have token APIs. The global cloud trio all have **official MCP servers or connectors confirmed in the Claude connector directory**:
- **Xero:** official GitHub MCP plus a hosted Claude connector
- **QuickBooks:** Intuit open-source MCP plus a hosted connector
- **Zoho Books:** a Zoho-documented MCP

Malaysia-specific gaps are significant. Xero's MCP payroll tools are NZ/UK-only. QuickBooks' MyInvois support relies on third-party apps. No local vendor (SQL, AutoCount, Bukku) ships an MCP server.

### Cited Findings
**Market share / installed base (weak evidence; no official survey)**
- AutoCount:
  - A market research report in its listing prospectus gave AutoCount a 13.79% share of Malaysian accounting software in 2021, 4.68% in POS and 2.21% in payroll. The data is from 2021, so it is stale.
  - A co-largest shareholder claimed 30–40% while acknowledging there is no official survey.
  - It has about 70,000 licences used by about 210,000 businesses across MY and SG.
  - [The Edge Malaysia](https://theedgemalaysia.com/node/713134); [Business Today 2023](https://www.businesstoday.com.my/2023/04/20/autocount-seeks-to-diversify-across-asean-after-local-success/)
- Directory listings claim AutoCount has 200,000+ Sdn Bhd users — [software-listing.com](https://software-listing.com/q/malaysia-myinvois-e-invoicing-software)
- SQL Account is claimed at 600,000+ users and called "most widely used" by reseller/vendor-affiliated sites. This is unverified marketing — [kcgroup.biz](https://kcgroup.biz/accounting-software-price-malaysia-2026/)
- SME Corp/Huawei digitalisation study (2,033 firms, undated, probably pre-2025): 54% use some business analytics, but 67% of those use spreadsheets — [SL Info](https://previous.slinfo.com.my/?p=8232)
- Most SMEs do not call the MyInvois API directly and rely on their accounting software instead — [einvoicingmalaysia.com](https://einvoicingmalaysia.com/myinvois-api)

**SQL Account (Estream): API weak/SDK; MyInvois yes**
- Listed with an "SDK integration" option in comparison guides. I found no official public API documentation — [kcgroup.biz](https://kcgroup.biz/autocount-accounting-malaysia/)
- SQL publishes a Peppol page — [sql.com.my/peppol](https://www.sql.com.my/peppol/)

**AutoCount: GATED cloud bridge (AOTG API)**
- AOTG is a RESTful API to create, update, delete and get AutoCount data. A local "AOTG Client" web service must run on the PC hosting the AutoCount server and relay to the AOTG cloud. The account book has to be activated by an AOTG admin. The Swagger reference is at aotg.cloud — [AutoCount wiki](https://wiki.autocountsoft.com/wiki/Introduction_to_AOTG_API)
- Apideck's unified API does not yet support AutoCount ("on the radar") — [Apideck](https://www.apideck.com/accounting-software/autocount)
- AutoCount has built-in MyInvois submission per the directory — [software-listing.com](https://software-listing.com/q/malaysia-myinvois-e-invoicing-software)

**Bukku (local cloud): OPEN-ish (per-company access token)**
- The access token is in Control Panel > Integrations and is used with the company subdomain. An unofficial npm client exists — [npm bukku-client](https://www.npmjs.com/package/bukku-client)
- Bukku submits e-invoices (including self-billed) to MyInvois and can cancel within 72h (vendor page) — [bukku.my](https://bukku.my/lhdn-e-invoice-compliant-cloud-accounting-software-malaysia)
- It is offered through UOB's SME digital programme — [UOB MY](https://www.uob.com.my/business/digital/accounting/bukku.page)
- Pricing conflicts across sources: RM39/mo, RM59/mo, or Pro at about RM99–129/mo, with e-invoice at Pro tier — [kcgroup.biz](https://kcgroup.biz/accounting-software-price-malaysia-2026/); [intbooks.my](https://intbooks.my/blog/best-accounting-software-malaysia-2026/)
- Bukku has payroll integrations — [bukku.my payroll integrations](https://bukku.my/payroll-integrations)

**Xero: OPEN API; OFFICIAL MCP**
- The XeroAPI GitHub org hosts xero-mcp-server (MIT, local stdio via npx):
  - Accounting tools, read and write: contacts, invoices, quotes, credit notes, payments, bank transactions, manual journals, items, tracking categories, and P&L / balance sheet / trial balance / aged reports
  - Payroll tools work only when the org region is **NZ or UK**
  - Auth via "custom connection" (client ID/secret) or bearer token. Custom connections created after 29 Apr 2026 use a V2 scope set
  - No hosted version is mentioned in the README; no Malaysia mention
  - [GitHub XeroAPI/xero-mcp-server](https://github.com/XeroAPI/xero-mcp-server)
- A hosted "Xero" connector appears in the Claude connector directory with mostly read/analysis tools (get_financial_position, get_profit_and_loss, aged receivables). SearchMcpRegistry lookup, 2026-10-15. A third-party guide also says the Claude connector is read-only while the GitHub server can write — [agentspay.ai](https://agentspay.ai/vs/quickbooks-mcp-server)
- MyInvois: the business adds Xero as an **intermediary** in the MyInvois portal and completes company details in Xero. Consolidated and self-billed e-invoices were supported during the relaxation period — [Xero MY guide](https://www.xero.com/my/accountant-bookkeeper-guides/what-is-e-invoicing/); [Xero MY PDF](https://brandfolder.xero.com/NE531UQB/at/p9jb6w5kqgwf485xxkpvn63j/Understanding_e-Invoicing_for_Malaysia-A_guide_to_getting_started.pdf)
- A third-party blog says Xero partners with Invoici (Peppol) for submission — [Fastlane](https://fastlane-global.com/my/blog/xero-e-invoicing-malaysia/)
- Users complain the flow still needs manual steps, such as adding MyInvois@invoi.ci as a recipient — [Xero product ideas](https://productideas.xero.com/forums/967115-invoices-quotes/suggestions/51559088-feature-request-default-myinvois-recipient-email)

**QuickBooks Online (Intuit): OPEN API; OFFICIAL MCP**
- Intuit's open-source intuit/quickbooks-online-mcp-server was an early preview around Oct 2025. It exposes about 140–145 tools over 29 entities plus 11 reports and uses an OAuth app from the Intuit Developer Portal — [CodeWords](https://www.codewords.ai/blog/quickbooks-mcp); [Kipper comparison](https://kipper.com/blog/quickbooks-mcp-server-options-compared/)
- Intuit also runs a hosted QuickBooks connector for Claude and a ChatGPT plugin. A 28 Jul 2026 update reportedly added create/send/schedule invoices, with payroll read-only. Third-party guides also say the hosted connector is US-only; this is unverified — [usecarly](https://www.usecarly.com/blog/quickbooks-mcp/); [DeepLedger](https://deepledger.ai/blog/quickbooks-mcp-server-guide)
- The Claude connector directory lists "Intuit QuickBooks" (official, 70+ tools), plus third-party "Meridian Connector for QuickBooks" (SearchMcpRegistry, 2026-10-15)
- Malaysia:
  - A Malaysia QBO edition exists, and QBO Accountant launched in 170+ countries including MY (2023) — [BusinessWire 2023](https://www.businesswire.com/news/home/20230508005034/en/Intuit-QuickBooks-Launches-QuickBooks-Online-Accountant-in-More-Than-170-Countries-Around-the-World-Including-Malaysia)
  - A May 2025 Intuit community reply says e-invoicing is not available in some accounts and points users to third-party apps. Users complain of being pushed to middleware — [Intuit community](https://quickbooks.intuit.com/community/other-questions-88/qbo-e-invoicing-feature-for-malaysia-180122)
  - The MY GST page notes QBO is not on the customs-approved list because there is no local subsidiary. This page is likely stale (GST era) — [QuickBooks MY GST](https://quickbooks.intuit.com/my/gst)

**Zoho Books: OPEN API; OFFICIAL MCP (Zoho-documented)**
- Zoho's help docs describe a "Zoho Books MCP" connecting a Books org to AI models via MCP. Zoho Books is a default connector in Claude with a limited tool set. Other actions need a custom connector built with Zoho MCP, and Zoho advises admin approval — [Zoho Books help (UK)](https://www.zoho.com/uk/books/help/mcp/zoho-books-mcp.html)
- Regional docs exist (AU, BH, DE) and there is a Taiwan blog. I found no MY-specific MCP page — [Zoho TW blog](https://www.zoho.com/blog/zh-tw/books/zoho-books-mcp-ai-accounting-taiwan.html)
- The Claude directory lists "Zoho Books — Zoho Books MCP for Smart Finance Ops" with 49+ tools (get_invoice, list_contacts, list_taxes, create_item…). SearchMcpRegistry, 2026-10-15

**Other accounting products**
- Community MCPs for Zoho Books exist via StackOne (104 actions) and Pipedream (15 actions) — [StackOne](https://stackone.com/connectors/zohobooks/mcp/); [Pipedream](https://mcp.pipedream.com/app/zoho_books)
- Financio, Biztory, Million, UBS, MYOB and Deskera: no API or MCP information found in searches (see Gaps).

### Inferences
- There is a two-tier reality. The tools most Malaysian SMEs actually run (SQL Account, AutoCount, UBS) are on-premise or desktop. Agent access needs a local bridge/agent: AutoCount's AOTG client pattern, or direct DB/SDK connectors. A hub that ships a lightweight on-prem connector for SQL Account and AutoCount would unlock the largest installed base. These vendors have no MCP plans visible.
- Xero, QuickBooks and Zoho give "free" MCP coverage, but Malaysia-specific features are thin: no MY payroll in Xero MCP, and QBO MyInvois depends on add-ons. A hub would need to add MyInvois submission and status tools on top.
- Bukku is the most agent-ready local cloud ledger (token API). It is a good early partner target.

### Gaps
- No independent 2024–2026 market-share survey for MY accounting software. SME Corp, MDEC and DOSM do not appear to publish vendor shares.
- SQL Account API/SDK documentation and Financio, Biztory, Million, UBS, MYOB and Deskera API status were not researched successfully.
- Whether Zoho Books' MCP works for MY-edition orgs (MyInvois fields), and whether Intuit's hosted connector serves MY accounts, are unconfirmed.
- Xero MY payroll does not exist natively as far as found; MY payroll is typically via Swingvy/Talenox integrations.

---

## Q4. HR/payroll (Kakitangan, Swingvy, PayrollPanda, Talenox, Info-Tech, Deskera): APIs and statutory automation

### Takeaway
All the major MY cloud payroll vendors claim automated EPF, SOCSO, EIS and PCB/MTD calculation, plus e-filing files (CP39, EA, Form E). Public developer APIs are rare. Only Talenox shows evidence of an API-key REST API (v2), via third-party connectors. Kakitangan, Swingvy and PayrollPanda show no public API documentation. I found no official MCP servers for any MY payroll vendor.

### Cited Findings
- **Kakitangan:** described as LHDN-approved. It handles EPF, SOCSO and PCB and generates CP39, EA, Form E/CP8D and e-files, with a free tier for the smallest teams. Pricing conflicts: "from RM50/mo" vs "RM30/mo + RM3/employee" — [Swingvy blog comparison](https://www.swingvy.com/blog-my/top-5-hr-systems-for-smes-in-malaysia); [Caltrix comparison](https://www.caltrix.asia/blog/which-cloud-payroll-software-to-use-in-malaysia-comparison/)
- **Swingvy:** automates EPF/KWSP, SOCSO/PERKESO, EIS and PCB/MTD e-submissions. It has GIRO/bank upload files and a Xero integration — [Swingvy blog](https://www.swingvy.com/blog-my/top-5-hr-systems-for-smes-in-malaysia)
- **Talenox:**
  - Auto-calculates EPF, SOCSO and MTD — [Talenox MY](https://www.talenox.com.my/payroll/)
  - Has a REST API at https://api.talenox.com/api/v2/ (e.g. /employees) with API-key Bearer auth, per Pipedream's connector. This is not Talenox's own documentation — [Pipedream Talenox](https://pipedream.com/apps/talenox.md)
  - Integrates with Deputy, StaffAny, Xero and QuickBooks per comparisons — [Caltrix](https://www.caltrix.asia/blog/which-cloud-payroll-software-to-use-in-malaysia-comparison/)
- AutoCount's 2021 payroll software share was 2.21% (prospectus data, stale) — [The Edge](https://theedgemalaysia.com/node/713134)
- Kakitangan API: a targeted search returned nothing relevant (no evidence of a public API).

### Inferences
- Payroll is mostly a "read and trigger" integration target for agents: headcount, payslips, leave. Statutory filing is handled inside the vendor. With most vendors lacking APIs, a hub may need partnerships (data-sharing agreements) or vendor-specific connectors. Talenox is the likeliest first API integration.

### Gaps
- PayrollPanda, Info-Tech and Deskera HR APIs: no data found.
- Whether EPF i-Akaun, PERKESO ASSIST and LHDN e-PCB expose any employer APIs (versus file upload) was not covered; this is likely in the government-API researcher's scope.
- I found no market-share data for MY payroll SaaS.

---

## Q5. POS / F&B (StoreHub, Qashier, Slurp, Eats365, Loyverse, Feedme)

### Takeaway
Loyverse is the only MY-relevant POS with a clearly documented self-serve public REST API (access tokens in the back office). StoreHub, the local leader, has a private, partner-gated API: credentials come from Customer Care, and it is reportedly an Enterprise-tier feature. I found no API documentation for Qashier, Slurp, Eats365 (beyond delivery-platform integrations) or Feedme. No POS vendor ships an MCP server.

### Cited Findings
- **Loyverse: OPEN.** Access tokens are created in Back Office > Access Tokens. They give unlimited access to all API resources, with up to 20 tokens per account — [Loyverse help](https://help.loyverse.com/help/loyverse-api); [Loyverse API page](https://loyverse.com/loyverse-pos-api)
  - Secondary sources describe OAuth 2.0 as an alternative, webhooks at /v1/webhooks and an X-Loyverse-Webhook-Signature header. These are unverified — [DEV Community](https://dev.to/gilbert_hathaway_a9c814a9/integrating-with-loyverse-pos-a-proper-guide-18ed)
- **StoreHub: PARTNER.**
  - Private, partner-gated REST API with no public OpenAPI spec or self-serve portal. API access is said to be Enterprise-tier, with credentials issued by Customer Care (third-party profile) — [API Evangelist](https://providers.apievangelist.com/providers/storehub/)
  - An integrator (Zetpy) needs a "Consumer Username/Secret" requested from StoreHub Customer Care — [Zetpy support](https://support.zetpy.com/doc/how-to-authorize-storehub-inside-zetpy)
  - StoreHub integrates with TNG, GrabPay and DuitNow QR, and with foodpanda, ShopeeFood, Otter and Orderlina — [StoreHub](https://storehub.com/?p=15976)
- **Eats365:** documents a GrabFood integration — [Eats365 support](https://support.eats365pos.com/integrations/integrate-grabfood-with-the-eats365-pos)
- Typical MY POS cost is about RM100–250 per terminal per month (comparison content) — [Loman.ai](https://loman.ai/blog/best-pos-system-for-restaurant-malaysia)
- AutoCount's 2021 POS share was 4.68% (stale) — [The Edge](https://theedgemalaysia.com/node/713134)

### Inferences
- POS is a fragmented, closed category. A hub likely needs commercial partnerships with StoreHub, Qashier and Eats365, and could self-serve only Loyverse. Delivery aggregators like Klikit and Otter may be a shortcut to F&B order data.

### Gaps
- Qashier, Slurp, Feedme and Eats365 open API status, and POS market share in MY: not found.

---

## Q6. Messaging: WhatsApp Business Platform (Cloud API), BSPs, Telegram

### Takeaway
WhatsApp is the de facto business channel in Malaysia. Meta's Cloud API is self-serve but billed per template message:
- Marketing: about US$0.086
- Utility and authentication: about US$0.014
- Service replies inside the 24h window: free

BSPs (SleekFlow, respond.io, Wati, Qiscus, Infobip, Twilio, Bird) add platform fees. There is no official Meta-published WhatsApp MCP server. Twilio, Infobip and Bird do have connectors in the Claude directory, and Meta has piloted "Business AI" on WhatsApp in Malaysia.

### Cited Findings
**Usage**
- Malaysia had 35.4M internet users at end-2025, 98.0% penetration — [DataReportal Digital 2026 Malaysia](https://datareportal.com/reports/digital-2026-malaysia)
- An unsourced marketing guide claims WhatsApp reach of 90.7% (weak) — [malaysia4u](https://malaysia4u.com/marketing-guide)
- An older YouGov/Reuters figure says 80.5% of internet users used WhatsApp weekly. This is 2019 data and stale (via the same search set).
- Malaysia was one of the early-access countries for Meta's Business AI on WhatsApp (Feb 2025) — [The Edge](https://theedgemalaysia.com/node/743669)
- Meta and KUSKOP launched an MSME programme for AI tools and WhatsApp Business in Sept 2026 (search-snippet attribution) — [Bernama](https://bernama.com/en/news.php?id=2612072)

**Pricing (per-message model)**
- Malaysia rates per message (as of 1 Jan and 1 Jul 2026):
  - Marketing: US$0.0860
  - Utility: US$0.0140
  - Authentication: US$0.0140
  - International authentication: US$0.0418
  - Service: US$0.0140, effective 1 Oct 2026, but free within the 24h customer-service window
  - Volume tiers apply to utility and authentication (not marketing)
  - Click-to-WhatsApp ad entry gives a 72h free window
  - [SleekFlow pricing table](https://sleekflow.io/en-us/blog/whatsapp-business-price)
- Conflicting or alternative quotes:
  - Qiscus quotes "Meta pricing + US$0.0045/msg (marketing), + US$0.0025 (utility)" as its markup, and notes utility-in-window rules change from October — [Qiscus](https://www.qiscus.com/en/blog/whatsapp-api-malaysia/)
  - Go4whatsup quotes the old conversation-based model at RM0.022–0.130, with plans from RM179/mo (stale model) — [go4whatsup](https://go4whatsup.com/malaysia/whatsapp-business-api-pricing/)

**BSPs**
- respond.io and SleekFlow each charge about US$15 per number per month in BSP fees on top of their plans, with pricing based on monthly active contacts (vendor pages) — [respond.io](https://respond.io/vi/alternatives/sleekflow); [SleekFlow](https://sleekflow.io/en-sg/blog/respondio-alternative)
- SleekFlow's "AgentFlow" AI agents send payment links and connect to Shopify catalogs via MCP (vendor claim) — [SleekFlow](https://sleekflow.io/en-sg/blog/respondio-alternative)
- respond.io supports the WhatsApp Business Calling API (vendor claim) — [respond.io](https://respond.io/vi/alternatives/sleekflow)
- Local AI-on-WhatsApp vendors: Qiscus AgentLabs, ForwardChat, Go4whatsup, Hiiiilo (Meteor Pulse) — [Qiscus](https://www.qiscus.com/en/blog/chatbot-for-whatsapp-business/); [Macau Business](https://macaubusiness.com/meteor-pulse-launches-hiiiilo-an-ai-whatsapp-receptionist/)

**MCP**
- Community WhatsApp MCP servers on the official Cloud API: codechap/mcp-server-whatsapp (template and free-form sends; needs access token and phone-number ID) — [mcpservers.org](https://mcpservers.org/servers/codechap/mcp-server-whatsapp); [Glama](https://glama.ai/mcp/servers/l0rlbhwz15)
- I found no Meta-official WhatsApp MCP.
- The Claude connector directory has Twilio (official, docs search/retrieve), Infobip Message (send SMS/RCS/MMS/Viber), Infobip Documentation, and Bird (email, SMS, **WhatsApp**, calls, verify; 300+ tools). SearchMcpRegistry, 2026-10-15

### Inferences
- WhatsApp is the most important agent channel in MY, and the per-message cost structure means agents should favour service-window replies and utility templates over marketing. A hub can either become a Meta Tech Provider/BSP itself or wrap existing BSP APIs. Bird and Infobip already offer MCP-native WhatsApp sending, which lowers build cost but means competing with global CPaaS.

### Gaps
- Meta's official MY rate card was not fetched directly. Rates come from BSP-reproduced tables, so verify on developers.facebook.com.
- Telegram Bot API usage among MY SMEs was not researched. The Bot API is free, but I found no MY business-usage data.
- Wati's MY presence and pricing were not verified.

---

## Q7. Telco network APIs (GSMA Open Gateway / CAMARA) and SMS/OTP in Malaysia

### Takeaway
In Sept 2025, Malaysia's five operators (CelcomDigi, Maxis, U Mobile, TM/Unifi, YTL) announced a **federated CAMARA Number Verification API**: one integration reaching all networks, targeted at banks and online retailers. I found no confirmation of public GA, pricing or a self-serve developer portal, and no evidence that SIM Swap or KYC Match are offered in MY. CelcomDigi became the first MY telco on Google Firebase's network-based phone verification (Feb 2026). Enterprise SMS/OTP is sold via aggregators. MCMC rules require originating-number sender codes.

### Cited Findings
- On 23 Sep 2025, CelcomDigi, Maxis, U Mobile, Telekom Malaysia and YTL Communications announced federated access to the Number Verification API for banks and online retailers, to fight fraud and identity theft. It positions network verification as an alternative to SMS OTP — [CelcomDigi press release](https://corporate.celcomdigi.com/news/malaysia-mobile-operators-to-launch-new-federated-network-service-to-help-online-businesses-combat-fraud-and-digital-identity-theft); [Maxis newsroom](https://www.maxis.com.my/en/about-maxis/newsroom/2025/september/malaysia-mobile-operators-to-launch-new-federated-network-service/); [The Star](https://www.thestar.com.my/business/business-news/2025/09/24/telcos-launch-bank-federated-number-verification-api)
- The API is CAMARA-based. Developers integrate once and reach all networks while each operator keeps control of data, policy and monetisation — [TeckNexus](https://tecknexus.com/malaysia-telcos-federate-gsma-open-gateway-number-verification-api/)
- Before federation, each telco had its own implementation, so developers had to integrate separately — [Developing Telecoms](https://developingtelecoms.com/telecom-technology/enterprise-ecosystems/19114-malaysian-telcos-to-federate-open-api-for-number-verification.html)
- Maxis cites its existing "Mobile Identity" enterprise solution and regional collaboration with TH and SG operators — [Maxis](https://www.maxis.com.my/en/about-maxis/newsroom/2025/september/malaysia-mobile-operators-to-launch-new-federated-network-service/)
- CelcomDigi, with Google Firebase and Telenor Linx, became the first MY telco offering network-based phone verification on Firebase (Feb 2026, Malay-language report) — [Berita Harian](https://www.bharian.com.my/amp/bisnes/korporat/2026/02/1505354/bhplus)
- Under an MCMC ruling, SMS sender display uses originating-number "sender codes". CelcomDigi publishes OTP/TAC sender codes — [CelcomDigi help](https://help.celcomdigi.com/en/support/solutions/articles/70000660039-celcomdigi-official-sender-codes)
- Local SMS API aggregators include iSMS and MoceanAPI (vendor claims) — [iSMS](https://ww2.isms.com.my/isms_services.php)

### Inferences
- For an agent hub, Number Verification is the realistic telco API (fraud and onboarding). SIM Swap and KYC Match are not evidenced in MY. Access is likely to be enterprise/contract (bank and retailer focus) rather than self-serve. Firebase may be the easiest developer route for CelcomDigi subscribers.
- SMS OTP remains the fallback, through aggregators or global CPaaS (Twilio, Infobip, Bird MCP connectors exist).

### Gaps
- Go-live status, pricing and onboarding of the federated NV service as of Oct 2026: no 2026 confirmation found.
- Whether any MY operator is on Aduna or exposes SIM Swap / Device Location / KYC Match: not found.
- Maxis and CelcomDigi enterprise CPaaS/SMS API portals: not found.

---

## Q8. E-signature and trust services (licensed CAs, DocuSign/Adobe Sign, MyDigital ID)

### Takeaway
Malaysia has a two-tier legal regime:
- **Digital signatures** under the Digital Signature Act 1997 (DSA) must use certificates from an MCMC-licensed CA.
- **Electronic signatures** under the Electronic Commerce Act 2006 (DocuSign-type) are valid if reliable, but with exclusions (power of attorney, wills, trusts, negotiable instruments).

Licensed CAs include MSC Trustgate and Pos Digicert. Trustgate offers an open signing API/SDK (MyTrust 365, on Ascertia SigningHub) and issues MyDigital ID certificates. DocuSign has an official MCP connector in the Claude directory. No Malaysian CA has an MCP server.

### Cited Findings
- **Legal regime:** the DSA 1997 governs digital signatures, which must be verifiable against a licensed CA certificate. The ECA 2006 governs broader e-signatures, which need reliability and intent. The ECA excludes powers of attorney, wills/codicils, trusts and negotiable instruments. Stamping acceptance by IRB is unclear — [Rödl & Partner (Mar 2025)](https://www.roedl.com/insights/newsflash-asean/2025_03/malaysia-legal-recognition-eletronic-signatures); [Low Partners](https://www.lowpartners.com/e-signing-a-faster-easier-and-safer-way-to-sign-your-documents/)
- **Pos Digicert:** licensed under DSA 1997, CA licence LPBP-1/2015(5) — [Pos Digicert](https://www.posdigicert.com.my/about-us)
- **MSC Trustgate**
  - Licensing:
    - Licensed CA regulated by MCMC under DSA 1997 / DSR 1998 — [MSC Trustgate](https://www.msctrustgate.com/vision)
    - Described as "one of the four CAs in Malaysia certified by MCMC" — [Trustgate info PDF](https://www.msctrustgate.com/assets/pdf_msctrustgate/guide/knowledge_center/Eng_Trustgate_Info.pdf)
  - MyDigital ID:
    - Its CPS includes MyDigital ID certificate policy OIDs. MyDigital ID certificates use specific roots from 2 Aug 2025 — [Trustgate CPS v6.1.2](https://msctrustgate.com/assets/pdf_msctrustgate/MSC_Trustgate_CPCPS_v6.1.2.pdf)
  - Signing products and APIs:
    - **MyTrust 365** is a signing portal with an open API and/or SDKs to embed e-signing in apps — [MyTrust 365](https://msctrustgate.com/mytrust-365)
    - **MyTrust.Biz** offers digital signature, seal, timestamp and encryption, plus eKYC-based Digital ID issuance — [MyTrust.Biz](https://www.msctrustgate.com/mytrust.biz)
    - It uses Ascertia SigningHub — [Cloud Signature Consortium](https://cloudsignatureconsortium.org/msc-trustgate-leverages-signinghub-for-enhanced-digital-signature-security/)
    - It offers AdES and QES; eID Easy exposes Trustgate AdES (PDF/CAdES/XAdES/ASiC-E) — [eID Easy](https://www.eideasy.com/supported-methods/msc-trustgate)
- Both Pos Digicert and MSC Trustgate are on Adobe's Approved Trust List — [Adobe AATL](https://helpx.adobe.com/acrobat/kb/approved-trust-list1.html)
- E-invoicing uses digital certificates for MyInvois API document signing (secondary) — [Complyance](https://complyance.io/malaysia-blog/digital-signature-e-invoicing-in-malaysia)
- **DocuSign:** official connector in the Claude directory (agreements, workflows, triggerWorkflow, etc.; SearchMcpRegistry, 2026-10-15). DocuSeal also has one. No Malaysia-specific DocuSign data was found.

### Inferences
- For agent-driven signing, DocuSign's MCP covers ECA-level e-signatures. Documents needing DSA-grade signatures (some government filings, MyInvois API signing certificates, high-value contracts) require a licensed-CA integration such as Trustgate MyTrust 365 or Pos Digicert. That is a concrete hub integration need with no MCP today.

### Gaps
- The full current list of MCMC-licensed CAs: one source says four. Telekom Applied Business and Raffcomm are commonly cited but **unverified here**, and licence-renewal status for 2025+ was not confirmed.
- Pos Digicert API and SDK availability, and whether MyDigital ID exposes a signing API for private businesses: not found.
- DocuSign and Adobe Sign MY data residency and market share: not found.

---

## Q9. Credit / KYC / business verification data (CTOS, Experian Malaysia, RAM)

### Takeaway
SSM (Companies Commission) has no public API. Programmatic company data flows through a handful of authorised SSM data service providers (e.g. Infomina) and credit bureaus. CTOS pulls real-time SSM data via Infomina's API (June 2025). Experian and RAM integration details are opaque, with enterprise sales only. No MCP servers were found.

### Cited Findings
- In June 2025, Infomina Berhad, "one of only four authorised SSM data service providers", partnered with CTOS Digital. CTOS pulls real-time SSM company data via Infomina's API for business verification and risk assessment (press release) — [Malaysia SME](https://www.malaysiasme.com.my/?p=5784)
- SSM's public MyData portal has no public API — [BusinessDataGuide MY](https://businessdataguide.com/blog/jurisdictions/malaysia-company-search-guide)
- CTOS links to SSM Section 60B beneficial-ownership disclosures and directorship/shareholder data. It is strongest on SME and consumer credit depth. Experian is stronger on multi-jurisdiction UBO tracing — [BusinessDataGuide CTOS vs Experian](https://businessdataguide.com/blog/comparisons/ctos-vs-experian-malaysia); [CTOS vs RAM](https://businessdataguide.com/blog/comparisons/ctos-vs-ram-credit-information-malaysia)

### Inferences
- KYB for a hub likely means a commercial contract with CTOS or an SSM data provider (Infomina and peers). There is no self-serve route, which makes this a candidate for a hub-negotiated, resold capability.

### Gaps
- Experian Malaysia and RAM Credit Information API specs, pricing and eKYC products: not found.
- The names of the other three authorised SSM data service providers: not found.

---

## Q10. E-invoice middleware, Peppol access points and the MyInvois integrator ecosystem

### Takeaway
LHDN's MyInvois offers a free portal and a free REST API. Taxpayers can integrate directly with OAuth client credentials, and intermediaries submit "on behalf of" a taxpayer TIN. A sandbox (preprod) is available by email request. Legal status of the rollout:
- Mandatory for businesses over RM1M turnover; those below RM1M are exempt from Jan 2026, per Dec 2025 announcements
- The RM1–5M cohort started 1 Jan 2026
- Sources conflict on that cohort's penalty-relief end date

MDEC is the Peppol Authority and runs an accredited Peppol service-provider list. Middleware pricing is commonly cited at about RM0.50–2.00 per validated invoice plus a monthly fee (weak evidence).

### Cited Findings
**MyInvois API**
- The Taxpayer login is for submitting your own documents. The Intermediary login is for service providers submitting on behalf of customers. Sandbox client ID and secret are requested by emailing sdkmyinvois@hasil.gov.my with the TIN and new business registration number. Sandbox hosts are preprod-api.myinvois.hasil.gov.my and preprod.myinvois.hasil.gov.my — [MyInvois SDK FAQ](https://sdk.myinvois.hasil.gov.my/faq)
- Token flow: client-credentials POST to /connect/token with scope InvoicingAPI. The `onbehalfof` header carries the taxpayer TIN for intermediaries. The token lasts about 1h — [Chilkat sample code](https://www.example-code.com/chilkat2-python/myinvois_malaysia_login_intermediary_system.asp)
- Open-source SDKs exist (e.g. Laravel jiannius/myinvois) — [Packagist](https://packagist.org/packages/jiannius/myinvois)
- LHDN does not require a third-party provider: businesses can use the free portal or direct API (search-result attribution) — [einvoicingmalaysia.com Peppol guide](https://einvoicingmalaysia.com/guides/peppol-malaysia)

**Mandate timeline**
- June 2025: LHDN deferred the RM1–5M group to 1 Jan 2026, set the ≤RM1M phase for 1 Jul 2026, and exempted businesses under RM500k — [NST](https://www.nst.com.my/amp/news/nation/2025/06/1226501/lhdn-e-invoice-implementation-revenue-below-rm5mil-deferred-jan-1-2026); [Malay Mail](https://www.malaymail.com/news/malaysia/2025/06/06/irb-malaysia-exempts-businesses-below-rm500000-from-e-invoicing-delays-mandate-for-rm1-5m-group-to-2026/179391)
- Dec 2025: the PM announced that the exemption threshold rises from RM500k to RM1M effective 1 Jan 2026, which cancels the July 2026 phase for smaller sellers (secondary sources) — [Jumix](https://jumixdesign.com/e-invoice-checklist-malaysia-online-sellers-2026/); [Chillhub](https://chillhub.com.my/?p=2669)
- **Conflict:** the Phase 4 (RM1–5M) relaxation period ends either 31 Dec 2027 per [Jumix](https://jumixdesign.com/e-invoice-checklist-malaysia-online-sellers-2026/) and [Chillhub](https://chillhub.com.my/?p=2669), or 30 Jun 2026 per [ClearTax](https://www.cleartax.com/my/en/different-phases-implementation-timelines-einvoicing-malaysia). Neither was verified against an LHDN primary document.
- One 2026 review claims "Phase 3 took effect 1 July 2026 at RM150,000 turnover". This conflicts with the above and looks unreliable — [intbooks.my](https://intbooks.my/blog/best-accounting-software-malaysia-2026/)

**Peppol and middleware market**
- MDEC is Malaysia's Peppol Authority and publishes a Peppol Service Providers list. The page was not fetchable — [MDEC Peppol SP list](https://www.mdec.my/national-einvoicing/peppol-service-providers)
- ClearTax publishes a "Top 10 MDEC-accredited" list — [ClearTax](https://www.cleartax.com/my/en/top-e-invoicing-solution-provider-malaysia)
- Global access points serving MY include Tickstar and Invoici (Xero's partner) — [Tickstar](https://www.tickstar.com/region/malaysia/); [Fastlane on Xero/Invoici](https://fastlane-global.com/my/blog/xero-e-invoicing-malaysia/)
- SQL publishes a Peppol page — [SQL Peppol](https://www.sql.com.my/peppol/)
- Pricing (weak evidence from comparison sites; search-snippet attribution):
  - Middleware is "typically RM0.50–2.00 per validated invoice + monthly platform fee"; one worked example uses RM600/mo plus RM1.20 per invoice
  - MDEC accreditation reportedly costs providers about €10,000
  - There is no fee for a Peppol ID itself
  - [JomeInvoice middleware list](https://jomeinvoice.my/article/best-e-invoice-middleware-malaysia/); [einvoicingmalaysia Peppol guide](https://einvoicingmalaysia.com/guides/peppol-malaysia)

### Inferences
- Because the MyInvois API is free and supports intermediaries, an agent hub can register as an intermediary and offer "submit/validate/cancel e-invoice" as MCP tools directly. That makes it a middleware competitor priced against roughly RM0.50–2.00 per invoice. The Dec 2025 RM1M exemption shrinks the mandatory SME pool, so voluntary or B2B-buyer-driven demand matters.

### Gaps
- The official MDEC accredited Peppol SP list (names and count) and official MyInvois API rate limits were not retrieved (sites blocked).
- No authoritative LHDN document confirmed the 2026–2027 relaxation dates.
- No MyInvois-specific MCP server was found in searches. This was not exhaustively checked on GitHub.

---

## Q11. Cross-category MCP / AI-agent readiness matrix (as of 2026-10-15)

### Takeaway
Official MCP coverage exists only for the global SaaS vendors MY SMEs use: Xero, QuickBooks, Zoho Books, DocuSign, Twilio, Infobip and Bird. TikTok has an Ads-only MCP. **No Malaysian-origin platform has an official MCP server**: none of Shopee, Lazada, the MY couriers, EasyParcel, SQL Account, AutoCount, Bukku, Kakitangan, StoreHub, CTOS, Trustgate, the telcos or MyInvois. This is the core white space for a Malaysian agent-connectivity hub.

### Cited Findings
| System | API access model | Official MCP? | Notes / source |
|---|---|---|---|
| Shopee Open Platform | GATED (approval, OAuth per shop) | No (community only) | [Qiscus](https://documentation.qiscus.com/app-center/shopee); [PulseMCP](https://www.pulsemcp.com/servers/nguyenducshuy-shopee) |
| Lazada Open Platform | GATED (app key, seller auth, HMAC) | No (Unified.to beta MCP) | [Jentic](https://jentic.com/apis/open.lazada.com/lazada); [Unified.to](https://unified.to/integrations/lazada) |
| TikTok Shop | GATED (Partner Center review) | No for Shop; **Ads MCP** (May 2026); AfterShip 3rd-party connector in Claude directory | [MintMCP](https://www.mintmcp.com/docs/tiktok-shop-mcp-setup); [Digiday](https://digiday.com/marketing/tiktok-launches-mcp-server-to-let-ai-agents-run-campaigns/) |
| GrabFood | PARTNER (official SDKs) | No | [grab SDK](https://github.com/grab/grabfood-api-sdk-java) |
| foodpanda | PARTNER (NDA + credentials) | No | [foodpanda integration docs](https://integration.foodpanda.com/en/documentation/) |
| EasyParcel | OPEN (OAuth, sandbox) | No | [developer.easyparcel.com](https://developer.easyparcel.com/) |
| Lalamove | OPEN (HMAC, sandbox) | No | [Lalamove docs](https://developers.lalamove.com/v2/index.html) |
| Ninja Van | GATED (review, OAuth2) | No | [Ninja Van API](https://api-docs.ninjavan.co/) |
| Xero | OPEN (OAuth2) | **Yes**: GitHub server + hosted Claude connector; payroll NZ/UK only | [GitHub](https://github.com/XeroAPI/xero-mcp-server) |
| QuickBooks Online | OPEN (OAuth2) | **Yes**: Intuit OSS server + hosted connector (reportedly US-focused) | [CodeWords](https://www.codewords.ai/blog/quickbooks-mcp) |
| Zoho Books | OPEN (OAuth2) | **Yes**: Zoho Books MCP / Claude default connector | [Zoho help](https://www.zoho.com/uk/books/help/mcp/zoho-books-mcp.html) |
| AutoCount | GATED (AOTG cloud bridge + local client) | No | [AutoCount wiki](https://wiki.autocountsoft.com/wiki/Introduction_to_AOTG_API) |
| Bukku | Token from app settings | No | [npm bukku-client](https://www.npmjs.com/package/bukku-client) |
| Talenox | API key (v2 REST) | No | [Pipedream](https://pipedream.com/apps/talenox.md) |
| Loyverse | OPEN (access tokens) | No | [Loyverse help](https://help.loyverse.com/help/loyverse-api) |
| StoreHub | PARTNER (Customer Care, Enterprise tier) | No | [API Evangelist](https://providers.apievangelist.com/providers/storehub/) |
| WhatsApp Cloud API | OPEN (Meta) / via BSPs | No Meta-official; community servers; Bird connector does WhatsApp | [mcpservers.org](https://mcpservers.org/servers/codechap/mcp-server-whatsapp) |
| Twilio / Infobip / Bird | OPEN | **Yes** (Claude directory) | SearchMcpRegistry lookup 2026-10-15 |
| MY telcos (Number Verification) | Federated, likely enterprise | No | [CelcomDigi PR](https://corporate.celcomdigi.com/news/malaysia-mobile-operators-to-launch-new-federated-network-service-to-help-online-businesses-combat-fraud-and-digital-identity-theft) |
| MSC Trustgate (MyTrust 365) | Open API/SDK (commercial) | No | [MyTrust 365](https://msctrustgate.com/mytrust-365) |
| DocuSign | OPEN | **Yes** (Claude directory) | SearchMcpRegistry lookup 2026-10-15 |
| CTOS / SSM data | PARTNER (via authorised SSM providers) | No | [Malaysia SME](https://www.malaysiasme.com.my/?p=5784) |
| MyInvois (LHDN) | OPEN (OAuth client credentials; intermediary mode; sandbox by email) | No | [MyInvois SDK FAQ](https://sdk.myinvois.hasil.gov.my/faq) |
| Easyship / Shippo (global shipping) | OPEN | **Yes** | [Easyship](https://easyship.com/blog/easyship-mcp-server); [Shippo](https://docs.goshippo.com/docs/guides_general/mcpserver) |

### Inferences
- Priority integration set for a MY hub, ranked by SME reach × API accessibility:
  1. WhatsApp (via Cloud API or BSP)
  2. Shopee, TikTok Shop and Lazada (ISV registration)
  3. MyInvois (intermediary)
  4. SQL Account and AutoCount (on-prem bridge)
  5. EasyParcel and Lalamove
  6. Bukku and Xero/QBO/Zoho (reuse official MCPs)
  7. Payment gateways (out of scope here)
  8. StoreHub/GrabFood/foodpanda (partnerships)
  9. Telco NV and Trustgate signing (enterprise contracts)
  10. CTOS (contract)
- Global CPaaS vendors (Bird, Infobip, Twilio) and unified-API vendors (Unified.to, AfterShip, Pipedream, StackOne) are the main competitive threat in agent connectivity. Their weak spots are Malaysia-specific systems: SQL, AutoCount, MyInvois, MY couriers, StoreHub and Trustgate.

### Gaps
- GitHub, mcp.so and Smithery were not exhaustively crawled. The official MCP registry check was limited to the Claude connector directory. Community MCPs for EasyParcel, MyInvois, SQL Account or AutoCount may exist without being surfaced.
- The status of several vendors (Financio, Biztory, Million, UBS, MYOB, Deskera, PayrollPanda, Info-Tech, Qashier, Slurp, Feedme, DHL eCommerce MY, Grab Express, Parcel Asia, Tracking.my, Experian MY, RAM, Telegram usage) remains unresearched or undocumented.
