// @vitest-environment jsdom
import React from "react";
import { createRoot, Root } from "react-dom/client";
import { act } from "react-dom/test-utils";
import { beforeEach, afterEach, describe, expect, it, vi } from "vitest";
import { AccessibilityToolbar } from "./AccessibilityToolbar";
let root: Root;
let page: HTMLDivElement;
let utterances: any[];
let speech: {speak: ReturnType<typeof vi.fn>; cancel: ReturnType<typeof vi.fn>; pause: ReturnType<typeof vi.fn>; resume: ReturnType<typeof vi.fn>; getVoices: ReturnType<typeof vi.fn>};
function button(name: string) { return Array.from(document.querySelectorAll<HTMLButtonElement>("button")).find(b => b.getAttribute("aria-label") === name || b.textContent?.trim() === name)!; }
async function click(name: string) { await act(async () => button(name).click()); }
beforeEach(async () => {
  (globalThis as any).IS_REACT_ACT_ENVIRONMENT = true;
  document.body.innerHTML = "";document.documentElement.className="";document.documentElement.removeAttribute("style");window.localStorage.clear();utterances=[];
  speech={speak:vi.fn(u=>utterances.push(u)),cancel:vi.fn(),pause:vi.fn(),resume:vi.fn(),getVoices:vi.fn(()=>[])};
  Object.defineProperty(window,"speechSynthesis",{value:speech,configurable:true});
  vi.stubGlobal("SpeechSynthesisUtterance",class {text:string;lang="";rate=1;onend:any;onerror:any;constructor(text:string){this.text=text;}});
  Element.prototype.scrollIntoView=vi.fn();
  page=document.createElement("div");page.id="test-page";page.setAttribute("aria-hidden","false");document.body.append(page);root=createRoot(page);
  await act(async()=>root.render(<><main><p id="selection">نص تجريبي للقراءة</p><button id="behind">خلفية</button></main><AccessibilityToolbar/></>));
});
afterEach(async()=>{await act(async()=>root.unmount());vi.unstubAllGlobals();document.body.innerHTML="";});
describe("dialog and speech lifecycle",()=>{
  it("isolates background siblings, guards focus and restores their attributes",async()=>{
    const wasInert=page.inert;
    const other=document.createElement("div");other.inert=true;other.setAttribute("aria-hidden","true");document.body.append(other);
    await click("أدوات سهولة الوصول");expect(page.inert).toBe(true);expect(page.getAttribute("aria-hidden")).toBe("true");
    await act(async()=>document.getElementById("behind")!.focus());expect(document.activeElement).toBe(button("إغلاق أدوات سهولة الوصول"));
    await click("إغلاق أدوات سهولة الوصول");expect(page.inert).toBe(wasInert);expect(page.getAttribute("aria-hidden")).toBe("false");expect(other.inert).toBe(true);expect(other.getAttribute("aria-hidden")).toBe("true");
  });
  it("does not restart the same selection on Tab and keeps Stop usable",async()=>{
    await click("أدوات سهولة الوصول");await click("قراءة صوتية للنص المحدد");await click("إغلاق أدوات سهولة الوصول");
    const text=document.getElementById("selection")!.firstChild!;const range=document.createRange();range.selectNodeContents(text);const sel=window.getSelection()!;sel.removeAllRanges();sel.addRange(range);
    await act(async()=>{document.dispatchEvent(new Event("selectionchange"));await new Promise(r=>setTimeout(r,220));});expect(speech.speak).toHaveBeenCalledTimes(1);
    await act(async()=>{document.dispatchEvent(new KeyboardEvent("keyup",{key:"Tab",bubbles:true}));document.dispatchEvent(new Event("selectionchange"));await new Promise(r=>setTimeout(r,220));});expect(speech.speak).toHaveBeenCalledTimes(1);
    await click("أدوات سهولة الوصول");expect(button("إيقاف").disabled).toBe(false);const before=speech.cancel.mock.calls.length;await click("إيقاف");expect(speech.cancel.mock.calls.length).toBeGreaterThan(before);
  });
  it("reset cancels queued speech and clears page highlights",async()=>{
    document.getElementById("selection")!.classList.add("a11y-reading-now");await click("أدوات سهولة الوصول");const before=speech.cancel.mock.calls.length;await click("إعادة الضبط");expect(document.querySelector(".a11y-reading-now")).toBeNull();expect(speech.cancel.mock.calls.length).toBeGreaterThan(before);expect(window.localStorage.getItem("a11y-settings-v2")).toBeNull();
  });
  it("the ADHD preset persists its guide and reduced motion",async()=>{
    await click("أدوات سهولة الوصول");const preset=Array.from(document.querySelectorAll<HTMLButtonElement>("button")).find(b=>b.textContent?.includes("دليل القراءة وتقليل الحركة (ADHD)"))!;await act(async()=>preset.click());
    const settings=JSON.parse(window.localStorage.getItem("a11y-settings-v2")!);expect(settings.profileId).toBe("adhd");expect(settings.readingGuide).toBe(true);expect(settings.reduceMotion).toBe(true);
    await click("إغلاق أدوات سهولة الوصول");expect(document.querySelector(".a11y-reading-guide")).not.toBeNull();
  });
});
