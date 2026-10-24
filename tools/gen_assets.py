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
    <clipPath id="cardClip"><rect width="1200" height="340" rx="20"/></clipPath>
    <clipPath id="globeClip"><circle cx="985" cy="150" r="74"/></clipPath>
  </defs>"""


def hero() -> str:
    rnd = random.Random(20261024)
    w, h = 1200, 340

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
    for cx, cy, s, dur, delay in [
        (232, 74, 6.5, 5.2, -1.1),
        (1180, 248, 5.2, 4.4, -3.2),
        (806, 58, 4.4, 6.1, -0.4),
        (140, 268, 4.0, 5.6, -2.7),
    ]:
        sparkles.append(
            f'<path d="M{cx} {cy - s} Q{cx} {cy} {cx + s} {cy} Q{cx} {cy} {cx} {cy + s} '
            f'Q{cx} {cy} {cx - s} {cy} Q{cx} {cy} {cx} {cy - s}Z" fill="#cffafe" '
            f'opacity=".75" style="animation:twinkle {dur:.1f}s ease-in-out {delay:.1f}s infinite"/>'
        )

    chips = []
    chip_labels = ["JAVA", "PYTHON", "GO", "RUST", "TYPESCRIPT"]
    chip_colors = ["#f89820", "#facc15", CYAN, "#fb923c", "#3b82f6"]
    x = 74
    for label, color in zip(chip_labels, chip_colors):
        width = 8.4 * len(label) + 22
        chips.append(
            f'<g><rect x="{x:.0f}" y="296" width="{width:.0f}" height="26" rx="7" '
            f'fill="#0a1224" stroke="#1e3a5f" stroke-opacity=".9"/>'
            f'<circle cx="{x + 12:.0f}" cy="309" r="2.6" fill="{color}"/>'
            f'<text x="{x + 21:.0f}" y="313.5" font-family="{FONT_MONO}" font-size="10.5" '
            f'letter-spacing="1.4" fill="#cbd5e1">{label}</text></g>'
        )
        x += width + 10

    bars = []
    bx = 862
    for i in range(18):
        bh = 7 + (math.sin(i * 0.9) * 0.5 + rnd.random() * 0.6) * 24
        delay = -rnd.uniform(0, 2.4)
        dur = rnd.uniform(1.4, 2.6)
        bars.append(
            f'<rect x="{bx + i * 14.5:.1f}" y="{302 - bh:.1f}" width="5.5" height="{bh:.1f}" rx="2.6" '
            f'fill="url(#barFill)" opacity=".85" '
            f'style="transform-box:fill-box;transform-origin:50% 100%;animation:eq {dur:.2f}s ease-in-out {delay:.2f}s infinite"/>'
        )

    body = f"""<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="340" viewBox="0 0 1200 340" role="img" aria-labelledby="heroTitle heroDesc">
  <title id="heroTitle">Jasper — AI Agent Tooling · DeepSeek Harness Ecosystem</title>
  <desc id="heroDesc">Neon deep-space banner: JASPER, AI agent tooling, DSH ecosystem, open source.</desc>
{hero_defs()}
  <style>
    @keyframes twinkle {{ 0%,100% {{ opacity:.14 }} 50% {{ opacity:.95 }} }}
    @keyframes sweep {{ 0% {{ transform:translateY(-140px) }} 100% {{ transform:translateY(380px) }} }}
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
    <rect width="1200" height="340" fill="url(#bgFill)"/>
    <rect width="1200" height="340" fill="url(#auroraCyan)"/>
    <rect width="1200" height="340" fill="url(#auroraViolet)"/>
    <rect width="1200" height="340" fill="url(#auroraPink)"/>
    <rect width="1200" height="340" fill="url(#grid)" opacity=".55"/>
    {''.join(stars)}
    {''.join(sparkles)}

    <!-- hologram globe -->
    <circle cx="985" cy="150" r="182" fill="url(#orbHalo)"/>
    <g clip-path="url(#globeClip)">
      <circle cx="985" cy="150" r="74" fill="url(#orbFill)"/>
      <g fill="none" stroke="{CYAN}" stroke-opacity=".22" stroke-width=".8">
        <ellipse cx="985" cy="150" rx="74" ry="24"/>
        <ellipse cx="985" cy="150" rx="74" ry="49"/>
        <ellipse cx="985" cy="150" rx="74" ry="73"/>
        <ellipse cx="985" cy="150" rx="24" ry="74"/>
        <ellipse cx="985" cy="150" rx="49" ry="74"/>
        <ellipse cx="985" cy="150" rx="73" ry="74"/>
      </g>
      <circle cx="985" cy="150" r="74" fill="none" stroke="{SKY}" stroke-opacity=".5" stroke-width="1.1"/>
    </g>
    <g transform="rotate(-18 985 150)">
      <ellipse cx="985" cy="150" rx="126" ry="38" fill="none" stroke="url(#ringFill)" stroke-width="1.3" stroke-dasharray="5 9"/>
      <ellipse cx="985" cy="150" rx="107" ry="30" fill="none" stroke="url(#ringFill)" stroke-width="1" stroke-dasharray="3 7" opacity=".8"/>
      <ellipse cx="985" cy="150" rx="88" ry="22" fill="none" stroke="url(#ringFill)" stroke-width=".9" stroke-dasharray="2 6" opacity=".65"/>
      <circle r="3.4" fill="#e0f2fe">
        <animateMotion dur="13s" repeatCount="indefinite" path="M859,150 a126,38 0 1,1 252,0 a126,38 0 1,1 -252,0"/>
      </circle>
      <circle r="9" fill="{CYAN}" opacity=".16">
        <animateMotion dur="13s" repeatCount="indefinite" path="M859,150 a126,38 0 1,1 252,0 a126,38 0 1,1 -252,0"/>
      </circle>
      <circle r="2.4" fill="{PINK}">
        <animateMotion dur="19s" repeatCount="indefinite" path="M878,150 a107,30 0 1,1 214,0 a107,30 0 1,1 -214,0" keyPoints="1;0" keyTimes="0;1" calcMode="linear"/>
      </circle>
    </g>
    <circle cx="985" cy="150" r="112" fill="none" stroke="{VIOLET}" stroke-opacity=".16" stroke-width=".8" stroke-dasharray="2 12"/>
    <circle cx="985" cy="150" r="112" fill="none" stroke="{SKY}" stroke-opacity=".08" stroke-width="8" class="pulse"/>

    <!-- terminal headline block -->
    <rect x="56" y="82" width="2.2" height="218" rx="1.1" fill="url(#edgeFill)"/>
    <rect x="52.6" y="82" width="9" height="9" rx="2" fill="{TEAL}" opacity=".9" style="animation:blink 2.4s steps(1,end) infinite"/>
    <rect x="52.6" y="291" width="9" height="9" rx="2" fill="{VIOLET}" opacity=".75"/>
    <text x="80" y="100" font-family="{FONT_MONO}" font-size="11.5" letter-spacing="3.2" fill="{CYAN}" opacity=".72">// PROFILE.SYS · AI APPLICATION ENGINEER</text>
    <text x="72" y="192" font-family="{FONT_SANS}" font-size="88" font-weight="800" letter-spacing="7" fill="{CYAN}" opacity=".5" filter="url(#soft2)">JASPER</text>
    <text x="72" y="192" font-family="{FONT_SANS}" font-size="88" font-weight="800" letter-spacing="7" fill="url(#titleFill)">JASPER</text>
    <path d="M75 215 H336" stroke="url(#lineFill)" stroke-width="1.6"/>
    <rect x="334" y="210.5" width="9" height="9" rx="2" transform="rotate(45 338.5 215)" fill="{CYAN}" opacity=".85"/>
    <text x="75" y="249" font-family="{FONT_MONO}" font-size="17" letter-spacing=".6" fill="#a5f3fc"><tspan fill="{VIOLET}">&gt;</tspan> AI APPLICATION &amp; AGENT ENGINEER</text>
    <text x="76" y="277" font-family="{FONT_SANS}" font-size="15.5" letter-spacing=".4" fill="{SLATE}">AI 应用 / 智能体 · 资深全栈 · 把想法做成能上线的产品</text>
    {''.join(chips)}
    <g opacity=".92">
      <text x="600" y="118" font-family="{FONT_MONO}" font-size="10" letter-spacing="2.4" fill="{MUTED}">$ cat .now</text>
      <text x="580" y="145" font-family="{FONT_MONO}" font-size="12.5" fill="#7c8aa5">├─ <tspan fill="#bae6fd">agent-blackbox</tspan> <tspan fill="#475569">(MIT)</tspan></text>
      <text x="580" y="168" font-family="{FONT_MONO}" font-size="12.5" fill="#7c8aa5">├─ <tspan fill="#c4b5fd">dsh-mcp-skills-board</tspan> <tspan fill="#475569">(MIT)</tspan></text>
      <text x="580" y="191" font-family="{FONT_MONO}" font-size="12.5" fill="#7c8aa5">└─ <tspan fill="#f9a8d4">open to AI Agent roles</tspan></text>
      <text x="580" y="214" font-family="{FONT_MONO}" font-size="12.5" fill="{SLATE}"><tspan fill="{GREEN}">●</tspan> keep building.</text>
    </g>
    <rect x="866" y="292" width="5.5" height="1.6" fill="#0b1220"/>

    <!-- equalizer + labels -->
    <text x="862" y="268" font-family="{FONT_MONO}" font-size="10" letter-spacing="2.6" fill="{MUTED}">SIGNAL // AGENTS</text>
    <path d="M862 302 H1128" stroke="{SKY}" stroke-opacity=".18" stroke-width="1"/>
    {''.join(bars)}

    <!-- HUD status -->
    <g>
      <circle cx="925" cy="52" r="3.1" fill="{GREEN}"/>
      <circle cx="925" cy="52" r="7.5" fill="{GREEN}" opacity=".16" class="pulse"/>
      <text x="1128" y="56" font-family="{FONT_MONO}" font-size="10.5" letter-spacing="2.2" fill="#86efac" text-anchor="end">OPEN TO WORK · AI AGENT</text>
    </g>

    <!-- corner brackets -->
    <g stroke="{SKY}" stroke-opacity=".32" stroke-width="1.2" fill="none">
      <path d="M28 44 V28 H44"/>
      <path d="M1152 314 H1172 V294"/>
    </g>

    <!-- CRT / vignette / sweep -->
    <rect width="1200" height="340" fill="url(#scan)"/>
    <rect width="1200" height="340" fill="url(#vignette)"/>
    <rect x="0" y="0" width="1200" height="130" fill="url(#sweepFill)" opacity=".1" style="animation:sweep 9s linear infinite"/>
    <g transform="translate(1082 34) rotate(32)" style="animation:shoot 9s ease-in infinite">
      <path d="M0 0 L-170 92" stroke="{CYAN}" stroke-width="1.6" stroke-linecap="round" opacity=".85"/>
      <path d="M0 0 L-74 40" stroke="#f0f9ff" stroke-width="2.4" stroke-linecap="round"/>
    </g>
  </g>
  <rect x=".75" y=".75" width="1198.5" height="338.5" rx="20" fill="none" stroke="url(#borderFill)" stroke-width="1.5"/>
</svg>
"""
    very_long = body
    return very_long


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
    en_size, en_ls = 13, 2.2
    zh_size = 13
    idx_size = 11
    idx_w = mono_w(f"[ {idx} ]", idx_size, 1.6)
    en_w = mono_w(en, en_size, en_ls)
    zh_w = sans_w(zh, zh_size)
    pill_w = 18 + idx_w + 14 + en_w + 14 + zh_w + 20
    py, ph = 4, 42
    line_x = pill_w + 20
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="50" viewBox="0 0 {w} 50" role="img" aria-label="{esc(en)} · {esc(zh)}">
{panel_defs()}
  <rect x="0" y="{py}" width="{pill_w:.0f}" height="{ph}" rx="10" fill="#070b14" stroke="#1e293b" stroke-opacity=".9"/>
  <rect x="0.75" y="{py}.75" width="{w - 1.5 if False else pill_w - 1.5:.0f}" height="{ph - 1.5}" rx="9" fill="none" stroke="url(#pBorder)" stroke-opacity=".35"/>
  <rect x="0" y="{py + 9}" width="3" height="{ph - 18}" rx="1.5" fill="url(#pAccent)"/>
  <text x="18" y="{py + 25}" font-family="{FONT_MONO}" font-size="{idx_size}" letter-spacing="1.6" fill="#475569">[ {idx} ]</text>
  <text x="{18 + idx_w + 14:.1f}" y="{py + 26}" font-family="{FONT_MONO}" font-size="{en_size}" letter-spacing="{en_ls}" fill="#e2e8f0">{esc(en)}</text>
  <text x="{18 + idx_w + 14 + en_w + 14:.1f}" y="{py + 26}" font-family="{FONT_SANS}" font-size="{zh_size}" fill="#94a3b8">{esc(zh)}</text>
  <defs>
    <linearGradient id="dl" x1="{line_x + 10:.0f}" y1="0" x2="1188" y2="0" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="#22d3ee" stop-opacity=".55"/>
      <stop offset=".45" stop-color="#a78bfa" stop-opacity=".22"/>
      <stop offset="1" stop-color="#a78bfa" stop-opacity="0"/>
    </linearGradient>
  </defs>
  <path d="M{line_x + 10:.0f} {py + 24} H1188" stroke="url(#dl)" stroke-width="1.4"/>
  <rect x="{line_x + 1:.0f}" y="{py + 21}" width="6" height="6" rx="1.5" transform="rotate(45 {line_x + 4:.0f} {py + 24})" fill="#22d3ee" opacity=".7"/>
</svg>
"""


# --------------------------------------------------------------------------
# stack marquee
# --------------------------------------------------------------------------


def stack_marquee() -> str:
    W, H = 1200, 86
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
        ("Tailwind", "#38bdf8"),
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
    fs = 12.0
    for label, color in skills:
        tw = mono_w(label.upper(), fs, 1.1)
        cw = 12 + 12 + tw + 14
        chips.append(
            f'<g transform="translate({x:.1f} 0)">'
            f'<rect x="0" y="26" width="{cw:.1f}" height="33" rx="9" fill="#0a1224" stroke="#1e3a5f" stroke-opacity=".85"/>'
            f'<circle cx="16" cy="42.5" r="3.2" fill="{color}" opacity=".95"/>'
            f'<text x="25" y="46.5" font-family="{FONT_MONO}" font-size="{fs}" letter-spacing="1.1" fill="#cbd5e1">{esc(label.upper())}</text>'
            f'</g>'
        )
        x += cw + 12
    total = x
    group = "".join(chips) + f'<g transform="translate({total:.1f} 0)">' + "".join(chips) + "</g>"
    dur = total / 55.0
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="{H}" viewBox="0 0 1200 {H}" role="img" aria-label="Tech stack marquee">
{panel_defs()}
  <style>
    @keyframes marq {{ 0% {{ transform:translateX(0) }} 100% {{ transform:translateX(-{total:.1f}px) }} }}
    .mq {{ animation:marq {dur:.1f}s linear infinite; }}
  </style>
  <defs>
    <clipPath id="mqClip"><rect x="0.75" y="0.75" width="1198.5" height="{H - 1.5}" rx="16"/></clipPath>
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
  <rect x="0.75" y="0.75" width="1198.5" height="{H - 1.5}" rx="16" fill="url(#pBg)" stroke="url(#pBorder)" stroke-opacity=".45" stroke-width="1.5"/>
  {corner_brackets(W, H, pad=22, size=13)}
  <path d="M24 0.75 H1176" stroke="url(#sl)" stroke-width="1" opacity=".8"/>
  <g clip-path="url(#mqClip)"><g mask="url(#fade)"><g class="mq">{group}</g></g></g>
  <text x="24" y="72" font-family="{FONT_MONO}" font-size="9.5" letter-spacing="2.4" fill="#475569">STACK// 日常使用的技术栈 · AI 应用 / 全栈 / 图形与基础设施</text>
</svg>
"""


# --------------------------------------------------------------------------
# capability panel
# --------------------------------------------------------------------------


def capability_card() -> str:
    W, H = 1200, 320
    cols = [
        ("01", "AI AGENTS", "智能体", "#4ade80",
         ["智能体架构与云端部署", "MCP Server · Skills 工具链", "多 Agent 协作 · 可观测性"]),
        ("02", "RAG", "知识库", "#67e8f9",
         ["混合检索 + RRF 重排", "文档处理 / 多租户", "权限与数据隔离"]),
        ("03", "FULL-STACK", "全栈交付", "#a78bfa",
         ["Java / Python / Go / Rust", "React / Next.js / Tauri", "架构 · 上线 · 维护"]),
        ("04", "GRAPHICS", "图形渲染", "#fb923c",
         ["Rust / GPU 渲染引擎", "音视频与跨语言接入", "性能与稳定性"]),
    ]
    blocks = []
    x0, colw = 48, 268
    for i, (idx, en, cn, color, rows) in enumerate(cols):
        x = x0 + i * colw
        if i:
            blocks.append(f'<path d="M{x - 20} 92 V276" stroke="#1e293b" stroke-opacity=".8" stroke-width="1"/>')
        blocks.append(
            f'<text x="{x}" y="106" font-family="{FONT_MONO}" font-size="10" letter-spacing="2.4" fill="{color}" opacity=".85">{idx}</text>'
            f'<text x="{x}" y="140" font-family="{FONT_SANS}" font-size="17" font-weight="700" fill="#e6edf7">{cn}</text>'
            f'<text x="{x}" y="160" font-family="{FONT_MONO}" font-size="9.5" letter-spacing="2.2" fill="#7c8aa5">{en}</text>'
        )
        for j, row in enumerate(rows):
            blocks.append(
                f'<circle cx="{x + 3}" cy="{192 + j * 27}" r="2.6" fill="{color}" opacity=".85"/>'
                f'<text x="{x + 14}" y="{195 + j * 27}" font-family="{FONT_SANS}" font-size="12" fill="#b6c2d4">{esc(row)}</text>'
            )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="What I do: AI agents, RAG, full-stack, graphics">
{panel_defs()}
  <rect x="0.75" y="0.75" width="{W - 1.5}" height="{H - 1.5}" rx="18" fill="url(#pBg)" stroke="url(#pBorder)" stroke-opacity=".45" stroke-width="1.5"/>
  {corner_brackets(W, H)}
  <text x="48" y="46" font-family="{FONT_MONO}" font-size="11" letter-spacing="3.2" fill="#67e8f9" opacity=".8">// WHAT I DO · 能力地图</text>
  <text x="1152" y="46" font-family="{FONT_MONO}" font-size="9" letter-spacing="1.8" fill="#7c8aa5" text-anchor="end">从架构到上线 · END-TO-END</text>
  <path d="M48 66 H1152" stroke="#22d3ee" stroke-opacity=".12" stroke-width="1"/>
  {''.join(blocks)}
  <text x="48" y="302" font-family="{FONT_MONO}" font-size="9" letter-spacing="1.4" fill="#8fa0b8">一边交付，一边把工具造得更好用 · DELIVER &amp; BUILD</text>
</svg>
"""


# --------------------------------------------------------------------------
# stack matrix
# --------------------------------------------------------------------------


def stack_matrix() -> str:
    W, H = 1200, 400
    rows = [
        ("AI 应用", "AI APPLICATION", "#4ade80",
         ["智能体架构", "云端部署", "RAG", "混合检索 + RRF", "LangChain", "LangGraph", "MCP Server"]),
        ("后端", "BACKEND", "#67e8f9",
         ["Java", "Spring Boot", "Spring Cloud", "Python", "FastAPI", "Go", "Rust", "C#", "Node.js", "Fastify"]),
        ("前端 / 客户端", "FRONTEND", "#a78bfa",
         ["React", "Next.js", "Vue", "uni-app", "Electron", "Tauri", "Tailwind CSS"]),
        ("数据 & 基建", "DATA / INFRA", "#38bdf8",
         ["PostgreSQL", "MySQL", "Redis", "Qdrant", "Docker", "Linux", "Nginx", "Prometheus", "OpenTelemetry"]),
        ("图形 & 质量", "GRAPHICS / QA", "#fb923c",
         ["Skia / Skottie", "Metal", "Vulkan", "CUDA", "FFmpeg", "Pytest", "Vitest", "Playwright"]),
    ]
    fs = 11.5
    blocks = []
    for ri, (cn, en, color, items) in enumerate(rows):
        y = 110 + ri * 57
        if ri % 2 == 0:
            blocks.append(f'<rect x="24" y="{y - 31}" width="1152" height="54" rx="10" fill="#0a1224" fill-opacity=".55"/>')
        blocks.append(f'<rect x="40" y="{y - 22}" width="2.6" height="26" rx="1.3" fill="{color}"/>')
        blocks.append(
            f'<text x="56" y="{y - 2}" font-family="{FONT_SANS}" font-size="13.5" font-weight="600" fill="#e6edf7">{esc(cn)}</text>'
            f'<text x="56" y="{y + 15}" font-family="{FONT_MONO}" font-size="8.5" letter-spacing="1.8" fill="#7c8aa5">{esc(en)}</text>'
        )
        x = 216.0
        for item in items:
            tw = sans_w(item, fs)
            cw = 24 + tw + 14
            blocks.append(
                f'<g transform="translate({x:.1f} 0)">'
                f'<rect x="0" y="{y - 22}" width="{cw:.1f}" height="26" rx="7" fill="{color}" fill-opacity=".08" stroke="{color}" stroke-opacity=".32"/>'
                f'<circle cx="12" cy="{y - 9}" r="2.5" fill="{color}" opacity=".9"/>'
                f'<text x="21" y="{y - 4}" font-family="{FONT_SANS}" font-size="{fs}" fill="#d7e1ee">{esc(item)}</text>'
                f'</g>'
            )
            x += cw + 8
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Stack matrix: AI application, backend, frontend, data, graphics">
{panel_defs()}
  <rect x="0.75" y="0.75" width="{W - 1.5}" height="{H - 1.5}" rx="18" fill="url(#pBg)" stroke="url(#pBorder)" stroke-opacity=".45" stroke-width="1.5"/>
  {corner_brackets(W, H)}
  <text x="48" y="46" font-family="{FONT_MONO}" font-size="11" letter-spacing="3.2" fill="#67e8f9" opacity=".8">// STACK MATRIX · 技术栈</text>
  <text x="1152" y="46" font-family="{FONT_MONO}" font-size="9" letter-spacing="1.8" fill="#7c8aa5" text-anchor="end">日常在用 · BATTLE-TESTED</text>
  <path d="M48 66 H1152" stroke="#22d3ee" stroke-opacity=".12" stroke-width="1"/>
  {''.join(blocks)}
  <text x="48" y="384" font-family="{FONT_MONO}" font-size="9" letter-spacing="1.4" fill="#8fa0b8">按场景分组 · GROUPED BY SCENARIO</text>
</svg>
"""


# --------------------------------------------------------------------------
# featured open-source card
# --------------------------------------------------------------------------


def featured_repo_card(index: str, name: str, cn: str, en: str, chips, meta: str,
                      cmd1: str, cmd2: str, status: str, status_note: str, aria: str) -> str:
    W, H = 1200, 264
    chip_svg, cx = [], 48
    for label, color in chips:
        cw = 18 + len(label) * 7.4
        chip_svg.append(
            f'<g transform="translate({cx} 0)">'
            f'<rect x="0" y="194" width="{cw:.0f}" height="26" rx="7" fill="{color}" fill-opacity=".12" stroke="{color}" stroke-opacity=".45"/>'
            f'<text x="{cw / 2:.0f}" y="211" font-family="{FONT_MONO}" font-size="9.5" letter-spacing="1.4" fill="{color}" text-anchor="middle">{label}</text>'
            f'</g>'
        )
        cx += cw + 10
    status_w = mono_w(f"✓ {status}", 11)
    cursor_x = 762 + status_w + 9
    note_x = cursor_x + 15
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{esc(aria)}">
{panel_defs()}
  <style>
    @keyframes blink {{ 0%,49% {{ opacity:1 }} 50%,100% {{ opacity:0 }} }}
    .cur {{ animation:blink 1.15s steps(1,end) infinite }}
  </style>
  <rect x="0.75" y="0.75" width="{W - 1.5}" height="{H - 1.5}" rx="18" fill="url(#pBg)" stroke="url(#pBorder)" stroke-opacity=".5" stroke-width="1.5"/>
  {corner_brackets(W, H)}
  <text x="48" y="44" font-family="{FONT_MONO}" font-size="10" letter-spacing="2.6" fill="#8fa0b8">{esc(index)}</text>
  <text x="48" y="100" font-family="{FONT_SANS}" font-size="34" font-weight="700" fill="#e6edf7" letter-spacing=".2">{esc(name)}</text>
  <text x="48" y="134" font-family="{FONT_SANS}" font-size="14.5" fill="#cbd5e1">{esc(cn)}</text>
  <text x="48" y="158" font-family="{FONT_SANS}" font-size="12" fill="#a8b3c7">{esc(en)}</text>
  {''.join(chip_svg)}
  <text x="48" y="248" font-family="{FONT_MONO}" font-size="9.5" letter-spacing="1.2" fill="#8fa0b8">{esc(meta)}</text>
  <text x="1152" y="44" font-family="{FONT_MONO}" font-size="10" letter-spacing="1.4" fill="url(#pText)" text-anchor="end">VIEW ON GITHUB ↗</text>
  <g>
    <rect x="742" y="84" width="410" height="150" rx="12" fill="#05080f" stroke="#1e3a5f" stroke-opacity=".9"/>
    <rect x="742" y="84" width="410" height="28" rx="12" fill="#0a1224"/>
    <circle cx="760" cy="98" r="3.2" fill="#f87171" opacity=".7"/>
    <circle cx="772" cy="98" r="3.2" fill="#fbbf24" opacity=".7"/>
    <circle cx="784" cy="98" r="3.2" fill="#4ade80" opacity=".7"/>
    <text x="800" y="102" font-family="{FONT_MONO}" font-size="8.5" letter-spacing="1.2" fill="#7c8aa5">terminal · quick start</text>
    <text x="762" y="142" font-family="{FONT_MONO}" font-size="11" fill="#7c8aa5">$</text>
    <text x="778" y="142" font-family="{FONT_MONO}" font-size="11" fill="#cbd5e1">{esc(cmd1)}</text>
    <text x="762" y="166" font-family="{FONT_MONO}" font-size="11" fill="#7c8aa5">$</text>
    <text x="778" y="166" font-family="{FONT_MONO}" font-size="11" fill="#67e8f9">{esc(cmd2)}</text>
    <text x="762" y="198" font-family="{FONT_MONO}" font-size="11" fill="#4ade80">✓ {esc(status)}</text>
    <rect x="{cursor_x:.0f}" y="186" width="6" height="13" rx="1.5" fill="#67e8f9" class="cur"/>
    <text x="{note_x:.0f}" y="198" font-family="{FONT_SANS}" font-size="10.5" fill="#8fa0b8">{esc(status_note)}</text>
  </g>
</svg>
"""


# --------------------------------------------------------------------------
# footer
# --------------------------------------------------------------------------


def footer() -> str:
    W, H = 1200, 128
    title = "THANKS FOR VISITING · 感谢到访"
    tw = mono_w(title, 12, 3.4)
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
  {corner_brackets(W, H, pad=28, size=14)}
  <defs>
    <linearGradient id="fl" x1="56" y1="0" x2="1160" y2="0" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="#22d3ee" stop-opacity=".05"/>
      <stop offset=".25" stop-color="#22d3ee" stop-opacity=".5"/>
      <stop offset=".75" stop-color="#a78bfa" stop-opacity=".35"/>
      <stop offset="1" stop-color="#f472b6" stop-opacity=".05"/>
    </linearGradient>
  </defs>
  <path class="flow" d="M56 22 H1160" stroke="url(#fl)" stroke-width="1.2" stroke-dasharray="10 22"/>
  <text x="{cx:.0f}" y="62" font-family="{FONT_MONO}" font-size="12" letter-spacing="3.4" fill="#cbd5e1" text-anchor="middle">{esc(title)}</text>
  <rect x="{cx + tw / 2 + 8:.1f}" y="51" width="6" height="14" rx="1.5" fill="#67e8f9" class="cur"/>
  <text x="{cx:.0f}" y="86" font-family="{FONT_MONO}" font-size="9" letter-spacing="2.2" fill="#8fa0b8" text-anchor="middle">FULL-STACK · AI APPLICATIONS · 2026</text>
  <text x="48" y="110" font-family="{FONT_MONO}" font-size="9" letter-spacing="1.4" fill="#7c8aa5">© 2026 JASPER</text>
  <text x="1140" y="110" font-family="{FONT_MONO}" font-size="9" letter-spacing="1.4" fill="#7c8aa5" text-anchor="end">EOF // SIGNAL ENDS</text>
  <g fill="#67e8f9">
    <circle cx="588" cy="110" r="2" opacity=".35"/><circle cx="600" cy="110" r="2" opacity=".25"/><circle cx="612" cy="110" r="2" opacity=".15"/>
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
    write(
        "repo-agent-blackbox.svg",
        featured_repo_card(
            index="OPEN SOURCE · 01",
            name="agent-blackbox",
            cn="AI 编程 agent 的飞行记录仪：本地优先，回放、归因与对比多 runtime 会话。",
            en="Flight recorder for AI coding agents — local-first replay, attribution and diff.",
            chips=[("REPLAY", "#67e8f9"), ("COST", "#4ade80"), ("COMPARE", "#f472b6"), ("LOCAL-FIRST", "#fb923c")],
            meta="TypeScript · MIT · Node ≥ 22.19 · DSH 插件已上 npm",
            cmd1="npm install",
            cmd2="npm run demo:ui",
            status="local-first",
            status_note="无遥测 · 零运行时依赖",
            aria="agent-blackbox — local-first flight recorder for AI coding agents",
        ),
    )
    write(
        "repo-dsh-mcp-skills-board.svg",
        featured_repo_card(
            index="OPEN SOURCE · 02",
            name="dsh-mcp-skills-board",
            cn="DSH 的 MCP / 技能管理面板：四态开关、MCP 增删改、导入导出与模板。",
            en="Codex-style MCP & Skills panel for DeepSeek Harness — toggles, templates, import/export.",
            chips=[("MCP", "#67e8f9"), ("SKILLS", "#a78bfa"), ("TEMPLATES", "#f472b6"), ("NPM", "#fb923c")],
            meta="JavaScript · MIT · npm 已发布 · DSH 插件",
            cmd1="dsh plugin --profile desktop add",
            cmd2="dsh-mcp-skills-board",
            status="installed",
            status_note="侧栏即可见 · ready in the sidebar",
            aria="dsh-mcp-skills-board — MCP and Skills panel for DeepSeek Harness",
        ),
    )


if __name__ == "__main__":
    main()
