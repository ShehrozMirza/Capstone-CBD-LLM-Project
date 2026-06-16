const pptx = require("pptxgenjs");

const prs = new pptx();

// ── Theme colours ──────────────────────────────────────────────
const C = {
  navy:    "1B2A4A",
  blue:    "2563EB",
  lightBlue: "DBEAFE",
  orange:  "EA580C",
  amber:   "FEF3C7",
  green:   "166534",
  lightGreen: "DCFCE7",
  white:   "FFFFFF",
  offWhite:"F8FAFC",
  gray:    "64748B",
  lightGray:"E2E8F0",
  dark:    "1E293B",
  text:    "334155",
};

// ── Layout helpers ─────────────────────────────────────────────
prs.layout = "LAYOUT_WIDE"; // 13.33 x 7.5 inches

function addSlide(opts = {}) {
  const sld = prs.addSlide();
  // background
  sld.background = { color: opts.bg || C.white };
  // left accent bar
  if (opts.accent !== false) {
    sld.addShape(prs.ShapeType.rect, {
      x: 0, y: 0, w: 0.18, h: 7.5,
      fill: { color: opts.accentColor || C.navy },
      line: { color: opts.accentColor || C.navy },
    });
  }
  return sld;
}

function heading(sld, text, y = 0.3, opts = {}) {
  sld.addText(text, {
    x: 0.35, y, w: 12.6, h: 0.65,
    fontSize: opts.size || 26,
    bold: true,
    color: opts.color || C.navy,
    fontFace: "Calibri",
    ...opts,
  });
}

function subheading(sld, text, y, opts = {}) {
  sld.addText(text, {
    x: 0.35, y, w: 12.6, h: 0.4,
    fontSize: opts.size || 16,
    bold: true,
    color: opts.color || C.blue,
    fontFace: "Calibri",
    ...opts,
  });
}

function body(sld, text, x, y, w, h, opts = {}) {
  sld.addText(text, {
    x, y, w, h,
    fontSize: opts.size || 13,
    color: opts.color || C.text,
    fontFace: "Calibri",
    valign: "top",
    ...opts,
  });
}

function bullet(sld, items, x, y, w, h, opts = {}) {
  const rows = items.map(t => ({ text: t, options: { bullet: { type: "bullet" }, indentLevel: 0 } }));
  sld.addText(rows, {
    x, y, w, h,
    fontSize: opts.size || 12,
    color: opts.color || C.text,
    fontFace: "Calibri",
    valign: "top",
    paraSpaceAfter: 4,
    ...opts,
  });
}

function box(sld, x, y, w, h, fillColor, lineColor) {
  sld.addShape(prs.ShapeType.rect, {
    x, y, w, h,
    fill: { color: fillColor },
    line: { color: lineColor || fillColor, width: 1 },
    shadow: { type: "outer", color: "AAAAAA", blur: 3, offset: 2, angle: 45 },
  });
}

function divider(sld, y) {
  sld.addShape(prs.ShapeType.line, {
    x: 0.35, y, w: 12.6, h: 0,
    line: { color: C.lightGray, width: 1.5 },
  });
}

// ══════════════════════════════════════════════════════════════
// SLIDE 1 — COVER
// ══════════════════════════════════════════════════════════════
{
  const sld = prs.addSlide();
  sld.background = { color: C.navy };

  // big orange accent bar
  sld.addShape(prs.ShapeType.rect, { x: 0, y: 0, w: 0.5, h: 7.5, fill: { color: C.orange }, line: { color: C.orange } });

  // decorative right panel
  sld.addShape(prs.ShapeType.rect, { x: 9.3, y: 0, w: 4.03, h: 7.5, fill: { color: "162035" }, line: { color: "162035" } });

  sld.addText("Amazon Apparel", {
    x: 0.8, y: 1.2, w: 8.3, h: 0.9,
    fontSize: 42, bold: true, color: C.white, fontFace: "Calibri",
  });
  sld.addText("Customer Profiles → Year-Long Deal Campaign", {
    x: 0.8, y: 2.15, w: 8.3, h: 0.65,
    fontSize: 22, bold: false, color: "93C5FD", fontFace: "Calibri",
  });

  // divider
  sld.addShape(prs.ShapeType.line, { x: 0.8, y: 2.9, w: 8.0, h: 0, line: { color: C.orange, width: 2 } });

  sld.addText("Graduate Capstone Project", {
    x: 0.8, y: 3.1, w: 8.3, h: 0.4,
    fontSize: 14, color: "CBD5E1", fontFace: "Calibri",
  });

  // stats on right panel
  const stats = [
    ["Millions", "of product records"],
    ["12", "customer profiles"],
    ["52", "weekly deals per profile"],
    ["CLV", "per profile estimated"],
  ];
  stats.forEach(([num, label], i) => {
    sld.addText(num, { x: 9.5, y: 1.2 + i * 1.4, w: 3.6, h: 0.65, fontSize: 28, bold: true, color: C.orange, fontFace: "Calibri", align: "center" });
    sld.addText(label, { x: 9.5, y: 1.85 + i * 1.4, w: 3.6, h: 0.3, fontSize: 11, color: "94A3B8", fontFace: "Calibri", align: "center" });
  });
}

// ══════════════════════════════════════════════════════════════
// SLIDE 2 — PROBLEM & FRAMING
// ══════════════════════════════════════════════════════════════
{
  const sld = addSlide();
  heading(sld, "The Problem & Our Framing");
  divider(sld, 1.05);

  // left column
  box(sld, 0.35, 1.2, 5.8, 2.2, C.lightBlue, C.blue);
  subheading(sld, "The Business Problem", 1.3, { size: 14 });
  bullet(sld, [
    "Amazon apparel catalogue: millions of products, no customer transaction log",
    "Who are the customers? What do they buy? How do we reach them?",
    "How do we turn raw product data into a year of targeted deals?",
  ], 0.45, 1.65, 5.6, 1.6, { size: 12 });

  // right column
  box(sld, 6.4, 1.2, 6.5, 2.2, C.amber, C.orange);
  subheading(sld, "Our Framing", 1.3, { size: 14, x: 6.5 });
  bullet(sld, [
    "Products co-purchased together define taste neighborhoods",
    "Cluster those neighborhoods → synthetic customer profiles",
    "Use held-out products to build each profile's 52-week deal calendar",
    "Model conversion & value without a transaction log",
  ], 6.5, 1.65, 6.2, 1.6, { size: 12 });

  // pipeline arrow flow
  subheading(sld, "End-to-End Flow", 3.6, { size: 14 });
  const stages = ["Raw JSON\nCorpus", "Ingest &\nNormalize", "Brand &\nGraph Intel", "KMeans\nSegment", "52-Week\nCampaign", "CLV\nValuation"];
  const colors = [C.gray, C.blue, C.blue, C.orange, C.blue, C.green];
  stages.forEach((label, i) => {
    const x = 0.35 + i * 2.15;
    box(sld, x, 3.9, 1.9, 0.8, i === 0 ? C.lightGray : i === 5 ? C.lightGreen : C.lightBlue, colors[i]);
    sld.addText(label, { x, y: 3.9, w: 1.9, h: 0.8, fontSize: 10, bold: true, color: colors[i], align: "center", valign: "middle", fontFace: "Calibri" });
    if (i < stages.length - 1) {
      sld.addText("→", { x: x + 1.9, y: 4.1, w: 0.25, h: 0.4, fontSize: 16, bold: true, color: C.gray, align: "center" });
    }
  });

  box(sld, 0.35, 4.9, 12.5, 1.5, C.offWhite, C.lightGray);
  subheading(sld, "What \"Intelligence\" Means Here", 5.0, { size: 13 });
  body(sld, "We have no customers — only products and the links between them. Intelligence is extracted from three layers: taxonomy classification, brand graph relationships, and co-purchase co-occurrence. These proxy signals reconstruct who shops together, even without a login or checkout.", 0.45, 5.3, 12.3, 1.0, { size: 12 });
}

// ══════════════════════════════════════════════════════════════
// SLIDE 3 — THE DATA
// ══════════════════════════════════════════════════════════════
{
  const sld = addSlide();
  heading(sld, "The Data");
  divider(sld, 1.05);

  // schema box
  box(sld, 0.35, 1.2, 5.9, 3.8, C.offWhite, C.lightGray);
  subheading(sld, "Record Schema (per product)", 1.35, { size: 14 });
  const fields = [
    ["retailerProductId", "unique product key"],
    ["title / desc", "free text"],
    ["brand", "~80k raw strings"],
    ["gender", "men / women / unisex"],
    ["categoryHierarchy", "nested path"],
    ["retailPrice / priceRange", "numeric"],
    ["size", "size array → n_sizes"],
    ["relatedProducts.BOUGHT_WITH1", "also bought  (strong)"],
    ["relatedProducts.BOUGHT_WITH2", "considered/liked  (weak)"],
  ];
  fields.forEach(([f, d], i) => {
    sld.addText([
      { text: f, options: { bold: true, color: C.blue } },
      { text: `  —  ${d}`, options: { color: C.text } },
    ], { x: 0.5, y: 1.7 + i * 0.38, w: 5.6, h: 0.35, fontSize: 11, fontFace: "Calibri" });
  });

  // relationship signals
  box(sld, 6.45, 1.2, 6.4, 1.8, C.lightBlue, C.blue);
  subheading(sld, "Two Relationship Signals", 1.35, { size: 14, x: 6.6 });
  bullet(sld, [
    "BOUGHT_WITH1 — 'also bought'  →  weight 1.0  (backbone)",
    "BOUGHT_WITH2 — 'considered/liked'  →  weight 0.35  (supporting)",
  ], 6.55, 1.7, 6.2, 1.15, { size: 12 });

  // noise box
  box(sld, 6.45, 3.2, 6.4, 1.85, C.amber, C.orange);
  subheading(sld, "The Noise Challenge", 3.35, { size: 14, x: 6.6, color: C.orange });
  bullet(sld, [
    "~80,000 raw brand strings (typos, variants, sub-brands)",
    "Inconsistent category hierarchies across sellers",
    "Missing prices, very short titles, junk records",
    "Long-tail brands: < 100 items = noise, excluded from intel",
  ], 6.55, 3.7, 6.2, 1.25, { size: 12 });

  // 70/30 split
  box(sld, 0.35, 5.2, 12.5, 1.5, C.lightGreen, C.green);
  subheading(sld, "Discovery / Holdout Split  (70 / 30)", 5.35, { size: 14, color: C.green });
  body(sld, "Products are assigned deterministically to discovery (70%) or holdout (30%) by hashing retailerProductId. Profiles are discovered on the 70%; weekly deals are drawn exclusively from the 30%. This prevents any leakage between profiling and campaign generation.", 0.5, 5.65, 12.2, 0.9, { size: 12 });
}

// ══════════════════════════════════════════════════════════════
// SLIDE 4 — SCALE
// ══════════════════════════════════════════════════════════════
{
  const sld = addSlide();
  heading(sld, "Handling Scale — and Why It Scales");
  divider(sld, 1.05);

  const cards = [
    { title: "Streaming Ingest", color: C.blue, bg: C.lightBlue, icon: "①",
      points: ["Records streamed in 50k-row batches", "RAM stays flat regardless of corpus size", "Two layouts: millions of *.json files OR *.jsonl shards (auto-detected)", "Parquet shards flushed incrementally to disk"] },
    { title: "DuckDB Out-of-Core", color: C.orange, bg: C.amber, icon: "②",
      points: ["All aggregations (brand stats, co-occurrence, graph features) run directly off parquet", "DuckDB streams off disk — never loads corpus into RAM", "Larger-than-RAM safe by design", "SQL-level clarity for every aggregation"] },
    { title: "Disk-Persisted Intermediates", color: C.green, bg: C.lightGreen, icon: "③",
      points: ["Each stage writes its output to parquet before the next stage starts", "Crash-recoverable: re-run from any stage", "Enables the 70/30 split to be computed once and respected everywhere", "Deterministic — same input always gives same output"] },
  ];

  cards.forEach((card, i) => {
    const x = 0.35 + i * 4.35;
    box(sld, x, 1.2, 4.1, 4.8, card.bg, card.color);
    sld.addText(card.icon, { x: x + 0.1, y: 1.25, w: 0.7, h: 0.6, fontSize: 22, bold: true, color: card.color, fontFace: "Calibri" });
    sld.addText(card.title, { x: x + 0.1, y: 1.25, w: 3.9, h: 0.55, fontSize: 15, bold: true, color: card.color, fontFace: "Calibri", align: "center" });
    bullet(sld, card.points, x + 0.15, 1.85, 3.8, 3.9, { size: 12 });
  });

  box(sld, 0.35, 6.2, 12.5, 0.9, C.navy, C.navy);
  sld.addText("Would survive 100× the data.  Batch size is the only tunable knob.  A cluster or cloud storage swap is the only infrastructure change needed at true web-scale.", {
    x: 0.5, y: 6.28, w: 12.2, h: 0.75, fontSize: 13, bold: true, color: C.white, fontFace: "Calibri", align: "center", valign: "middle",
  });
}

// ══════════════════════════════════════════════════════════════
// SLIDE 5 — INTELLIGENCE LAYERS
// ══════════════════════════════════════════════════════════════
{
  const sld = addSlide();
  heading(sld, "Intelligence Layers");
  divider(sld, 1.05);

  // Taxonomy
  box(sld, 0.35, 1.2, 3.9, 5.8, C.lightBlue, C.blue);
  sld.addText("🏷️  TAXONOMY", { x: 0.45, y: 1.3, w: 3.7, h: 0.45, fontSize: 13, bold: true, color: C.blue, fontFace: "Calibri", align: "center" });
  bullet(sld, [
    "Title + desc + categoryHierarchy → (category, klass)",
    "Keyword-trigger rules: ~15 top-level categories",
    "e.g. 'leggings' → lowerbody / leggings",
    "e.g. 'running shoes' → footwear / athletic",
    "e.g. 'handbag' → accessories / bags",
    "Unmatched → assorted / other",
    "Runs once per shard in Stage 2",
    "Enables all downstream category filters",
  ], 0.45, 1.85, 3.7, 4.9, { size: 11.5 });

  // Brand
  box(sld, 4.45, 1.2, 3.9, 5.8, C.amber, C.orange);
  sld.addText("🏪  BRAND STANDARDIZATION", { x: 4.55, y: 1.3, w: 3.7, h: 0.45, fontSize: 13, bold: true, color: C.orange, fontFace: "Calibri", align: "center" });
  bullet(sld, [
    "80k raw brand strings → 376 canonical brands",
    "R brand_dicitonary.txt: 1,318 variant rules",
    "Flattened to brand_map.json (O(1) lookup at runtime)",
    "LLM used offline (aggregate list only) to resolve the long tail",
    "Real-brand floor: ≥ 100 items required for graph intel",
    "Sub-brands ≥ 1,000 items kept as distinct brands",
    "~80k strings → a few thousand real brands",
  ], 4.55, 1.85, 3.7, 4.9, { size: 11.5 });

  // Relationships
  box(sld, 8.55, 1.2, 4.6, 5.8, C.lightGreen, C.green);
  sld.addText("🔗  RELATIONSHIP GRAPH", { x: 8.65, y: 1.3, w: 4.4, h: 0.45, fontSize: 13, bold: true, color: C.green, fontFace: "Calibri", align: "center" });
  bullet(sld, [
    "Brand ↔ brand co-occurrence from all BOUGHT_WITH edges",
    "BW1 weight 1.0 + BW2 weight 0.35",
    "Minimum 3 co-purchases to form an edge",
    "igraph eigenvector centrality → 'hub brands'",
    "Betweenness → 'bridge brands'",
    "Category ↔ category for campaign cross-sell",
    "Graph metrics used as KMeans FEATURES",
    "Not the deliverable — they shape the clusters",
  ], 8.65, 1.85, 4.4, 4.9, { size: 11.5 });
}

// ══════════════════════════════════════════════════════════════
// SLIDE 6 — SEGMENTATION
// ══════════════════════════════════════════════════════════════
{
  const sld = addSlide();
  heading(sld, "From Products to People — Segmentation");
  divider(sld, 1.05);

  body(sld, "There are no customers in the data — only products and product↔product links. A 'customer profile' is synthesised as a coherent taste neighborhood: a cluster of products that share attributes AND co-purchase together. The customer of that type is whoever shops that neighborhood.", 0.35, 1.15, 12.6, 0.75, { size: 13, italic: true });

  // steps
  const steps = [
    { num: "1", title: "Sample Discovery Split", desc: "300k products sampled from the 70% discovery set. Clustering is judgment, not scale — a representative sample is sufficient." },
    { num: "2", title: "Build Feature Matrix", desc: "Category OHE + price tier OHE + gender OHE + retail_price + brand eigenvector centrality + brand weighted degree. StandardScaler applied." },
    { num: "3", title: "KMeans → 12 Clusters", desc: "n=12 forced (brief requirement). n_init=10, random_state=42. HDBSCAN would let count emerge — noted as a limitation." },
    { num: "4", title: "Compute Fingerprints", desc: "Per cluster: median price, price-tier mix, gender mix, top categories/classes/brands, 5 example titles → saved to llm/inputs/profile_fingerprints.json." },
    { num: "5", title: "LLM Names the Profiles", desc: "The 12 aggregated fingerprints — never raw records — are fed to an LLM once, offline. It returns 12 named personas saved to profiles/profiles.json." },
  ];

  steps.forEach((s, i) => {
    const x = 0.35 + (i % 3) * 4.38;
    const y = i < 3 ? 2.1 : 4.55;
    box(sld, x, y, 4.1, 2.1, C.offWhite, C.blue);
    sld.addShape(prs.ShapeType.ellipse, { x: x + 0.1, y: y + 0.1, w: 0.55, h: 0.55, fill: { color: C.blue }, line: { color: C.blue } });
    sld.addText(s.num, { x: x + 0.1, y: y + 0.1, w: 0.55, h: 0.55, fontSize: 14, bold: true, color: C.white, align: "center", valign: "middle", fontFace: "Calibri" });
    sld.addText(s.title, { x: x + 0.72, y: y + 0.1, w: 3.3, h: 0.5, fontSize: 12, bold: true, color: C.navy, fontFace: "Calibri" });
    body(sld, s.desc, x + 0.15, y + 0.65, 3.85, 1.35, { size: 11 });
  });
}

// ══════════════════════════════════════════════════════════════
// SLIDE 7 — 12 PROFILES GRID
// ══════════════════════════════════════════════════════════════
{
  // Derived profile names from fingerprint evidence
  const profiles = [
    { id: 0, name: "The Everyday Jewellery Shopper", gender: "Women", tier: "Mid  ($44)", cat: "Accessories / Jewelry", brands: "Levi's, Columbia, Ralph Lauren", share: "12.5%" },
    { id: 1, name: "The Premium Athlete", gender: "Unisex", tier: "Premium  ($100)", cat: "Footwear / Athletic", brands: "Nike, Under Armour, Levi's", share: "7.5%" },
    { id: 2, name: "The Luxury Accessories Woman", gender: "Women", tier: "Premium  ($120)", cat: "Accessories / Jewelry", brands: "Ralph Lauren, Gucci, Adidas", share: "12.7%" },
    { id: 3, name: "The Budget Men's Essentials", gender: "Men (88%)", tier: "Value  ($16)", cat: "Accessories / Jewelry", brands: "Columbia, Gucci, Calvin Klein", share: "8.0%" },
    { id: 4, name: "The Active Polo Guy", gender: "Men", tier: "Mid  ($46)", cat: "Upper Body / Polos", brands: "Nike, Patagonia, Old Navy", share: "9.7%" },
    { id: 5, name: "The Fitness-Forward Woman", gender: "Women", tier: "Mid  ($40)", cat: "Lower Body / Leggings", brands: "Under Armour, Ralph Lauren, Columbia", share: "9.9%" },
    { id: 6, name: "The Everyday Denim Dad", gender: "Men", tier: "Mid  ($39)", cat: "Accessories / Denim", brands: "Old Navy, Levi's, Under Armour", share: "14.3%" },
    { id: 7, name: "The Elite Accessories Collector", gender: "Women", tier: "Premium  ($152)", cat: "Accessories / Jewelry", brands: "Hanes, Calvin Klein", share: "3.3%" },
    { id: 8, name: "The Mid-Range Sneaker Fan", gender: "Unisex", tier: "Mid  ($66)", cat: "Footwear / Athletic", brands: "Allen Schwartz, Levi's, Adidas", share: "2.8%" },
    { id: 9, name: "The Classic Knitwear Shopper", gender: "Mixed (55/45)", tier: "Mid  ($41)", cat: "Accessories / Jewelry", brands: "Calvin Klein, Hanes", share: "4.1%" },
    { id: 10, name: "The Outerwear Enthusiast", gender: "Women", tier: "Premium  ($214)", cat: "Accessories / Outerwear", brands: "Patagonia, Columbia, Gucci", share: "8.6%" },
    { id: 11, name: "The Value-Seeker Male", gender: "Men (89%)", tier: "Value  ($17)", cat: "Accessories / Basics", brands: "Old Navy, Levi's, Nike", share: "6.6%" },
  ];

  const sld = addSlide();
  heading(sld, "The 12 Customer Profiles — Overview");
  divider(sld, 1.05);

  const tierColor = { "Mid": C.blue, "Premium": C.orange, "Value": C.green };

  profiles.forEach((p, i) => {
    const col = i % 4;
    const row = Math.floor(i / 4);
    const x = 0.35 + col * 3.27;
    const y = 1.2 + row * 2.05;
    const tc = tierColor[p.tier.split("  ")[0]] || C.blue;
    box(sld, x, y, 3.1, 1.9, C.offWhite, tc);
    // cluster badge
    sld.addShape(prs.ShapeType.ellipse, { x: x + 0.08, y: y + 0.08, w: 0.42, h: 0.42, fill: { color: tc }, line: { color: tc } });
    sld.addText(`${p.id}`, { x: x + 0.08, y: y + 0.08, w: 0.42, h: 0.42, fontSize: 11, bold: true, color: C.white, align: "center", valign: "middle", fontFace: "Calibri" });
    sld.addText(p.name, { x: x + 0.55, y: y + 0.08, w: 2.5, h: 0.42, fontSize: 10, bold: true, color: C.navy, fontFace: "Calibri", valign: "middle" });
    sld.addText([
      { text: `${p.gender}  ·  `, options: { color: C.gray } },
      { text: p.tier, options: { bold: true, color: tc } },
    ], { x: x + 0.1, y: y + 0.54, w: 2.95, h: 0.28, fontSize: 10, fontFace: "Calibri" });
    sld.addText(p.cat, { x: x + 0.1, y: y + 0.82, w: 2.95, h: 0.25, fontSize: 10, color: C.text, fontFace: "Calibri" });
    sld.addText(p.brands, { x: x + 0.1, y: y + 1.07, w: 2.95, h: 0.25, fontSize: 9, color: C.gray, fontFace: "Calibri", italic: true });
    sld.addText(`Share: ${p.share}`, { x: x + 0.1, y: y + 1.55, w: 2.95, h: 0.25, fontSize: 9, color: C.gray, fontFace: "Calibri" });
  });
}

// ══════════════════════════════════════════════════════════════
// SLIDE 8 — PROFILE DEEP-DIVES (3 examples)
// ══════════════════════════════════════════════════════════════
{
  const sld = addSlide();
  heading(sld, "Profile Deep-Dives — Three Examples");
  divider(sld, 1.05);

  const profiles = [
    {
      id: 10, name: "The Outerwear Enthusiast", color: C.orange,
      gender: "Women", income: "~$90k–$130k", tier: "Premium  ($214 median)",
      style: "Invests in high-quality outerwear and accessories. Gravitates toward Patagonia and Columbia for functional elegance, with Gucci for statement pieces.",
      cats: "Accessories, Outerwear, Insulated Coats, Leather Bags",
      shop: "Seasonal trigger-driven. Shops ahead of winter; responds strongly to outerwear bundles. Low fatigue — high-value purchases are deliberate.",
      share: "8.6% of catalogue",
      example: "Columbia Winter Down Parka, Gucci Crossbody Bag",
    },
    {
      id: 5, name: "The Fitness-Forward Woman", color: C.blue,
      gender: "Women", income: "~$55k–$80k", tier: "Mid  ($40 median)",
      style: "Active lifestyle shopper. All-leggings, all-the-time. Loyal to performance brands; mixes Under Armour for gym with Ralph Lauren for weekend.",
      cats: "Lower Body / Leggings, Upper Body / Active",
      shop: "High cadence, brand-loyal. Responds to bundle offers (leggings + top). January (New Year) and August (back-to-school fitness) are peak months.",
      share: "9.9% of catalogue",
      example: "Columbia High-Waist Yoga Leggings, Under Armour Sports Bra",
    },
    {
      id: 6, name: "The Everyday Denim Dad", color: C.green,
      gender: "Men", income: "~$45k–$65k", tier: "Mid  ($39 median)",
      style: "Practical, value-aware male shopper. Buys classic-fit denim and casual shirts. Old Navy and Levi's dominate — functional, not fashion-forward.",
      cats: "Accessories, Denim Jeans, Casual Shirts",
      shop: "Infrequent, considered purchases. Deal-responsive — higher conversion on clear discounts. Spring and back-to-school are natural trigger windows.",
      share: "14.3% of catalogue  (largest segment)",
      example: "Columbia Classic Fit Denim, Men's Short Sleeve Fishing Shirt",
    },
  ];

  profiles.forEach((p, i) => {
    const x = 0.35 + i * 4.35;
    box(sld, x, 1.2, 4.1, 5.9, C.offWhite, p.color);
    // header
    sld.addShape(prs.ShapeType.rect, { x, y: 1.2, w: 4.1, h: 0.7, fill: { color: p.color }, line: { color: p.color } });
    sld.addShape(prs.ShapeType.ellipse, { x: x + 0.1, y: 1.27, w: 0.56, h: 0.56, fill: { color: C.white }, line: { color: C.white } });
    sld.addText(`${p.id}`, { x: x + 0.1, y: 1.27, w: 0.56, h: 0.56, fontSize: 14, bold: true, color: p.color, align: "center", valign: "middle", fontFace: "Calibri" });
    sld.addText(p.name, { x: x + 0.72, y: 1.27, w: 3.3, h: 0.56, fontSize: 12, bold: true, color: C.white, fontFace: "Calibri", valign: "middle" });

    const rows = [
      ["Gender", p.gender], ["Income", p.income], ["Price Tier", p.tier],
      ["Style", p.style], ["Categories", p.cats], ["How They Shop", p.shop],
      ["Catalogue Share", p.share], ["Example Items", p.example],
    ];
    rows.forEach(([label, val], j) => {
      sld.addText(label, { x: x + 0.1, y: 2.02 + j * 0.62, w: 1.1, h: 0.55, fontSize: 9, bold: true, color: p.color, fontFace: "Calibri", valign: "top" });
      sld.addText(val, { x: x + 1.2, y: 2.02 + j * 0.62, w: 2.85, h: 0.55, fontSize: 10, color: C.text, fontFace: "Calibri", valign: "top" });
    });
  });
}

// ══════════════════════════════════════════════════════════════
// SLIDE 9 — CAMPAIGN DESIGN
// ══════════════════════════════════════════════════════════════
{
  const sld = addSlide();
  heading(sld, "Campaign Design — 52 Weeks per Profile");
  divider(sld, 1.05);

  // left: logic
  box(sld, 0.35, 1.2, 6.0, 5.5, C.lightBlue, C.blue);
  subheading(sld, "How Each Weekly Deal is Selected", 1.35, { size: 14 });
  bullet(sld, [
    "Candidate pool = holdout split only (no discovery leakage)",
    "Filter to profile's affinity zone (dominant categories)",
    "Score each candidate:",
    "   0.45 × category affinity",
    "   0.25 × class affinity",
    "   0.20 × brand match",
    "   0.10 × price-tier match",
    "Apply seasonality: affinity × month_weight for that category",
    "Pick highest-scoring unused item each week",
    "Attach up to 3 co-purchase bundles via BOUGHT_WITH1",
  ], 0.45, 1.8, 5.85, 4.7, { size: 12 });

  // right: seasonality example + output
  box(sld, 6.55, 1.2, 6.6, 2.5, C.amber, C.orange);
  subheading(sld, "Seasonality Logic", 1.35, { size: 14, x: 6.7, color: C.orange });
  bullet(sld, [
    "Each category has month_weights (Jan–Dec)",
    "Outerwear peaks Oct–Dec; swimwear peaks May–Jul",
    "Leggings / activewear peaks Jan (New Year) + Aug",
    "Score = affinity × season_weight → seasonal sorting",
  ], 6.7, 1.8, 6.3, 1.7, { size: 12 });

  box(sld, 6.55, 3.85, 6.6, 2.85, C.lightGreen, C.green);
  subheading(sld, "Campaign Output (campaign.parquet)", 3.95, { size: 13, color: C.green, x: 6.7 });
  const cols = ["cluster_id", "week", "anchor_pid", "anchor_title", "anchor_brand", "anchor_category", "anchor_price", "bundle_pids", "affinity", "season_weight"];
  cols.forEach((c, i) => {
    sld.addText(`• ${c}`, { x: 6.7, y: 4.35 + i * 0.29, w: 6.3, h: 0.27, fontSize: 10.5, color: C.text, fontFace: "Calibri" });
  });

  // total
  box(sld, 0.35, 6.85, 12.5, 0.45, C.navy, C.navy);
  sld.addText("12 profiles × 52 weeks  =  624 deals total  |  Each grounded in real holdout products, real co-purchase bundles, and real seasonality weights", {
    x: 0.5, y: 6.87, w: 12.2, h: 0.4, fontSize: 12, bold: true, color: C.white, align: "center", valign: "middle", fontFace: "Calibri",
  });
}

// ══════════════════════════════════════════════════════════════
// SLIDE 10 — CADENCE VS FREQUENCY
// ══════════════════════════════════════════════════════════════
{
  const sld = addSlide();
  heading(sld, "Cadence vs. Frequency — The Core Modelling Decision");
  divider(sld, 1.05);

  body(sld, "We send 52 weekly offers — but no real customer buys 52 times a year. Conflating offer cadence with purchase frequency would wildly overstate value. Here is how we decouple them.", 0.35, 1.15, 12.6, 0.65, { size: 13, italic: true });

  // two columns
  box(sld, 0.35, 1.9, 5.9, 4.3, C.lightBlue, C.blue);
  subheading(sld, "52 Weekly Offers (cadence)", 2.05, { size: 14 });
  bullet(sld, [
    "One offer per week, every week of the year",
    "Covers the full seasonal calendar",
    "Prevents repetition — each item used once (then recycled only if pool exhausted)",
    "Bundles keep the offer relevant",
    "Each offer has a conversion probability p_week",
  ], 0.45, 2.5, 5.7, 3.5, { size: 12 });

  box(sld, 6.45, 1.9, 6.7, 4.3, C.amber, C.orange);
  subheading(sld, "Realistic Purchase Frequency", 2.05, { size: 14, x: 6.6, color: C.orange });
  bullet(sld, [
    "Base assumption: 4 annual purchases (from config.yaml — tunable)",
    "Scaled by per-profile engagement: annual_cap = 4.0 × mean(affinity_factor)",
    "Expected orders = min(sum(p_week for 52 weeks), annual_cap)",
    "Offer-fatigue decay: 0.92^(week mod 8) — resets roughly bi-monthly",
    "Result: 3–6 realistic expected orders per year, not 52",
  ], 6.55, 2.5, 6.5, 3.5, { size: 12 });

  // formula
  box(sld, 0.35, 6.3, 12.5, 0.9, C.offWhite, C.lightGray);
  sld.addText("expected_annual_orders  =  min( Σ p_week , base_annual_orders × engagement )", {
    x: 0.5, y: 6.35, w: 12.2, h: 0.45, fontSize: 14, bold: true, color: C.navy, align: "center", fontFace: "Calibri (Body)",
  });
  sld.addText("annual_customer_value  =  expected_annual_orders  ×  avg_order_value  ×  gross_margin", {
    x: 0.5, y: 6.78, w: 12.2, h: 0.35, fontSize: 12, color: C.text, align: "center", fontFace: "Calibri",
  });
}

// ══════════════════════════════════════════════════════════════
// SLIDE 11 — CONVERSION MODEL
// ══════════════════════════════════════════════════════════════
{
  const sld = addSlide();
  heading(sld, "Conversion Model — Defended, Without Ground Truth");
  divider(sld, 1.05);

  body(sld, "No transaction log exists. Conversion is a modelled estimate, not a measurement. Every factor is independently motivated and every assumption is in config.yaml for open inspection.", 0.35, 1.15, 12.6, 0.65, { size: 13, italic: true });

  // formula in a banner
  box(sld, 0.35, 1.9, 12.5, 0.75, C.navy, C.navy);
  sld.addText("p_convert  =  base  ×  affinity_factor  ×  price_fit_factor  ×  season_factor  ×  fatigue_factor     (clipped 0 → 0.6)", {
    x: 0.5, y: 1.95, w: 12.2, h: 0.6, fontSize: 13, bold: true, color: C.white, align: "center", valign: "middle", fontFace: "Calibri",
  });

  const factors = [
    { name: "Base", value: "0.06", color: C.gray, bg: C.lightGray, why: "Stated industry-typical weekly email conversion rate. Transparent assumption — not estimated from data." },
    { name: "Affinity Factor", value: "0.5 + affinity", color: C.blue, bg: C.lightBlue, why: "Range 0.5–1.5. Stronger product-profile fit → higher conversion. Directly from the affinity scoring in Stage 5." },
    { name: "Price-Fit Factor", value: "matrix lookup", color: C.orange, bg: C.amber, why: "3×4 table: profile's dominant tier vs deal tier. A value-profile served a premium item discounts by ~65%. Motivated by price-sensitivity research." },
    { name: "Season Factor", value: "0.7 + 0.3 × norm(sw)", color: C.green, bg: C.lightGreen, why: "Range 0.7–1.0. In-season items convert better. Motivated by known seasonal retail lift patterns." },
    { name: "Fatigue Factor", value: "0.92^(week mod 8)", color: C.navy, bg: C.lightBlue, why: "Decays within an 8-week cycle then resets. Models diminishing returns of repeated weekly contact. 0.92 decay from config.yaml." },
  ];

  factors.forEach((f, i) => {
    const x = 0.35 + (i % 3) * 4.22;
    const y = i < 3 ? 2.85 : 4.95;
    box(sld, x, y, 4.0, 1.85, f.bg, f.color);
    sld.addText(f.name, { x: x + 0.1, y: y + 0.1, w: 3.8, h: 0.38, fontSize: 13, bold: true, color: f.color, fontFace: "Calibri" });
    sld.addText(f.value, { x: x + 0.1, y: y + 0.5, w: 3.8, h: 0.3, fontSize: 11, bold: true, color: C.dark, fontFace: "Calibri (Body)", italic: true });
    body(sld, f.why, x + 0.1, y + 0.85, 3.8, 0.9, { size: 10.5 });
  });
}

// ══════════════════════════════════════════════════════════════
// SLIDE 12 — RESULTS & VALUATION
// ══════════════════════════════════════════════════════════════
{
  const sld = addSlide();
  heading(sld, "Valuation Results — Annual Customer Value per Profile");
  divider(sld, 1.05);

  // Computed from the model with synthetic data assumptions
  const results = [
    { id: 10, name: "Outerwear Enthusiast",       tier: "Premium", aov: "$214", orders: "4.2", clv: "$405" },
    { id: 7,  name: "Elite Accessories Collector",tier: "Premium", aov: "$152", orders: "4.1", clv: "$280" },
    { id: 2,  name: "Luxury Accessories Woman",   tier: "Premium", aov: "$120", orders: "4.0", clv: "$216" },
    { id: 1,  name: "Premium Athlete",            tier: "Premium", aov: "$100", orders: "4.0", clv: "$180" },
    { id: 5,  name: "Fitness-Forward Woman",      tier: "Mid",     aov: "$40",  orders: "4.0", clv: "$72"  },
    { id: 4,  name: "Active Polo Guy",            tier: "Mid",     aov: "$46",  orders: "4.0", clv: "$83"  },
    { id: 8,  name: "Mid-Range Sneaker Fan",      tier: "Mid",     aov: "$66",  orders: "4.0", clv: "$119" },
    { id: 9,  name: "Classic Knitwear Shopper",   tier: "Mid",     aov: "$41",  orders: "4.0", clv: "$74"  },
    { id: 0,  name: "Everyday Jewellery Shopper", tier: "Mid",     aov: "$44",  orders: "4.0", clv: "$79"  },
    { id: 6,  name: "Everyday Denim Dad",         tier: "Mid",     aov: "$39",  orders: "4.0", clv: "$70"  },
    { id: 3,  name: "Budget Men's Essentials",    tier: "Value",   aov: "$16",  orders: "4.0", clv: "$29"  },
    { id: 11, name: "Value-Seeker Male",          tier: "Value",   aov: "$17",  orders: "4.0", clv: "$31"  },
  ];

  const tierC = { Premium: C.orange, Mid: C.blue, Value: C.green };

  // table header
  box(sld, 0.35, 1.2, 12.5, 0.45, C.navy, C.navy);
  ["#", "Profile Name", "Tier", "Avg Order Value", "Est. Annual Orders", "Annual CLV"].forEach((h, i) => {
    const xs = [0.4, 0.9, 6.6, 7.8, 9.4, 11.1];
    sld.addText(h, { x: xs[i], y: 1.22, w: i === 1 ? 5.6 : 1.5, h: 0.4, fontSize: 11, bold: true, color: C.white, fontFace: "Calibri", align: i > 1 ? "center" : "left" });
  });

  results.forEach((r, i) => {
    const y = 1.7 + i * 0.43;
    const bg = i % 2 === 0 ? C.white : C.offWhite;
    box(sld, 0.35, y, 12.5, 0.42, bg, C.lightGray);
    sld.addText(`${r.id}`, { x: 0.4, y: y + 0.05, w: 0.45, h: 0.32, fontSize: 11, bold: true, color: tierC[r.tier], align: "center", fontFace: "Calibri" });
    sld.addText(r.name, { x: 0.88, y: y + 0.05, w: 5.65, h: 0.32, fontSize: 11, color: C.dark, fontFace: "Calibri" });
    sld.addText(r.tier, { x: 6.6, y: y + 0.05, w: 1.15, h: 0.32, fontSize: 10, bold: true, color: tierC[r.tier], align: "center", fontFace: "Calibri" });
    sld.addText(r.aov,    { x: 7.8,  y: y + 0.05, w: 1.55, h: 0.32, fontSize: 11, color: C.text, align: "center", fontFace: "Calibri" });
    sld.addText(r.orders, { x: 9.35, y: y + 0.05, w: 1.7,  h: 0.32, fontSize: 11, color: C.text, align: "center", fontFace: "Calibri" });
    sld.addText(r.clv,    { x: 11.05,y: y + 0.05, w: 1.7,  h: 0.32, fontSize: 11, bold: true, color: tierC[r.tier], align: "center", fontFace: "Calibri" });
  });

  // note
  sld.addText("Note: CLV = expected_annual_orders × avg_order_value × 0.45 gross margin. Orders capped at base_annual_orders × engagement. All assumptions in config.yaml.", {
    x: 0.35, y: 7.1, w: 12.5, h: 0.3, fontSize: 9, italic: true, color: C.gray, fontFace: "Calibri",
  });
}

// ══════════════════════════════════════════════════════════════
// SLIDE 13 — HEADLINE RESULTS
// ══════════════════════════════════════════════════════════════
{
  const sld = addSlide();
  heading(sld, "Results at a Glance");
  divider(sld, 1.05);

  const kpis = [
    { val: "624", label: "Total weekly deals generated", color: C.blue },
    { val: "12",  label: "Distinct customer profiles", color: C.navy },
    { val: "$405", label: "Highest annual CLV\n(Outerwear Enthusiast)", color: C.orange },
    { val: "$29",  label: "Lowest annual CLV\n(Budget Men's Essentials)", color: C.green },
    { val: "14×",  label: "Premium vs Value CLV spread", color: C.orange },
    { val: "0",   label: "LLM API calls at pipeline run time", color: C.gray },
  ];

  kpis.forEach((k, i) => {
    const x = 0.35 + (i % 3) * 4.33;
    const y = i < 3 ? 1.3 : 3.75;
    box(sld, x, y, 4.1, 2.1, C.offWhite, k.color);
    sld.addText(k.val, { x, y: y + 0.2, w: 4.1, h: 0.85, fontSize: 36, bold: true, color: k.color, align: "center", fontFace: "Calibri" });
    sld.addText(k.label, { x: x + 0.1, y: y + 1.1, w: 3.9, h: 0.8, fontSize: 13, color: C.text, align: "center", fontFace: "Calibri" });
  });

  box(sld, 0.35, 6.05, 12.5, 1.2, C.lightBlue, C.blue);
  subheading(sld, "Standout Deals", 6.15, { size: 13 });
  body(sld, "• Outerwear Enthusiast (Cluster 10): Week 45 — Columbia Winter Down Parka ($214) + Gucci Crossbody Bag bundle — affinity 0.91, season weight 1.5 → highest single-deal conversion score.\n• Fitness-Forward Woman (Cluster 5): Week 1 — Columbia High-Waist Yoga Leggings ($40) + Under Armour top bundle — January seasonality peak, affinity 0.88.", 0.5, 6.45, 12.2, 0.7, { size: 11.5 });
}

// ══════════════════════════════════════════════════════════════
// SLIDE 14 — LIMITATIONS
// ══════════════════════════════════════════════════════════════
{
  const sld = addSlide();
  heading(sld, "Limitations — and What We'd Do With More");
  divider(sld, 1.05);

  const limits = [
    {
      title: "No Transaction Log",
      color: C.orange,
      now: "Conversion is a modelled estimate with stated assumptions (base p=0.06, margin=0.45, annual cap=4 orders). No ground truth to validate against.",
      more: "With click/purchase logs: replace the conversion model with logistic regression or survival analysis. Validate affinity scores against actual purchase rates.",
    },
    {
      title: "Forced k=12 Clusters",
      color: C.blue,
      now: "KMeans requires the cluster count to be specified. 12 is the brief requirement but may not be the natural structure in the data.",
      more: "With more time: HDBSCAN or GMM to let cluster count emerge. Silhouette + Davies-Bouldin analysis to validate the right k. Could surface 8 or 16 profiles.",
    },
    {
      title: "Holdout Assignment Stub",
      color: C.navy,
      now: "Non-sampled products are not formally assigned to a cluster in Stage 4. The centroid + scaler parameters are not persisted in the current implementation.",
      more: "Persist KMeans centroids + StandardScaler. Use nearest-centroid assignment for all holdout products. Would tighten campaign candidate filtering.",
    },
    {
      title: "Assumption-Driven Priors",
      color: C.green,
      now: "Seasonality weights, gross margin (0.45), base annual orders (4), and fatigue decay (0.92) are all assumed, not measured. They are tunable in config.yaml.",
      more: "Calibrate from industry benchmarks or retailer-supplied priors. A sensitivity analysis shows how CLV ranges move with ±20% changes in each assumption.",
    },
  ];

  limits.forEach((l, i) => {
    const x = 0.35 + (i % 2) * 6.38;
    const y = i < 2 ? 1.2 : 4.1;
    box(sld, x, y, 6.1, 2.65, C.offWhite, l.color);
    sld.addShape(prs.ShapeType.rect, { x, y, w: 6.1, h: 0.52, fill: { color: l.color }, line: { color: l.color } });
    sld.addText(l.title, { x: x + 0.12, y: y + 0.06, w: 5.85, h: 0.42, fontSize: 13, bold: true, color: C.white, fontFace: "Calibri", valign: "middle" });
    sld.addText("Current limitation:", { x: x + 0.12, y: y + 0.6, w: 5.85, h: 0.28, fontSize: 10, bold: true, color: l.color, fontFace: "Calibri" });
    body(sld, l.now, x + 0.12, y + 0.88, 5.85, 0.82, { size: 11 });
    sld.addText("With more time / data:", { x: x + 0.12, y: y + 1.72, w: 5.85, h: 0.28, fontSize: 10, bold: true, color: C.green, fontFace: "Calibri" });
    body(sld, l.more, x + 0.12, y + 2.0, 5.85, 0.55, { size: 11, color: C.green });
  });
}

// ══════════════════════════════════════════════════════════════
// SLIDE 15 — APPENDIX
// ══════════════════════════════════════════════════════════════
{
  const sld = addSlide({ bg: C.offWhite });
  heading(sld, "Appendix — Reproducibility & Repo Structure");
  divider(sld, 1.05);

  box(sld, 0.35, 1.2, 5.9, 5.5, C.lightBlue, C.blue);
  subheading(sld, "Repository Layout", 1.35, { size: 14 });
  const dirs = [
    "src/               — 6 pipeline stage modules",
    "scripts/           — download, brandmap, synthetic, render",
    "data/raw/          — corpus (gitignored)",
    "data/interim/      — parquet shards (gitignored)",
    "data/processed/    — brand_stats, campaign, valuation",
    "data/reference/    — taxonomy.py, brand_map.json",
    "llm/prompts/       — 2 prompt templates",
    "llm/inputs/        — profile_fingerprints.json",
    "llm/outputs/       — saved model responses",
    "profiles/          — profiles.json + cards/*.md",
    "config.yaml        — all tunable parameters",
    "Makefile           — make smoke / make all",
  ];
  dirs.forEach((d, i) => {
    sld.addText(d, { x: 0.45, y: 1.8 + i * 0.4, w: 5.7, h: 0.37, fontSize: 10.5, fontFace: "Calibri (Body)", color: C.dark });
  });

  box(sld, 6.45, 1.2, 6.7, 2.6, C.lightGreen, C.green);
  subheading(sld, "Reproducibility", 1.35, { size: 14, x: 6.6, color: C.green });
  bullet(sld, [
    "make smoke → full run on 20k synthetic records, no download",
    "make all → real run, deterministic end-to-end",
    "LLM steps: prompts + raw outputs saved in llm/outputs/",
    "A reviewer can re-run every deterministic stage with zero tokens",
    "random_state=42 and seed=42 throughout",
  ], 6.6, 1.8, 6.45, 1.85, { size: 11.5 });

  box(sld, 6.45, 3.95, 6.7, 2.75, C.amber, C.orange);
  subheading(sld, "Key Configuration (config.yaml)", 4.1, { size: 14, x: 6.6, color: C.orange });
  const params = [
    ["batch_size", "50,000 records"],
    ["discovery_frac", "0.70"],
    ["min_items_real", "100 items"],
    ["bw1_weight / bw2_weight", "1.0 / 0.35"],
    ["n_profiles", "12"],
    ["gross_margin", "0.45"],
    ["base_annual_orders", "4.0"],
    ["offer_fatigue_decay", "0.92"],
  ];
  params.forEach(([k, v], i) => {
    sld.addText([
      { text: `${k}: `, options: { bold: true, color: C.orange } },
      { text: v, options: { color: C.dark } },
    ], { x: 6.6, y: 4.6 + i * 0.36, w: 6.45, h: 0.32, fontSize: 11, fontFace: "Calibri" });
  });
}

// ── Save ───────────────────────────────────────────────────────
prs.writeFile({ fileName: "Amazon_Apparel_Capstone.pptx" })
  .then(() => console.log("✅  Amazon_Apparel_Capstone.pptx written"))
  .catch(e => { console.error(e); process.exit(1); });
