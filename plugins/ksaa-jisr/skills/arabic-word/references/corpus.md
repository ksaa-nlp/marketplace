# Usage evidence from the Falak corpora

Read this only for "how is this word actually used", collocation or frequency questions.
Meaning questions belong to the `siwar_` tools, not Falak.

1. If the user named no corpus, call `falak_list_corpora` and choose by its descriptions.
   Never invent a corpus ID.
2. Pick the tool:

   | Need | Tool |
   |---|---|
   | the word in context (KWIC) | `falak_concordance` |
   | words that co-occur with it | `falak_collocations` |
   | recurring word sequences | `falak_ngrams` |
   | most frequent words of a corpus | `falak_most_frequent` |
   | published frequency lists | `falak_frequency_lists` |
   | a corpus's size and makeup | `falak_get_corpus` · `falak_corpus_statistics` |
   | example sentences | `falak_search_sentences` |
   | stop words | `falak_stop_words` |

3. Quote context lines verbatim with the corpus name; never paraphrase them.
4. `reason: not_supported` means this corpus does not offer that analysis — not that the word is
   absent. Say so, and offer another corpus.
5. Collocations on the largest corpora can exceed the upstream timeout; if that happens, retry
   on a smaller corpus.
