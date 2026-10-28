---
name: arabic-word
description: "يجيب عن أسئلة الكلمة العربية الفصيحة من معجم الرياض (منصة سوار) ومدونات فلك: المعنى والجذر والوزن والقسم الكلامي والتصريف والمشتقات والمرادف والضد والأمثلة والمقابل الإنجليزي والنطق وشواهد الاستعمال والمتلازمات والشيوع. استعمله كلما سُئل عن كلمة عربية ولو لم يُذكر المعجم، قبل الإجابة من معرفتك؛ لا عند مجرد الكتابة أو الترجمة بالعربية. Arabic word meaning, root, usage."
argument-hint: "[كلمة أو سؤال عنها]"
---

# Arabic word lookup — معجم الرياض and Falak corpora

Answer from the KSAA tools, not from memory. Reply in the user's language (Arabic by default).

## Load the tools once

The tools are deferred. Fetch every tool the question needs in **one** tool search, by bare
name: whatever prefix this install gives the server, the full name ends with the bare name
(`…siwar_get_word_meaning`).

| Question | Tool |
|---|---|
| what a word means | `siwar_get_word_meaning` |
| everything about a word | `siwar_get_full_entry` (pass only the `sections` asked for) |
| root · pattern · part of speech · forms | `siwar_get_word_root` · `siwar_get_word_pattern` · `siwar_get_word_pos` · `siwar_get_word_forms` |
| synonyms · antonyms · other relations | `siwar_get_synonyms` · `siwar_get_antonyms` · `siwar_get_sense_relations` |
| examples · English equivalents · pronunciation | `siwar_get_word_examples` · `siwar_get_word_translations` · `siwar_get_word_audio` |
| words from a root · derivatives | `siwar_search_by_root` · `siwar_get_derivatives` |
| difference between two words | `siwar_compare_words` |
| which entry is meant | `siwar_resolve_lemma` |
| how the word is actually used, collocations, frequency | read `references/corpus.md` first |

## Answering

- An unvocalized word may have several entries (عين → عَيْن، عَيَّنَ). Present the returned
  entry, list its `homographs` alternatives, and re-query with the vocalized form the user means.
- Give every returned sense on its own numbered line. Offer «المزيد من المعاني» only when the
  result says more exist.
- Quote examples verbatim. Never write a sense, example or root yourself; a sense without an
  example is shown without one.
- Name the source: «معجم الرياض للغة العربية المعاصرة», or the corpus by name.
- `found: false` → relay `message` verbatim. Dialect words are outside the dictionary; say so
  rather than answering from elsewhere.
- No tool names, JSON or technical fields in the reply. Mark any remark of your own:
  «توضيح من المساعد، وليس من المصدر». Put pronunciation links at the end.

## If the tools are missing or need sign-in

Say so in one line — «أدوات منصات المجمع غير متصلة؛ شغّل /ksaa-jisr:setup» — and answer from
general knowledge only if the user asks, marked as such.
