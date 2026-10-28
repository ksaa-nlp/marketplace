---
name: arabic-usage
description: "يجيب عن صحة الاستعمال العربي من خزانة «المستشار اللغوي» بنصها: أيهما أصح، هل يجوز، الإملاء والهمزات، النحو والصرف، الأسلوب والأخطاء الشائعة؛ ويعطي المختصر العربي المعتمد لمصطلح أو اسم جهة، أو يفكّ مختصرًا، من سجل «اختصار». استعمله لهذه الأسئلة ولو لم تُذكر المنصة، قبل الإجابة من معرفتك. Is this Arabic correct? Arabic abbreviations."
argument-hint: "[سؤال الاستعمال أو المصطلح أو المختصر]"
---

# Arabic usage and abbreviations — المستشار اللغوي and «اختصار»

Answer from the KSAA tools, not from memory. Fetch the tools the question needs in **one** tool
search, by bare name (the full name ends with it, e.g. `…almustashar_search_bank`). Reply in the
user's language (Arabic by default).

## Is it correct? (أيهما أصح، هل يجوز، إملاء، همزة، نحو، صرف، أسلوب)

1. Call `almustashar_search_bank` with the user's question as written.
2. Show each matching consultation the way `references/consultations.md` lists. Quote question
   and answer verbatim; never summarise, correct or extend the consultant's answer.
3. No exact or close match: say no identical consultation exists, show the related ones, and give
   the returned new-question link. Do not answer in the consultant's place. You may add dictionary
   evidence (`siwar_` meaning, `falak_` usage), attributed, and mark any remark of your own
   «توضيح من المساعد، وليس من المصدر».
4. A consultation by number (٤٩٠٠، @4900، a `/bank/4900` link) → `almustashar_get_consultation`.
   "Who answers these?" → `almustashar_consultants`.

## Abbreviations (ما مختصر…؟ ماذا تعني…؟ كيف نختصر اسم جهتنا؟)

- Term or organisation name → its abbreviation: `acronymer_search_registry`.
- Abbreviation → full name, Arabic or Latin, with or without «ال»: `acronymer_expand`.
- The method, the formation patterns, or a standard by number (٤-٣-١): `acronymer_guide`.
- State each form's status exactly as returned (معتمدة، قيد الفحص، مقترحة، بديل غير معتمد).
  Never present a proposal as approved; lead with the approved form and point variants to it.
- Never coin an abbreviation. If the registry has none, relay `message` with its links to the
  tool's own generator.

## Always

Relay `found: false` messages verbatim; no tool names, JSON or technical fields in the reply.
If the tools are missing or need sign-in, say so in one line pointing to `/ksaa-jisr:setup`.
