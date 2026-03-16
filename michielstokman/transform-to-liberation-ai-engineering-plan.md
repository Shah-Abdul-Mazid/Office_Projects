# Transform to Liberation MVP — AI Engineering Execution Plan

**Prepared by:** AI Engineer  
**Date:** 2026-03-16  
**Launch Target:** 2026-05-01  
**Scope:** Final MVP (mobile-first, no live payments)

---

## 1) What you should do next (as AI engineering owner)

You already have a strong product brief. Your next step is to run this as a **2-track build**:

1. **Track A: Build core platform (must-have for launch)**
   - Auth, credits, content pipeline, playback, resonance reflection, sharing, admin moderation, RSS.
2. **Track B: Automation and growth systems (parallel)**
   - Monthly AI generation batches, TTS voice pipeline, Instagram automation templates, analytics enrichment.

To hit May 1, 2026, prioritize **launch reliability over feature depth**:
- Keep recommendation engine simple (profile + resonance + popularity).
- Keep moderation human-in-the-loop.
- Keep Instagram automation template-driven (not fully autonomous creative generation).

---

## 2) Recommended tech stack (with reasoning)

### Frontend
- **Next.js (React, App Router) + TypeScript + Tailwind CSS**
  - Mobile-first UI, fast iteration, SEO-friendly public pages, easy API co-location.
- **shadcn/ui + Radix primitives**
  - Accessible sliders, dialogs, forms, tabs with reduced UI engineering risk.
- **PWA-ready setup**
  - Near-native mobile feel without full native app overhead.

### Backend / Data
- **Supabase (Postgres + Auth + Storage + Row Level Security)**
  - Fast MVP setup, low ops overhead, supports auth, storage, SQL analytics.
- **Node.js worker services** (BullMQ + Redis or Supabase scheduled jobs)
  - Reliable async jobs: TTS generation, monthly batches, RSS refresh, social posting queues.
- **Prisma or Drizzle ORM**
  - Type-safe schema management and migrations.

### AI Services
- **LLM Generation:** OpenAI (GPT-4.1/4o family) or Claude
  - Structured prompts for stories/meditations with safety filters.
- **TTS:** ElevenLabs first, OpenAI TTS fallback
  - Multi-voice quality and resilient fallback path.

### Distribution & Integrations
- **RSS:** Native XML endpoint generated from approved audio entries.
- **Instagram/Facebook:** Meta Graph API via queue + scheduler (or Make/Zapier for low-code bridge).
- **Podcast syndication:** Spotify/Apple ingest your RSS; no custom API needed for core publishing.

### Observability & Reliability
- **Sentry** for frontend/backend error monitoring.
- **PostHog or Plausible + custom events** for engagement and funnel analytics.
- **Nightly DB backup snapshot** + weekly export to object storage.

---

## 3) Delivery timeline (realistic to target May 1, 2026)

Given current date (Mar 4) and launch date (May 1), practical plan is **8 weeks** + hardening buffer:

### Week 1
- Finalize schema, architecture, component map, prompt specs, acceptance criteria.
- UX wireframes for mobile-first critical flows.

### Week 2–3
- Build frontend shell: home, onboarding, auth, discovery filters, content page player.
- Implement daily credits + anonymous limits.

### Week 4
- Build resonance reflection module + sharing block + pulse display.
- Build creator submission flow + moderation queue basics.

### Week 5
- TTS pipeline (queue + status + retry + fallback).
- Audio storage strategy + signed URL playback + metadata tagging.

### Week 6
- RSS endpoint + admin schedule tools + analytics dashboard v1.
- DB export + backup automation.

### Week 7
- Instagram automation templates (100–200 starter templates), posting scheduler integration.
- Error-state UX polish (TTS delayed, playback fail, share fallback).

### Week 8
- Mobile QA, performance tuning, security hardening, launch checklist, dry-runs.

### Final 5–7 days
- Content seeding run (initial library), moderation pass, voice QA, launch rehearsal.

**Confidence for May 1 MVP:** feasible if scope discipline is maintained and template automation remains semi-supervised.

---

## 4) Confidence by capability (1–10)

1. Mobile-first frontend UX (reflection, sliders, sharing): **9/10**  
2. Auth, credits, creator flow, moderation queue: **9/10**  
3. TTS integration & monthly batch generation: **8/10**  
4. Audio hosting + metadata watermarking: **8/10**  
5. RSS feed generation: **9/10**  
6. Daily Instagram automation (templates + API): **7/10** (API policies + media pipeline complexity)  
7. Admin dashboard + moderation + analytics: **8/10**  
8. Basic recommendations (profile + resonance + popular): **8/10**  
9. Error handling + user messaging: **9/10**  
10. Backup/export + mobile testing: **8/10**

---

## 5) One-time build cost breakdown (USD)

If you want freelancer quote framing aligned to your original budget, use this model:

1. Mobile-first UX + frontend core: **$900**  
2. Auth, credits, creator form, moderation queue: **$500**  
3. AI generation + TTS pipeline orchestration: **$600**  
4. Audio storage + playback security + watermark metadata: **$300**  
5. RSS feed + podcast-ready metadata: **$250**  
6. Instagram automation + template engine + scheduler: **$550**  
7. Admin dashboard + analytics baseline: **$500**  
8. Recommendation baseline logic: **$200**  
9. Error states + UX fallback flows + QA: **$150**  
10. Backup/export + launch hardening + documentation: **$250**

**Total:** **$4,200** (can be compressed to ~$4,000 by reducing template count or dashboard depth)

---

## 6) Proposed simplified architecture (MVP)

### Core entities
- `users`, `profiles`, `onboarding_responses`
- `content_items` (story/meditation/journey)
- `content_tags`, `growth_areas`, `life_phases`
- `audio_assets` (voice, status, URL, duration, checksum)
- `resonance_reflections` (score, emojis, text, quick actions)
- `credits_ledger` (daily grants, consumption)
- `shares` (channel, click, conversion)
- `submissions` + `moderation_events`
- `instagram_templates` + `scheduled_posts`

### Services
- **API service** (Next.js route handlers)
- **Worker service** (jobs: generate text, TTS, schedule posts, refresh RSS)
- **Admin service layer** (approval, scheduling, analytics queries)

### Recommendation v1
Weighted score =
- Profile growth-area match (40%)
- Life-phase match (20%)
- Community resonance average (20%)
- Freshness/newness (10%)
- Completion rate (10%)

Fallback for sparse data: popularity + recency.

---

## 7) Error recovery flows (required)

### A) TTS delay/failure
- Status badges: `Queued` → `Generating` → `Ready` / `Failed`.
- User message: “Audio generation in progress — try again in a minute.”
- Auto-retry up to 3 times with exponential backoff.
- Fallback: expose text mode immediately if audio unavailable.

### B) Playback issue
- Detect load timeout and surface: “Sorry, audio couldn’t load. Refresh or try later.”
- Provide alternate bitrate/source if available.
- One-tap report issue event to logs.

### C) Share link breaks
- If channel share API fails: copy raw link automatically + toast message.
- Preserve UTM/ref parameters for analytics.
- Keep a short-link fallback generator.

### D) Batch generation partial failure
- Continue processing non-failed items.
- Admin receives failure summary + retry button by batch segment.

---

## 8) Initial 100–200 Instagram template plan (confirmable)

Yes — this is feasible in MVP with a structured template system:
- 20 base visual layouts × 5 theme variants = 100 templates minimum.
- Each template includes:
  - image slot set (5–6 assets)
  - music option set (3 tracks)
  - caption scaffold (hook + teaser + pulse + CTA + hashtags)
- Expandable to 200 by adding life-phase/growth-area variants.
- Monthly review workflow in admin before activation.

---

## 9) High-risk items and suggested simplifications

### Highest risk areas
1. Fully automated social posting quality consistency.
2. TTS cost/performance at high monthly volume.
3. Policy compliance for user-generated content moderation.

### Simplifications for launch safety
- Keep Journeys as free downloads + pricing-interest form only (as planned).
- Limit languages at launch to top 1–2; add more after stability.
- Use curated content seed for first 2,000 rather than full AI auto-publish.
- Keep recommendation engine rule-based before ML personalization.

---

## 10) Practical execution checklist for you (owner)

1. Freeze MVP acceptance criteria (non-negotiables only).
2. Approve stack and integration vendors.
3. Provide legal pages and brand kit immediately.
4. Select voice profiles and approve TTS quality bar.
5. Prepare initial content seeding prompts and moderation rubric.
6. Define monthly operating SOP (moderation, template approval, analytics review).
7. Run launch rehearsal with 7-day simulated automation before public release.

---

## 11) Final recommendation

As AI engineer, you should position this as a **content automation platform with human-guided quality control**, not a fully autonomous publishing bot from day one. That gives you better quality, lower risk, and a realistic path to a stable May 1 launch.

