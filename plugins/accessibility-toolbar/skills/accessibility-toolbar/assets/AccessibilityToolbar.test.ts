import { describe, expect, it } from "vitest";
import { normalizeSettings } from "./AccessibilityToolbar";

const base = normalizeSettings({} as never, {
  fontScale: 100,
  letterSpacing: 0,
  wordSpacing: 0,
  lineHeight: 0,
  colorFilter: "none",
  darkMode: false,
  pageZoom: 100,
  highContrast: false,
  smartContrast: false,
  monochrome: false,
  lowSaturation: false,
  highSaturation: false,
});

describe("normalizeSettings", () => {
  it("turning on dark mode switches off high contrast", () => {
    const s = normalizeSettings({ ...base, highContrast: true }, { darkMode: true });
    expect(s.darkMode).toBe(true);
    expect(s.highContrast).toBe(false);
  });

  it("choosing a colour filter switches off grayscale", () => {
    const s = normalizeSettings({ ...base, monochrome: true }, { colorFilter: "protan" });
    expect(s.colorFilter).toBe("protan");
    expect(s.monochrome).toBe(false);
  });

  it("turning on grayscale clears the colour filter", () => {
    const s = normalizeSettings({ ...base, colorFilter: "deutan" }, { monochrome: true });
    expect(s.colorFilter).toBe("none");
  });

  it("line height never goes below 1.5 when set", () => {
    expect(normalizeSettings(base, { lineHeight: 1.1 }).lineHeight).toBe(1.5);
    expect(normalizeSettings(base, { lineHeight: 0 }).lineHeight).toBe(0);
  });

  it("changing font size keeps other options", () => {
    const s = normalizeSettings({ ...base, highContrast: true }, { fontScale: 120 });
    expect(s.highContrast).toBe(true);
  });
});

import { clampLauncherPosition } from "./AccessibilityToolbar";
describe("restoration and preset invariants", () => {
  it("keeps a stored desktop position inside a 320px screen", () => {
    expect(clampLauncherPosition(704, 270, 320, 700)).toEqual({ x: 256, y: 270 });
  });
  it("uses the real enlarged launcher size", () => {
    expect(clampLauncherPosition(256, 900, 320, 700, 68)).toEqual({ x: 244, y: 624 });
  });
  it("handles malformed coordinates without losing the launcher", () => {
    expect(clampLauncherPosition(NaN, Infinity, 320, 700)).toEqual({ x: 8, y: 8 });
  });
  it("restoring an explicit colour choice clears incompatible modes", () => {
    const s = normalizeSettings({ ...base, highContrast: true, monochrome: true }, { highContrast: true });
    expect(s.highContrast).toBe(true);
    expect(s.monochrome).toBe(false);
  });
  it("rejects out-of-range stored scale and spacing", () => {
    const s = normalizeSettings(base, { fontScale: 900, pageZoom: -1, wordSpacing: 100, letterSpacing: -10 });
    expect([s.fontScale, s.pageZoom, s.wordSpacing, s.letterSpacing]).toEqual([180, 100, 16, 0]);
  });
  it("retains the ADHD preset id with its actual settings", () => {
    const s = normalizeSettings(base, { profileId: "adhd", readingGuide: true, reduceMotion: true });
    expect(s.profileId).toBe("adhd");
    expect(s.readingGuide).toBe(true);
    expect(s.reduceMotion).toBe(true);
  });
});
