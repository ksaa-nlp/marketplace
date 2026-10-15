"use client";
import { useCallback, useEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";
import {
  ALargeSmall,
  AlignRight,
  Baseline,
  Brain,
  Contrast,
  Droplet,
  Droplets,
  Eye,
  EyeOff,
  Focus,
  ImageOff,
  Keyboard,
  Link2,
  MousePointer2,
  MousePointerClick,
  Move,
  PauseCircle,
  RotateCcw,
  Ruler,
  ScanLine,
  Sparkles,
  Speech,
  Type,
  Volume2,
  X,
  ZoomIn,
} from "lucide-react";

function AccessibilityBadge({ className }: { className?: string }) {
  return (
    <span
      className={`grid place-items-center rounded-full bg-primary text-primary-foreground ${className ?? ""}`}
    >
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" className="h-[70%] w-[70%]">
        <circle cx="12" cy="12" r="10.5" />
        <circle cx="12" cy="6.3" r="1.4" fill="currentColor" stroke="none" />
        <path d="M6.5 9.2 12 10.2l5.5-1" />
        <path d="M12 10.2v4.3" />
        <path d="m9.3 18.6 2.7-4.1 2.7 4.1" />
      </svg>
    </span>
  );
}

type BoolKey =
  | "highContrast"
  | "smartContrast"
  | "monochrome"
  | "lowSaturation"
  | "highSaturation"
  | "readableFont"
  | "dyslexiaFont"
  | "highlightTitles"
  | "underlineLinks"
  | "justifyText"
  | "bigCursor"
  | "bigCursorLight"
  | "readingGuide"
  | "readingMask"
  | "hideImages"
  | "muteSounds"
  | "reduceMotion"
  | "highlightHover"
  | "highlightFocus"
  | "textToSpeech";

interface A11ySettings extends Record<BoolKey, boolean> {
  fontScale: number;
  letterSpacing: number;
  wordSpacing: number;
  lineHeight: number;
  colorFilter: ColorFilter;
  darkMode: boolean;
  pageZoom: number;
  profileId: string | null;
}

type ColorFilter = "none" | "protan" | "deutan" | "tritan";

const DEFAULTS: A11ySettings = {
  fontScale: 100,
  letterSpacing: 0,
  wordSpacing: 0,
  lineHeight: 0,
  colorFilter: "none",
  darkMode: false,
  pageZoom: 100,
  profileId: null,
  highContrast: false,
  smartContrast: false,
  monochrome: false,
  lowSaturation: false,
  highSaturation: false,
  readableFont: false,
  dyslexiaFont: false,
  highlightTitles: false,
  underlineLinks: false,
  justifyText: false,
  bigCursor: false,
  bigCursorLight: false,
  readingGuide: false,
  readingMask: false,
  hideImages: false,
  muteSounds: false,
  reduceMotion: false,
  highlightHover: false,
  highlightFocus: false,
  textToSpeech: false,
};

const CLASS_MAP: Partial<Record<BoolKey, string>> = {
  highContrast: "a11y-contrast",
  smartContrast: "a11y-smart-contrast",
  monochrome: "a11y-monochrome",
  lowSaturation: "a11y-low-saturation",
  highSaturation: "a11y-high-saturation",
  readableFont: "a11y-readable-font",
  dyslexiaFont: "a11y-dyslexia-font",
  highlightTitles: "a11y-highlight-titles",
  underlineLinks: "a11y-underline-links",
  justifyText: "a11y-justify",
  bigCursor: "a11y-big-cursor",
  bigCursorLight: "a11y-big-cursor-light",
  hideImages: "a11y-hide-images",
  reduceMotion: "a11y-reduce-motion",
  highlightHover: "a11y-highlight-hover",
  highlightFocus: "a11y-highlight-focus",
};

const STORAGE_KEY = "a11y-settings-v2";
const POS_KEY = "a11y-launcher-pos";

const PROFILES: {
  id: string;
  label: string;
  hint: string;
  icon: React.ReactNode;
  patch: Partial<A11ySettings>;
}[] = [
  {
    id: "epilepsy",
    label: "تقليل الحركة والألوان",
    hint: "يوقف الحركات ويخفّف تشبّع الألوان",
    icon: <Brain className="h-4 w-4" aria-hidden="true" />,
    patch: { reduceMotion: true, lowSaturation: true },
  },
  {
    id: "vision",
    label: "ضعف الرؤية",
    hint: "تحسين مظهر المواقع",
    icon: <Eye className="h-4 w-4" aria-hidden="true" />,
    patch: { fontScale: 130, highContrast: true, highlightTitles: true, underlineLinks: true },
  },
  {
    id: "cognitive",
    label: "تركيز على المحتوى",
    hint: "يساعد على التركيز على المحتوى المعيّن",
    icon: <Sparkles className="h-4 w-4" aria-hidden="true" />,
    patch: { readingMask: true, readableFont: true, reduceMotion: true },
  },
  {
    id: "motor",
    label: "تصفح بلوحة المفاتيح",
    hint: "يسهّل تصفح الموقع باستخدام لوحة المفاتيح",
    icon: <Keyboard className="h-4 w-4" aria-hidden="true" />,
    patch: { highlightFocus: true, bigCursor: true, highlightHover: true },
  },
  {
    id: "colorblind",
    label: "تجربة فلاتر الألوان",
    hint: "فلاتر بصرية تجريبية — لا تعني تصحيحًا طبيًا",
    icon: <Droplet className="h-4 w-4" aria-hidden="true" />,
    patch: { colorFilter: "deutan", underlineLinks: true },
  },
  {
    id: "dyslexia",
    label: "تباعد مريح للنص",
    hint: "خط بديل وتباعد أوسع للحروف والأسطر",
    icon: <Type className="h-4 w-4" aria-hidden="true" />,
    patch: { dyslexiaFont: true, lineHeight: 2, letterSpacing: 1 },
  },
  {
    id: "adhd",
    label: "دليل القراءة وتقليل الحركة (ADHD)",
    hint: "دليل واضح يتبع المؤشر أو التركيز؛ أغلق اللوحة لمعاينته",
    icon: <Focus className="h-4 w-4" aria-hidden="true" />,
    patch: { readingGuide: true, reduceMotion: true, hideImages: false },
  },
  {
    id: "blind",
    label: "قراءة صوتية وتكبير",
    hint: "قراءة النص المحدد بصوت مسموع مع تكبير الخط — لا يغني عن قارئ الشاشة",
    icon: <Speech className="h-4 w-4" aria-hidden="true" />,
    patch: { textToSpeech: true, fontScale: 120 },
  },
];

/** Safe line-height range: below MIN, Arabic diacritics and lines start to overlap. */
const MIN_LINE_HEIGHT = 1.5;
const MAX_LINE_HEIGHT = 3;
const DRAG_THRESHOLD = 6;

/** Colour adjustments that each set a `filter`; only one may be active at a time. */
const EXCLUSIVE_COLOR: (keyof A11ySettings)[] = [
  "highContrast",
  "smartContrast",
  "monochrome",
  "lowSaturation",
  "highSaturation",
  "darkMode",
];

/** Enforce one colour mode at a time and a safe line-height. Exported for tests. */
export function normalizeSettings(prev: A11ySettings, patch: Partial<A11ySettings>): A11ySettings {
  const next = { ...DEFAULTS, ...prev };
  for (const key of Object.keys(DEFAULTS) as (keyof A11ySettings)[]) {
    if (typeof DEFAULTS[key] === "boolean" && typeof patch[key] === "boolean") {
      (next[key] as boolean) = patch[key] as boolean;
    }
  }
  const number = (key: "fontScale" | "pageZoom" | "letterSpacing" | "wordSpacing" | "lineHeight", min: number, max: number) => {
    const value = patch[key];
    if (typeof value === "number" && Number.isFinite(value)) next[key] = Math.min(max, Math.max(min, value));
  };
  number("fontScale", 80, 180);
  number("pageZoom", 100, 200);
  number("letterSpacing", 0, 6);
  number("wordSpacing", 0, 16);
  number("lineHeight", 0, MAX_LINE_HEIGHT);
  if (["none", "protan", "deutan", "tritan"].includes(String(patch.colorFilter))) next.colorFilter = patch.colorFilter!;
  if (patch.profileId === null || PROFILES.some((p) => p.id === patch.profileId)) next.profileId = patch.profileId!;
  const filterOn = patch.colorFilter !== undefined && patch.colorFilter !== "none" && next.colorFilter === patch.colorFilter;
  const selected = EXCLUSIVE_COLOR.find((key) => patch[key] === true);
  if (filterOn) {
    for (const key of EXCLUSIVE_COLOR) (next[key] as boolean) = false;
  } else if (selected) {
    for (const key of EXCLUSIVE_COLOR) (next[key] as boolean) = key === selected;
    next.colorFilter = "none";
  }
  if (next.lineHeight) next.lineHeight = Math.max(MIN_LINE_HEIGHT, next.lineHeight);
  return next;
}

/** Coordinates are CSS viewport pixels; use the actual launcher dimensions. */
export function clampLauncherPosition(x: number, y: number, width: number, height: number, size = 56) {
  return {
    x: Math.min(Math.max(8, Number.isFinite(x) ? x : 8), Math.max(8, width - size - 8)),
    y: Math.min(Math.max(8, Number.isFinite(y) ? y : 8), Math.max(8, height - size - 8)),
  };
}

/** Helpers consume complete colours even when the site's tokens are HSL components. */
function syncHelperColors() {
  const root = document.documentElement;
  const computed = getComputedStyle(root);
  for (const [name, fallback] of Object.entries({ primary: "Highlight", foreground: "CanvasText", card: "Canvas", border: "ButtonText", "primary-foreground": "HighlightText" })) {
    const raw = computed.getPropertyValue(`--${name}`).trim();
    const full = window.CSS?.supports("color", raw) ? raw : window.CSS?.supports("color", `hsl(${raw})`) ? `hsl(${raw})` : fallback;
    root.style.setProperty(`--a11y-${name}`, full);
  }
}

function applySettings(s: A11ySettings, prev?: A11ySettings) {
  const root = document.documentElement;
  root.style.fontSize = `${s.fontScale}%`;
  root.style.setProperty("--a11y-letter-spacing", `${s.letterSpacing}px`);
  root.style.setProperty("--a11y-word-spacing", `${s.wordSpacing}px`);
  root.style.setProperty("--a11y-line-height", s.lineHeight ? String(s.lineHeight) : "");
  root.classList.toggle(
    "a11y-spacing",
    s.letterSpacing > 0 || s.wordSpacing > 0 || s.lineHeight > 0,
  );
  for (const [key, cls] of Object.entries(CLASS_MAP)) {
    root.classList.toggle(cls, Boolean(s[key as BoolKey]));
  }
  const filters: string[] = [];
  if (s.highContrast) filters.push("contrast(1.25)");
  if (s.smartContrast) filters.push("contrast(1.15) brightness(1.05)");
  if (s.monochrome) filters.push("grayscale(1)");
  if (s.lowSaturation) filters.push("saturate(0.5)");
  if (s.highSaturation) filters.push("saturate(1.7)");
  if (s.darkMode) filters.push("invert(0.92) hue-rotate(180deg)");
  if (s.colorFilter !== "none") filters.push(`url(#a11y-cb-${s.colorFilter})`);
  root.style.setProperty("--a11y-content-filter", filters.join(" "));
  root.classList.toggle("a11y-filter-active", filters.length > 0);
  root.classList.toggle("a11y-dark", s.darkMode);
  syncHelperColors();
  document.body.style.zoom = s.pageZoom === 100 ? "" : String(s.pageZoom / 100);
  // Only touch media when the mute option itself changed (or on first load with mute on),
  // so unrelated changes never override a visitor's own mute choice.
  const muteChanged = prev ? prev.muteSounds !== s.muteSounds : s.muteSounds;
  if (muteChanged) {
    document.querySelectorAll("video, audio").forEach((el) => {
      (el as HTMLMediaElement).muted = s.muteSounds;
    });
  }
}

/** Floating, draggable accessibility launcher with a full right-side settings drawer. */
export function AccessibilityToolbar() {
  const [open, setOpen] = useState(false);
  const [hidden, setHidden] = useState(false);
  const [settings, setSettings] = useState<A11ySettings>(DEFAULTS);
  const activeProfile = settings.profileId;
  const [portal, setPortal] = useState<HTMLDivElement | null>(null);
  const [notice, setNotice] = useState("");
  const [speechKind, setSpeechKind] = useState<"page" | "selection" | null>(null);
  const [pos, setPos] = useState<{ x: number; y: number } | null>(null);
  const [reader, setReader] = useState<"idle" | "playing" | "paused">("idle");
  const [rate, setRate] = useState(1);
  const utteranceRef = useRef<SpeechSynthesisUtterance | null>(null);
  const speechKindRef = useRef<"page" | "selection" | null>(null);
  const lastSelectionRef = useRef<{ text: string; anchor: Node | null; focus: Node | null; start: number; end: number } | null>(null);
  const openRef = useRef(open);
  openRef.current = open;
  const rateRef = useRef(rate);
  rateRef.current = rate;
  const readerRef = useRef<{ blocks: HTMLElement[]; i: number } | null>(null);
  const dragRef = useRef<{ dx: number; dy: number; sx: number; sy: number; moved: boolean } | null>(
    null,
  );
  const suppressClickRef = useRef(false);
  const launcherRef = useRef<HTMLButtonElement>(null);
  const showRef = useRef<HTMLButtonElement>(null);
  const closeRef = useRef<HTMLButtonElement>(null);
  const stopRef = useRef<HTMLButtonElement>(null);
  const panelRef = useRef<HTMLDivElement>(null);
  const reduceMotionRef = useRef(false);
  reduceMotionRef.current = settings.reduceMotion;

  useEffect(() => {
    const layer = document.createElement("div");
    layer.dataset.a11yLayer = "true";
    layer.className = "a11y-layer";
    document.body.append(layer);
    setPortal(layer);
    syncHelperColors();
    return () => layer.remove();
  }, []);

  useEffect(() => {
    if (portal) portal.style.zoom = String(100 / settings.pageZoom);
  }, [portal, settings.pageZoom]);

  useEffect(() => {
    try {
      const raw = window.localStorage.getItem(STORAGE_KEY);
      if (raw) {
        const parsed = normalizeSettings(DEFAULTS, JSON.parse(raw) as Partial<A11ySettings>);
        setSettings(parsed);
        applySettings(parsed);
      }
      const rawPos = window.localStorage.getItem(POS_KEY);
      if (rawPos) {
        const saved = JSON.parse(rawPos) as { x: number; y: number };
        setPos(clampLauncherPosition(saved.x, saved.y, window.innerWidth, window.innerHeight, Math.max(44, 56 * (settings.fontScale / 100))));
      }
    } catch {
      /* ignore malformed storage */
    }
  }, []);

  const update = useCallback((patch: Partial<A11ySettings>) => {
    setSettings((prev) => {
      const next = normalizeSettings(prev, { ...patch, profileId: patch.profileId ?? null });
      applySettings(next, prev);
      try {
        window.localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
      } catch {
        /* storage may be unavailable */
      }
      return next;
    });
  }, []);

  // Reading helpers work with a mouse, touch, text selection and keyboard focus.
  useEffect(() => {
    if (!settings.readingGuide && !settings.readingMask) return;
    const root = document.documentElement;
    const point = (y: number) => root.style.setProperty("--a11y-pointer-y", `${Math.max(0, Math.min(window.innerHeight, y))}px`);
    point(window.innerHeight / 2);
    const onMove = (e: PointerEvent) => {
      if (!(e.target as Element | null)?.closest?.("[data-a11y-layer]")) point(e.clientY);
    };
    const onFocus = (e: FocusEvent) => {
      const el = e.target as HTMLElement;
      if (!el?.getBoundingClientRect || el.closest("[data-a11y-layer]")) return;
      const r = el.getBoundingClientRect();
      point(r.top + r.height / 2);
    };
    const onSelection = () => {
      if (openRef.current) return;
      const selection = window.getSelection();
      if (!selection?.rangeCount) return;
      const el = selection.anchorNode?.parentElement;
      if (el?.closest("[data-a11y-layer]")) return;
      const r = selection.getRangeAt(0).getBoundingClientRect();
      if (r.height) point(r.top + r.height / 2);
    };
    window.addEventListener("pointermove", onMove);
    window.addEventListener("pointerdown", onMove);
    document.addEventListener("focusin", onFocus);
    document.addEventListener("selectionchange", onSelection);
    return () => {
      window.removeEventListener("pointermove", onMove);
      window.removeEventListener("pointerdown", onMove);
      document.removeEventListener("focusin", onFocus);
      document.removeEventListener("selectionchange", onSelection);
    };
  }, [settings.readingGuide, settings.readingMask]);

  const clearReadMark = () => document.querySelectorAll(".a11y-reading-now").forEach((el) => el.classList.remove("a11y-reading-now"));
  const stopReader = useCallback(() => {
    if (openRef.current && document.activeElement === stopRef.current) closeRef.current?.focus();
    utteranceRef.current = null;
    readerRef.current = null;
    speechKindRef.current = null;
    window.speechSynthesis?.cancel();
    clearReadMark();
    setSpeechKind(null);
    setReader("idle");
  }, []);
  const prepareUtterance = (text: string, r: number) => {
    const utterance = new SpeechSynthesisUtterance(text);
    const voice = window.speechSynthesis.getVoices().find((v) => v.lang.toLowerCase().startsWith("ar"));
    if (voice) utterance.voice = voice;
    utterance.lang = voice?.lang ?? "ar-SA";
    utterance.rate = r;
    return utterance;
  };

  // React only to a new selection; ordinary Tab/keyup never restarts speech.
  useEffect(() => {
    if (!settings.textToSpeech || !window.speechSynthesis) return;
    let timer: ReturnType<typeof setTimeout> | undefined;
    let selecting = false;
    const readSelection = () => {
      if (openRef.current || selecting) return;
      const selection = window.getSelection();
      const text = selection?.toString().trim() ?? "";
      if (!selection || !text) { lastSelectionRef.current = null; return; }
      const el = selection.anchorNode?.parentElement;
      if (el?.closest("[data-a11y-layer], input, textarea, [contenteditable=true]")) return;
      const next = { text, anchor: selection.anchorNode, focus: selection.focusNode, start: selection.anchorOffset, end: selection.focusOffset };
      const last = lastSelectionRef.current;
      if (last && Object.keys(next).every((k) => next[k as keyof typeof next] === last[k as keyof typeof last])) return;
      lastSelectionRef.current = next;
      stopReader();
      const u = prepareUtterance(text, rateRef.current);
      utteranceRef.current = u;
      speechKindRef.current = "selection";
      setSpeechKind("selection");
      setReader("playing");
      const finish = () => {
        if (utteranceRef.current !== u) return;
        utteranceRef.current = null;
        speechKindRef.current = null;
        setSpeechKind(null);
        setReader("idle");
      };
      u.onend = finish;
      u.onerror = () => { finish(); setNotice("تعذر تشغيل القراءة الصوتية في هذا المتصفح."); };
      window.speechSynthesis.speak(u);
    };
    const schedule = () => { clearTimeout(timer); timer = setTimeout(readSelection, 180); };
    const down = () => { selecting = true; clearTimeout(timer); };
    const up = () => { selecting = false; schedule(); };
    document.addEventListener("selectionchange", schedule);
    document.addEventListener("pointerdown", down);
    document.addEventListener("pointerup", up);
    return () => {
      clearTimeout(timer);
      document.removeEventListener("selectionchange", schedule);
      document.removeEventListener("pointerdown", down);
      document.removeEventListener("pointerup", up);
      if (speechKindRef.current === "selection") stopReader();
      lastSelectionRef.current = null;
    };
  }, [settings.textToSpeech, stopReader]);

  const speakBlock = useCallback((r: number) => {
    const st = readerRef.current;
    if (!st) return;
    clearReadMark();
    const el = st.blocks[st.i];
    if (!el) { readerRef.current = null; utteranceRef.current = null; speechKindRef.current = null; setSpeechKind(null); setReader("idle"); return; }
    el.classList.add("a11y-reading-now");
    const reduce = reduceMotionRef.current || window.matchMedia?.("(prefers-reduced-motion: reduce)").matches;
    el.scrollIntoView({ block: "center", behavior: reduce ? "auto" : "smooth" });
    const u = prepareUtterance(el.innerText, r);
    utteranceRef.current = u;
    u.onend = () => {
      if (readerRef.current !== st || utteranceRef.current !== u) return;
      st.i += 1;
      speakBlock(r);
    };
    u.onerror = () => {
      if (utteranceRef.current !== u) return;
      stopReader();
      setNotice("تعذر تشغيل القراءة الصوتية في هذا المتصفح.");
    };
    window.speechSynthesis.speak(u);
  }, [stopReader]);
  const startReader = () => {
    if (!window.speechSynthesis) { setNotice("القراءة الصوتية غير متاحة في هذا المتصفح."); return; }
    if (reader === "paused") { window.speechSynthesis.resume(); setReader("playing"); return; }
    stopReader();
    const scope = document.querySelector("main") ?? document.body;
    const blocks = Array.from(scope.querySelectorAll<HTMLElement>("h1,h2,h3,h4,p,li,blockquote,td")).filter((el) => el.innerText.trim() && !el.closest("[data-a11y-layer]") && !el.querySelector("p,li"));
    readerRef.current = { blocks, i: 0 };
    speechKindRef.current = "page";
    setSpeechKind("page");
    setReader("playing");
    speakBlock(rate);
  };
  const pauseReader = () => { window.speechSynthesis?.pause(); setReader("paused"); };
  useEffect(() => () => { utteranceRef.current = null; readerRef.current = null; window.speechSynthesis?.cancel(); }, []);

  const reset = () => {
    stopReader();
    window.speechSynthesis?.cancel();
    setSettings((prev) => {
      applySettings(DEFAULTS, prev);
      return DEFAULTS;
    });
    setNotice("");
    lastSelectionRef.current = null;
    try {
      window.localStorage.removeItem(STORAGE_KEY);
    } catch {
      /* ignore */
    }
  };

  const applyProfile = (id: string, patch: Partial<A11ySettings>) => {
    if (activeProfile === id) {
      reset();
      return;
    }
    setNotice(id === "adhd" ? "تم تفعيل دليل القراءة وتقليل الحركة. أغلق اللوحة وحرّك المؤشر أو انتقل بـTab لمعاينة الدليل." : "تم تطبيق الإعدادات؛ يمكنك تعديلها أو إعادة ضبطها.");
    update({ ...DEFAULTS, ...patch, profileId: id });
  };

  // ---- Panel open/close + focus management ----
  const closePanel = useCallback((hide = false) => {
    setOpen(false);
    if (hide) setHidden(true);
  }, []);

  // After the panel closes, return focus to the control that opened it (or the "show" tab).
  const wasOpenRef = useRef(false);
  useEffect(() => {
    if (open) {
      wasOpenRef.current = true;
      return;
    }
    if (!wasOpenRef.current) return;
    wasOpenRef.current = false;
    (hidden ? showRef.current : launcherRef.current)?.focus();
  }, [open, hidden]);

  useEffect(() => {
    if (!open || !portal) return;
    const previous = new Map<HTMLElement, { inert: boolean; aria: string | null }>();
    const isolate = () => {
      for (const node of Array.from(document.body.children)) {
        if (!(node instanceof HTMLElement) || node === portal || previous.has(node)) continue;
        previous.set(node, { inert: node.inert, aria: node.getAttribute("aria-hidden") });
        node.inert = true;
        node.setAttribute("aria-hidden", "true");
      }
    };
    isolate();
    const observer = new MutationObserver(isolate);
    observer.observe(document.body, { childList: true });
    const overflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    closeRef.current?.focus();
    const onFocus = (e: FocusEvent) => {
      if (!panelRef.current?.contains(e.target as Node)) closeRef.current?.focus();
    };
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") { e.preventDefault(); closePanel(); }
    };
    document.addEventListener("focusin", onFocus, true);
    document.addEventListener("keydown", onKey);
    return () => {
      observer.disconnect();
      document.body.style.overflow = overflow;
      document.removeEventListener("focusin", onFocus, true);
      document.removeEventListener("keydown", onKey);
      for (const [node, state] of previous) {
        node.inert = state.inert;
        if (state.aria === null) node.removeAttribute("aria-hidden"); else node.setAttribute("aria-hidden", state.aria);
      }
    };
  }, [open, portal, closePanel]);

  // Disabling Stop after completion must not leave focus on the inert page.
  useEffect(() => {
    if (!open || reader !== "idle") return;
    const frame = requestAnimationFrame(() => {
      if (panelRef.current && !panelRef.current.contains(document.activeElement)) closeRef.current?.focus();
    });
    return () => cancelAnimationFrame(frame);
  }, [open, reader, settings.textToSpeech]);

  // Keep Tab / Shift+Tab inside the dialog while it is open.
  const onPanelKeyDown = (e: React.KeyboardEvent) => {
    if (e.key !== "Tab" || !panelRef.current) return;
    const items = Array.from(
      panelRef.current.querySelectorAll<HTMLElement>(
        'button:not([disabled]), select, input, a[href], [tabindex]:not([tabindex="-1"])',
      ),
    ).filter((el) => el.offsetParent !== null);
    if (!items.length) return;
    const first = items[0];
    const last = items[items.length - 1];
    if (e.shiftKey && document.activeElement === first) {
      e.preventDefault();
      last.focus();
    } else if (!e.shiftKey && document.activeElement === last) {
      e.preventDefault();
      first.focus();
    }
  };

  const clampAndStore = useCallback((x: number, y: number) => {
    const size = Math.max(44, launcherRef.current?.getBoundingClientRect().width ?? 56);
    const next = clampLauncherPosition(x, y, window.innerWidth, window.innerHeight, size);
    setPos(next);
    try {
      window.localStorage.setItem(POS_KEY, JSON.stringify(next));
    } catch {
      /* ignore */
    }
  }, []);

  useEffect(() => {
    const fit = () => setPos((previous) => {
      if (!previous) return previous;
      const size = Math.max(44, launcherRef.current?.getBoundingClientRect().width ?? 56 * settings.fontScale / 100);
      const next = clampLauncherPosition(previous.x, previous.y, window.innerWidth, window.innerHeight, size);
      try { window.localStorage.setItem(POS_KEY, JSON.stringify(next)); } catch { /* optional storage */ }
      return next;
    });
    fit();
    window.addEventListener("resize", fit);
    window.visualViewport?.addEventListener("resize", fit);
    return () => { window.removeEventListener("resize", fit); window.visualViewport?.removeEventListener("resize", fit); };
  }, [portal, settings.fontScale, settings.pageZoom]);

  // ---- Launcher: pointer drag is separated from activation ----
  // A drag only starts after the pointer travels DRAG_THRESHOLD px; activation is
  // handled by the native click event, so Enter and Space work like any button.
  const onPointerDown = (e: React.PointerEvent) => {
    if (e.button !== 0) return;
    suppressClickRef.current = false;
    e.preventDefault(); // native click is still the activation path
    const rect = (e.currentTarget as HTMLElement).getBoundingClientRect();
    dragRef.current = {
      dx: e.clientX - rect.left,
      dy: e.clientY - rect.top,
      sx: e.clientX,
      sy: e.clientY,
      moved: false,
    };
    (e.currentTarget as HTMLElement).setPointerCapture(e.pointerId);
  };

  const onPointerMove = (e: React.PointerEvent) => {
    const d = dragRef.current;
    if (!d) return;
    if (!d.moved && Math.hypot(e.clientX - d.sx, e.clientY - d.sy) < DRAG_THRESHOLD) return;
    d.moved = true;
    clampAndStore(e.clientX - d.dx, e.clientY - d.dy);
  };

  const onPointerUp = () => {
    if (dragRef.current?.moved) suppressClickRef.current = true;
    dragRef.current = null;
  };

  const onLauncherClick = (e: React.MouseEvent) => {
    if (suppressClickRef.current) {
      suppressClickRef.current = false;
      if (e.detail !== 0) return; // only suppress the pointer click following a drag
    }
    setOpen((v) => !v);
  };

  const onLauncherKeyDown = (e: React.KeyboardEvent) => {
    // Optional keyboard repositioning: Alt + arrow keys.
    if (!e.altKey) return;
    const step = 16;
    const rect = (e.currentTarget as HTMLElement).getBoundingClientRect();
    const delta: Record<string, [number, number]> = {
      ArrowUp: [0, -step],
      ArrowDown: [0, step],
      ArrowLeft: [-step, 0],
      ArrowRight: [step, 0],
    };
    const d = delta[e.key];
    if (!d) return;
    e.preventDefault();
    clampAndStore(rect.left + d[0], rect.top + d[1]);
  };

  // The portal host cancels body zoom for every control and overlay.
  if (!portal) return null;

  const launcherStyle: React.CSSProperties = pos
    ? { position: "fixed", left: pos.x, top: pos.y, right: "auto", bottom: "auto" }
    : {};

  return createPortal(
    <>
      <svg aria-hidden="true" width="0" height="0" style={{ position: "absolute" }}>
        <defs>
          <filter id="a11y-cb-protan">
            <feColorMatrix
              type="matrix"
              values="1 0 0 0 0  0.7 0.3 0 0 0  0.7 0 0.3 0 0  0 0 0 1 0"
            />
          </filter>
          <filter id="a11y-cb-deutan">
            <feColorMatrix
              type="matrix"
              values="0.3 0.7 0 0 0  0 1 0 0 0  0 0.7 0.3 0 0  0 0 0 1 0"
            />
          </filter>
          <filter id="a11y-cb-tritan">
            <feColorMatrix
              type="matrix"
              values="1 0 0 0 0  0 1 0 0 0  0.3 0.4 0.3 0 0  0 0 0 1 0"
            />
          </filter>
        </defs>
      </svg>
      {/* Reading helpers */}
      {!open && settings.readingGuide && <div className="a11y-reading-guide" aria-hidden="true" />}
      {!open && settings.readingMask && <div className="a11y-reading-mask" aria-hidden="true" />}

      {hidden ? (
        <button
          ref={showRef}
          type="button"
          onClick={() => {
            setHidden(false);
            requestAnimationFrame(() => launcherRef.current?.focus());
          }}
          aria-label="إظهار أدوات سهولة الوصول"
          className="fixed top-28 right-0 z-[60] min-h-11 rounded-r-none rounded-l-xl border-2 border-primary border-r-0 bg-card px-2 py-3 shadow-lg print:hidden"
        >
          <AccessibilityBadge className="h-6 w-6" />
        </button>
      ) : (
        <div
          className="fixed top-24 right-4 z-[60] print:hidden"
          style={launcherStyle}
          dir="rtl"
        >
          <button
            ref={launcherRef}
            type="button"
            aria-label="أدوات سهولة الوصول"
            aria-haspopup="dialog"
            aria-expanded={open}
            aria-controls={open ? "a11y-panel" : undefined}
            onPointerDown={onPointerDown}
            onPointerMove={onPointerMove}
            onPointerUp={onPointerUp}
            onPointerCancel={() => { suppressClickRef.current = false; dragRef.current = null; }}
            onClick={onLauncherClick}
            onKeyDown={onLauncherKeyDown}
            className="grid h-14 w-14 cursor-grab touch-none place-items-center rounded-full bg-card shadow-xl ring-1 ring-border transition hover:scale-105 active:cursor-grabbing focus-visible:outline focus-visible:outline-4 focus-visible:outline-offset-2 focus-visible:outline-ring"
          >
            <AccessibilityBadge className="h-12 w-12" />
          </button>
        </div>
      )}

      {open && (
        <>
          <div
            className="fixed inset-0 z-[70] bg-foreground/30 print:hidden"
            onClick={() => closePanel()}
            aria-hidden="true"
          />
          <div
            ref={panelRef}
            id="a11y-panel"
            role="dialog"
            aria-modal="true"
            aria-labelledby="a11y-panel-title"
            dir="rtl"
            onKeyDown={onPanelKeyDown}
            className="fixed inset-y-0 right-0 z-[71] flex w-[min(100vw,26rem)] flex-col border-l border-border bg-popover text-base shadow-2xl print:hidden animate-fade-in-soft"
          >
            <div className="flex items-center justify-between gap-2 border-b border-border px-4 py-3">
              <div className="flex min-w-0 items-center gap-2">
                <AccessibilityBadge className="h-9 w-9 shrink-0" />
                <h2 id="a11y-panel-title" className="break-words text-lg font-bold text-foreground">
                  أدوات سهولة الوصول
                </h2>
              </div>
              <button
                ref={closeRef}
                type="button"
                onClick={() => closePanel()}
                aria-label="إغلاق أدوات سهولة الوصول"
                className="grid h-11 w-11 shrink-0 place-items-center rounded-full text-foreground hover:bg-muted focus-visible:outline focus-visible:outline-2 focus-visible:outline-ring"
              >
                <X className="h-5 w-5" aria-hidden="true" />
              </button>
            </div>

            <div className="flex-1 overflow-y-auto px-4 py-4">
              <Section title="الإعاقة البصرية">
                <div className="space-y-4">
                  <Choice
                    label="حجم النص"
                    options={[
                      { v: 90, t: "A-" },
                      { v: 100, t: "A" },
                      { v: 120, t: "A+" },
                    ]}
                    value={settings.fontScale}
                    onChange={(v) => update({ fontScale: v })}
                  />
                  <Choice
                    label="تكبير الصفحة"
                    options={[100, 125, 150, 200].map((v) => ({ v, t: `${v}%` }))}
                    value={settings.pageZoom}
                    onChange={(v) => update({ pageZoom: v })}
                  />
                  <Choice
                    label="فلاتر ألوان تجريبية"
                    options={[
                      { v: "none", t: "بدون" },
                      { v: "protan", t: "ضعف الأحمر" },
                      { v: "deutan", t: "ضعف الأخضر" },
                      { v: "tritan", t: "ضعف الأزرق" },
                    ]}
                    value={settings.colorFilter}
                    onChange={(v) => update({ colorFilter: v as ColorFilter })}
                  />
                  <p className="text-sm text-muted-foreground">
                    فلاتر بصرية مساعدة، لا تعني تصحيحًا طبيًا ولا تضمن وضوح كل الألوان.
                  </p>
                  <div className="a11y-tools-grid grid gap-2">
                    <Tile
                      icon={<Contrast className="h-5 w-5" aria-hidden="true" />}
                      label="تباين عالٍ"
                      active={settings.highContrast}
                      onClick={() => update({ highContrast: !settings.highContrast })}
                    />
                    <Tile
                      icon={<Eye className="h-5 w-5" aria-hidden="true" />}
                      label="الوضع الداكن"
                      active={settings.darkMode}
                      onClick={() => update({ darkMode: !settings.darkMode })}
                    />
                    <Tile
                      icon={<Droplets className="h-5 w-5" aria-hidden="true" />}
                      label="تدرّج رمادي"
                      active={settings.monochrome}
                      onClick={() => update({ monochrome: !settings.monochrome })}
                    />
                  </div>
                  <div className="rounded-xl border border-border bg-card p-3">
                    <p className="mb-2 flex items-center gap-2 text-base font-semibold text-foreground">
                      <Volume2 className="h-4 w-4" aria-hidden="true" /> قراءة صوتية للصفحة
                    </p>
                    <div className="flex flex-wrap items-center gap-2">
                      {reader === "playing" ? (
                        <button type="button" onClick={pauseReader} className="a11y-btn">
                          إيقاف مؤقت
                        </button>
                      ) : (
                        <button
                          type="button"
                          onClick={startReader}
                          className="a11y-btn a11y-btn-primary"
                        >
                          {reader === "paused" ? "متابعة" : "تشغيل"}
                        </button>
                      )}
                      <button
                        type="button"
                        ref={stopRef}
                        onClick={stopReader}
                        disabled={reader === "idle" && !settings.textToSpeech}
                        className="a11y-btn"
                      >
                        إيقاف
                      </button>
                      <label className="flex items-center gap-1 text-sm text-foreground">
                        السرعة
                        <select
                          value={rate}
                          onChange={(e) => {
                            const r = Number(e.target.value);
                            setRate(r);
                            if (readerRef.current) {
                              utteranceRef.current = null;
                              window.speechSynthesis.cancel();
                              setReader("playing");
                              speakBlock(r);
                            }
                          }}
                          className="min-h-11 rounded-lg border border-border bg-background px-2 text-foreground"
                        >
                          {[0.75, 1, 1.25, 1.5].map((r) => (
                            <option key={r} value={r}>
                              {r}×
                            </option>
                          ))}
                        </select>
                      </label>
                    </div>
                    <p className="mt-2 text-sm text-foreground" aria-live="polite">
                      {speechKind === "selection" ? "قراءة التحديد" : speechKind === "page" ? "قراءة الصفحة" : ""}
                    </p>
                    <p className="sr-only" aria-live="polite">
                      {reader === "playing"
                        ? "جارٍ القراءة"
                        : reader === "paused"
                          ? "متوقف مؤقتًا"
                          : ""}
                    </p>
                  </div>
                </div>
              </Section>

              <Section title="أنماط المساعدة">
                <p role="status" className="mb-3 text-sm text-foreground">{notice || (settings.readingGuide ? "دليل القراءة مفعّل؛ أغلق اللوحة لمعاينته." : "")}</p>
                <div className="space-y-2">
                  {PROFILES.map((p) => (
                    <ProfileRow
                      key={p.id}
                      icon={p.icon}
                      label={p.label}
                      hint={p.hint}
                      active={activeProfile === p.id}
                      onClick={() => applyProfile(p.id, p.patch)}
                    />
                  ))}
                </div>
              </Section>

              <Section title="تجربة قراءة مريحة">
                <div className="a11y-tools-grid grid gap-2">
                  <TileStepper
                    icon={<ZoomIn className="h-5 w-5" aria-hidden="true" />}
                    label="حجم النص"
                    value={`${settings.fontScale}%`}
                    onDec={() => update({ fontScale: Math.max(80, settings.fontScale - 10) })}
                    onInc={() => update({ fontScale: Math.min(180, settings.fontScale + 10) })}
                  />
                  <TileStepper
                    icon={<Move className="h-5 w-5 rotate-90" aria-hidden="true" />}
                    label="تباعد الأسطر"
                    value={settings.lineHeight ? settings.lineHeight.toFixed(1) : "افتراضي"}
                    onDec={() =>
                      update({
                        lineHeight:
                          settings.lineHeight <= MIN_LINE_HEIGHT
                            ? 0
                            : +(settings.lineHeight - 0.2).toFixed(1),
                      })
                    }
                    onInc={() =>
                      update({
                        lineHeight: settings.lineHeight
                          ? Math.min(MAX_LINE_HEIGHT, +(settings.lineHeight + 0.2).toFixed(1))
                          : MIN_LINE_HEIGHT,
                      })
                    }
                  />
                  <TileStepper
                    icon={<Move className="h-5 w-5" aria-hidden="true" />}
                    label="تباعد الحروف"
                    value={`${settings.letterSpacing}`}
                    onDec={() => update({ letterSpacing: Math.max(0, settings.letterSpacing - 1) })}
                    onInc={() => update({ letterSpacing: Math.min(6, settings.letterSpacing + 1) })}
                  />
                  <TileStepper
                    icon={<Move className="h-5 w-5" aria-hidden="true" />}
                    label="تباعد الكلمات"
                    value={`${settings.wordSpacing}`}
                    onDec={() => update({ wordSpacing: Math.max(0, settings.wordSpacing - 2) })}
                    onInc={() => update({ wordSpacing: Math.min(16, settings.wordSpacing + 2) })}
                  />
                  <Tile
                    icon={<Type className="h-5 w-5" aria-hidden="true" />}
                    label="خط لقراءة أسهل"
                    active={settings.readableFont}
                    onClick={() =>
                      update({ readableFont: !settings.readableFont, dyslexiaFont: false })
                    }
                  />
                  <Tile
                    icon={<ALargeSmall className="h-5 w-5" aria-hidden="true" />}
                    label="خط بديل وتباعد أوسع"
                    active={settings.dyslexiaFont}
                    onClick={() =>
                      update({ dyslexiaFont: !settings.dyslexiaFont, readableFont: false })
                    }
                  />
                  <Tile
                    icon={<Baseline className="h-5 w-5" aria-hidden="true" />}
                    label="تمييز العناوين"
                    active={settings.highlightTitles}
                    onClick={() => update({ highlightTitles: !settings.highlightTitles })}
                  />
                  <Tile
                    icon={<Link2 className="h-5 w-5" aria-hidden="true" />}
                    label="تمييز الروابط"
                    active={settings.underlineLinks}
                    onClick={() => update({ underlineLinks: !settings.underlineLinks })}
                  />
                  <Tile
                    icon={<AlignRight className="h-5 w-5" aria-hidden="true" />}
                    label="محاذاة النص"
                    active={settings.justifyText}
                    onClick={() => update({ justifyText: !settings.justifyText })}
                  />
                  <Tile
                    icon={<Speech className="h-5 w-5" aria-hidden="true" />}
                    label="قراءة صوتية للنص المحدد"
                    active={settings.textToSpeech}
                    onClick={() => update({ textToSpeech: !settings.textToSpeech })}
                  />
                </div>
              </Section>

              <Section title="تجربة بصرية">
                <p className="mb-2 text-sm text-muted-foreground">
                  يُفعَّل خيار لوني واحد في كل مرة لتجنّب تعارض الفلاتر.
                </p>
                <div className="a11y-tools-grid grid gap-2">
                  <Tile
                    icon={<Contrast className="h-5 w-5" aria-hidden="true" />}
                    label="تباين عالٍ"
                    active={settings.highContrast}
                    onClick={() => update({ highContrast: !settings.highContrast })}
                  />
                  <Tile
                    icon={<Droplet className="h-5 w-5" aria-hidden="true" />}
                    label="أحادي اللون"
                    active={settings.monochrome}
                    onClick={() => update({ monochrome: !settings.monochrome })}
                  />
                  <Tile
                    icon={<Sparkles className="h-5 w-5" aria-hidden="true" />}
                    label="تباين ذكي"
                    active={settings.smartContrast}
                    onClick={() => update({ smartContrast: !settings.smartContrast })}
                  />
                  <Tile
                    icon={<Droplets className="h-5 w-5" aria-hidden="true" />}
                    label="تشبع منخفض"
                    active={settings.lowSaturation}
                    onClick={() =>
                      update({ lowSaturation: !settings.lowSaturation, highSaturation: false })
                    }
                  />
                  <Tile
                    icon={<Droplets className="h-5 w-5" aria-hidden="true" />}
                    label="تشبع عالي"
                    active={settings.highSaturation}
                    onClick={() =>
                      update({ highSaturation: !settings.highSaturation, lowSaturation: false })
                    }
                  />
                </div>
              </Section>

              <Section title="قابلية الانتقال والتوجيه">
                <div className="a11y-tools-grid grid gap-2">
                  <Tile
                    icon={<Volume2 className="h-5 w-5" aria-hidden="true" />}
                    label="كتم الأصوات"
                    active={settings.muteSounds}
                    onClick={() => update({ muteSounds: !settings.muteSounds })}
                  />
                  <Tile
                    icon={<ImageOff className="h-5 w-5" aria-hidden="true" />}
                    label="إخفاء الصور"
                    active={settings.hideImages}
                    onClick={() => update({ hideImages: !settings.hideImages })}
                  />
                  <Tile
                    icon={<Ruler className="h-5 w-5" aria-hidden="true" />}
                    label="دليل القراءة"
                    active={settings.readingGuide}
                    onClick={() => update({ readingGuide: !settings.readingGuide })}
                  />
                  <Tile
                    icon={<ScanLine className="h-5 w-5" aria-hidden="true" />}
                    label="قناع القراءة"
                    active={settings.readingMask}
                    onClick={() => update({ readingMask: !settings.readingMask })}
                  />
                  <Tile
                    icon={<PauseCircle className="h-5 w-5" aria-hidden="true" />}
                    label="إيقاف المؤثرات الحركية"
                    active={settings.reduceMotion}
                    onClick={() => update({ reduceMotion: !settings.reduceMotion })}
                  />
                  <Tile
                    icon={<MousePointerClick className="h-5 w-5" aria-hidden="true" />}
                    label="تمييز مرور المؤشر"
                    active={settings.highlightHover}
                    onClick={() => update({ highlightHover: !settings.highlightHover })}
                  />
                  <Tile
                    icon={<Focus className="h-5 w-5" aria-hidden="true" />}
                    label="تمييز التركيز"
                    active={settings.highlightFocus}
                    onClick={() => update({ highlightFocus: !settings.highlightFocus })}
                  />
                  <Tile
                    icon={<MousePointer2 className="h-5 w-5" aria-hidden="true" />}
                    label="مؤشر كبير داكن"
                    active={settings.bigCursor}
                    onClick={() =>
                      update({ bigCursor: !settings.bigCursor, bigCursorLight: false })
                    }
                  />
                  <Tile
                    icon={<MousePointer2 className="h-5 w-5" aria-hidden="true" />}
                    label="مؤشر كبير فاتح"
                    active={settings.bigCursorLight}
                    onClick={() =>
                      update({ bigCursorLight: !settings.bigCursorLight, bigCursor: false })
                    }
                  />
                </div>
              </Section>
            </div>

            <div className="grid grid-cols-2 gap-2 border-t border-border px-4 py-3">
              <button
                type="button"
                onClick={reset}
                className="inline-flex min-h-11 items-center justify-center gap-1.5 rounded-lg border border-border text-base text-foreground hover:bg-muted"
              >
                <RotateCcw className="h-4 w-4" aria-hidden="true" />
                إعادة الضبط
              </button>
              <button
                type="button"
                onClick={() => {
                  closePanel(true);
                }}
                className="inline-flex min-h-11 items-center justify-center gap-1.5 rounded-lg border border-border text-base text-foreground hover:bg-muted"
              >
                <EyeOff className="h-4 w-4" aria-hidden="true" />
                إخفاء الأداة
              </button>
            </div>
          </div>
        </>
      )}
    </>,
    portal,
  );
}

function Choice<T extends string | number>({
  label,
  options,
  value,
  onChange,
}: {
  label: string;
  options: { v: T; t: string }[];
  value: T;
  onChange: (v: T) => void;
}) {
  return (
    <div role="group" aria-label={label}>
      <p className="mb-1.5 text-sm font-semibold text-foreground">{label}</p>
      <div className="flex flex-wrap gap-2">
        {options.map((o) => (
          <button
            key={String(o.v)}
            type="button"
            aria-pressed={value === o.v}
            onClick={() => onChange(o.v)}
            className={`min-h-11 min-w-11 rounded-lg border-2 px-3 text-base transition ${
              value === o.v
                ? "border-primary bg-primary text-primary-foreground"
                : "border-border bg-card text-foreground hover:bg-muted"
            }`}
          >
            {o.t}
          </button>
        ))}
      </div>
    </div>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="mb-6">
      <h3 className="mb-3 text-base font-bold text-foreground">{title}</h3>
      {children}
    </section>
  );
}

function ProfileRow({
  icon,
  label,
  hint,
  active,
  onClick,
}: {
  icon: React.ReactNode;
  label: string;
  hint: string;
  active: boolean;
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      aria-pressed={active}
      onClick={onClick}
      className={`flex min-h-11 w-full items-start gap-3 rounded-xl border-2 px-3 py-3 text-right transition ${
        active ? "border-primary bg-primary/10" : "border-border hover:bg-muted"
      }`}
    >
      <span
        className={`mt-0.5 grid h-9 w-9 shrink-0 place-items-center rounded-lg ${
          active ? "bg-primary text-primary-foreground" : "bg-muted text-primary"
        }`}
      >
        {icon}
      </span>
      <span className="min-w-0 flex-1">
        <span className="block break-words text-base font-semibold text-foreground">{label}</span>
        <span className="block break-words text-sm text-muted-foreground">{hint}</span>
      </span>
    </button>
  );
}

function Tile({
  icon,
  label,
  active,
  onClick,
}: {
  icon: React.ReactNode;
  label: string;
  active: boolean;
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      aria-pressed={active}
      onClick={onClick}
      className={`flex min-h-24 min-w-0 flex-col items-center justify-center gap-2 rounded-xl border-2 px-2 py-3 text-center transition ${
        active
          ? "border-primary bg-primary/10 text-primary"
          : "border-transparent bg-muted text-foreground hover:bg-muted/70"
      }`}
    >
      <span className="text-primary">{icon}</span>
      <span className="break-words text-sm leading-snug">{label}</span>
    </button>
  );
}

function TileStepper({
  icon,
  label,
  value,
  onDec,
  onInc,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
  onDec: () => void;
  onInc: () => void;
}) {
  return (
    <div
      role="group"
      aria-label={label}
      className="flex min-h-24 min-w-0 flex-col items-center justify-center gap-1.5 rounded-xl bg-muted px-2 py-3 text-center"
    >
      <span className="text-primary">{icon}</span>
      <span className="break-words text-sm leading-snug text-foreground">{label}</span>
      <span className="a11y-stepper-controls">
        <button
          type="button"
          aria-label={`تقليل ${label}`}
          onClick={onDec}
          className="grid h-11 w-11 place-items-center rounded-lg border border-border bg-background text-lg text-foreground"
        >
          −
        </button>
        <span className="min-w-0 break-words text-sm text-foreground" aria-live="polite">
          {value}
        </span>
        <button
          type="button"
          aria-label={`زيادة ${label}`}
          onClick={onInc}
          className="grid h-11 w-11 place-items-center rounded-lg border border-border bg-background text-lg text-foreground"
        >
          +
        </button>
      </span>
    </div>
  );
}
