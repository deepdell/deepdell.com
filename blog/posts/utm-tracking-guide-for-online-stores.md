---
title: "UTM Tracking for Online Stores: A Practical Guide"
description: "Learn how UTM tracking shows which ads, emails and posts bring paying customers to your store, with naming rules and mistakes to avoid."
date: 2026-11-28
category: Analytics
tags: [utm, google analytics, campaigns, tracking]
keywords: [utm tracking, utm parameters, campaign tracking, google analytics]
faq:
  - q: "What is a UTM parameter?"
    a: "A UTM parameter is a short tag added to the end of a link, such as utm_source=newsletter. Analytics tools read it to show which channel, campaign or ad sent each visitor."
  - q: "Do I need UTM tags on every link?"
    a: "Add them to links you place on other platforms, such as ads, emails, social bios and influencer posts. Do not add them to links between pages of your own store, because that breaks the original source."
  - q: "Are UTM tags case sensitive?"
    a: "Yes. Facebook and facebook appear as two different sources in your reports, so use lowercase everywhere."
---
UTM tracking is the simplest way to find out which marketing actually brings customers to your store. Without it, much of your traffic lands in a bucket called "direct" or "unassigned", and you end up guessing where to spend your budget. This guide explains what UTM parameters are, how to name them, and how to keep your reports clean.

## What UTM tracking does

A UTM parameter is a small tag added to a link. When someone clicks, your analytics tool reads the tag and records where the visit came from. There are five tags:

| Tag | What it answers | Example |
|---|---|---|
| utm_source | Where did the click come from? | google, newsletter |
| utm_medium | What type of channel is it? | cpc, email, social |
| utm_campaign | Which campaign was it? | spring_sale |
| utm_term | Which paid keyword? (optional) | running_shoes |
| utm_content | Which ad or link version? (optional) | blue_banner |

The first three are the ones that matter most. Source, medium and campaign together tell you the full story of a visit.

## When to use UTM tags

Use them on every link you place outside your own website:

- Paid ads on Google, Meta, Snapchat and other platforms
- Email and SMS campaigns
- Links in social media bios and posts
- Influencer and affiliate links
- QR codes on packaging, flyers and shop windows

Never add them to links between pages inside your own store. A UTM tag on an internal link starts a new session and replaces the real source, which makes your reports wrong.

## A naming system that stays clean

Most UTM problems come from inconsistent names. Agree on a few simple rules and write them down:

1. **Use lowercase only.** Analytics treats `Facebook` and `facebook` as different sources.
2. **Use underscores instead of spaces.** Write `spring_sale`, not `Spring Sale`.
3. **Keep a fixed list of sources and mediums.** For example `google / cpc`, `facebook / paid_social`, `newsletter / email`.
4. **Put the date or season in campaign names.** `black_friday_2026` is easy to compare next year.
5. **Never put personal data in a tag.** Links are visible, so keep emails and names out of them.

You can build correct links in seconds with our free [UTM link builder](/utm-builder.html), which also offers one-click presets for the common ad platforms.

## How to read the results

In Google Analytics, open the acquisition reports and look at source and medium together. Then compare channels using numbers that matter for the business, not just visits:

- Conversion rate for each source and medium
- Revenue and average order value for each campaign
- Cost per order for paid campaigns

Our [ad performance calculator](/ad-calculator.html) turns ad spend and revenue into ROAS and break-even figures, so you can see whether a campaign really makes money after product costs.

## Common mistakes to avoid

- **Mixing names.** Using `fb`, `facebook` and `Facebook` splits one channel into three rows.
- **Tagging internal links.** This overwrites the true source of the visit.
- **Forgetting redirects.** Some link shorteners and redirects drop the tags. Test every link before you publish.
- **Skipping the medium.** A source without a medium is hard to group into channels.
- **Not documenting the rules.** If three people tag links differently, the data becomes unreliable.

## Make it automatic

Once the naming rules are fixed, the next step is to stop building links by hand. A simple spreadsheet or a small custom utility can generate tagged links for every campaign and push the results into one dashboard. If your reporting is spread over several platforms, our [data and BI services](/data.html) show how a single view of ads, store and email performance can be built around your process.

## Quick checklist

- Decide your list of sources and mediums
- Use lowercase and underscores
- Tag every external link and QR code
- Test links before launch
- Review source and medium reports every month
