import html
import pandas as pd
import streamlit as st

from agents.broker_orchestrator import run_broker_workflow
from brokers.alpaca_client import check_alpaca_connection
from database.trade_history import save_workflow_run, get_recent_workflow_runs
from utils.voice import transcribe_audio

st.set_page_config(
    page_title="Intelligent Broker Desk",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(
    """
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=IBM+Plex+Mono:wght@400;500;600&display=swap" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,400,0,0&display=swap" rel="stylesheet">

    <style>
        :root {
            --bg: #f4f7fb;
            --bg2: #eef3f8;
            --panel: #ffffff;
            --panel-soft: #f8fafc;
            --panel-blue: #eef6ff;
            --navy: #071827;
            --navy-2: #0b2033;
            --blue: #2563eb;
            --blue-soft: #dbeafe;
            --cyan: #0ea5e9;
            --cyan-soft: #e0f2fe;
            --emerald: #10b981;
            --emerald-soft: #d1fae5;
            --amber: #f59e0b;
            --amber-soft: #fef3c7;
            --red: #ef4444;
            --red-soft: #fee2e2;
            --ink: #111827;
            --ink-muted: #526071;
            --ink-light: #8492a6;
            --line: rgba(15, 23, 42, 0.10);
            --line-strong: rgba(37, 99, 235, 0.18);
            --shadow: 0 12px 35px rgba(15, 23, 42, 0.08);
            --shadow-m: 0 18px 55px rgba(15, 23, 42, 0.12);
            --shadow-lg: 0 24px 80px rgba(15, 23, 42, 0.18);
            --radius: 20px;
        }

        /* Global shell */
        html, body, [class*="css"] {
            font-family: 'Plus Jakarta Sans', system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
            background: var(--bg) !important;
            color: var(--ink) !important;
            letter-spacing: -0.01em;
        }
        .stApp {
            background:
                radial-gradient(circle at top left, rgba(37, 99, 235, 0.08), transparent 30rem),
                radial-gradient(circle at top right, rgba(14, 165, 233, 0.08), transparent 32rem),
                var(--bg) !important;
        }
        #MainMenu, footer, header { visibility: hidden; }
        .block-container {
            padding-top: 0 !important;
            padding-bottom: 4rem !important;
            max-width: 1440px !important;
        }
        h1, h2, h3, h4, h5, h6 {
            font-family: 'Plus Jakarta Sans', system-ui, sans-serif !important;
            letter-spacing: -0.035em !important;
            color: var(--ink) !important;
            font-weight: 750 !important;
        }
        p, li, label, div, span {
            text-rendering: geometricPrecision;
        }

        /* Hero */
        .hero {
            position: relative;
            overflow: hidden;
            background:
                linear-gradient(135deg, rgba(7, 24, 39, 0.97) 0%, rgba(11, 32, 51, 0.97) 50%, rgba(14, 54, 88, 0.96) 100%),
                radial-gradient(circle at 20% 20%, rgba(37, 99, 235, 0.30), transparent 30rem);
            border-radius: 0 0 34px 34px;
            padding: 3.2rem 4rem 0 4rem;
            margin: -1rem -1rem 2.35rem -1rem;
            min-height: 318px;
            box-shadow: var(--shadow-lg);
        }
        .hero::after {
            content: '';
            position: absolute;
            inset: 0;
            background-image:
                linear-gradient(rgba(255,255,255,0.035) 1px, transparent 1px),
                linear-gradient(90deg, rgba(255,255,255,0.035) 1px, transparent 1px);
            background-size: 48px 48px;
            mask-image: linear-gradient(to bottom, black, transparent 92%);
            pointer-events: none;
        }
        .hero-orb1 {
            position: absolute; width: 520px; height: 520px; border-radius: 50%;
            background: radial-gradient(circle, rgba(37, 99, 235,0.30) 0%, transparent 68%);
            top: -160px; right: 3%;
            animation: orbFloat1 10s ease-in-out infinite alternate;
            pointer-events: none;
        }
        .hero-orb2 {
            position: absolute; width: 320px; height: 320px; border-radius: 50%;
            background: radial-gradient(circle, rgba(16,185,129,0.22) 0%, transparent 70%);
            bottom: -40px; left: 28%;
            animation: orbFloat2 13s ease-in-out infinite alternate;
            pointer-events: none;
        }
        .hero-orb3 {
            position: absolute; width: 220px; height: 220px; border-radius: 50%;
            background: radial-gradient(circle, rgba(14,165,233,0.24) 0%, transparent 70%);
            top: 30px; left: 8%;
            animation: orbFloat3 8s ease-in-out infinite alternate;
            pointer-events: none;
        }
        @keyframes orbFloat1 { 0% { transform:translate(0,0) scale(1); } 100% { transform:translate(-28px,22px) scale(1.08); } }
        @keyframes orbFloat2 { 0% { transform:translate(0,0) scale(1); } 100% { transform:translate(22px,-18px) scale(1.05); } }
        @keyframes orbFloat3 { 0% { transform:translate(0,0) scale(1); } 100% { transform:translate(14px,16px) scale(0.93); } }

        .hero-inner { position: relative; z-index: 3; }
        .hero-eyebrow {
            font-family: 'IBM Plex Mono', monospace;
            font-size: 0.70rem;
            letter-spacing: 0.18em;
            text-transform: uppercase;
            color: rgba(224,242,254,0.84);
            margin-bottom: 1rem;
            display: flex; align-items: center; gap: 0.8rem;
            opacity: 0; animation: fadeUp 0.7s ease forwards 0.15s;
        }
        .hero-eyebrow::before {
            content: ''; display: inline-block;
            width: 34px; height: 1px; background: linear-gradient(90deg, var(--cyan), transparent);
        }
        .hero-h1 {
            font-family: 'Plus Jakarta Sans', system-ui, sans-serif !important;
            font-size: clamp(3rem, 5.2vw, 5.2rem) !important;
            font-weight: 800 !important;
            line-height: 0.98 !important;
            color: #ffffff !important;
            letter-spacing: -0.07em !important;
            margin: 0 0 0.9rem !important;
            opacity: 0; animation: fadeUp 0.7s ease forwards 0.3s;
        }
        .hero-h1 em {
            font-style: normal;
            background: linear-gradient(90deg, #60a5fa, #22d3ee, #34d399);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        .hero-sub {
            font-size: 1.02rem;
            color: rgba(226,232,240,0.76);
            font-weight: 400;
            max-width: 650px;
            line-height: 1.7;
            opacity: 0; animation: fadeUp 0.7s ease forwards 0.45s;
        }
        @keyframes fadeUp {
            from { opacity:0; transform:translateY(20px); }
            to   { opacity:1; transform:translateY(0); }
        }

        .hero-pills {
            display: flex; gap: 0.6rem; margin-top: 1.7rem;
            flex-wrap: wrap;
            opacity: 0; animation: fadeUp 0.7s ease forwards 0.6s;
        }
        .hero-pill {
            font-family: 'IBM Plex Mono', monospace;
            font-size: 0.68rem;
            padding: 0.42rem 0.85rem;
            border-radius: 999px;
            border: 1px solid rgba(255,255,255,0.12);
            color: rgba(226,232,240,0.78);
            background: rgba(255,255,255,0.055);
            letter-spacing: 0.03em;
            backdrop-filter: blur(10px);
        }
        .hero-pill.active {
            border-color: rgba(16,185,129,0.55);
            color: #d1fae5;
            background: rgba(16,185,129,0.12);
        }
        .live-dot {
            display: inline-block; width: 7px; height: 7px;
            border-radius: 50%; background: var(--emerald); margin-right: 0.42rem;
            animation: livePulse 1.6s ease-in-out infinite; vertical-align: middle;
        }
        @keyframes livePulse {
            0%,100% { opacity:1; transform:scale(1); box-shadow:0 0 0 0 rgba(16,185,129,0.45); }
            50% { opacity:0.62; transform:scale(0.75); box-shadow:0 0 0 6px rgba(16,185,129,0); }
        }

        .ticker-band {
            margin-top: 2.3rem;
            border-top: 1px solid rgba(255,255,255,0.09);
            padding: 0.82rem 0;
            overflow: hidden;
            position: relative;
        }
        .ticker-band::before, .ticker-band::after {
            content: ''; position: absolute; top:0; bottom:0; width:90px; z-index:2;
        }
        .ticker-band::before { left:0;  background:linear-gradient(90deg, #071827, transparent); }
        .ticker-band::after  { right:0; background:linear-gradient(-90deg, #0e3658, transparent); }
        .ticker-track {
            display: flex; gap: 2.2rem; white-space: nowrap;
            animation: tickerSlide 32s linear infinite;
        }
        .ticker-track:hover { animation-play-state: paused; }
        @keyframes tickerSlide { 0% { transform:translateX(0); } 100% { transform:translateX(-50%); } }
        .ticker-item {
            font-family: 'IBM Plex Mono', monospace;
            font-size: 0.72rem;
            color: rgba(226,232,240,0.50);
            letter-spacing: 0.035em;
        }
        .ticker-item .t-sym  { color: rgba(255,255,255,0.86); font-weight: 600; }
        .ticker-item .t-up   { color: #34d399; }
        .ticker-item .t-down { color: #fb7185; }

        /* Sidebar */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%) !important;
            border-right: 1px solid var(--line) !important;
            box-shadow: 18px 0 55px rgba(15, 23, 42, 0.04);
        }
        [data-testid="stSidebar"] > div:first-child { padding: 1.6rem 1.2rem !important; }
        .sb-logo {
            font-size: 1.35rem;
            font-weight: 800;
            color: var(--navy);
            padding-bottom: 1.1rem;
            margin-bottom: 1rem;
            border-bottom: 1px solid var(--line);
            letter-spacing: -0.04em;
        }
        .sb-logo em {
            font-style: normal;
            background: linear-gradient(90deg, var(--blue), var(--cyan));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        .sb-sec {
            font-family: 'IBM Plex Mono', monospace;
            font-size: 0.62rem;
            letter-spacing: 0.15em;
            text-transform: uppercase;
            color: var(--ink-light);
            margin: 1.35rem 0 0.6rem;
            font-weight: 600;
        }
        .sb-trade-card {
            background: linear-gradient(180deg, #f8fbff, #ffffff);
            border: 1px solid var(--line-strong);
            border-radius: 18px;
            padding: 0.95rem 1rem;
            box-shadow: var(--shadow);
            margin-bottom: 0.75rem;
        }
        .sb-card-kicker {
            font-family: 'IBM Plex Mono', monospace;
            font-size: 0.58rem;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            color: var(--blue);
            margin-bottom: 0.32rem;
            font-weight: 700;
        }
        .sb-card-title {
            color: var(--navy);
            font-size: 0.95rem;
            font-weight: 750;
            letter-spacing: -0.02em;
            margin-bottom: 0.25rem;
        }
        .sb-card-copy {
            color: var(--ink-muted);
            font-size: 0.78rem;
            line-height: 1.45;
        }
        div[data-testid="stRadio"] {
            background: white;
            border: 1px solid var(--line);
            border-radius: 16px;
            padding: 0.55rem 0.75rem 0.75rem;
            margin-bottom: 0.75rem;
            box-shadow: 0 6px 20px rgba(15, 23, 42, 0.04);
        }
        div[data-testid="stRadio"] label {
            font-weight: 650 !important;
            color: var(--navy) !important;
            font-size: 0.86rem !important;
        }
        div[data-testid="stRadio"] p {
            font-size: 0.82rem !important;
            color: var(--ink) !important;
            font-weight: 600 !important;
        }
        .mode-banner {
            border-radius: 15px;
            padding: 0.78rem 0.9rem;
            font-size: 0.82rem;
            line-height: 1.45;
            border: 1px solid var(--line);
            margin: 0.45rem 0 0.65rem;
        }
        .mode-banner.safe {
            background: var(--emerald-soft);
            color: #065f46;
            border-color: rgba(16,185,129,0.25);
        }
        .mode-banner.armed {
            background: var(--amber-soft);
            color: #78350f;
            border-color: rgba(245,158,11,0.35);
        }
        .run-row {
            display: flex; align-items: center; gap: 0.55rem;
            padding: 0.62rem 0.78rem;
            border-radius: 14px;
            border: 1px solid var(--line);
            background: #ffffff;
            margin-bottom: 0.45rem;
            font-size: 0.78rem;
            color: var(--ink-muted);
            transition: border-color 0.15s, box-shadow 0.15s, transform 0.15s;
        }
        .run-row:hover {
            border-color: rgba(37,99,235,0.32);
            box-shadow: var(--shadow);
            transform: translateY(-1px);
        }
        .run-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }

        /* Section dividers */
        .sec-div {
            display: flex; align-items: center; gap: 0.9rem;
            margin: 2.1rem 0 1.15rem;
        }
        .sec-div-line {
            flex: 1; height: 1px;
            background: linear-gradient(90deg, transparent, var(--line), transparent);
        }
        .sec-div-dot  {
            width: 6px; height: 6px;
            border-radius: 50%;
            background: linear-gradient(135deg, var(--blue), var(--cyan));
            flex-shrink:0;
            box-shadow: 0 0 0 4px rgba(37,99,235,0.08);
        }
        .sec-div-text {
            font-family: 'IBM Plex Mono', monospace;
            font-size: 0.66rem;
            letter-spacing: 0.15em;
            text-transform: uppercase;
            color: var(--ink-light);
            font-weight: 700;
        }

        /* Inputs */
        div[data-testid="stTextInput"] label {
            font-family: 'IBM Plex Mono', monospace !important;
            font-size: 0.66rem !important;
            letter-spacing: 0.12em !important;
            text-transform: uppercase !important;
            color: var(--ink-light) !important;
            font-weight: 700 !important;
        }
        div[data-testid="stTextInput"] input {
            font-family: 'Plus Jakarta Sans', system-ui, sans-serif !important;
            font-size: 1.02rem !important;
            border: 1px solid var(--line) !important;
            border-radius: 16px !important;
            background: white !important;
            padding: 0.88rem 1rem !important;
            color: var(--ink) !important;
            box-shadow: 0 8px 28px rgba(15,23,42,0.05) !important;
            transition: border-color 0.2s, box-shadow 0.2s !important;
        }
        div[data-testid="stTextInput"] input:focus {
            border-color: rgba(37,99,235,0.50) !important;
            box-shadow: 0 0 0 4px rgba(37,99,235,0.10), 0 8px 28px rgba(15,23,42,0.06) !important;
            outline: none !important;
        }

        /* Metrics */
        div[data-testid="stMetric"] {
            background: var(--panel) !important;
            border: 1px solid var(--line) !important;
            border-radius: 18px !important;
            padding: 1.05rem 1.1rem !important;
            box-shadow: var(--shadow) !important;
            transition: transform 0.18s, box-shadow 0.18s, border-color 0.18s !important;
        }
        div[data-testid="stMetric"]:hover {
            transform: translateY(-3px) !important;
            box-shadow: var(--shadow-m) !important;
            border-color: rgba(37,99,235,0.28) !important;
        }
        div[data-testid="stMetric"] label {
            font-family: 'IBM Plex Mono', monospace !important;
            font-size: 0.62rem !important;
            letter-spacing: 0.11em !important;
            text-transform: uppercase !important;
            color: var(--ink-light) !important;
            font-weight: 700 !important;
        }
        div[data-testid="stMetric"] [data-testid="stMetricValue"] {
            font-family: 'Plus Jakarta Sans', system-ui, sans-serif !important;
            font-size: 1.55rem !important;
            color: var(--navy) !important;
            font-weight: 800 !important;
            letter-spacing: -0.05em !important;
        }

        /* Agent cards */
        .agent-card {
            background: var(--panel);
            border: 1px solid var(--line);
            border-radius: 20px;
            padding: 1.25rem;
            box-shadow: var(--shadow);
            height: 100%;
            position: relative;
            overflow: hidden;
            transition: transform 0.2s, box-shadow 0.2s, border-color 0.2s;
        }
        .agent-card:hover {
            transform: translateY(-4px);
            box-shadow: var(--shadow-lg);
            border-color: rgba(37,99,235,0.22);
        }
        .agent-card::after {
            content: ''; position: absolute; bottom:0; left:0; right:0;
            height: 3px; border-radius: 0 0 20px 20px;
        }
        .agent-card.success::after { background: linear-gradient(90deg, var(--emerald), #22c55e); }
        .agent-card.warning::after { background: linear-gradient(90deg, var(--amber), #fbbf24); }
        .agent-card.error::after   { background: linear-gradient(90deg, var(--red), #fb7185); }
        .agent-card.neutral::after { background: linear-gradient(90deg, var(--blue), var(--cyan)); }
        .agent-card-icon {
            position: absolute; top: 0.95rem; right: 1rem;
            font-size: 1.55rem; opacity: 0.12;
        }
        .agent-badge {
            display: inline-flex; align-items: center; gap: 0.35rem;
            padding: 0.26rem 0.65rem; border-radius: 999px;
            font-family: 'IBM Plex Mono', monospace;
            font-size: 0.60rem;
            letter-spacing: 0.06em;
            margin-bottom: 0.72rem;
            font-weight: 700;
            text-transform: uppercase;
        }
        .agent-badge::before { content:''; width:6px; height:6px; border-radius:50%; }
        .agent-badge.success { background:var(--emerald-soft); color:#047857; }
        .agent-badge.success::before { background:var(--emerald); }
        .agent-badge.warning { background:var(--amber-soft); color:#92400e; }
        .agent-badge.warning::before { background:var(--amber); }
        .agent-badge.error { background:var(--red-soft); color:#b91c1c; }
        .agent-badge.error::before { background:var(--red); }
        .agent-badge.neutral { background:var(--blue-soft); color:#1d4ed8; }
        .agent-badge.neutral::before { background:var(--blue); }
        .agent-title {
            font-size: 0.98rem;
            font-weight: 800;
            color: var(--navy);
            margin-bottom: 0.38rem;
            letter-spacing: -0.03em;
        }
        .agent-summary {
            font-size: 0.80rem;
            color: var(--ink-muted);
            line-height: 1.55;
        }

        .agent-market-mini {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 0.55rem;
            margin-top: 0.75rem;
        }

        .agent-market-mini div {
            background: rgba(236, 245, 255, 0.72);
            border: 1px solid rgba(47, 109, 246, 0.12);
            border-radius: 12px;
            padding: 0.55rem 0.6rem;
        }

        .agent-market-mini span {
            display: block;
            font-family: 'IBM Plex Mono', monospace;
            font-size: 0.50rem;
            letter-spacing: 0.10em;
            text-transform: uppercase;
            color: var(--ink-light);
            margin-bottom: 0.18rem;
        }

        .agent-market-mini strong {
            display: block;
            font-size: 0.82rem;
            color: var(--navy);
            font-weight: 800;
        }

        .market-insight-card {
            background: var(--panel);
            border: 1px solid var(--line);
            border-radius: 18px;
            padding: 1.2rem 1.25rem;
            box-shadow: var(--shadow);
            margin-top: 0.8rem;
        }

        .market-insight-kicker {
            font-family: 'IBM Plex Mono', monospace;
            font-size: 0.60rem;
            letter-spacing: 0.13em;
            text-transform: uppercase;
            color: var(--ink-light);
            font-weight: 700;
            margin-bottom: 0.45rem;
        }

        .market-insight-title {
            font-size: 1.15rem;
            font-weight: 800;
            color: var(--navy);
            letter-spacing: -0.035em;
            margin-bottom: 0.35rem;
        }

        .market-insight-copy {
            font-size: 0.88rem;
            color: var(--ink-muted);
            line-height: 1.55;
            margin-bottom: 1rem;
        }

        .market-blue-panel {
            background: linear-gradient(180deg, #e8f2ff, #dbeafe);
            border: 1px solid rgba(47, 109, 246, 0.18);
            border-radius: 16px;
            padding: 1.05rem 1.1rem;
            margin-top: 1rem;
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.72);
        }

        .market-blue-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 0.7rem;
        }

        .market-blue-cell {
            background: rgba(255, 255, 255, 0.58);
            border: 1px solid rgba(47, 109, 246, 0.14);
            border-radius: 13px;
            padding: 0.78rem 0.85rem;
        }

        .market-blue-cell span {
            display: block;
            font-family: 'IBM Plex Mono', monospace;
            font-size: 0.54rem;
            letter-spacing: 0.11em;
            text-transform: uppercase;
            color: #4f78a9;
            margin-bottom: 0.28rem;
            font-weight: 700;
        }

        .market-blue-cell strong {
            display: block;
            font-size: 1rem;
            color: #12355b;
            font-weight: 800;
        }

        .market-insight-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 0.65rem;
        }

        .market-insight-cell {
            background: #ffffff;
            border: 1px solid var(--line);
            border-radius: 14px;
            padding: 0.78rem 0.85rem;
            box-shadow: 0 8px 24px rgba(23, 50, 77, 0.04);
        }

        .market-insight-cell span {
            display: block;
            font-family: 'IBM Plex Mono', monospace;
            font-size: 0.54rem;
            letter-spacing: 0.11em;
            text-transform: uppercase;
            color: var(--ink-light);
            margin-bottom: 0.28rem;
            font-weight: 700;
        }

        .market-insight-cell strong {
            display: block;
            font-size: 1rem;
            color: var(--navy);
            font-weight: 800;
        }

        .market-score-card {
            height: 100%;
            text-align: center;
        }

        .market-score-copy {
            font-size: 0.80rem;
            color: var(--ink-muted);
            line-height: 1.5;
            margin-top: 0.8rem;
        }

        @media (max-width: 900px) {
            .market-insight-grid,
            .market-blue-grid {
                grid-template-columns: 1fr 1fr;
            }
        }

        @media (max-width: 640px) {
            .market-insight-grid,
            .market-blue-grid {
                grid-template-columns: 1fr;
            }
        }
        
        /* Decision banner */
        .dec-banner {
            background: linear-gradient(135deg, #071827 0%, #0b2033 55%, #0e3658 100%);
            border-radius: 24px;
            padding: 1.7rem 2.1rem;
            margin-bottom: 2rem;
            display: flex; align-items: center; gap: 1.35rem; flex-wrap: wrap;
            position: relative; overflow: hidden;
            box-shadow: var(--shadow-lg);
            border: 1px solid rgba(255,255,255,0.08);
        }
        .dec-banner::before {
            content:''; position:absolute; inset:0;
            background:
                radial-gradient(ellipse 60% 80% at 90% 50%, rgba(14,165,233,0.18) 0%, transparent 60%),
                radial-gradient(ellipse 45% 65% at 10% 50%, rgba(16,185,129,0.12) 0%, transparent 55%);
            pointer-events:none;
        }
        .dec-cell { position:relative; z-index:1; }
        .dec-label {
            font-family:'IBM Plex Mono',monospace;
            font-size:0.58rem;
            letter-spacing:0.14em;
            text-transform:uppercase;
            color:rgba(226,232,240,0.50);
            margin-bottom:0.32rem;
            font-weight: 700;
        }
        .dec-value {
            font-size:1.42rem;
            font-weight:800;
            color:#ffffff;
            line-height:1;
            letter-spacing:-0.04em;
        }
        .dec-value.pos { color:#34d399; }
        .dec-value.neg { color:#fb7185; }
        .dec-value.lav { color:#60a5fa; }
        .dec-div { width:1px; height:42px; background:rgba(255,255,255,0.10); }

        /* Animated charts and gauges */
        .bar-chart-wrap {
            display:flex; align-items:flex-end; gap:6px;
            height:90px; margin:1rem 0; padding:0 4px;
        }
        .bar-col { display:flex; flex-direction:column; align-items:center; flex:1; height:100%; }
        .bar-fill {
            width:100%; border-radius:6px 6px 0 0;
            background: linear-gradient(180deg, var(--blue), var(--cyan));
            transform-origin:bottom; transform:scaleY(0);
            animation: barGrow 0.9s cubic-bezier(.4,0,.2,1) forwards;
        }
        @keyframes barGrow { to { transform:scaleY(1); } }
        @keyframes barGrowX { to { transform:scaleX(1); } }
        .bar-lbl {
            font-family:'IBM Plex Mono',monospace;
            font-size:0.50rem;
            color:var(--ink-light);
            margin-top:4px;
            letter-spacing:0.04em;
        }
        .score-ring-wrap { display:flex; align-items:center; justify-content:center; padding:1rem 0; }
        .score-ring { position:relative; width:110px; height:110px; }
        .score-ring svg { transform:rotate(-90deg); }
        .score-ring-bg { fill:none; stroke:var(--blue-soft); stroke-width:8; }
        .score-ring-fg {
            fill:none; stroke-width:8; stroke-linecap:round; stroke:url(#ringGrad);
            transition:stroke-dashoffset 1.2s cubic-bezier(.4,0,.2,1);
        }
        .score-ring-label {
            position:absolute; inset:0;
            display:flex; flex-direction:column; align-items:center; justify-content:center;
        }
        .score-ring-num {
            font-size:1.55rem;
            color:var(--navy);
            line-height:1;
            font-weight:800;
            letter-spacing:-0.04em;
        }
        .score-ring-sub {
            font-family:'IBM Plex Mono',monospace;
            font-size:0.52rem;
            letter-spacing:0.1em;
            text-transform:uppercase;
            color:var(--ink-light);
            font-weight:700;
        }
        .gauge-wrap { display:flex; align-items:center; gap:1.2rem; margin:1rem 0; }
        .gauge-track {
            flex:1; height:10px; border-radius:999px;
            background:linear-gradient(90deg, var(--red-soft), var(--blue-soft), var(--emerald-soft));
            position:relative;
        }
        .gauge-fill {
            position:absolute; top:0; left:0; bottom:0; border-radius:999px;
            background:linear-gradient(90deg, var(--red), var(--blue), var(--emerald));
            transition:width 1.4s cubic-bezier(.4,0,.2,1);
        }
        .gauge-thumb {
            position:absolute; top:-4px; width:18px; height:18px; border-radius:50%;
            background:white; border:2px solid var(--blue);
            box-shadow:0 2px 8px rgba(37,99,235,0.28);
            transform:translateX(-50%);
            transition:left 1.4s cubic-bezier(.4,0,.2,1);
        }
        .gauge-lbl {
            font-family:'IBM Plex Mono',monospace;
            font-size:0.58rem;
            color:var(--ink-light);
            white-space:nowrap;
            letter-spacing:0.08em;
            font-weight:700;
        }

        /* Tabs */
        div[data-testid="stTabs"] button {
            font-family:'Plus Jakarta Sans',system-ui,sans-serif !important;
            font-size:0.84rem !important;
            font-weight:700 !important;
            color:var(--ink-muted) !important;
            border:none !important;
            border-radius:12px 12px 0 0 !important;
            padding:0.66rem 1rem !important;
        }
        div[data-testid="stTabs"] button[aria-selected="true"] {
            color:var(--blue) !important;
            background:white !important;
            border-bottom:2px solid var(--blue) !important;
        }
        div[data-testid="stTabPanel"] {
            background:white;
            border:1px solid var(--line);
            border-radius:0 16px 16px 16px;
            padding:1.6rem !important;
            box-shadow: var(--shadow);
        }

        /* Buttons */
        div[data-testid="stButton"] > button[kind="primary"] {
            background:linear-gradient(135deg, var(--blue), var(--cyan)) !important;
            color:white !important;
            border:none !important;
            border-radius:14px !important;
            font-family:'Plus Jakarta Sans',system-ui,sans-serif !important;
            font-size:0.92rem !important;
            font-weight:750 !important;
            padding:0.74rem 1.4rem !important;
            box-shadow:0 10px 28px rgba(37,99,235,0.26) !important;
            transition:transform 0.15s, box-shadow 0.15s !important;
        }
        div[data-testid="stButton"] > button[kind="primary"]:hover {
            transform:translateY(-2px) !important;
            box-shadow:0 16px 36px rgba(37,99,235,0.34) !important;
        }
        div[data-testid="stButton"] > button:not([kind="primary"]) {
            background:white !important;
            color:var(--navy) !important;
            border:1px solid var(--line) !important;
            border-radius:14px !important;
            font-family:'Plus Jakarta Sans',system-ui,sans-serif !important;
            font-size:0.88rem !important;
            font-weight:650 !important;
            padding:0.70rem 1.2rem !important;
            transition:border-color 0.15s, transform 0.12s, box-shadow 0.12s !important;
        }
        div[data-testid="stButton"] > button:not([kind="primary"]):hover {
            border-color:rgba(37,99,235,0.32) !important;
            transform:translateY(-1px) !important;
            box-shadow: 0 8px 24px rgba(15,23,42,0.06) !important;
        }

        /* Misc */
        div[data-testid="stAlert"] {
            border-radius:15px !important;
            font-size:0.86rem !important;
            border: 1px solid var(--line) !important;
        }
        .info-card {
            background:linear-gradient(180deg, #ffffff, #f8fafc);
            border:1px solid var(--line);
            border-left:4px solid var(--blue);
            border-radius:0 16px 16px 0;
            padding:1rem 1.15rem;
            font-size:0.88rem;
            color:var(--ink-muted);
            margin-bottom:1rem;
            box-shadow: 0 8px 28px rgba(15,23,42,0.04);
            line-height: 1.55;
        }
        code, pre {
            font-family:'IBM Plex Mono',monospace !important;
            font-size:0.78rem !important;
        }
        div[data-testid="stDataFrame"] {
            border:1px solid var(--line) !important;
            border-radius:14px !important;
            overflow:hidden !important;
            box-shadow: var(--shadow);
        }
        hr {
            border:none !important;
            border-top:1px solid var(--line) !important;
            margin:1.4rem 0 !important;
        }
        [data-testid="stSidebar"] label {
            font-size:0.82rem !important;
            color:var(--ink-muted) !important;
        }
        .stMarkdown a {
            color: var(--blue) !important;
            text-decoration: none !important;
            font-weight: 650;
        }



        /* V2 light institutional fintech refresh */
        :root {
            --bg: #f5f8fc;
            --bg2: #edf4fb;
            --panel: #ffffff;
            --panel-soft: #f8fbff;
            --panel-blue: #ecf5ff;
            --navy: #17324d;
            --navy-2: #24425f;
            --blue: #2f6df6;
            --blue-soft: #e4efff;
            --cyan: #28a9e8;
            --cyan-soft: #e5f7ff;
            --emerald: #10a37f;
            --emerald-soft: #dcf8ef;
            --amber: #d99613;
            --amber-soft: #fff2d7;
            --red: #de5353;
            --red-soft: #ffe8e8;
            --ink: #172033;
            --ink-muted: #53667a;
            --ink-light: #8da0b3;
            --line: rgba(23, 50, 77, 0.12);
            --line-strong: rgba(47, 109, 246, 0.22);
            --shadow: 0 14px 34px rgba(23, 50, 77, 0.08);
            --shadow-m: 0 20px 52px rgba(23, 50, 77, 0.12);
            --shadow-lg: 0 28px 78px rgba(23, 50, 77, 0.16);
        }
        html, body, [class*="css"], .stApp, p, li, label, div, span, button, input, textarea {
            font-family: 'Plus Jakarta Sans', system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
        }
        code, pre, .hero-eyebrow, .hero-pill, .ticker-item, .sb-sec, .sec-div-text,
        div[data-testid="stTextInput"] label, div[data-testid="stMetric"] label,
        .dec-label, .agent-badge, .gauge-lbl, .bar-lbl, .sb-card-kicker {
            font-family: 'IBM Plex Mono', monospace !important;
        }
        .stApp {
            background:
                radial-gradient(circle at 12% 0%, rgba(47,109,246,0.12), transparent 28rem),
                radial-gradient(circle at 94% 6%, rgba(40,169,232,0.12), transparent 30rem),
                linear-gradient(180deg, #f7fbff 0%, #f3f7fc 45%, #eef4fa 100%) !important;
        }
        .hero {
            background:
                radial-gradient(circle at 78% 8%, rgba(40,169,232,0.24), transparent 28rem),
                radial-gradient(circle at 18% 20%, rgba(47,109,246,0.20), transparent 24rem),
                linear-gradient(135deg, #ffffff 0%, #eff7ff 46%, #dfeefe 100%) !important;
            border: 1px solid rgba(47,109,246,0.10);
            border-top: 0;
            box-shadow: 0 24px 70px rgba(23,50,77,0.12) !important;
        }
        .hero::after {
            background-image:
                linear-gradient(rgba(47,109,246,0.055) 1px, transparent 1px),
                linear-gradient(90deg, rgba(47,109,246,0.055) 1px, transparent 1px) !important;
        }
        .hero-eyebrow { color: #2f6df6 !important; }
        .hero-eyebrow::before { background: linear-gradient(90deg, #2f6df6, transparent) !important; }
        .hero-h1 { color: #17324d !important; letter-spacing: -0.065em !important; }
        .hero-h1 em {
            background: linear-gradient(90deg, #2f6df6, #28a9e8, #10a37f) !important;
            -webkit-background-clip: text !important;
            -webkit-text-fill-color: transparent !important;
            background-clip: text !important;
        }
        .hero-sub { color: #53667a !important; }
        .hero-pill {
            background: rgba(255,255,255,0.72) !important;
            border-color: rgba(47,109,246,0.16) !important;
            color: #53667a !important;
            box-shadow: 0 10px 24px rgba(23,50,77,0.06);
        }
        .hero-pill.active {
            background: rgba(16,163,127,0.10) !important;
            border-color: rgba(16,163,127,0.26) !important;
            color: #0f7a60 !important;
        }
        .ticker-band { border-top-color: rgba(47,109,246,0.14) !important; }
        .ticker-band::before { background: linear-gradient(90deg, #ffffff, transparent) !important; }
        .ticker-band::after { background: linear-gradient(-90deg, #dfeefe, transparent) !important; }
        .ticker-item { color: #7d91a8 !important; }
        .ticker-item .t-sym { color: #17324d !important; }
        .ticker-item .t-up { color: #10a37f !important; }
        .ticker-item .t-down { color: #de5353 !important; }
        .hero-orb1 { background: radial-gradient(circle, rgba(47,109,246,0.22) 0%, transparent 68%) !important; }
        .hero-orb2 { background: radial-gradient(circle, rgba(16,163,127,0.16) 0%, transparent 70%) !important; }
        .hero-orb3 { background: radial-gradient(circle, rgba(40,169,232,0.18) 0%, transparent 70%) !important; }

        /* Always-visible main execution controls */
        .execution-panel {
            background: rgba(255,255,255,0.86);
            border: 1px solid var(--line-strong);
            border-radius: 24px;
            padding: 1.25rem 1.35rem;
            margin: 0.25rem 0 1.2rem;
            box-shadow: var(--shadow);
            backdrop-filter: blur(14px);
        }
        .execution-kicker {
            font-family: 'IBM Plex Mono', monospace !important;
            font-size: 0.64rem;
            letter-spacing: 0.15em;
            text-transform: uppercase;
            color: var(--blue);
            font-weight: 700;
            margin-bottom: 0.35rem;
        }
        .execution-title {
            font-size: 1.35rem;
            line-height: 1.15;
            letter-spacing: -0.04em;
            color: var(--navy);
            font-weight: 800;
            margin-bottom: 0.35rem;
        }
        .execution-copy {
            color: var(--ink-muted);
            font-size: 0.92rem;
            line-height: 1.6;
            max-width: 840px;
        }
        .inline-status {
            border-radius: 18px;
            padding: 0.95rem 1rem;
            border: 1px solid var(--line);
            font-size: 0.88rem;
            line-height: 1.45;
            margin-top: 0.85rem;
            box-shadow: 0 8px 24px rgba(23,50,77,0.05);
        }
        .inline-status.safe {
            background: linear-gradient(180deg, #f2fff9, var(--emerald-soft));
            color: #0f6b55;
            border-color: rgba(16,163,127,0.22);
        }
        .inline-status.armed {
            background: linear-gradient(180deg, #fffaf0, var(--amber-soft));
            color: #7a4b05;
            border-color: rgba(217,150,19,0.30);
        }
        div[data-testid="stRadio"] {
            background: #ffffff !important;
            border: 1px solid var(--line) !important;
            border-radius: 18px !important;
            padding: 0.7rem 0.85rem 0.85rem !important;
            box-shadow: 0 8px 24px rgba(23,50,77,0.05) !important;
        }
        div[data-testid="stRadio"] label { color: var(--navy) !important; }
        div[data-testid="InputInstructions"] { display: none !important; }
        div[data-testid="stTextInput"] input {
            min-height: 56px !important;
            padding-right: 1.25rem !important;
            font-size: 0.98rem !important;
            border-color: rgba(47,109,246,0.20) !important;
        }
        div[data-testid="stTextInput"] input::placeholder {
            color: #8da0b3 !important;
            opacity: 1 !important;
        }
        div[data-testid="stButton"] > button[kind="primary"] {
            background: linear-gradient(135deg, #2f6df6, #28a9e8) !important;
        }
        .dec-banner {
            background: linear-gradient(135deg, #17324d 0%, #24425f 55%, #2f6df6 145%) !important;
        }
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #ffffff 0%, #f3f8fd 100%) !important;
        }


        /* Streamlit popover chevron fix */
        span[data-testid="stIconMaterial"],
        [data-testid="stIconMaterial"],
        .material-symbols-rounded,
        .material-symbols-outlined,
        .material-symbols-sharp,
        span[class*="material-symbols"],
        i[class*="material-symbols"] {
            font-family: 'Material Symbols Rounded' !important;
            font-weight: normal !important;
            font-style: normal !important;
            font-size: 1.12rem !important;
            line-height: 1 !important;
            letter-spacing: normal !important;
            text-transform: none !important;
            white-space: nowrap !important;
            word-wrap: normal !important;
            direction: ltr !important;
            -webkit-font-feature-settings: 'liga' !important;
            font-feature-settings: 'liga' !important;
            -webkit-font-smoothing: antialiased !important;
            font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24 !important;
        }

        div[data-testid="stPopover"] button {
            justify-content: center !important;
            gap: 0.45rem !important;
        }

        @media (max-width: 900px) {
            .hero { padding: 2.5rem 1.4rem 0 1.4rem; margin-left: -0.6rem; margin-right: -0.6rem; }
            .dec-banner { padding: 1.3rem; gap: 1rem; }
            .dec-div { display: none; }
        }
    </style>
    """,
    unsafe_allow_html=True
)



# ── Badge helpers ──────────────────────────────────────────────────────────────

def badge_for_agent(agent_result: dict, agent_type: str = "generic") -> tuple[str, str]:
    status = agent_result.get("status", "unknown")
    if status == "complete":
        return "Complete", "success"
    if status == "disabled":
        return "Disabled", "neutral"
    if status == "blocked":
        return "Blocked", "warning"
    if status == "error":
        return "Error", "error"
    if agent_type == "risk":
        approval = agent_result.get("data", {}).get("approval", "")
        if str(approval).startswith("Approved"):
            return "Approved", "success"
        return "Blocked", "warning"
    return status.title(), "neutral"


AGENT_ICONS = {
    "Market Agent":   "📈",
    "News Agent":     "📰",
    "Strategy Agent": "🧭",
    "Risk Agent":     "🛡",
    "Execution Agent":"⚡",
}

def render_agent_card(title: str, agent_result: dict, agent_type: str = "generic") -> None:
    label, badge_cls = badge_for_agent(agent_result, agent_type)
    summary = agent_result.get("summary", "No summary available.")
    icon = AGENT_ICONS.get(title, "✦")

    st.markdown(
        f"""
        <div class="agent-card {badge_cls}">
            <div class="agent-card-icon">{icon}</div>
            <div class="agent-badge {badge_cls}">{label}</div>
            <div class="agent-title">{title}</div>
            <div class="agent-summary">{summary}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

def safe_metric_value(value, default="N/A"):
    return default if value is None else value

def sec_div(text):
    st.markdown(
        f"""<div class="sec-div">
            <div class="sec-div-line"></div>
            <div class="sec-div-dot"></div>
            <div class="sec-div-text">{text}</div>
            <div class="sec-div-dot"></div>
            <div class="sec-div-line"></div>
        </div>""",
        unsafe_allow_html=True
    )

# ── Ticker items ───────────────────────────────────────────────────────────────
TICKERS = [
    ("AAPL","+0.84","up"), ("NVDA","+2.31","up"), ("MSFT","-0.12","down"),
    ("TSLA","+1.55","up"), ("AMZN","+0.67","up"), ("META","+1.02","up"),
    ("GOOG","-0.44","down"),("JPM","+0.29","up"), ("SPY","+0.38","up"),
    ("QQQ","+0.91","up"), ("NFLX","+1.77","up"), ("AMD","-0.53","down"),
]

ticker_html = "&nbsp;&nbsp;<span style='color:rgba(253,249,251,0.18)'>·</span>&nbsp;&nbsp;".join(
    f'<span class="ticker-item"><span class="t-sym">{s}</span>&nbsp;<span class="t-{"up" if d=="up" else "down"}">'
    f'{"▲" if d=="up" else "▼"}&nbsp;{p}%</span></span>'
    for s, p, d in TICKERS * 2
)

# ── Hero ───────────────────────────────────────────────────────────────────────
st.markdown(
    f"""
    <div class="hero">
      <div class="hero-orb1"></div>
      <div class="hero-orb2"></div>
      <div class="hero-orb3"></div>
      <div class="hero-inner">
        <div class="hero-eyebrow">Intelligent Broker Desk</div>
        <h1 class="hero-h1">Trade decisions,<br><em>before execution.</em></h1>
        <p class="hero-sub">
            A clean paper-trading workspace for equity analysis, pre-trade risk review
            and order testing. The desk combines market movement, news context, strategy
            signals, risk limits and Alpaca paper routing into one controlled workflow
            for clear, repeatable decisions.
        </p>
        <div class="hero-pills">
          <div class="hero-pill active"><span class="live-dot"></span>All Systems Operational</div>
          <div class="hero-pill">Dry Run Available</div>
          <div class="hero-pill">Alpaca Paper Routing</div>
          <div class="hero-pill">Strategy Signal</div>
          <div class="hero-pill">Pre-Trade Risk</div>
        </div>
        <div class="ticker-band">
          <div class="ticker-track">{ticker_html}</div>
        </div>
      </div>
    </div>
    """,
    unsafe_allow_html=True
)

st.info("Paper-trading environment only — not investment advice. Orders are routed to Alpaca only when Paper Trading mode is explicitly selected.")

# ── Main execution controls ────────────────────────────────────────────────────
st.markdown(
    """
    <div class="execution-panel">
        <div class="execution-kicker">Order Routing · Execution Mode</div>
        <div class="execution-title">Select your execution environment</div>
        <div class="execution-copy">
            Run the full agent pipeline in dry-run mode to analyse a trade without routing any order.
            Switch to Alpaca Paper Trading when you're ready to submit to your paper account —
            a useful final step before committing to a live strategy.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

exec_col, conn_col = st.columns([1.15, 0.85])

with exec_col:
    execution_mode = st.radio(
        "Execution mode",
        options=["Dry Run Only", "Alpaca Paper Trading"],
        index=0,
        horizontal=True,
        help="Dry Run processes the full pipeline — market, news, strategy, risk — without placing an order. Alpaca Paper Trading routes approved orders to your Alpaca paper account in real time.",
        key="main_execution_mode"
    )

submit_paper_order = execution_mode == "Alpaca Paper Trading"

with exec_col:
    if submit_paper_order:
        st.markdown(
            '<div class="inline-status armed">⚡ <b>Paper execution armed.</b><br>Any order that clears risk review will be submitted to your Alpaca paper account.</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            '<div class="inline-status safe">🛡️ <b>Dry-run mode active.</b><br>The pipeline will price, analyse and risk-check the trade — no order will be placed.</div>',
            unsafe_allow_html=True
        )

with conn_col:
    st.markdown(
        '<div class="info-card"><b>Alpaca account status</b><br>Verify your paper account is connected and has sufficient buying power before arming execution.</div>',
        unsafe_allow_html=True
    )
    if st.button("Check Alpaca Connection", use_container_width=True, key="main_verify_alpaca"):
        connection = check_alpaca_connection()
        if connection["status"] == "connected":
            st.success("Connected to Alpaca")
            st.write(f"Account Status: {connection['account_status']}")
            st.write(f"Buying Power: ${connection['buying_power']}")
            st.write(f"Cash: ${connection['cash']}")
        else:
            st.error("Unable to reach Alpaca — check your API credentials.")
            st.write(connection["message"])

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sb-logo"><em>Intelligent</em><br>Broker Desk ✦</div>', unsafe_allow_html=True)

    st.markdown('<div class="sb-sec">Execution Status</div>', unsafe_allow_html=True)

    st.markdown(
        f"""
        <div class="sb-trade-card">
            <div class="sb-card-kicker">Active Mode</div>
            <div class="sb-card-title">{execution_mode}</div>
            <div class="sb-card-copy">
                The execution toggle is also pinned to the main canvas, so it stays
                accessible even when the sidebar is collapsed.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    if submit_paper_order:
        st.markdown(
            '<div class="mode-banner armed">⚡ <b>Paper execution armed.</b><br>Approved orders will be routed to Alpaca paper trading.</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            '<div class="mode-banner safe">🛡️ <b>Dry-run mode active.</b><br>The full pipeline runs without placing any orders.</div>',
            unsafe_allow_html=True
        )

    st.markdown('<div class="sb-sec">Connectivity</div>', unsafe_allow_html=True)

    if st.button("Verify Alpaca Connection", use_container_width=True, key="sidebar_verify_alpaca"):
        connection = check_alpaca_connection()
        if connection["status"] == "connected":
            st.success("Connected to Alpaca")
            st.write(f"Account Status: {connection['account_status']}")
            st.write(f"Buying Power: ${connection['buying_power']}")
            st.write(f"Cash: ${connection['cash']}")
        else:
            st.error("Unable to reach Alpaca — check your API credentials.")
            st.write(connection["message"])

    st.markdown('<div class="sb-sec">Sample Instructions</div>', unsafe_allow_html=True)
    for q in ["Buy 10 AAPL at market", "Should I buy Nvidia today?", "Analyse Microsoft fundamentals", "Buy 100 Tesla at market"]:
        st.code(q)

    st.markdown('<div class="sb-sec">Recent Runs</div>', unsafe_allow_html=True)
    recent_runs = get_recent_workflow_runs(limit=5)
    if recent_runs:
        for run in recent_runs:
            sig = run['strategy_signal']
            dot_col = "#7aad8f" if sig in ("BUY","STRONG_BUY") else "#c96b7a" if sig == "SELL" else "#b8a9d9"
            st.markdown(
                f"""<div class="run-row">
                    <div class="run-dot" style="background:{dot_col}"></div>
                    <span><b>#{run['id']}</b> · {run['ticker']} · {sig} · {run['execution_status']}</span>
                </div>""",
                unsafe_allow_html=True
            )
    else:
        st.caption("No runs recorded yet — submit an instruction to get started.")

# ── Request input ──────────────────────────────────────────────────────────────
sec_div("Trade Instruction")

if "broker_query_text" not in st.session_state:
    st.session_state["broker_query_text"] = ""

if "pending_voice_text" in st.session_state:
    st.session_state["broker_query_text"] = st.session_state["pending_voice_text"]
    del st.session_state["pending_voice_text"]

st.markdown(
    '<div class="info-card"><b>How to write an instruction</b><br>'
    'Specify the ticker, quantity and order intent. '
    'Examples: <em>Buy 10 AAPL at market</em> · <em>Should I buy Nvidia today?</em> · <em>Analyse Microsoft</em></div>',
    unsafe_allow_html=True
)

st.text_input(
    "Trade instruction",
    key="broker_query_text",
    placeholder="e.g. Buy 10 AAPL at market"
)

button_col1, button_col2 = st.columns([1, 1])

with button_col1:
    run_button = st.button("✦ Run Trading Workflow", type="primary", use_container_width=True)

with button_col2:
    with st.popover("🎙️ Voice Command", use_container_width=True):
        st.caption("Record your instruction, then hit Transcribe to populate the field above.")
        audio_value = st.audio_input(
            "Record voice instruction",
            sample_rate=16000,
            help="Say something like: 'Buy ten Apple at market.'"
        )
        if st.button("Transcribe & Use", use_container_width=True):
            if audio_value is None:
                st.error("No recording detected — please record an instruction first.")
            else:
                with st.spinner("Transcribing…"):
                    transcription_result = transcribe_audio(audio_value)
                if transcription_result["status"] == "complete":
                    st.session_state["pending_voice_text"] = transcription_result["text"]
                    st.success("Transcription complete — instruction loaded.")
                    st.rerun()
                else:
                    st.error(transcription_result["summary"])

query = st.session_state.get("broker_query_text", "")

if run_button:
    if not query:
        st.error("Please enter a trade instruction before running the pipeline.")
    else:
        with st.spinner("Running market data, news sentiment, strategy, risk and execution agents…"):
            workflow_result = run_broker_workflow(
                query=query,
                submit_paper_order=submit_paper_order
            )
            run_id = save_workflow_run(workflow_result)
            workflow_result["database_run_id"] = run_id
            st.session_state["workflow_result"] = workflow_result
            st.success(f"✦ Pipeline complete — saved as Run #{run_id}")

# ── Results ────────────────────────────────────────────────────────────────────
workflow_result = st.session_state.get("workflow_result")

if workflow_result:
    parsed         = workflow_result["parsed_request"]
    final_decision = workflow_result["final_decision"]
    agents         = workflow_result["agents"]

    market_result    = agents["market"]
    news_result      = agents["news"]
    strategy_result  = agents["strategy"]
    risk_result      = agents["risk"]
    execution_result = agents["execution"]

    market_data    = market_result.get("data", {})
    news_data      = news_result.get("data", {})
    strategy_data  = strategy_result.get("data", {})
    risk_data      = risk_result.get("data", {})
    execution_data = execution_result.get("data", {})

    # ── Decision banner ────────────────────────────────────────────────────────
    sec_div("Trade Decision")

    sig   = final_decision.get("strategy_signal", "—")
    risk  = final_decision.get("risk_approval", "—")
    exec_ = final_decision.get("execution_status", "—")
    conf  = final_decision.get("confidence", 0)

    sig_cls  = "pos" if "BUY" in sig  else "neg" if "SELL" in sig else ""
    risk_cls = "pos" if "Approved" in risk else "neg"

    st.markdown(
        f"""
        <div class="dec-banner">
            <div class="dec-cell"><div class="dec-label">Ticker</div>
              <div class="dec-value">{parsed.get('ticker','—')}</div></div>
            <div class="dec-div"></div>
            <div class="dec-cell"><div class="dec-label">Side</div>
              <div class="dec-value">{parsed.get('side','—')}</div></div>
            <div class="dec-div"></div>
            <div class="dec-cell"><div class="dec-label">Quantity</div>
              <div class="dec-value">{parsed.get('requested_quantity','—')}</div></div>
            <div class="dec-div"></div>
            <div class="dec-cell"><div class="dec-label">Signal</div>
              <div class="dec-value {sig_cls}">{sig}</div></div>
            <div class="dec-div"></div>
            <div class="dec-cell"><div class="dec-label">Conviction</div>
              <div class="dec-value lav">{conf}%</div></div>
            <div class="dec-div"></div>
            <div class="dec-cell"><div class="dec-label">Risk</div>
              <div class="dec-value {risk_cls}">{risk}</div></div>
            <div class="dec-div"></div>
            <div class="dec-cell"><div class="dec-label">Execution</div>
              <div class="dec-value lav">{exec_}</div></div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # ── Market snapshot metrics ────────────────────────────────────────────────
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with col1:  st.metric("Last Price",    f"${market_data.get('latest_price', 'N/A')}")
    with col2:  st.metric("Day Change",    f"{market_data.get('daily_change_pct', 'N/A')}%")
    with col3:  st.metric("Trend",          market_data.get("trend", "N/A"))
    with col4:  st.metric("20-Day MA",     f"${market_data.get('ma20', 'N/A')}")
    with col5:  st.metric("50-Day MA",     f"${market_data.get('ma50', 'N/A')}")
    with col6:  st.metric("Trend Score",   f"{market_data.get('trend_score', 'N/A')}/100")

    # ── Agent activity cards ───────────────────────────────────────────────────
    sec_div("Agent Pipeline")

    ac1, ac2, ac3, ac4, ac5 = st.columns(5)
    with ac1: render_agent_card("Market Agent",    market_result)
    with ac2: render_agent_card("News Agent",      news_result)
    with ac3: render_agent_card("Strategy Agent",  strategy_result)
    with ac4: render_agent_card("Risk Agent",      risk_result, agent_type="risk")
    with ac5: render_agent_card("Execution Agent", execution_result)

    # ── Tabs ───────────────────────────────────────────────────────────────────
    sec_div("Deep Dive")

    tab_market, tab_news, tab_strategy, tab_risk, tab_execution, tab_audit, tab_history, tab_raw = st.tabs(
        ["📈 Market", "📰 News", "🧭 Strategy", "🛡 Risk", "⚡ Execution", "🔍 Audit Trail", "🕓 History", "⚙ Raw Output"]
    )

    with tab_market:
        st.subheader("Market Data & Technical Indicators")
        if market_result["status"] == "complete":
            # The detailed card below already shows price, move, trend, MA20, MA50
            # and trend score. Keep only one version in the Market tab to avoid
            # repeating the same technical data twice.

            # ── Technical read card and animated trend score ───────────────────
            market_ticker = market_data.get("ticker", "UNKNOWN")
            market_trend = market_data.get("trend", "Neutral")
            latest_price = market_data.get("latest_price", "N/A")
            daily_change = market_data.get("daily_change_pct", "N/A")
            ma20 = market_data.get("ma20", "N/A")
            ma50 = market_data.get("ma50", "N/A")
            trend_score = market_data.get("trend_score", "N/A")

            price_display = f"${latest_price}" if latest_price != "N/A" else "N/A"
            ma20_display = f"${ma20}" if ma20 != "N/A" else "N/A"
            ma50_display = f"${ma50}" if ma50 != "N/A" else "N/A"
            day_display = f"{daily_change}%" if daily_change != "N/A" else "N/A"
            trend_score_display = f"{trend_score}/100" if trend_score != "N/A" else "N/A"

            if market_trend == "Bullish":
                market_comment = "Price is trading above the key moving averages, giving the setup a constructive technical bias."
            elif market_trend == "Bearish":
                market_comment = "Price is trading below the key moving averages, keeping the setup under technical pressure."
            else:
                market_comment = "Price action is mixed around the key moving averages, so the technical setup remains neutral."

            try:
                ts = max(5, min(100, int(float(market_data.get("trend_score", 50)))))
            except (TypeError, ValueError):
                ts = 50

            circ = 2 * 3.14159 * 44
            offset = circ * (1 - ts / 100)

            weights = [0.45, 0.62, 0.50, 0.78, 0.55, 0.88, 0.70, 0.65, 0.82, ts / 100]
            bars_html = ""
            for i, w in enumerate(weights):
                h = max(8, int(w * 100))
                bars_html += (
                    f'<div class="bar-col">'
                    f'<div class="bar-fill" style="height:{h}%;animation-delay:{i*0.09}s"></div>'
                    f'<div class="bar-lbl">T{i+1}</div></div>'
                )

            score_col, insight_col = st.columns([0.9, 1.7])

            with score_col:
                st.markdown(
                    f"""
                    <div class="market-insight-card market-score-card">
                        <div class="market-insight-kicker">Trend Score</div>
                        <div class="score-ring-wrap">
                            <div class="score-ring">
                                <svg width="110" height="110" viewBox="0 0 110 110">
                                    <defs>
                                        <linearGradient id="ringGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                                            <stop offset="0%" stop-color="#2f6df6" />
                                            <stop offset="55%" stop-color="#28a9e8" />
                                            <stop offset="100%" stop-color="#10a37f" />
                                        </linearGradient>
                                    </defs>
                                    <circle class="score-ring-bg" cx="55" cy="55" r="44"></circle>
                                    <circle class="score-ring-fg" cx="55" cy="55" r="44"
                                        stroke-dasharray="{circ}"
                                        stroke-dashoffset="{offset}">
                                    </circle>
                                </svg>
                                <div class="score-ring-label">
                                    <div class="score-ring-num">{ts}</div>
                                    <div class="score-ring-sub">/100</div>
                                </div>
                            </div>
                        </div>
                        <div class="market-score-copy">
                            The score summarises price direction versus the short and medium moving averages.
                        </div>
                        <div class="bar-chart-wrap">{bars_html}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            with insight_col:
                market_cells_html = "".join([
                    f'<div class="market-blue-cell"><span>Last Price</span><strong>{price_display}</strong></div>',
                    f'<div class="market-blue-cell"><span>1-Day Move</span><strong>{day_display}</strong></div>',
                    f'<div class="market-blue-cell"><span>Trend Score</span><strong>{trend_score_display}</strong></div>',
                    f'<div class="market-blue-cell"><span>20-Day MA</span><strong>{ma20_display}</strong></div>',
                    f'<div class="market-blue-cell"><span>50-Day MA</span><strong>{ma50_display}</strong></div>',
                    f'<div class="market-blue-cell"><span>Signal Bias</span><strong>{market_trend}</strong></div>',
                ])

                technical_read_html = (
                    '<div class="market-insight-card">'
                    '<div class="market-insight-kicker">Technical Read</div>'
                    f'<div class="market-insight-title">{market_ticker} Market Snapshot · {market_trend}</div>'
                    f'<div class="market-insight-copy">{market_comment}</div>'
                    '<div class="market-blue-panel">'
                    f'<div class="market-blue-grid">{market_cells_html}</div>'
                    '</div>'
                    '</div>'
                )

                st.markdown(technical_read_html, unsafe_allow_html=True)
        else:
            st.error(market_result.get("summary", "Market Agent did not complete successfully."))

    with tab_news:
        st.subheader("News Flow & Sentiment Analysis")
        if news_result["status"] == "complete":
            n1, n2 = st.columns(2)
            with n1: st.metric("Sentiment",       news_data.get("sentiment", "N/A"))
            with n2: st.metric("Sentiment Score", f"{news_data.get('sentiment_score', 'N/A')}%")

            # ── Animated sentiment gauge ──────────────────────────────────────
            try:
                score = max(0, min(100, int(news_data.get("sentiment_score", 50))))
            except (TypeError, ValueError):
                score = 50
            st.markdown(
                f"""
                <div class="gauge-wrap">
                  <div class="gauge-lbl">Bearish</div>
                  <div class="gauge-track">
                    <div class="gauge-fill" style="width:{score}%"></div>
                    <div class="gauge-thumb" style="left:{score}%"></div>
                  </div>
                  <div class="gauge-lbl">Bullish</div>
                </div>
                <div style="font-family:'IBM Plex Mono',monospace;font-size:0.58rem;color:var(--ink-light);
                  text-align:center;margin-bottom:0.8rem">Sentiment Reading · {score}%</div>
                """,
                unsafe_allow_html=True
            )

            st.markdown("#### Recent Headlines")
            articles = news_data.get("articles", [])
            if articles:
                for article in articles:
                    title = article.get("title")
                    link  = article.get("link")
                    if link:
                        st.markdown(f"- [{title}]({link})")
                    else:
                        st.write(f"- {title}")
            else:
                st.info("No recent headlines found — sentiment defaulted to Neutral.")
            st.info(news_result.get("summary", "No news summary available."))
        else:
            st.error(news_result.get("summary", "News Agent did not complete successfully."))

    with tab_strategy:
        st.subheader("Strategy Signal & Entry Rationale")
        s1, s2, s3 = st.columns(3)
        with s1: st.metric("Signal",     strategy_data.get("signal", "HOLD"))
        with s2: st.metric("Conviction", f"{strategy_data.get('confidence', 50)}%")
        with s3: st.metric("Volatility", strategy_data.get("volatility_status", "Unknown"))

        s4, s5, s6 = st.columns(3)
        with s4: st.metric("Trend Score",      f"{strategy_data.get('trend_score', 'N/A')}/100")
        with s5: st.metric("Sentiment Score",  f"{strategy_data.get('sentiment_score', 'N/A')}/100")
        with s6: st.metric("Volatility Score", f"{strategy_data.get('volatility_score', 'N/A')}/100")

        # ── 3-score animated progress bars ───────────────────────────────────
        score_items = [
            ("Trend",      strategy_data.get("trend_score", 50),      "#2563eb"),
            ("Sentiment",  strategy_data.get("sentiment_score", 50),  "#0ea5e9"),
            ("Volatility", strategy_data.get("volatility_score", 50), "#10b981"),
        ]
        bars3 = ""
        for i, (lbl, val, col) in enumerate(score_items):
            try:
                pct = max(4, min(100, int(val)))
            except (TypeError, ValueError):
                pct = 50
            bars3 += f"""
            <div style="margin-bottom:0.8rem">
              <div style="display:flex;justify-content:space-between;font-family:'IBM Plex Mono',monospace;
                font-size:0.6rem;color:var(--ink-light);margin-bottom:5px">
                <span>{lbl}</span><span>{pct}/100</span>
              </div>
              <div style="background:var(--lav-pale);border-radius:999px;height:9px;overflow:hidden">
                <div style="height:100%;width:{pct}%;background:{col};border-radius:999px;
                  animation:barGrowX 1s cubic-bezier(.4,0,.2,1) {i*0.15}s forwards;
                  transform:scaleX(0);transform-origin:left"></div>
              </div>
            </div>"""
        st.markdown(f'<div style="margin:1rem 0 0.5rem">{bars3}</div>', unsafe_allow_html=True)
        st.markdown("#### Strategy Rationale")
        st.info(strategy_data.get("reason", "No strategy rationale available."))

    with tab_risk:
        st.subheader("Pre-Trade Risk Review")
        r1, r2, r3, r4 = st.columns(4)
        with r1: st.metric("Decision",      risk_data.get("approval", "Blocked"))
        with r2: st.metric("Risk Level",    risk_data.get("risk_level", "High"))
        with r3: st.metric("Requested Qty", risk_data.get("requested_quantity", parsed.get("requested_quantity", "N/A")))
        with r4: st.metric("Approved Qty",  risk_data.get("approved_quantity", 0))

        r5, r6, r7, r8 = st.columns(4)
        with r5: st.metric("Notional Value",    f"${risk_data.get('notional', 0)}")
        with r6:
            stop_loss = risk_data.get("stop_loss")
            st.metric("Stop Loss", f"${stop_loss}" if stop_loss else "Not set")
        with r7: st.metric("Risk Score",        f"{risk_data.get('risk_score', 0)}/100")
        with r8: st.metric("Demo Position Cap", f"${risk_data.get('max_demo_notional', 0)}")

        # ── Risk score bar ────────────────────────────────────────────────────
        try:
            rscore = max(0, min(100, int(risk_data.get("risk_score", 50))))
        except (TypeError, ValueError):
            rscore = 50
        risk_col = "#ef4444" if rscore > 70 else "#f59e0b" if rscore > 40 else "#10b981"
        st.markdown(
            f"""
            <div style="margin:1rem 0">
              <div style="font-family:'IBM Plex Mono',monospace;font-size:0.6rem;color:var(--ink-light);
                margin-bottom:6px;letter-spacing:0.1em;text-transform:uppercase">Composite Risk Score</div>
              <div style="background:var(--lav-pale);border-radius:999px;height:12px;overflow:hidden">
                <div style="height:100%;width:{rscore}%;background:{risk_col};border-radius:999px;
                  animation:barGrowX 1.2s cubic-bezier(.4,0,.2,1) forwards;
                  transform:scaleX(0);transform-origin:left"></div>
              </div>
              <div style="font-family:'IBM Plex Mono',monospace;font-size:0.6rem;color:{risk_col};margin-top:5px;text-align:right">
                {rscore}/100
              </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.markdown("#### Risk Rationale")
        st.info(risk_data.get("reason", "No risk rationale available."))

    with tab_execution:
        st.subheader("Order Execution")
        e1, e2, e3 = st.columns(3)
        with e1: st.metric("Routing Mode",  execution_data.get("execution_mode", "Paper"))
        with e2: st.metric("Order Status",  execution_data.get("order_status", "N/A"))
        with e3: st.metric("Filled Qty",    execution_data.get("quantity", "N/A"))

        if execution_result["status"] == "complete":
            st.success("✦ Paper order submitted successfully.")
            dc1, dc2 = st.columns(2)
            with dc1:
                st.write(f"**Order ID:** {execution_data.get('order_id')}")
                st.write(f"**Client Order ID:** {execution_data.get('client_order_id')}")
                st.write(f"**Ticker:** {execution_data.get('ticker')}")
                st.write(f"**Side:** {execution_data.get('side')}")
            with dc2:
                st.write(f"**Order Type:** {execution_data.get('order_type')}")
                st.write(f"**Time in Force:** {execution_data.get('time_in_force')}")
                st.write(f"**Submitted At:** {execution_data.get('submitted_at')}")
            if execution_data.get("order_status") in ["accepted", "new"]:
                st.info("Order accepted and queued — it will remain pending until the US equity session opens.")
        elif execution_result["status"] == "disabled":
            st.info(execution_data.get("reason", "Execution is currently in dry-run mode."))
        elif execution_result["status"] == "blocked":
            st.warning(execution_data.get("reason", "Order blocked by pre-trade risk controls."))
        else:
            st.error(execution_data.get("reason", "Execution failed — check the audit trail for details."))

    with tab_audit:
        st.subheader("Audit Trail")
        audit_log = workflow_result.get("audit", [])
        if audit_log:
            for event in audit_log:
                st.write(f"✦  {event}")
        else:
            st.info("No audit events recorded for this run.")

    with tab_history:
        st.subheader("Run History")
        history_rows = get_recent_workflow_runs(limit=20)
        if history_rows:
            history_df = pd.DataFrame(history_rows)
            display_df = history_df.rename(columns={
                "id": "Run ID", "created_at": "Timestamp", "query": "Instruction",
                "ticker": "Ticker", "side": "Side", "requested_quantity": "Requested Qty",
                "approved_quantity": "Approved Qty", "strategy_signal": "Signal",
                "confidence": "Conviction", "risk_approval": "Risk Decision",
                "risk_level": "Risk Level", "execution_status": "Execution Status",
                "order_id": "Order ID",
            })
            st.dataframe(display_df, use_container_width=True, hide_index=True)
            st.info(
                "Runs are stored locally in SQLite. Order IDs appear only when paper execution "
                "is enabled and Alpaca confirms the submission."
            )
        else:
            st.info("No run history yet — submit your first instruction above.")

    with tab_raw:
        st.subheader("Raw Pipeline Output")
        st.json(workflow_result)

else:
    st.markdown(
        """
        <div class="info-card">
            <b>Ready.</b> Enter a trade instruction above and press
            <em>✦ Run Trading Workflow</em> to launch the pipeline.
            Keep <b>Dry Run Only</b> selected while exploring ideas —
            switch to <b>Alpaca Paper Trading</b> only when you want a real paper order submitted.
        </div>
        """,
        unsafe_allow_html=True
    )
