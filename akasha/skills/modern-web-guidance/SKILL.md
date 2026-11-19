---
name: modern-web-guidance
description: "GoogleChrome/modern-web-guidance (v1.0.0) 官方现代 Web 标准与 Baseline 最佳实践协议：覆盖 203 个用例与 250 项现代 HTML/CSS/JS 特性，自动区分浏览器 Web 与 Electron/Tauri 桌面宿主。"
---

# Modern Web Guidance (`GoogleChrome/modern-web-guidance` — AI-Executable)

## 1. TRIGGER SCOPE
- **MANDATORY FIRST STEP** for all HTML, CSS, and client-side JS/TS tasks: dialogs/modals/popovers, tooltips, tables, dark mode, CSS anchor positioning, container queries, view transitions, scroll-driven animations, forms/validation/autofill, custom selects, scrollbars, Core Web Vitals (LCP/INP/CLS), `content-visibility`, `scheduler.yield`, passkeys/WebAuthn, Sanitizer API, Web Components, `Temporal`, and built-in AI.
- **SKIP** for pure backend (Rust/Go/Python/SQL/API routes), CLI scripts, or non-HTML native shaders.

## 2. FOUR-STEP EXECUTION WORKFLOW
1. **Search Use Cases**: Run `npx -y modern-web-guidance@latest search "<2-5 word UI primitive>"` (Windows: `npx.cmd`; omit framework/domain nouns). If offline or `>8s`, immediately apply the Section 3 Baseline Matrix.
2. **Retrieve Best Practices**: Run `npx -y modern-web-guidance@latest retrieve "<id1>,<id2>"` (read temp file in full if `>9.5KB`).
3. **Framework & Host Branching**:
   - Cast newly shipped JSX/TS HTML attributes (`{...({ popover: 'auto', commandfor: id } as any)}`).
   - Guard SSR `window`/`HTMLElement`; use `useId()` for unique `popovertarget`/`anchor-name`.
   - **Desktop Chromium Host (Electron/Tauri/WebView2)**: Use Baseline & Newly Available features natively without legacy fallbacks.
   - **Public Browser Web App**: Add `@supports` progressive enhancement for Newly/Limited Available features.
4. **Disclosure**: Include a concise `### Modern Web Guidance` block citing applied guide IDs / rules.

## 3. COMPILED HIGH-FREQUENCY BASELINE MATRIX (ZERO-LATENCY OFFLINE REFERENCE)
| UI / Web Task | Legacy Anti-Pattern (FORBIDDEN) | Modern Web Baseline Pattern (MANDATORY) |
|---|---|---|
| **Modal / Dialog** | `<div class="modal">` + `z-index: 9999` + custom focus trap | `<dialog>` + `showModal()` + `method="dialog"` + `::backdrop` + `closedby="any"` |
| **Popover / Tooltip** | Manual `document.addEventListener('click')` + JS top/left math | Popover API (`popover="auto"`) + CSS Anchor Positioning (`anchor-name`, `position-anchor`, `position-area`) |
| **Entry/Exit Motion** | JS `setTimeout` unmount hacks | `@starting-style` + `transition-behavior: allow-discrete` |
| **Responsive Cards** | Viewport `@media` for reusable components | `container-type: inline-size` + `@container` + `clamp()` |
| **Parent/State CSS** | JS class toggling on parent nodes | `:has(> input:checked)`, `:has(:user-invalid)`, `:focus-within` |
| **Form Validation** | `:invalid` (premature red error on empty load) | `:user-invalid` & `:user-valid` + `aria-describedby` |
| **Viewport & Scroll** | `100vh` + scrollbar layout shift | `100dvh` + `scrollbar-gutter: stable` + `overscroll-behavior: contain` |
| **Long Tasks & INP** | Monolithic sync loops `>50ms` | `await scheduler.yield()` + `content-visibility: auto` |
| **Safe HTML** | Raw `innerHTML = untrusted` | `element.setHTML(untrusted)` or `DOMPurify` fallback |
| **Dates & Timezones** | Mutable `new Date()` timezone math | `Temporal.Now.zonedDateTimeISO()`, `Temporal.PlainDate`, `Intl.DateTimeFormat` |
