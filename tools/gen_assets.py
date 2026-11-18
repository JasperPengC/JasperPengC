#!/usr/bin/env python3
"""Generate the custom neon SVG artwork for JasperPengC's profile README.

Everything here is self-contained: no external fonts, no scripts, only CSS/SMIL
animations that GitHub's camo proxy serves untouched. Run from anywhere:

    python3 tools/gen_assets.py

Outputs go to ../assets relative to this file (repo root/assets).
"""

from __future__ import annotations

import html
import math
import re
import pathlib
import random

ROOT = pathlib.Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"

FONT_SANS = (
    "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', "
    "Arial, 'PingFang SC', 'Microsoft YaHei', 'Noto Sans SC', sans-serif"
)
FONT_MONO = (
    "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, "
    "'Liberation Mono', 'Courier New', monospace"
)

CYAN = "#67e8f9"
TEAL = "#22d3ee"
SKY = "#7dd3fc"
VIOLET = "#a78bfa"
PURPLE = "#c084fc"
PINK = "#f472b6"
GREEN = "#4ade80"
SLATE = "#94a3b8"
MUTED = "#64748b"
INK = "#04060e"


def esc(text: str) -> str:
    return html.escape(text, quote=False)


def write(name: str, body: str) -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    path = ASSETS / name
    path.write_text(body, encoding="utf-8")
    print(f"  wrote {path.relative_to(ROOT)} ({len(body) / 1024:.1f} kB)")
    if name.endswith(".svg"):
        day = lighten(body, name)
        day_path = ASSETS / f"{name[:-4]}-light.svg"
        day_path.write_text(day, encoding="utf-8")
        print(f"  wrote {day_path.relative_to(ROOT)} ({len(day) / 1024:.1f} kB)")


# --------------------------------------------------------------------------
# light theme (day mode) — derived from the dark SVGs by palette remapping
# --------------------------------------------------------------------------

LIGHT_MAP = {
    # surfaces
    "#05070f": "#ffffff", "#070c1a": "#f6f8ff", "#090513": "#f8f5ff",
    "#0a1020": "#f3f6ff", "#070b14": "#fbfcff", "#0a0713": "#f5f3ff",
    "#04060e": "#ffffff", "#0b1020": "#bae6fd", "#020617": "#ffffff",
    "#05080f": "#f1f5f9", "#0a1224": "#f1f5f9", "#0b1220": "#ffffff",
    "#1e3a5f": "#c7d2e3", "#1e293b": "#dbe3ef", "#01030a": "#ffffff",
    # text (inverted hierarchy)
    "#e6edf7": "#0f172a", "#e2e8f0": "#0f172a", "#dbe7f5": "#0f172a",
    "#f0f6fc": "#0f172a", "#cbd5e1": "#334155", "#b6c2d4": "#334155",
    "#a8b3c7": "#475569", "#94a3b8": "#475569", "#8fa0b8": "#475569",
    "#7c8aa5": "#64748b", "#64748b": "#64748b", "#475569": "#64748b",
    "#d7e1ee": "#334155",
    "#334155": "#94a3b8",
    # accents (darker for contrast on white)
    "#67e8f9": "#0891b2", "#22d3ee": "#0e7490", "#38bdf8": "#0284c7",
    "#7dd3fc": "#0ea5e9", "#a5f3fc": "#0e7490", "#cffafe": "#0891b2",
    "#bae6fd": "#0369a1", "#ddd6fe": "#7c3aed", "#fbcfe8": "#db2777",
    "#c4b5fd": "#7c3aed", "#a78bfa": "#6d28d9", "#c084fc": "#7e22ce",
    "#8b5cf6": "#6d28d9", "#f472b6": "#db2777", "#fb7185": "#e11d48",
    "#f9a8d4": "#db2777", "#4ade80": "#15803d", "#86efac": "#15803d",
    "#10b981": "#047857", "#fb923c": "#c2410c", "#fdba74": "#c2410c",
    "#fbbf24": "#b45309", "#facc15": "#a16207", "#f7df1e": "#a16207",
    "#f89820": "#c2410c", "#3b82f6": "#1d4ed8", "#61dafb": "#0e7490",
    "#42b883": "#0f766e", "#9feaf9": "#0e7490", "#ffc131": "#b45309",
    "#5b8cba": "#1e40af", "#4a90c2": "#1d4ed8", "#ff6b5b": "#dc2626",
    "#e879f9": "#a21caf", "#84cc16": "#4d7c0f", "#fc6d26": "#c2410c",
    "#2dd4bf": "#0f766e", "#6db33f": "#15803d", "#e0f2fe": "#0ea5e9",
    "#f0f9ff": "#0e7490", "#f87171": "#dc2626", "#9ae6ff": "#94a3b8",
    "#7c3aed": "#6d28d9", "#6d28d9": "#5b21b6", "#0891b2": "#0e7490",
}


def _scale_gradient_opacity(svg: str, gid: str, factor: float) -> str:
    m = re.search(r'(<radialGradient id="%s"[\s\S]*?</radialGradient>)' % re.escape(gid), svg)
    if not m:
        return svg
    block = m.group(1)
    scaled = re.sub(
        r'stop-opacity="([0-9.]+)"',
        lambda mm: 'stop-opacity="%.3f"' % (float(mm.group(1)) * factor),
        block,
    )
    return svg.replace(block, scaled)


def lighten(svg: str, name: str) -> str:
    # day mode: no star field / sparkles in the hero sky
    if name == "hero.svg":
        svg = re.sub(r'<circle[^>]*style="animation:twinkle[^"]*"[^>]*/>\s*', '', svg)
        svg = re.sub(r'<path d="[^"]*"[^>]*style="animation:twinkle[^"]*"[^>]*/>\s*', '', svg)
        # drop the blurred glow copy of the wordmark
        svg = re.sub(r'\s*<text[^>]*filter="url\(#soft2\)"[^>]*>JASPER</text>', '', svg)
    # palette remap (longest first so prefixes never collide)
    for k in sorted(LIGHT_MAP, key=len, reverse=True):
        svg = svg.replace(k, LIGHT_MAP[k])
    # softer lights for daytime
    for gid, f in (("auroraCyan", .42), ("auroraViolet", .42), ("auroraPink", .42),
                   ("orbHalo", .5), ("vignette", .5)):
        svg = _scale_gradient_opacity(svg, gid, f)
    return svg


# --------------------------------------------------------------------------
# shared defs
# --------------------------------------------------------------------------


def hero_defs() -> str:
    return f"""
  <defs>
    <linearGradient id="bgFill" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#070c1a"/>
      <stop offset=".52" stop-color="#05070f"/>
      <stop offset="1" stop-color="#090513"/>
    </linearGradient>
    <radialGradient id="auroraCyan" cx="150" cy="-90" r="660" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="{TEAL}" stop-opacity=".34"/>
      <stop offset=".42" stop-color="#0891b2" stop-opacity=".12"/>
      <stop offset="1" stop-color="#020617" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="auroraViolet" cx="1090" cy="30" r="590" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="{VIOLET}" stop-opacity=".32"/>
      <stop offset=".45" stop-color="#7c3aed" stop-opacity=".12"/>
      <stop offset="1" stop-color="#05070f" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="auroraPink" cx="620" cy="400" r="560" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="{PINK}" stop-opacity=".13"/>
      <stop offset="1" stop-color="#05070f" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="titleFill" x1="60" y1="0" x2="640" y2="0" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="#cffafe"/>
      <stop offset=".3" stop-color="{CYAN}"/>
      <stop offset=".66" stop-color="{VIOLET}"/>
      <stop offset=".9" stop-color="{PINK}"/>
      <stop offset="1" stop-color="#fb7185"/>
    </linearGradient>
    <linearGradient id="lineFill" x1="75" y1="0" x2="336" y2="0" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="{TEAL}" stop-opacity=".9"/>
      <stop offset="1" stop-color="{VIOLET}" stop-opacity="0"/>
    </linearGradient>
    <linearGradient id="edgeFill" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="{TEAL}" stop-opacity="0"/>
      <stop offset=".18" stop-color="{TEAL}" stop-opacity=".9"/>
      <stop offset=".82" stop-color="{VIOLET}" stop-opacity=".9"/>
      <stop offset="1" stop-color="{VIOLET}" stop-opacity="0"/>
    </linearGradient>
    <linearGradient id="borderFill" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="{TEAL}" stop-opacity=".55"/>
      <stop offset=".5" stop-color="{VIOLET}" stop-opacity=".18"/>
      <stop offset="1" stop-color="{PINK}" stop-opacity=".5"/>
    </linearGradient>
    <linearGradient id="sweepFill" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="{TEAL}" stop-opacity="0"/>
      <stop offset=".5" stop-color="{CYAN}" stop-opacity=".5"/>
      <stop offset="1" stop-color="{TEAL}" stop-opacity="0"/>
    </linearGradient>
    <linearGradient id="barFill" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="{CYAN}"/>
      <stop offset="1" stop-color="{PURPLE}" stop-opacity=".55"/>
    </linearGradient>
    <radialGradient id="orbFill" cx=".34" cy=".26" r=".92">
      <stop offset="0" stop-color="#e0f2fe" stop-opacity=".85"/>
      <stop offset=".22" stop-color="{SKY}" stop-opacity=".42"/>
      <stop offset=".55" stop-color="#6d28d9" stop-opacity=".26"/>
      <stop offset="1" stop-color="#0b1020" stop-opacity=".06"/>
    </radialGradient>
    <radialGradient id="orbHalo" cx=".5" cy=".5" r=".5">
      <stop offset="0" stop-color="{TEAL}" stop-opacity=".26"/>
      <stop offset=".55" stop-color="{VIOLET}" stop-opacity=".10"/>
      <stop offset="1" stop-color="#05070f" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="ringFill" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="{TEAL}" stop-opacity=".05"/>
      <stop offset=".5" stop-color="{CYAN}" stop-opacity=".55"/>
      <stop offset="1" stop-color="{VIOLET}" stop-opacity=".08"/>
    </linearGradient>
    <radialGradient id="vignette" cx=".5" cy=".46" r=".78">
      <stop offset=".55" stop-color="#000" stop-opacity="0"/>
      <stop offset="1" stop-color="#01030a" stop-opacity=".72"/>
    </radialGradient>
    <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
      <path d="M40 0H0V40" fill="none" stroke="{SKY}" stroke-opacity=".055" stroke-width="1"/>
    </pattern>
    <pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse">
      <rect width="4" height="1.2" fill="#9ae6ff" opacity=".022"/>
    </pattern>
    <filter id="soft" x="-40%" y="-40%" width="180%" height="180%">
      <feGaussianBlur stdDeviation="7"/>
    </filter>
    <filter id="soft2" x="-60%" y="-60%" width="220%" height="220%">
      <feGaussianBlur stdDeviation="14"/>
    </filter>
    <clipPath id="cardClip"><rect width="1200" height="440" rx="20"/></clipPath>
    <clipPath id="globeClip"><circle cx="985" cy="175" r="80"/></clipPath>
  </defs>"""


def hero() -> str:
    rnd = random.Random(20261024)
    w, h = 1200, 440

    stars = []
    for _ in range(92):
        x = rnd.uniform(4, w - 4)
        y = rnd.uniform(4, h - 4)
        r = rnd.choice([0.6, 0.7, 0.9, 1.1, 1.4, 1.8, 2.2])
        op = rnd.uniform(0.16, 0.8)
        dur = rnd.uniform(2.6, 7.4)
        delay = -rnd.uniform(0, 9)
        fill = rnd.choice(["#e2e8f0", "#bae6fd", "#ddd6fe", "#fbcfe8"])
        stars.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{fill}" opacity="{op:.2f}" '
            f'style="animation:twinkle {dur:.2f}s ease-in-out {delay:.2f}s infinite"/>'
        )

    # four-point sparkles
    sparkles = []
    for cx, cy, s_, dur, delay in [
        (232, 84, 7.0, 5.2, -1.1),
        (1180, 300, 5.6, 4.4, -3.2),
        (806, 64, 4.8, 6.1, -0.4),
        (140, 330, 4.4, 5.6, -2.7),
    ]:
        sparkles.append(
            f'<path d="M{cx} {cy - s_} Q{cx} {cy} {cx + s_} {cy} Q{cx} {cy} {cx} {cy + s_} '
            f'Q{cx} {cy} {cx - s_} {cy} Q{cx} {cy} {cx} {cy - s_}Z" fill="#cffafe" '
            f'opacity=".75" style="animation:twinkle {dur:.1f}s ease-in-out {delay:.1f}s infinite"/>'
        )

    chips = []
    # chips mirror what the public repos are actually built with
    chip_labels = ["TYPESCRIPT", "RUST", "TAURI", "MCP", "DOCKER"]
    chip_colors = ["#3b82f6", "#fb923c", "#fbbf24", CYAN, "#38bdf8"]
    x = 74
    for label, color in zip(chip_labels, chip_colors):
        width = 9.2 * len(label) + 42
        chips.append(
            f'<g><rect x="{x:.0f}" y="368" width="{width:.0f}" height="32" rx="9" '
            f'fill="#0a1224" stroke="#1e3a5f" stroke-opacity=".9"/>'
            f'<circle cx="{x + 16:.0f}" cy="384" r="3.2" fill="{color}"/>'
            f'<text x="{x + 28:.0f}" y="389" font-family="{FONT_MONO}" font-size="13" '
            f'letter-spacing="1.4" fill="#cbd5e1">{label}</text></g>'
        )
        x += width + 10

    bars = []
    bx = 862
    for i in range(18):
        bh = 10 + (math.sin(i * 0.9) * 0.5 + rnd.random() * 0.6) * 30
        delay = -rnd.uniform(0, 2.4)
        dur = rnd.uniform(1.4, 2.6)
        bars.append(
            f'<rect x="{bx + i * 14.5:.1f}" y="{360 - bh:.1f}" width="6.5" height="{bh:.1f}" rx="3" '
            f'fill="url(#barFill)" opacity=".85" '
            f'style="transform-box:fill-box;transform-origin:50% 100%;animation:eq {dur:.2f}s ease-in-out {delay:.2f}s infinite"/>'
        )

    body = f"""<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="440" viewBox="0 0 1200 440" role="img" aria-labelledby="heroTitle heroDesc">
  <title id="heroTitle">Jasper — AI Agent Tooling · DeepSeek Harness Ecosystem</title>
  <desc id="heroDesc">Neon deep-space banner: JASPER, AI agent tooling, DSH ecosystem, open source.</desc>
{hero_defs()}
  <style>
    @keyframes twinkle {{ 0%,100% {{ opacity:.14 }} 50% {{ opacity:.95 }} }}
    @keyframes sweep {{ 0% {{ transform:translateY(-160px) }} 100% {{ transform:translateY(460px) }} }}
    @keyframes shoot {{
      0%,64% {{ opacity:0; transform:translate(0,0) }}
      68% {{ opacity:.95; transform:translate(-44px,26px) }}
      84% {{ opacity:0; transform:translate(-190px,112px) }}
      100% {{ opacity:0; transform:translate(-190px,112px) }}
    }}
    @keyframes eq {{ 0%,100% {{ transform:scaleY(.35) }} 50% {{ transform:scaleY(1) }} }}
    @keyframes blink {{ 0%,49% {{ opacity:1 }} 50%,100% {{ opacity:0 }} }}
    @keyframes pulse {{ 0%,100% {{ opacity:.35; transform:scale(1) }} 50% {{ opacity:.05; transform:scale(1.06) }} }}
    @keyframes spin-slow {{ 0% {{ transform:rotate(0deg) }} 100% {{ transform:rotate(360deg) }} }}
    .pulse {{ transform-box:fill-box; transform-origin:center; animation:pulse 4.2s ease-in-out infinite }}
    .cursor {{ animation:blink 1.15s steps(1,end) infinite }}
  </style>
  <g clip-path="url(#cardClip)">
    <rect width="1200" height="440" fill="url(#bgFill)"/>
    <rect width="1200" height="440" fill="url(#auroraCyan)"/>
    <rect width="1200" height="440" fill="url(#auroraViolet)"/>
    <rect width="1200" height="440" fill="url(#auroraPink)"/>
    <rect width="1200" height="440" fill="url(#grid)" opacity=".55"/>
    {''.join(stars)}
    {''.join(sparkles)}

    <!-- hologram globe -->
    <circle cx="985" cy="175" r="196" fill="url(#orbHalo)"/>
    <g clip-path="url(#globeClip)">
      <circle cx="985" cy="175" r="80" fill="url(#orbFill)"/>
      <g fill="none" stroke="{CYAN}" stroke-opacity=".22" stroke-width=".8">
        <ellipse cx="985" cy="175" rx="80" ry="26"/>
        <ellipse cx="985" cy="175" rx="80" ry="53"/>
        <ellipse cx="985" cy="175" rx="80" ry="79"/>
        <ellipse cx="985" cy="175" rx="26" ry="80"/>
        <ellipse cx="985" cy="175" rx="53" ry="80"/>
        <ellipse cx="985" cy="175" rx="79" ry="80"/>
      </g>
      <circle cx="985" cy="175" r="80" fill="none" stroke="{SKY}" stroke-opacity=".5" stroke-width="1.1"/>
    </g>
    <g transform="rotate(-18 985 175)">
      <ellipse cx="985" cy="175" rx="136" ry="41" fill="none" stroke="url(#ringFill)" stroke-width="1.3" stroke-dasharray="5 9"/>
      <ellipse cx="985" cy="175" rx="116" ry="35" fill="none" stroke="url(#ringFill)" stroke-width="1" stroke-dasharray="3 7" opacity=".8"/>
      <ellipse cx="985" cy="175" rx="95" ry="24" fill="none" stroke="url(#ringFill)" stroke-width=".9" stroke-dasharray="2 6" opacity=".65"/>
      <circle r="3.4" fill="#e0f2fe">
        <animateMotion dur="13s" repeatCount="indefinite" path="M849,175 a136,41 0 1,1 272,0 a136,41 0 1,1 -272,0"/>
      </circle>
      <circle r="9" fill="{CYAN}" opacity=".16">
        <animateMotion dur="13s" repeatCount="indefinite" path="M849,175 a136,41 0 1,1 272,0 a136,41 0 1,1 -272,0"/>
      </circle>
      <circle r="2.4" fill="{PINK}">
        <animateMotion dur="19s" repeatCount="indefinite" path="M869,175 a116,35 0 1,1 232,0 a116,35 0 1,1 -232,0" keyPoints="1;0" keyTimes="0;1" calcMode="linear"/>
      </circle>
    </g>
    <circle cx="985" cy="175" r="120" fill="none" stroke="{VIOLET}" stroke-opacity=".16" stroke-width=".8" stroke-dasharray="2 12"/>
    <circle cx="985" cy="175" r="120" fill="none" stroke="{SKY}" stroke-opacity=".08" stroke-width="8" class="pulse"/>

    <!-- terminal headline block -->
    <rect x="56" y="82" width="2.2" height="320" rx="1.1" fill="url(#edgeFill)"/>
    <rect x="52.6" y="82" width="10" height="10" rx="2" fill="{TEAL}" opacity=".9" style="animation:blink 2.4s steps(1,end) infinite"/>
    <rect x="52.6" y="392" width="10" height="10" rx="2" fill="{VIOLET}" opacity=".75"/>
    <text x="80" y="108" font-family="{FONT_MONO}" font-size="14" letter-spacing="3.0" fill="{CYAN}" opacity=".72">// PROFILE.SYS · AI APPLICATION ENGINEER</text>
    <text x="72" y="214" font-family="{FONT_SANS}" font-size="96" font-weight="800" letter-spacing="7" fill="{CYAN}" opacity=".5" filter="url(#soft2)">JASPER</text>
    <text x="72" y="214" font-family="{FONT_SANS}" font-size="96" font-weight="800" letter-spacing="7" fill="url(#titleFill)">JASPER</text>
    <path d="M75 240 H360" stroke="url(#lineFill)" stroke-width="1.8"/>
    <rect x="356" y="235.5" width="10" height="10" rx="2" transform="rotate(45 361 240.5)" fill="{CYAN}" opacity=".85"/>
    <text x="75" y="280" font-family="{FONT_MONO}" font-size="20" letter-spacing=".6" fill="#a5f3fc"><tspan fill="{VIOLET}">&gt;</tspan> AI APPLICATION &amp; AGENT ENGINEER</text>
    <text x="76" y="314" font-family="{FONT_SANS}" font-size="18" letter-spacing=".4" fill="{SLATE}">AI 应用 / 智能体 · 资深全栈</text>
    <text x="76" y="344" font-family="{FONT_SANS}" font-size="18" letter-spacing=".4" fill="{SLATE}">把想法做成能上线的产品</text>
    {''.join(chips)}
    <g opacity=".92">
      <text x="600" y="118" font-family="{FONT_MONO}" font-size="13" letter-spacing="2.2" fill="{MUTED}">$ cat .focus</text>
      <text x="580" y="154" font-family="{FONT_MONO}" font-size="15.5" fill="#7c8aa5">├─ <tspan fill="#bae6fd">agents · mcp · rag</tspan></text>
      <text x="580" y="184" font-family="{FONT_MONO}" font-size="15.5" fill="#7c8aa5">├─ <tspan fill="#a5f3fc">desktop apps · tauri</tspan></text>
      <text x="580" y="214" font-family="{FONT_MONO}" font-size="15.5" fill="#7c8aa5">├─ <tspan fill="#f9a8d4">h5 games · canvas</tspan></text>
      <text x="580" y="244" font-family="{FONT_MONO}" font-size="15.5" fill="#7c8aa5">└─ <tspan fill="#c4b5fd">open to AI Agent roles</tspan></text>
      <text x="580" y="278" font-family="{FONT_MONO}" font-size="15.5" fill="{SLATE}"><tspan fill="{GREEN}">●</tspan> keep building.</text>
    </g>

    <!-- equalizer + labels -->
    <text x="862" y="300" font-family="{FONT_MONO}" font-size="13.5" letter-spacing="2.4" fill="{MUTED}">SIGNAL // AGENTS</text>
    <path d="M862 360 H1128" stroke="{SKY}" stroke-opacity=".18" stroke-width="1"/>
    {''.join(bars)}

    <!-- HUD status -->
    <g>
      <circle cx="856" cy="54" r="3.6" fill="{GREEN}"/>
      <circle cx="856" cy="54" r="8.5" fill="{GREEN}" opacity=".16" class="pulse"/>
      <text x="1128" y="59" font-family="{FONT_MONO}" font-size="14" letter-spacing="2.2" fill="#86efac" text-anchor="end">OPEN TO WORK · AI AGENT</text>
    </g>

    <!-- corner brackets -->
    <g stroke="{SKY}" stroke-opacity=".32" stroke-width="1.4" fill="none">
      <path d="M28 44 V28 H44"/>
      <path d="M1152 416 H1172 V396"/>
    </g>

    <!-- CRT / vignette / sweep -->
    <rect width="1200" height="440" fill="url(#scan)"/>
    <rect width="1200" height="440" fill="url(#vignette)"/>
    <rect x="0" y="0" width="1200" height="150" fill="url(#sweepFill)" opacity=".1" style="animation:sweep 9s linear infinite"/>
    <g transform="translate(1082 40) rotate(32)" style="animation:shoot 9s ease-in infinite">
      <path d="M0 0 L-170 92" stroke="{CYAN}" stroke-width="1.6" stroke-linecap="round" opacity=".85"/>
      <path d="M0 0 L-74 40" stroke="#f0f9ff" stroke-width="2.4" stroke-linecap="round"/>
    </g>
  </g>
  <rect x=".75" y=".75" width="1198.5" height="438.5" rx="20" fill="none" stroke="url(#borderFill)" stroke-width="1.5"/>
</svg>
"""
    return body


# --------------------------------------------------------------------------
# shared panel defs
# --------------------------------------------------------------------------


def panel_defs(Glow="#22d3ee", Glow2="#a78bfa"):
    return f"""
  <defs>
    <linearGradient id="pBg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#0a1020"/>
      <stop offset=".55" stop-color="#070b14"/>
      <stop offset="1" stop-color="#0a0713"/>
    </linearGradient>
    <linearGradient id="pBorder" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="{Glow}" stop-opacity=".55"/>
      <stop offset=".48" stop-color="{Glow2}" stop-opacity=".16"/>
      <stop offset="1" stop-color="#f472b6" stop-opacity=".42"/>
    </linearGradient>
    <linearGradient id="pAccent" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="{Glow}"/>
      <stop offset="1" stop-color="{Glow2}"/>
    </linearGradient>
    <linearGradient id="pLine" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="{Glow}" stop-opacity=".65"/>
      <stop offset=".4" stop-color="{Glow2}" stop-opacity=".3"/>
      <stop offset="1" stop-color="{Glow2}" stop-opacity="0"/>
    </linearGradient>
    <linearGradient id="pText" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#a5f3fc"/>
      <stop offset=".55" stop-color="{Glow}"/>
      <stop offset="1" stop-color="{Glow2}"/>
    </linearGradient>
  </defs>"""


def mono_w(text: str, size: float, ls: float = 0.0) -> float:
    return len(text) * (size * 0.6 + ls)


def sans_w(text: str, size: float) -> float:
    w = 0.0
    for ch in text:
        w += size if ord(ch) > 0x2E80 else size * 0.54
    return w


def wrap_px(text: str, size: float, max_w: float) -> list[str]:
    lines, cur = [], ""
    for ch in text:
        if sans_w(cur + ch, size) > max_w and cur:
            # try to break at last space
            if " " in cur:
                cut = cur.rfind(" ")
                head, tail = cur[:cut], cur[cut + 1 :]
                lines.append(head)
                cur = tail + ch
            else:
                lines.append(cur)
                cur = ch
        else:
            cur += ch
    if cur:
        lines.append(cur)
    return lines


def corner_brackets(W: int, H: int, pad: int = 28, size: int = 16, color: str = "#7dd3fc") -> str:
    """Decorative frame: top-left + bottom-right corner brackets."""
    tl = f'<path d="M{pad} {pad + size} V{pad} H{pad + size}" stroke="{color}" stroke-opacity=".38" stroke-width="1.4" fill="none"/>'
    br = f'<path d="M{W - pad} {H - pad - size} V{H - pad} H{W - pad - size}" stroke="{color}" stroke-opacity=".38" stroke-width="1.4" fill="none"/>'
    return tl + "\n  " + br


# --------------------------------------------------------------------------
# section divider pill
# --------------------------------------------------------------------------


def divider(idx: str, en: str, zh: str) -> str:
    w = 1200
    en_size, en_ls = 16.5, 2.0
    zh_size = 16.5
    idx_size = 14.5
    idx_w = mono_w(f"[ {idx} ]", idx_size, 1.4)
    en_w = mono_w(en, en_size, en_ls)
    zh_w = sans_w(zh, zh_size)
    pill_w = 20 + idx_w + 14 + en_w + 14 + zh_w + 22
    py, ph = 4, 52
    line_x = pill_w + 22
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="62" viewBox="0 0 {w} 62" role="img" aria-label="{esc(en)} · {esc(zh)}">
{panel_defs()}
  <rect x="0" y="{py}" width="{pill_w:.0f}" height="{ph}" rx="12" fill="#070b14" stroke="#1e293b" stroke-opacity=".9"/>
  <rect x="0.75" y="{py}.75" width="{pill_w - 1.5:.0f}" height="{ph - 1.5}" rx="11" fill="none" stroke="url(#pBorder)" stroke-opacity=".35"/>
  <rect x="0" y="{py + 12}" width="3" height="{ph - 24}" rx="1.5" fill="url(#pAccent)"/>
  <text x="20" y="{py + 33}" font-family="{FONT_MONO}" font-size="{idx_size}" letter-spacing="1.4" fill="#475569">[ {idx} ]</text>
  <text x="{20 + idx_w + 14:.1f}" y="{py + 34}" font-family="{FONT_MONO}" font-size="{en_size}" letter-spacing="{en_ls}" fill="#e2e8f0">{esc(en)}</text>
  <text x="{20 + idx_w + 14 + en_w + 14:.1f}" y="{py + 34}" font-family="{FONT_SANS}" font-size="{zh_size}" fill="#94a3b8">{esc(zh)}</text>
  <defs>
    <linearGradient id="dl" x1="{line_x + 12:.0f}" y1="0" x2="1188" y2="0" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="#22d3ee" stop-opacity=".55"/>
      <stop offset=".45" stop-color="#a78bfa" stop-opacity=".22"/>
      <stop offset="1" stop-color="#a78bfa" stop-opacity="0"/>
    </linearGradient>
  </defs>
  <path d="M{line_x + 12:.0f} {py + 30} H1188" stroke="url(#dl)" stroke-width="1.6"/>
  <rect x="{line_x + 1:.0f}" y="{py + 26.5}" width="7" height="7" rx="1.6" transform="rotate(45 {line_x + 4.5:.0f} {py + 30})" fill="#22d3ee" opacity=".7"/>
</svg>
"""


# --------------------------------------------------------------------------
# stack marquee
# --------------------------------------------------------------------------


def stack_marquee() -> str:
    W, H = 1200, 104
    skills = [
        # languages
        ("Java", "#f89820"), ("Python", "#facc15"), ("Go", "#22d3ee"),
        ("Rust", "#fb923c"), ("C#", "#a78bfa"), ("TypeScript", "#3b82f6"),
        ("JavaScript", "#f7df1e"),
        # backend
        ("Spring Boot", "#6db33f"), ("FastAPI", "#10b981"), ("Fastify", "#94a3b8"),
        # frontend / client
        ("React", "#61dafb"), ("Next.js", "#e2e8f0"), ("Vue", "#42b883"),
        ("uni-app", "#22d3ee"), ("Electron", "#9feaf9"), ("Tauri", "#ffc131"),
        ("Tailwind", "#38bdf8"), ("Bun", "#94a3b8"), ("Canvas 2D", "#fb923c"),
        # data
        ("PostgreSQL", "#5b8cba"), ("MySQL", "#4a90c2"), ("Redis", "#ff6b5b"),
        ("Qdrant", "#e879f9"),
        # AI
        ("LangChain", "#84cc16"), ("LangGraph", "#8b5cf6"), ("MCP", "#67e8f9"),
        ("RAG", "#fb7185"), ("Agent", "#c084fc"),
        # ops / quality
        ("Docker", "#38bdf8"), ("Linux", "#fbbf24"), ("Nginx", "#4ade80"),
        ("GitLab CI", "#fc6d26"), ("Playwright", "#2dd4bf"), ("Pytest", "#38bdf8"),
    ]
    chips, x = [], 0.0
    fs = 15.0
    for label, color in skills:
        tw = mono_w(label.upper(), fs, 1.0)
        cw = 14 + 12 + tw + 16
        chips.append(
            f'<g transform="translate({x:.1f} 0)">'
            f'<rect x="0" y="30" width="{cw:.1f}" height="40" rx="10" fill="#0a1224" stroke="#1e3a5f" stroke-opacity=".85"/>'
            f'<circle cx="18" cy="50" r="3.8" fill="{color}" opacity=".95"/>'
            f'<text x="29" y="55.5" font-family="{FONT_MONO}" font-size="{fs}" letter-spacing="1.0" fill="#d7e1ee">{esc(label.upper())}</text>'
            f'</g>'
        )
        x += cw + 12
    total = x
    group = "".join(chips) + f'<g transform="translate({total:.1f} 0)">' + "".join(chips) + "</g>"
    dur = total / 55.0
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Tech stack marquee">
{panel_defs()}
  <style>
    @keyframes marq {{ 0% {{ transform:translateX(0) }} 100% {{ transform:translateX(-{total:.1f}px) }} }}
    .mq {{ animation:marq {dur:.1f}s linear infinite; }}
  </style>
  <defs>
    <clipPath id="mqClip"><rect x="0.75" y="0.75" width="1198.5" height="{H - 1.5}" rx="18"/></clipPath>
    <mask id="fade">
      <linearGradient id="fadeGrad" x1="0" y1="0" x2="1" y2="0">
        <stop offset="0" stop-color="#000"/><stop offset=".09" stop-color="#fff"/>
        <stop offset=".91" stop-color="#fff"/><stop offset="1" stop-color="#000"/>
      </linearGradient>
      <rect width="1200" height="{H}" fill="url(#fadeGrad)"/>
    </mask>
    <linearGradient id="sl" x1="24" y1="0" x2="1176" y2="0" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="#22d3ee" stop-opacity=".5"/>
      <stop offset=".5" stop-color="#a78bfa" stop-opacity=".25"/>
      <stop offset="1" stop-color="#f472b6" stop-opacity=".12"/>
    </linearGradient>
  </defs>
  <rect x="0.75" y="0.75" width="1198.5" height="{H - 1.5}" rx="18" fill="url(#pBg)" stroke="url(#pBorder)" stroke-opacity=".45" stroke-width="1.5"/>
  {corner_brackets(W, H, pad=24, size=14)}
  <path d="M24 0.75 H1176" stroke="url(#sl)" stroke-width="1" opacity=".8"/>
  <g clip-path="url(#mqClip)"><g mask="url(#fade)"><g class="mq">{group}</g></g></g>
  <text x="24" y="90" font-family="{FONT_MONO}" font-size="14" letter-spacing="2.2" fill="#7c8aa5">STACK// 日常使用的技术栈 · AI 应用 / 全栈 / 图形与基础设施</text>
</svg>
"""


# --------------------------------------------------------------------------
# capability panel
# --------------------------------------------------------------------------


def capability_card() -> str:
    W, H = 1200, 360
    cols = [
        ("01", "AI AGENTS", "智能体", "#4ade80",
         ["智能体架构与云端部署", "MCP Server · Skills 工具链", "会话回放 · 归因 · 成本"]),
        ("02", "RAG", "知识库", "#67e8f9",
         ["混合检索 + RRF 重排", "文档处理 / 多租户", "权限与数据隔离"]),
        ("03", "FULL-STACK", "全栈 · 客户端", "#a78bfa",
         ["Java / Python / Go / Rust", "React / Next.js / Tauri", "自托管 · Docker 部署"]),
        ("04", "GRAPHICS", "图形 · 交互", "#fb923c",
         ["Rust / GPU 渲染引擎", "Canvas 2D · H5 游戏", "性能与稳定性"]),
    ]
    blocks = []
    x0, colw = 48, 268
    for i, (idx, en, cn, color, rows) in enumerate(cols):
        x = x0 + i * colw
        if i:
            blocks.append(f'<path d="M{x - 20} 96 V300" stroke="#1e293b" stroke-opacity=".8" stroke-width="1"/>')
        blocks.append(
            f'<text x="{x}" y="112" font-family="{FONT_MONO}" font-size="13" letter-spacing="2.2" fill="{color}" opacity=".85">{idx}</text>'
            f'<text x="{x}" y="150" font-family="{FONT_SANS}" font-size="21" font-weight="700" fill="#e6edf7">{cn}</text>'
            f'<text x="{x}" y="172" font-family="{FONT_MONO}" font-size="12.5" letter-spacing="2" fill="#7c8aa5">{en}</text>'
        )
        for j, row in enumerate(rows):
            blocks.append(
                f'<circle cx="{x + 3}" cy="{201 + j * 34}" r="2.8" fill="{color}" opacity=".85"/>'
                f'<text x="{x + 15}" y="{206 + j * 34}" font-family="{FONT_SANS}" font-size="15.5" fill="#b6c2d4">{esc(row)}</text>'
            )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="What I do: AI agents, RAG, full-stack and clients, graphics">
{panel_defs()}
  <rect x="0.75" y="0.75" width="{W - 1.5}" height="{H - 1.5}" rx="18" fill="url(#pBg)" stroke="url(#pBorder)" stroke-opacity=".45" stroke-width="1.5"/>
  {corner_brackets(W, H)}
  <text x="48" y="48" font-family="{FONT_MONO}" font-size="14" letter-spacing="2.8" fill="#67e8f9" opacity=".8">// WHAT I DO · 能力地图</text>
  <text x="1152" y="48" font-family="{FONT_MONO}" font-size="12.5" letter-spacing="1.6" fill="#7c8aa5" text-anchor="end">从架构到上线 · END-TO-END</text>
  <path d="M48 70 H1152" stroke="#22d3ee" stroke-opacity=".12" stroke-width="1"/>
  {''.join(blocks)}
  <text x="48" y="330" font-family="{FONT_MONO}" font-size="12.5" letter-spacing="1.2" fill="#8fa0b8">一边交付，一边把工具造得更好用 · DELIVER &amp; BUILD</text>
</svg>
"""


# --------------------------------------------------------------------------
# stack matrix
# --------------------------------------------------------------------------


def stack_matrix() -> str:
    W, H = 1200, 500
    rows = [
        ("AI 应用", "AI APPLICATION", "#4ade80",
         ["智能体架构", "云端部署", "RAG", "混合检索 + RRF", "LangChain", "LangGraph", "MCP Server"]),
        ("后端", "BACKEND", "#67e8f9",
         ["Java", "Spring Boot", "Spring Cloud", "Python", "FastAPI", "Go", "Rust", "C#", "Node.js", "Fastify"]),
        ("前端 / 客户端", "FRONTEND / CLIENT", "#a78bfa",
         ["React", "Next.js", "Vue", "uni-app", "Electron", "Tauri", "Tailwind CSS", "Canvas 2D", "Bun"]),
        ("数据 & 基建", "DATA / INFRA", "#38bdf8",
         ["PostgreSQL", "MySQL", "Redis", "Qdrant", "Drizzle", "Docker", "Linux", "Nginx", "Prometheus", "OpenTelemetry"]),
        ("图形 & 质量", "GRAPHICS / QA", "#fb923c",
         ["Skia / Skottie", "Metal", "Vulkan", "CUDA", "FFmpeg", "Pytest", "Vitest", "Playwright"]),
    ]
    fs = 14.5
    blocks = []
    for ri, (cn, en, color, items) in enumerate(rows):
        y = 120 + ri * 72
        if ri % 2 == 0:
            blocks.append(f'<rect x="24" y="{y - 36}" width="1152" height="66" rx="12" fill="#0a1224" fill-opacity=".55"/>')
        blocks.append(f'<rect x="40" y="{y - 26}" width="3" height="32" rx="1.5" fill="{color}"/>')
        blocks.append(
            f'<text x="58" y="{y - 4}" font-family="{FONT_SANS}" font-size="17" font-weight="600" fill="#e6edf7">{esc(cn)}</text>'
            f'<text x="58" y="{y + 16}" font-family="{FONT_MONO}" font-size="13.5" letter-spacing="1.6" fill="#7c8aa5">{esc(en)}</text>'
        )
        x = 220.0
        for item in items:
            tw = sans_w(item, fs)
            cw = 22 + tw + 12
            blocks.append(
                f'<g transform="translate({x:.1f} 0)">'
                f'<rect x="0" y="{y - 27}" width="{cw:.1f}" height="32" rx="8" fill="{color}" fill-opacity=".08" stroke="{color}" stroke-opacity=".32"/>'
                f'<circle cx="12" cy="{y - 11}" r="2.8" fill="{color}" opacity=".9"/>'
                f'<text x="21" y="{y - 5}" font-family="{FONT_SANS}" font-size="{fs}" fill="#d7e1ee">{esc(item)}</text>'
                f'</g>'
            )
            x += cw + 6
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Stack matrix: AI application, backend, frontend, data, graphics">
{panel_defs()}
  <rect x="0.75" y="0.75" width="{W - 1.5}" height="{H - 1.5}" rx="18" fill="url(#pBg)" stroke="url(#pBorder)" stroke-opacity=".45" stroke-width="1.5"/>
  {corner_brackets(W, H)}
  <text x="48" y="48" font-family="{FONT_MONO}" font-size="14" letter-spacing="2.8" fill="#67e8f9" opacity=".8">// STACK MATRIX · 技术栈</text>
  <text x="1152" y="48" font-family="{FONT_MONO}" font-size="13.5" letter-spacing="1.6" fill="#7c8aa5" text-anchor="end">日常在用 · BATTLE-TESTED</text>
  <path d="M48 70 H1152" stroke="#22d3ee" stroke-opacity=".12" stroke-width="1"/>
  {''.join(blocks)}
  <text x="48" y="470" font-family="{FONT_MONO}" font-size="14" letter-spacing="1.2" fill="#8fa0b8">按场景分组 · GROUPED BY SCENARIO</text>
</svg>
"""


# --------------------------------------------------------------------------
# featured open-source card
# --------------------------------------------------------------------------


def project_card(index: str, name: str, cn: str, en: str, tag: str, tag_color: str,
                 meta: str, aria: str) -> str:
    """Compact clickable project card, 2-up grid (584 px wide)."""
    W, H = 584, 204
    tag_w = mono_w(tag, 12, 1.3) + 26
    tag_x = W - 28 - tag_w
    name_size = 28 if sans_w(name, 28) <= 470 else 24
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{esc(aria)}">
{panel_defs()}
  <rect x="0.75" y="0.75" width="{W - 1.5}" height="{H - 1.5}" rx="16" fill="url(#pBg)" stroke="url(#pBorder)" stroke-opacity=".5" stroke-width="1.5"/>
  {corner_brackets(W, H, pad=22, size=14)}
  <text x="30" y="42" font-family="{FONT_MONO}" font-size="12.5" letter-spacing="2.2" fill="#8fa0b8">{esc(index)}</text>
  <g transform="translate({tag_x:.0f} 26)">
    <rect x="0" y="0" width="{tag_w:.0f}" height="24" rx="7" fill="{tag_color}" fill-opacity=".12" stroke="{tag_color}" stroke-opacity=".45"/>
    <text x="{tag_w / 2:.0f}" y="16.5" font-family="{FONT_MONO}" font-size="12" letter-spacing="1.3" fill="{tag_color}" text-anchor="middle">{esc(tag)}</text>
  </g>
  <text x="30" y="88" font-family="{FONT_SANS}" font-size="{name_size}" font-weight="700" fill="#e6edf7" letter-spacing=".2">{esc(name)}</text>
  <text x="30" y="124" font-family="{FONT_SANS}" font-size="16" fill="#cbd5e1">{esc(cn)}</text>
  <text x="30" y="148" font-family="{FONT_SANS}" font-size="13.5" fill="#a8b3c7">{esc(en)}</text>
  <path d="M30 166 H520" stroke="#22d3ee" stroke-opacity=".1" stroke-width="1"/>
  <text x="30" y="190" font-family="{FONT_MONO}" font-size="13" letter-spacing=".8" fill="#8fa0b8">{esc(meta)}</text>
  <text x="536" y="191" font-family="{FONT_MONO}" font-size="17" fill="url(#pText)" text-anchor="end">↗</text>
</svg>
"""


# --------------------------------------------------------------------------
# footer
# --------------------------------------------------------------------------


def footer() -> str:
    W, H = 1200, 160
    title = "THANKS FOR VISITING · 感谢到访"
    tw = mono_w(title, 15, 3.2)
    cx = W / 2
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Thanks for visiting">
{panel_defs()}
  <style>
    @keyframes dash {{ 0% {{ stroke-dashoffset:0 }} 100% {{ stroke-dashoffset:-160 }} }}
    @keyframes blink {{ 0%,49% {{ opacity:1 }} 50%,100% {{ opacity:0 }} }}
    .flow {{ animation:dash 6s linear infinite }}
    .cur {{ animation:blink 1.1s steps(1,end) infinite }}
  </style>
  <rect x="0.75" y="0.75" width="{W - 1.5}" height="{H - 1.5}" rx="18" fill="url(#pBg)" stroke="url(#pBorder)" stroke-opacity=".45" stroke-width="1.5"/>
  {corner_brackets(W, H, pad=28, size=15)}
  <defs>
    <linearGradient id="fl" x1="56" y1="0" x2="1160" y2="0" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="#22d3ee" stop-opacity=".05"/>
      <stop offset=".25" stop-color="#22d3ee" stop-opacity=".5"/>
      <stop offset=".75" stop-color="#a78bfa" stop-opacity=".35"/>
      <stop offset="1" stop-color="#f472b6" stop-opacity=".05"/>
    </linearGradient>
  </defs>
  <path class="flow" d="M56 26 H1160" stroke="url(#fl)" stroke-width="1.4" stroke-dasharray="10 22"/>
  <text x="{cx:.0f}" y="78" font-family="{FONT_MONO}" font-size="15" letter-spacing="3.2" fill="#cbd5e1" text-anchor="middle">{esc(title)}</text>
  <rect x="{cx + tw / 2 + 9:.1f}" y="64" width="7" height="17" rx="2" fill="#67e8f9" class="cur"/>
  <text x="{cx:.0f}" y="108" font-family="{FONT_MONO}" font-size="14" letter-spacing="2" fill="#8fa0b8" text-anchor="middle">FULL-STACK · AI APPLICATIONS · 2026</text>
  <text x="48" y="140" font-family="{FONT_MONO}" font-size="14" letter-spacing="1.2" fill="#7c8aa5">© 2026 JASPER</text>
  <text x="1136" y="140" font-family="{FONT_MONO}" font-size="14" letter-spacing="1.2" fill="#7c8aa5" text-anchor="end">EOF // SIGNAL ENDS</text>
  <g fill="#67e8f9">
    <circle cx="588" cy="140" r="2.2" opacity=".35"/><circle cx="600" cy="140" r="2.2" opacity=".25"/><circle cx="612" cy="140" r="2.2" opacity=".15"/>
  </g>
</svg>
"""


def main() -> None:
    print("generating neon assets …")
    write("hero.svg", hero())
    write("footer.svg", footer())
    write("divider-about.svg", divider("01", "ABOUT ME", "关于我"))
    write("divider-whatido.svg", divider("02", "WHAT I DO", "我在做什么"))
    write("divider-opensource.svg", divider("03", "OPEN SOURCE", "开源作品"))
    write("divider-stack.svg", divider("04", "STACK", "技术栈"))
    write("divider-connect.svg", divider("05", "CONNECT", "联系"))
    write("capability.svg", capability_card())
    write("stack.svg", stack_marquee())
    write("stack-matrix.svg", stack_matrix())

    projects = [
        dict(
            name="feronavi",
            cn="为人和 Agent 而生的开源项目协作平台，内置 RAG 与 MCP。",
            en="Self-hosted collaboration workspace with built-in RAG and MCP.",
            tag="MCP · RAG", tag_color="#4ade80",
            meta="TypeScript · AGPL-3.0 · 自托管",
            aria="feronavi — self-hosted collaboration workspace with RAG and MCP",
        ),
        dict(
            name="PP-Clash",
            cn="开箱即用的跨平台 Clash 客户端：Tauri + mihomo。",
            en="Cross-platform Clash client built with Tauri and mihomo.",
            tag="DESKTOP", tag_color="#fb923c",
            meta="TypeScript · AGPL-3.0 · v0.2.2",
            aria="PP-Clash — cross-platform Clash client built with Tauri and mihomo",
        ),
        dict(
            name="marble-wreckers",
            cn="弹珠拆迁队：论坛水楼题材的弹珠 Roguelike。",
            en="Marble Wreckers — a marble roguelike that runs in the browser.",
            tag="GAME", tag_color="#f472b6",
            meta="TypeScript · Canvas 2D · H5",
            aria="marble-wreckers — a marble roguelike browser game",
        ),
        dict(
            name="agent-blackbox",
            cn="AI 编程 agent 的飞行记录仪：回放、归因、对比。",
            en="Flight recorder for coding agents — replay, attribution, diff.",
            tag="AGENT", tag_color="#67e8f9",
            meta="TypeScript · MIT · 6 ★",
            aria="agent-blackbox — local-first flight recorder for AI coding agents",
        ),
        dict(
            name="dsh-mcp-skills-board",
            cn="DSH 的 MCP / 技能管理面板，四态开关与模板。",
            en="MCP and Skills panel for DeepSeek Harness.",
            tag="DSH PLUGIN", tag_color="#a78bfa",
            meta="JavaScript · MIT · npm 0.3.0",
            aria="dsh-mcp-skills-board — MCP and Skills panel for DeepSeek Harness",
        ),
        dict(
            name="dsh-agent-blackbox",
            cn="把 agent-blackbox 装进 DSH 侧栏的官方插件。",
            en="DSH plugin: the blackbox dashboard inside the sidebar.",
            tag="DSH PLUGIN", tag_color="#a78bfa",
            meta="JavaScript · npm 0.1.2",
            aria="dsh-agent-blackbox — DSH plugin for the agent-blackbox dashboard",
        ),
    ]
    for i, pr in enumerate(projects, start=1):
        write(f"proj-{pr['name'].lower()}.svg", project_card(index=f"{i:02d}", **pr))


if __name__ == "__main__":
    main()
