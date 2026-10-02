#!/usr/bin/env python3
"""Generates the animated cosmic SVGs used by the profile README.

Run:  python3 scripts/build_svgs.py
Output goes to assets/. The seed is fixed so the starfields are stable between runs.
"""
import math
import random
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets"
OUT.mkdir(exist_ok=True)
random.seed(1997)

SANS = "'Segoe UI', 'Helvetica Neue', Helvetica, Arial, sans-serif"
MONO = "'SFMono-Regular', 'JetBrains Mono', Menlo, Consolas, 'Liberation Mono', monospace"

# palette
SPACE = "#05060f"
VIOLET = "#a78bfa"
CYAN = "#67e8f9"
PINK = "#f472b6"
GOLD = "#fcd34d"
INK = "#e2e8f0"
DIM = "#64748b"

BASE_CSS = """
  .tw { animation: tw var(--d,4s) ease-in-out infinite; animation-delay: var(--o,0s); }
  @keyframes tw { 0%,100% { opacity: .15 } 50% { opacity: 1 } }
  .neb { animation: neb 14s ease-in-out infinite; transform-box: fill-box; transform-origin: center; }
  @keyframes neb { 0%,100% { opacity: .55; transform: scale(1) } 50% { opacity: .9; transform: scale(1.08) } }
  @media (prefers-reduced-motion: reduce) { * { animation: none !important; } }
"""


def f(x):
    return f"{x:.1f}".rstrip("0").rstrip(".")


def starfield(w, h, n_static, n_twinkle, y_max=None):
    y_max = y_max or h
    out = []
    for _ in range(n_static):
        r = random.choice([0.5, 0.6, 0.7, 0.8, 1.0])
        c = random.choice(["#cbd5e1", "#94a3b8", "#c4b5fd", "#a5f3fc"])
        o = random.uniform(0.25, 0.8)
        out.append(f'<circle cx="{f(random.uniform(0, w))}" cy="{f(random.uniform(0, y_max))}" r="{r}" fill="{c}" opacity="{o:.2f}"/>')
    for _ in range(n_twinkle):
        r = random.choice([0.9, 1.1, 1.3, 1.6])
        c = random.choice(["#ffffff", "#e0e7ff", "#cffafe", "#fbcfe8"])
        d = random.uniform(2.5, 6.5)
        o = random.uniform(0, 6)
        out.append(
            f'<circle class="tw" style="--d:{d:.1f}s;--o:-{o:.1f}s" cx="{f(random.uniform(0, w))}" '
            f'cy="{f(random.uniform(0, y_max))}" r="{r}" fill="{c}"/>'
        )
    return "\n".join(out)


def sparkle(x, y, s, color, dur, delay):
    """Four-point star that pulses."""
    p = f"M{x},{y-s} Q{x},{y} {x+s},{y} Q{x},{y} {x},{y+s} Q{x},{y} {x-s},{y} Q{x},{y} {x},{y-s}Z"
    return (
        f'<path d="{p}" fill="{color}" class="tw" style="--d:{dur}s;--o:-{delay}s"/>'
    )


def shooting_star(x, y, length, angle, dur, begin, color="#ffffff"):
    dx = math.cos(math.radians(angle)) * 520
    dy = math.sin(math.radians(angle)) * 520
    tx = -math.cos(math.radians(angle)) * length
    ty = -math.sin(math.radians(angle)) * length
    gid = f"ss{random.randint(0, 99999)}"
    return f"""
  <linearGradient id="{gid}" x1="0" y1="0" x2="{f(tx)}" y2="{f(ty)}" gradientUnits="userSpaceOnUse">
    <stop offset="0" stop-color="{color}"/><stop offset="1" stop-color="{color}" stop-opacity="0"/>
  </linearGradient>
  <g opacity="0">
    <line x1="0" y1="0" x2="{f(tx)}" y2="{f(ty)}" stroke="url(#{gid})" stroke-width="1.6" stroke-linecap="round"/>
    <circle r="1.6" fill="{color}"/>
    <animateTransform attributeName="transform" type="translate" values="{x},{y};{f(x+dx)},{f(y+dy)}"
      keyTimes="0;1" dur="{dur}s" begin="{begin}s" repeatCount="indefinite" calcMode="spline" keySplines=".3 0 .7 1"/>
    <animate attributeName="opacity" values="0;1;1;0;0" keyTimes="0;.05;.12;.18;1" dur="{dur}s" begin="{begin}s" repeatCount="indefinite"/>
  </g>"""


def galaxy_points(n_arms=2, per_arm=520, a=10, b=0.24, turns=1.9):
    pts = []
    for arm in range(n_arms):
        off = arm * 2 * math.pi / n_arms
        for i in range(per_arm):
            t = (i / per_arm) * turns * 2 * math.pi
            r = a * math.exp(b * t)
            spread = 1.5 + r * 0.075
            ang = t + off
            x = r * math.cos(ang) + random.gauss(0, spread)
            y = r * math.sin(ang) + random.gauss(0, spread)
            frac = min(1, r / 170)
            if frac < 0.25:
                col = random.choice(["#fff7ed", "#fde68a", "#fbcfe8"])
            elif frac < 0.6:
                col = random.choice(["#f0abfc", "#c4b5fd", "#e9d5ff", "#ffffff"])
            else:
                col = random.choice(["#a5b4fc", "#67e8f9", "#93c5fd", "#c4b5fd"])
            size = random.choice([0.7, 0.9, 1.1, 1.3]) * (1.25 - frac * 0.5)
            op = random.uniform(0.5, 1.0) * (1.1 - frac * 0.3)
            pts.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(size)}" fill="{col}" opacity="{op:.2f}"/>')
    # core haze
    for _ in range(180):
        r = abs(random.gauss(0, 14))
        ang = random.uniform(0, 2 * math.pi)
        pts.append(
            f'<circle cx="{f(r*math.cos(ang))}" cy="{f(r*math.sin(ang))}" r="{f(random.uniform(.5,1.2))}" '
            f'fill="#fff7ed" opacity="{random.uniform(.4,.9):.2f}"/>'
        )
    return "\n".join(pts)


# --------------------------------------------------------------------------- banner
def banner():
    W, H = 1200, 440
    gal = galaxy_points()
    s = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Daniel Gualán · Software Engineer">
<defs>
  <style>{BASE_CSS}
    .name {{ font: 800 66px {SANS}; letter-spacing: 3px; }}
    .role {{ font: 600 17px {MONO}; letter-spacing: 5px; fill: {INK}; }}
    .hud {{ font: 500 11px {MONO}; letter-spacing: 2px; fill: {DIM}; }}
    .rise {{ animation: rise 1.4s cubic-bezier(.2,.7,.2,1) both; }}
    .rise2 {{ animation: rise 1.4s .35s cubic-bezier(.2,.7,.2,1) both; }}
    .rise3 {{ animation: rise 1.4s .7s cubic-bezier(.2,.7,.2,1) both; }}
    @keyframes rise {{ from {{ opacity: 0; transform: translateY(14px) }} to {{ opacity: 1; transform: none }} }}
    .blink {{ animation: blink 1.6s steps(1) infinite; }}
    @keyframes blink {{ 50% {{ opacity: 0 }} }}
  </style>
  <clipPath id="frame"><rect width="{W}" height="{H}" rx="22"/></clipPath>
  <radialGradient id="bg" cx="70%" cy="45%" r="85%">
    <stop offset="0" stop-color="#140c2e"/><stop offset=".55" stop-color="#090a1c"/><stop offset="1" stop-color="{SPACE}"/>
  </radialGradient>
  <radialGradient id="core" r=".5">
    <stop offset="0" stop-color="#fff7ed"/><stop offset=".18" stop-color="#fde68a" stop-opacity=".9"/>
    <stop offset=".45" stop-color="#f0abfc" stop-opacity=".35"/><stop offset="1" stop-color="#7c3aed" stop-opacity="0"/>
  </radialGradient>
  <radialGradient id="n1" r=".5"><stop offset="0" stop-color="#7c3aed" stop-opacity=".55"/><stop offset="1" stop-color="#7c3aed" stop-opacity="0"/></radialGradient>
  <radialGradient id="n2" r=".5"><stop offset="0" stop-color="#db2777" stop-opacity=".4"/><stop offset="1" stop-color="#db2777" stop-opacity="0"/></radialGradient>
  <radialGradient id="n3" r=".5"><stop offset="0" stop-color="#0891b2" stop-opacity=".45"/><stop offset="1" stop-color="#0891b2" stop-opacity="0"/></radialGradient>
  <linearGradient id="nameGrad" x1="0" y1="0" x2="600" y2="0" gradientUnits="userSpaceOnUse" spreadMethod="reflect">
    <stop offset="0" stop-color="{CYAN}"/><stop offset=".35" stop-color="#e0e7ff"/><stop offset=".7" stop-color="{VIOLET}"/><stop offset="1" stop-color="{PINK}"/>
    <animateTransform attributeName="gradientTransform" type="translate" values="0 0;600 0;0 0" dur="12s" repeatCount="indefinite"/>
  </linearGradient>
  <radialGradient id="planet" cx="35%" cy="30%" r="75%">
    <stop offset="0" stop-color="#fbcfe8"/><stop offset=".45" stop-color="#c026d3"/><stop offset="1" stop-color="#2e1065"/>
  </radialGradient>
  <linearGradient id="ring" x1="0" x2="1">
    <stop offset="0" stop-color="{CYAN}" stop-opacity=".1"/><stop offset=".5" stop-color="{CYAN}" stop-opacity=".9"/><stop offset="1" stop-color="{CYAN}" stop-opacity=".1"/>
  </linearGradient>
  <radialGradient id="moon" cx="35%" cy="35%"><stop offset="0" stop-color="#f1f5f9"/><stop offset="1" stop-color="#475569"/></radialGradient>
  <filter id="blur" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="22"/></filter>
  <filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
</defs>
<g clip-path="url(#frame)">
  <rect width="{W}" height="{H}" fill="url(#bg)"/>
  <ellipse class="neb" cx="880" cy="190" rx="300" ry="170" fill="url(#n1)" filter="url(#blur)"/>
  <ellipse class="neb" style="animation-delay:-5s" cx="1050" cy="330" rx="220" ry="120" fill="url(#n2)" filter="url(#blur)"/>
  <ellipse class="neb" style="animation-delay:-9s" cx="260" cy="90" rx="280" ry="110" fill="url(#n3)" filter="url(#blur)"/>
  <g>{starfield(W, H, 260, 55)}</g>

  <!-- spiral galaxy -->
  <g transform="translate(850 210) rotate(-20) scale(1 .5)">
    <ellipse rx="260" ry="260" fill="url(#core)" opacity=".45"/>
    <g>
      <animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="140s" repeatCount="indefinite"/>
      {gal}
    </g>
    <circle r="34" fill="url(#core)"/>
  </g>
  {sparkle(850, 210, 16, "#fff7ed", 5, 1)}

  <!-- distant small planet -->
  <g transform="translate(560 380)">
    <circle r="11" fill="#0e7490"/><circle r="11" fill="url(#moon)" opacity=".25"/>
    <path d="M-11,0 A11,11 0 0 0 11,0 A11,6 0 0 1 -11,0" fill="#000" opacity=".35"/>
  </g>

  {shooting_star(120, 20, 120, 28, 9, 1.5)}
  {shooting_star(620, -10, 90, 35, 13, 6, "#cffafe")}
  {shooting_star(340, 40, 70, 22, 17, 11, "#fbcfe8")}

  <!-- copy -->
  <g transform="translate(70 0)">
    <g class="rise"><text class="hud" x="0" y="118">◉ TRANSMISSION · ORIGIN: EARTH · LAT -02.9° LON -79.0°</text></g>
    <g class="rise2" filter="url(#glow)"><text class="name" x="-3" y="198" fill="url(#nameGrad)">DANIEL GUALÁN</text></g>
    <g class="rise3">
      <text class="role" x="0" y="240">SOFTWARE ENGINEER</text>
      <rect x="0" y="264" width="54" height="3" rx="1.5" fill="{PINK}"/>
      <rect x="62" y="264" width="18" height="3" rx="1.5" fill="{CYAN}"/>
      <rect x="88" y="264" width="8" height="3" rx="1.5" fill="{VIOLET}"/>
    </g>
  </g>

  <!-- HUD footer -->
  <g class="hud">
    <line x1="70" y1="392" x2="460" y2="392" stroke="#1e293b"/>
    <text x="70" y="414">SYS.STATUS <tspan fill="#4ade80">● ONLINE</tspan>  ·  OPEN TO MISSIONS<tspan class="blink" fill="{CYAN}"> ▌</tspan></text>
    <text x="1130" y="414" text-anchor="end">GALAXY DG-1997 · CLASS SBc</text>
  </g>
  <rect width="{W}" height="{H}" rx="22" fill="none" stroke="#a78bfa" stroke-opacity=".25"/>
</g>
</svg>"""
    (OUT / "banner.svg").write_text(s, encoding="utf-8")


# --------------------------------------------------------------------------- whoami console
def whoami():
    W, H = 1200, 400
    lines = [
        ("p", "whoami"),
        ("o", "Daniel Gualán — Software Engineer"),
        ("p", "cat mission.log"),
        ("o", "REST APIs · offline-sync · hardware-linked apps"),
        ("o", "backend architecture · data integrity · clean code"),
        ("p", "status --availability"),
        ("g", "● OPEN — freelance &amp; full-time roles"),
    ]
    cycle = 18.0
    rows = []
    clips = []
    t = 0.6
    for i, (kind, text) in enumerate(lines):
        y = 112 + i * 34
        w = 30 + (len(text.replace("&amp;", "&")) + (16 if kind == "p" else 0)) * 9.6
        start = t
        typing = 0.9 if kind == "p" else 1.3
        end = start + typing
        t = end + (0.35 if kind == "p" else 0.25)
        k1, k2 = start / cycle, end / cycle
        clips.append(
            f'<clipPath id="c{i}"><rect x="48" y="{y-20}" height="30" width="0">'
            f'<animate attributeName="width" values="0;0;{f(w)};{f(w)};0" keyTimes="0;{k1:.3f};{k2:.3f};.94;1" '
            f'dur="{cycle}s" repeatCount="indefinite"/></rect></clipPath>'
        )
        if kind == "p":
            body = f'<tspan fill="{PINK}">dg@milky-way</tspan><tspan fill="{DIM}">:</tspan><tspan fill="{CYAN}">~</tspan><tspan fill="{DIM}">$ </tspan><tspan fill="{INK}">{text}</tspan>'
        elif kind == "g":
            body = f'<tspan fill="#4ade80">  {text}</tspan>'
        else:
            body = f'<tspan fill="{VIOLET}">  ›</tspan><tspan fill="#cbd5e1"> {text}</tspan>'
        rows.append(f'<text x="52" y="{y}" class="t" clip-path="url(#c{i})">{body}</text>')

    # rotating globe with meridians
    gx, gy, gr = 960, 214, 92
    meridians = []
    for k in range(6):
        d = 12
        beg = -k * d / 6
        meridians.append(
            f'<ellipse cx="{gx}" cy="{gy}" rx="{gr}" ry="{gr}" fill="none" stroke="{CYAN}" stroke-opacity=".45" stroke-width="1">'
            f'<animate attributeName="rx" values="{gr};0;{gr}" dur="{d}s" begin="{beg:.1f}s" repeatCount="indefinite"/></ellipse>'
        )
    parallels = "".join(
        f'<ellipse cx="{gx}" cy="{f(gy + gr*math.sin(math.radians(a)))}" rx="{f(gr*math.cos(math.radians(a)))}" '
        f'ry="{f(gr*math.cos(math.radians(a))*0.16)}" fill="none" stroke="{CYAN}" stroke-opacity=".3"/>'
        for a in (-60, -30, 0, 30, 60)
    )
    bars = [("BACKEND", 0.92, PINK), ("APIs / ARCH", 0.86, VIOLET), ("FRONTEND", 0.74, CYAN), ("MOBILE / IoT", 0.66, GOLD)]
    bar_svg = []
    for i, (label, v, c) in enumerate(bars):
        y = 112 + i * 52
        bar_svg.append(
            f'<text x="660" y="{y}" class="h">{label}</text>'
            f'<rect x="660" y="{y+10}" width="150" height="5" rx="2.5" fill="#1e293b"/>'
            f'<rect x="660" y="{y+10}" height="5" rx="2.5" fill="{c}" width="0">'
            f'<animate attributeName="width" values="0;{f(150*v)};{f(150*v)};0" keyTimes="0;.12;.94;1" dur="{cycle}s" begin="{.4+i*.2:.1f}s" repeatCount="indefinite"/></rect>'
        )

    s = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="whoami: Daniel Gualán, Software Engineer, open to freelance and full-time roles">
<defs>
  <style>{BASE_CSS}
    .t {{ font: 500 15px {MONO}; }}
    .h {{ font: 600 10.5px {MONO}; letter-spacing: 2px; fill: {DIM}; }}
    .blink {{ animation: blink 1.1s steps(1) infinite; }}
    @keyframes blink {{ 50% {{ opacity: 0 }} }}
  </style>
  <clipPath id="frame"><rect width="{W}" height="{H}" rx="22"/></clipPath>
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0b0d22"/><stop offset="1" stop-color="{SPACE}"/></linearGradient>
  <radialGradient id="globe" cx="38%" cy="32%" r="75%"><stop offset="0" stop-color="#155e75"/><stop offset=".6" stop-color="#0c1a3a"/><stop offset="1" stop-color="#050617"/></radialGradient>
  <radialGradient id="halo" r=".5"><stop offset=".7" stop-color="{CYAN}" stop-opacity=".25"/><stop offset="1" stop-color="{CYAN}" stop-opacity="0"/></radialGradient>
  <linearGradient id="sweep" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{CYAN}" stop-opacity="0"/><stop offset="1" stop-color="{CYAN}" stop-opacity=".35"/></linearGradient>
  <clipPath id="g"><circle cx="{gx}" cy="{gy}" r="{gr}"/></clipPath>
  {''.join(clips)}
</defs>
<g clip-path="url(#frame)">
  <rect width="{W}" height="{H}" fill="url(#bg)"/>
  <g>{starfield(W, H, 120, 30)}</g>

  <!-- terminal window -->
  <rect x="24" y="24" width="600" height="352" rx="14" fill="#0a0c1d" fill-opacity=".88" stroke="{VIOLET}" stroke-opacity=".3"/>
  <circle cx="48" cy="48" r="5.5" fill="#f87171"/><circle cx="68" cy="48" r="5.5" fill="#fbbf24"/><circle cx="88" cy="48" r="5.5" fill="#4ade80"/>
  <text x="324" y="52" class="h" text-anchor="middle">mission-control — zsh</text>
  <line x1="24" y1="68" x2="624" y2="68" stroke="{VIOLET}" stroke-opacity=".2"/>
  {''.join(rows)}
  <rect x="52" y="{112 + len(lines)*34 - 16}" width="10" height="20" fill="{CYAN}" class="blink"/>

  <!-- telemetry -->
  <text x="660" y="62" class="h" style="fill:{INK}">TELEMETRY</text>
  <line x1="660" y1="74" x2="830" y2="74" stroke="#1e293b"/>
  {''.join(bar_svg)}
  <text x="660" y="340" class="h">UPLINK <tspan fill="#4ade80">STABLE</tspan></text>
  <text x="660" y="358" class="h">LATENCY <tspan fill="{CYAN}">12ms</tspan></text>

  <!-- globe -->
  <circle cx="{gx}" cy="{gy}" r="{gr+26}" fill="url(#halo)"/>
  <circle cx="{gx}" cy="{gy}" r="{gr}" fill="url(#globe)"/>
  <g clip-path="url(#g)">{parallels}{''.join(meridians)}
    <path d="M{gx},{gy} L{gx+gr*1.2},{gy} A{gr*1.2},{gr*1.2} 0 0 0 {f(gx+gr*1.2*math.cos(math.radians(-40)))},{f(gy+gr*1.2*math.sin(math.radians(-40)))}Z" fill="url(#sweep)">
      <animateTransform attributeName="transform" type="rotate" from="0 {gx} {gy}" to="360 {gx} {gy}" dur="6s" repeatCount="indefinite"/>
    </path>
  </g>
  <circle cx="{gx}" cy="{gy}" r="{gr}" fill="none" stroke="{CYAN}" stroke-opacity=".6"/>
  <!-- pin -->
  <circle cx="{gx-24}" cy="{gy+18}" r="3.5" fill="{PINK}"/>
  <circle cx="{gx-24}" cy="{gy+18}" r="3.5" fill="none" stroke="{PINK}">
    <animate attributeName="r" values="3.5;16" dur="2.2s" repeatCount="indefinite"/>
    <animate attributeName="opacity" values="1;0" dur="2.2s" repeatCount="indefinite"/>
  </circle>
  <!-- orbit + satellite -->
  <g transform="translate({gx} {gy}) rotate(-20)">
    <ellipse rx="150" ry="38" fill="none" stroke="{VIOLET}" stroke-opacity=".45" stroke-dasharray="3 6"/>
    <g>
      <animateMotion dur="9s" repeatCount="indefinite" path="M150,0 A150,38 0 1 1 -150,0 A150,38 0 1 1 150,0"/>
      <rect x="-9" y="-2.5" width="6" height="5" fill="{CYAN}"/><rect x="3" y="-2.5" width="6" height="5" fill="{CYAN}"/>
      <rect x="-3" y="-3.5" width="6" height="7" rx="1.5" fill="#e2e8f0"/>
    </g>
  </g>
  <text x="{gx}" y="348" class="h" text-anchor="middle">TARGET · EARTH-01 · <tspan fill="{PINK}">ECUADOR</tspan></text>
  <rect width="{W}" height="{H}" rx="22" fill="none" stroke="{VIOLET}" stroke-opacity=".25"/>
</g>
</svg>"""
    (OUT / "whoami.svg").write_text(s, encoding="utf-8")


# --------------------------------------------------------------------------- tech-stack solar system
def orbits():
    W, H = 1200, 600
    cx, cy = 600, 300
    tilt = 0.36
    rings = [
        ("LANGUAGES", 120, 38, PINK, ["Java", "TypeScript", "Kotlin"]),
        ("BACKEND", 215, 62, VIOLET, ["Spring Boot", "NestJS", ".NET Core"]),
        ("FRONT · MOBILE", 315, 88, CYAN, ["React", "Next.js", "Android"]),
        ("DATA · OPS", 430, 120, GOLD, ["PostgreSQL", "SQL Server", "Docker", "Linux", "Git", "GitLab"]),
    ]
    back, front, planets, legend = [], [], [], []
    for idx, (label, rx, dur, col, techs) in enumerate(rings):
        ry = rx * tilt
        path = f"M{cx+rx},{cy} A{rx},{f(ry)} 0 1 1 {cx-rx},{cy} A{rx},{f(ry)} 0 1 1 {cx+rx},{cy}"
        back.append(
            f'<path d="M{cx-rx},{cy} A{rx},{f(ry)} 0 0 1 {cx+rx},{cy}" fill="none" stroke="{col}" stroke-opacity=".22" stroke-dasharray="2 5"/>'
        )
        front.append(
            f'<path d="M{cx+rx},{cy} A{rx},{f(ry)} 0 0 1 {cx-rx},{cy}" fill="none" stroke="{col}" stroke-opacity=".5"/>'
        )
        for j, tech in enumerate(techs):
            beg = -dur * (j / len(techs) + idx * 0.23)
            size = 7 - idx * 0.6 + random.uniform(-0.6, 0.6)
            pid = f"p{idx}{j}"
            planets.append(f"""
  <g>
    <animateMotion dur="{dur}s" begin="{beg:.2f}s" repeatCount="indefinite" path="{path}"/>
    <circle r="{f(size*2.4)}" fill="url(#halo{idx})"/>
    <circle r="{f(size)}" fill="url(#pl{idx})"/>
    <g transform="translate(0 {f(-size-10)})">
      <rect x="{f(-len(tech)*3.9-9)}" y="-13" width="{f(len(tech)*7.8+18)}" height="19" rx="9.5" fill="#0b0d22" fill-opacity=".85" stroke="{col}" stroke-opacity=".55"/>
      <text class="lbl" y="1" text-anchor="middle">{tech}</text>
    </g>
  </g>""")
        # ring label on the left edge
        legend.append(f'<circle cx="46" cy="{f(H-118+idx*22)}" r="4" fill="{col}"/><text class="ring" x="60" y="{f(H-114+idx*22)}" style="fill:{col}">{label}</text>')

    defs_pl = "".join(
        f'<radialGradient id="pl{i}" cx="35%" cy="30%" r="75%"><stop offset="0" stop-color="#ffffff"/><stop offset=".35" stop-color="{c}"/><stop offset="1" stop-color="#1e1b4b"/></radialGradient>'
        f'<radialGradient id="halo{i}" r=".5"><stop offset="0" stop-color="{c}" stop-opacity=".45"/><stop offset="1" stop-color="{c}" stop-opacity="0"/></radialGradient>'
        for i, (_, _, _, c, _) in enumerate(rings)
    )

    s = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Tech stack as a solar system: Java, TypeScript, Kotlin, Spring Boot, NestJS, .NET Core, React, Next.js, Android, PostgreSQL, SQL Server, Docker, Linux, Git, GitLab">
<defs>
  <style>{BASE_CSS}
    .lbl {{ font: 600 11.5px {MONO}; fill: {INK}; }}
    .ring {{ font: 700 10px {MONO}; letter-spacing: 2px; opacity: .8; }}
    .h {{ font: 600 11px {MONO}; letter-spacing: 3px; fill: {DIM}; }}
    .sun {{ animation: sun 5s ease-in-out infinite; transform-box: fill-box; transform-origin: center; }}
    @keyframes sun {{ 0%,100% {{ transform: scale(1) }} 50% {{ transform: scale(1.12) }} }}
  </style>
  <clipPath id="frame"><rect width="{W}" height="{H}" rx="22"/></clipPath>
  <radialGradient id="bg" cx="50%" cy="50%" r="70%"><stop offset="0" stop-color="#140c2e"/><stop offset="1" stop-color="{SPACE}"/></radialGradient>
  <radialGradient id="sunG" cx="40%" cy="38%" r="65%"><stop offset="0" stop-color="#fffbeb"/><stop offset=".4" stop-color="#fcd34d"/><stop offset="1" stop-color="#f97316"/></radialGradient>
  <radialGradient id="corona" r=".5"><stop offset=".25" stop-color="#fbbf24" stop-opacity=".55"/><stop offset=".6" stop-color="#f472b6" stop-opacity=".15"/><stop offset="1" stop-color="#7c3aed" stop-opacity="0"/></radialGradient>
  <radialGradient id="neb" r=".5"><stop offset="0" stop-color="#7c3aed" stop-opacity=".35"/><stop offset="1" stop-color="#7c3aed" stop-opacity="0"/></radialGradient>
  <filter id="blur" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="30"/></filter>
  {defs_pl}
</defs>
<g clip-path="url(#frame)">
  <rect width="{W}" height="{H}" fill="url(#bg)"/>
  <ellipse class="neb" cx="{cx}" cy="{cy}" rx="520" ry="220" fill="url(#neb)" filter="url(#blur)"/>
  <g>{starfield(W, H, 220, 45)}</g>
  <text x="40" y="48" class="h" style="fill:{INK}">STACK.SYSTEM</text>
  <text x="40" y="68" class="h">4 ORBITS · 15 BODIES · STABLE</text>
  <text x="{W-40}" y="48" class="h" text-anchor="end">HELIOCENTRIC VIEW</text>
  <text x="{W-40}" y="68" class="h" text-anchor="end">T+∞ <tspan fill="#4ade80">●</tspan></text>
  <text x="40" y="{H-142}" class="h" style="fill:{INK}">ORBITS</text>
  {''.join(legend)}
  {''.join(back)}
  <circle class="sun" cx="{cx}" cy="{cy}" r="90" fill="url(#corona)"/>
  <circle cx="{cx}" cy="{cy}" r="36" fill="url(#sunG)"/>
  <text x="{cx}" y="{cy+6}" text-anchor="middle" style="font:800 17px {SANS};fill:#7c2d12;letter-spacing:1px">DG</text>
  {''.join(front)}
  {''.join(planets)}
  {shooting_star(900, 10, 90, 145, 15, 4, "#cffafe")}
  <rect width="{W}" height="{H}" rx="22" fill="none" stroke="{VIOLET}" stroke-opacity=".25"/>
</g>
</svg>"""
    (OUT / "orbits.svg").write_text(s, encoding="utf-8")


# --------------------------------------------------------------------------- footer horizon
def footer():
    W, H = 1200, 220
    s = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="End of transmission">
<defs>
  <style>{BASE_CSS}
    .h {{ font: 600 11px {MONO}; letter-spacing: 4px; fill: {DIM}; }}
    .atm {{ animation: atm 7s ease-in-out infinite; }}
    @keyframes atm {{ 0%,100% {{ opacity: .6 }} 50% {{ opacity: 1 }} }}
  </style>
  <clipPath id="frame"><rect width="{W}" height="{H}" rx="22"/></clipPath>
  <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{SPACE}"/><stop offset="1" stop-color="#140c2e"/></linearGradient>
  <radialGradient id="earth" cx="50%" cy="0%" r="70%"><stop offset="0" stop-color="#1e3a8a"/><stop offset=".5" stop-color="#0b1230"/><stop offset="1" stop-color="{SPACE}"/></radialGradient>
  <linearGradient id="rim" x1="0" x2="1"><stop offset="0" stop-color="{PINK}" stop-opacity="0"/><stop offset=".3" stop-color="{VIOLET}"/><stop offset=".5" stop-color="{CYAN}"/><stop offset=".7" stop-color="{VIOLET}"/><stop offset="1" stop-color="{PINK}" stop-opacity="0"/></linearGradient>
  <filter id="glow" x="-20%" y="-200%" width="140%" height="500%"><feGaussianBlur stdDeviation="8"/></filter>
  <linearGradient id="sun" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
</defs>
<g clip-path="url(#frame)">
  <rect width="{W}" height="{H}" fill="url(#bg)"/>
  <g>{starfield(W, H, 140, 35, y_max=150)}</g>
  <text x="{W/2}" y="70" class="h" text-anchor="middle">— END OF TRANSMISSION —</text>
  <text x="{W/2}" y="92" class="h" text-anchor="middle" style="letter-spacing:2px;font-size:10px">THANKS FOR VISITING · SEE YOU AMONG THE STARS</text>
  <path class="atm" d="M-100,260 Q600,110 1300,260" fill="none" stroke="url(#rim)" stroke-width="14" filter="url(#glow)"/>
  <path d="M-100,260 Q600,120 1300,260 L1300,300 L-100,300Z" fill="url(#earth)"/>
  <path d="M-100,260 Q600,120 1300,260" fill="none" stroke="url(#rim)" stroke-width="1.5"/>
  <ellipse cx="600" cy="190" rx="120" ry="2" fill="url(#sun)" class="atm"/>
  <!-- satellite crossing -->
  <g>
    <animateMotion dur="22s" repeatCount="indefinite" path="M-40,150 Q600,95 1240,150"/>
    <rect x="-10" y="-2.5" width="7" height="5" fill="{CYAN}"/><rect x="3" y="-2.5" width="7" height="5" fill="{CYAN}"/>
    <rect x="-3" y="-3.5" width="6" height="7" rx="1.5" fill="#e2e8f0"/>
    <circle cx="0" cy="-6" r="1.4" fill="#f87171" class="tw" style="--d:1s"/>
  </g>
  <rect width="{W}" height="{H}" rx="22" fill="none" stroke="{VIOLET}" stroke-opacity=".25"/>
</g>
</svg>"""
    (OUT / "footer.svg").write_text(s, encoding="utf-8")


def divider():
    W, H = 1200, 24
    stars = "".join(
        f'<circle class="tw" style="--d:{random.uniform(2,5):.1f}s;--o:-{random.uniform(0,5):.1f}s" cx="{f(x)}" cy="{f(12+random.uniform(-5,5))}" r="{random.choice([.8,1,1.3])}" fill="#e0e7ff"/>'
        for x in range(20, W, 37)
    )
    s = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" aria-hidden="true">
<defs><style>{BASE_CSS}</style>
  <linearGradient id="l" x1="0" x2="1"><stop offset="0" stop-color="{CYAN}" stop-opacity="0"/><stop offset=".5" stop-color="{VIOLET}"/><stop offset="1" stop-color="{PINK}" stop-opacity="0"/></linearGradient>
</defs>
<rect y="11.5" width="{W}" height="1" fill="url(#l)" opacity=".7"/>
{stars}
<circle cy="12" r="3" fill="#fff">
  <animate attributeName="cx" values="0;{W}" dur="8s" repeatCount="indefinite"/>
  <animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.1;.9;1" dur="8s" repeatCount="indefinite"/>
</circle>
</svg>"""
    (OUT / "divider.svg").write_text(s, encoding="utf-8")


if __name__ == "__main__":
    banner()
    whoami()
    orbits()
    footer()
    divider()
    for p in sorted(OUT.glob("*.svg")):
        print(f"{p.name:14} {p.stat().st_size/1024:6.1f} KB")
