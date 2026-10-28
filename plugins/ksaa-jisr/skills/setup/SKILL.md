---
name: setup
description: "يتحقق من اتصال Claude بخادم «جسر المجمع» وتسجيل الدخول، ويعرض المنصات المتاحة."
disable-model-invocation: true
---

# Connect «جسر المجمع»

Reply in Arabic.

1. Fetch and call `list_platforms` (tool search by that name).
2. If it answers: list the platforms and what each one answers, from the result, then one line:
   «جاهز. اسأل عن كلمة عربية، أو صحة استعمال، أو مختصر، أو موارد المجمع.»
3. If the tool is missing or asks for sign-in:
   - Claude Code: «شغّل `/mcp` واختر الخادم `plugin:ksaa-jisr:ksaa`، ثم سجّل الدخول بحساب Google. التسجيل مجاني.»
   - claude.ai or Cowork: «افتح تبويب Connectors في إعدادات الإضافة، واربط "جسر المجمع"، ثم سجّل الدخول بحساب Google.»
4. If the server does not respond: «الخادم https://mcp.arai.center غير متاح الآن؛ أعد المحاولة لاحقًا.»
