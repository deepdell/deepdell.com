---
name: digital-card
description: Create a private DEEPDELL digital card (visiting card with QR code) for an executive, referral partner or affiliate partner. Use when the user asks for a digital card, visiting card, business card or partner card for a person.
---
# DEEPDELL private digital cards

Cards are PRIVATE. Never commit them, never put them in this repository, never publish or link them from deepdell.com. The generator refuses to write inside the repo. Hand the files to the user with SendUserFile and nothing else.

## 1. Ask for the details first (never invent them)
Ask for anything missing before generating. Use AskUserQuestion for the choices, plain questions for the free text.

EVERY card is bilingual: English plus ONE second language, Arabic or Malay. Ask which one (default suggestion: Arabic for Gulf and Middle East contacts, Malay for Malaysia). English is the front, the second language is the back with the QR code.

Required:
- Second language: Arabic or Malay
- Full name; for Arabic also the name written in Arabic (ask, do not transliterate it yourself)
- Job title in English; plus the title in Arabic (for Arabic) or in Malay (for Malay). Offer a translation and let the user confirm it
- Role: executive, referral partner, or affiliate partner
- Mobile number with country code (this is also used for WhatsApp unless another is given)
- Email address

Ask about, but optional:
- City and country
- Separate WhatsApp number
- LinkedIn profile link
- Partner or referral code (referral and affiliate partners)
- What the QR code opens: saves contact details (default, works offline), opens deepdell.com, or opens a tracked referral link (needs a code)

Do not ask for anything sensitive (ID numbers, bank details, home address). Use only what the person gave you.

## 2. Generate
```
pip install segno      # first time only
python3 tools/digital_card.py --name "..." --title "..." --role executive|referral|affiliate \
  --phone "+971 ..." --email ... [--city ...] [--whatsapp ...] [--linkedin URL] [--code CODE] \
  --second ar|ms [--name-ar ... --title-ar ... | --title-ms ...] [--qr contact|website|referral]
```
Output goes to `~/deepdell-private-cards/<name>/`: `card-front.png` (English), `card-back.png` (Arabic or Malay, with the QR), `card.pdf` (print size 3.5 x 2 in), `card.html` (mobile card with Save contact, Call, Email, WhatsApp buttons, marked noindex), `contact.vcf`, `qr.svg`, `qr.png`.

## 3. Check, then deliver
- Look at card-front.png and card-back.png. Confirm the name, title and numbers match what the user gave.
- Decode the QR (jsQR) and confirm it matches the details.
- Send the files with SendUserFile: front and back PNG, the PDF, card.html and contact.vcf.
- Remind the user: share the card only with the person it is for; the QR holds their phone and email in plain form; the tracked referral link only counts visits if the website records the `ref` parameter, which it does not do yet.
- Never create a git commit for card files.
