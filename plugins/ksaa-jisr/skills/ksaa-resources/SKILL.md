---
name: ksaa-resources
description: "يجيب من منصات مجمع الملك سلمان العالمي للغة العربية: كتب المجمع وبحوث مجلاته المحكّمة وروابط قراءتها والنشر فيها (المكتبة الرقمية)، والألعاب اللغوية للمتعلمين، ونتائج النماذج اللغوية على العربية (مؤشر بلسم)، وحال حوسبة العربية (المرصد)، والأسئلة عن المنصات نفسها. استعمله لهذه الأسئلة ولو لم يُذكر المجمع. KSAA books, Arabic LLM benchmarks, NLP report."
argument-hint: "[سؤالك عن موارد المجمع]"
---

# KSAA resources — library, games, BALSAM, Marsad, the platforms

Answer from the KSAA tools, not from memory. Fetch the tools the question needs in **one** tool
search, by bare name (the full name ends with it, e.g. `…library_search`). Reply in the user's
language (Arabic by default) and name the platform each answer comes from.

| Question | Tools | Keep in the answer |
|---|---|---|
| a book, a journal article, an author or a subject; where to read or download it | `library_search` → `library_get_item` | title, author, year, read and download links as returned; for an article its issue and DOI |
| publishing in a KSAA journal, its rules or editors | `library_journals` · `library_contacts` | each email with its own stated purpose; never give one journal's email for another |
| a language game for a learner | `games_list_games` → `games_get_game` · `games_list_leagues` | ask the learner's age or level first if unknown (للصغار، للكبار، للمتخصصين); name, level, link |
| how language models score on Arabic tasks | `balsam_leaderboard` · `balsam_list_categories` · `balsam_list_models` · `balsam_list_tasks` | the metric's name with every score (0–1); no ranking or score the tool did not return |
| the state of Arabic NLP — tools, data, models | `marsad_overview` · `marsad_search_report` · `marsad_get_chapter` | numbers as written, with the edition and its coverage period |
| the platforms themselves — what one is, accounts, APIs | `search_platform_help` · `describe_platform` | the returned text and its source link |
| unsure which platform fits | `list_platforms` | — |

When the library finds nothing, relay `message` and the returned email addresses with their
purposes. Relay any other `found: false` message verbatim; no tool names, JSON or technical
fields in the reply; mark any remark of your own «توضيح من المساعد، وليس من المصدر».
If the tools are missing or need sign-in, say so in one line pointing to `/ksaa-jisr:setup`.
