# NCA frameworks: versions and status (verified October 2026)

Re-check nca.gov.sa for newer editions before relying on this list.

## In force

### ECC-2:2024 — Essential Cybersecurity Controls (الضوابط الأساسية للأمن السيبراني)
- Replaced ECC-1:2018 in October 2024. 4 domains, 28 subdomains, 108 main controls, 92 subcontrols.
- Scope: government agencies and their affiliated companies (inside and outside KSA), and private entities owning, operating or hosting CNI. Others are encouraged to use it.
- Domain 5 (industrial control systems) moved to OTCC.
- Data privacy and data localization controls moved out of ECC to NDMO (SDAIA). Refer to NDMO / PDPL for those.
- Cryptography control 2-8-3 now requires, at minimum, the NCA National Cryptographic Standards.
- Official PDF (EN): https://cdn.nca.gov.sa/api/files/public/upload/86e09090-44e4-481f-bc28-355673607654_ECC--2024-EN.pdf

### NCNICC-1:2025 — Non-CNI Private Sector Entities Cybersecurity Controls (ضوابط الأمن السيبراني لجهات القطاع الخاص غير المصنفة بنية تحتية حساسة)
- Adopted by NCA on 28 December 2025. Mandatory reference for private-sector entities that are not CNI.
- 3 components: Governance (14 controls), Defense (45 controls, 15 sub-components incl. IAM, data, cryptography, backup, vulnerability, pen-test, logging/SOC, incident, web), Third-Party & Cloud (6 controls). 65 main controls, 47 subcontrols.
- Class A (large: >250 full-time employees or >SAR 200M revenue): all 65 mandatory.
- Class B (SME: 6–249 employees or SAR 3M–200M revenue): 26 Defense controls mandatory, 39 recommended.
- Control codes reported by secondary sources (verify against the official text before citing in audits):
  - 1-1-1 independent cybersecurity unit separate from IT; 1-1-2 Saudi nationals in cyber leadership roles
  - 2-2-1-2 MFA for remote access including external applications; 2-2-1-4 privileged access management
  - 2-4-1-2 email domain documented through NCA's Haseen platform with SPF, DKIM, DMARC
  - 2-9-1-2 periodic backup restoration testing
  - 2-13-1-2 report incidents to NCA; 2-13-1-3 share cybersecurity information with NCA
  - 3-2-1-2 logical separation from other cloud tenants
  - NCA-licensed managed SOC: mandatory for Class A, recommended for Class B

### NCS-2:2025 — National Cryptographic Standards (المعايير الوطنية للتشفير)
- **Published and in force — supersedes NCS-1:2020.** Verified on nca.gov.sa in October 2026; the final
  Arabic PDF is on the NCA CDN. Earlier editions of this file listed it as a pending draft — it is not.
- Updates over NCS-1:2020: post-quantum algorithms, random number generators (PRNG), and
  quantum key distribution; refreshed cryptographic designs and primitives.
- Two strength levels: MODERATE and ADVANCED. Choose by data sensitivity and risk assessment.
- Covers accepted symmetric/asymmetric primitives and schemes, common cryptographic application
  protocols, PKI and Key Lifecycle Management (KLM).
- https://nca.gov.sa/en/regulatory-documents/frameworks-and-standard-list/ncs/
- Cite NCS-2:2025 in audits. Only fall back to NCS-1:2020 if the entity is still formally bound to it.

### Other NCA frameworks to add when relevant
- CCC (Cloud Cybersecurity Controls): cloud providers and entities using cloud.
- CSCC (Critical Systems Cybersecurity Controls): systems classified as critical.
- DCC-1:2022 (Data Cybersecurity Controls): data handling across lifecycle.
- OTCC-1:2022: operational technology / industrial systems.
- National Cybersecurity Risk Management Framework (released July 2025).
- NECC-1:2026 (National Events Cybersecurity Controls): applies to systems supporting national events.
- Sector regulators may add requirements (e.g. SAMA Cyber Security Framework for financial sector).

## Drafts / pending (track, do not treat as binding yet)
- AI Cybersecurity Guidelines (إرشادات الأمن السيبراني للذكاء الاصطناعي): public consultation announced July 2026. If the app uses AI/LLMs, check for the final version.
- Classification of cybersecurity violations and penalties: consultation June 2026.

## NCA templates relevant to developers (free, from nca.gov.sa)
- Secure Coding Standard template (نموذج معيار التطوير الآمن للتطبيقات)
- Web Application Protection Policy and Standard templates (نموذج سياسة/معيار حماية تطبيقات الويب)
Their technical content is summarized in `dev-checklist.md`.
