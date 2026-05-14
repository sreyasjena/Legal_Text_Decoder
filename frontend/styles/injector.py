"""
frontend/styles/injector.py
────────────────────────────
Injects global CSS and the fixed legal SVG background
illustrations into the Streamlit page.
Called once from app.py on every page load.
"""

import streamlit as st
from frontend.styles.main_css import CSS


# ─────────────────────────────────────────────────────────
# LEGAL SVG ILLUSTRATIONS  (fixed behind all content)
# ─────────────────────────────────────────────────────────
SVG_BACKGROUNDS = """
<div class="legal-bg">

  <!-- Scale of Justice (left) -->
  <svg class="svg-justice" viewBox="0 0 200 220" fill="none" xmlns="http://www.w3.org/2000/svg">
    <line x1="100" y1="10" x2="100" y2="200" stroke="white" stroke-width="3"/>
    <line x1="40" y1="50" x2="160" y2="50" stroke="white" stroke-width="3"/>
    <line x1="40" y1="50" x2="20" y2="100" stroke="white" stroke-width="2"/>
    <line x1="40" y1="50" x2="60" y2="100" stroke="white" stroke-width="2"/>
    <line x1="160" y1="50" x2="140" y2="100" stroke="white" stroke-width="2"/>
    <line x1="160" y1="50" x2="180" y2="100" stroke="white" stroke-width="2"/>
    <ellipse cx="40" cy="105" rx="25" ry="8" stroke="white" stroke-width="2"/>
    <ellipse cx="160" cy="102" rx="25" ry="8" stroke="white" stroke-width="2"/>
    <circle cx="100" cy="10" r="5" stroke="white" stroke-width="2"/>
    <line x1="70" y1="200" x2="130" y2="200" stroke="white" stroke-width="4"/>
    <line x1="85" y1="180" x2="115" y2="180" stroke="white" stroke-width="3"/>
  </svg>

  <!-- Gavel (top right) -->
  <svg class="svg-gavel" viewBox="0 0 220 200" fill="none" xmlns="http://www.w3.org/2000/svg">
    <rect x="60" y="30" width="100" height="45" rx="8" stroke="white" stroke-width="3" transform="rotate(-35 110 52)"/>
    <rect x="68" y="34" width="84" height="18" rx="4" stroke="white" stroke-width="2" transform="rotate(-35 110 43)"/>
    <line x1="130" y1="95" x2="185" y2="165" stroke="white" stroke-width="8" stroke-linecap="round"/>
    <line x1="30" y1="175" x2="190" y2="175" stroke="white" stroke-width="4" stroke-linecap="round"/>
  </svg>

  <!-- Open Book (bottom centre) -->
  <svg class="svg-book" viewBox="0 0 400 180" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M200 20 Q120 10 40 30 L40 160 Q120 140 200 155" stroke="white" stroke-width="2.5" fill="none"/>
    <path d="M200 20 Q280 10 360 30 L360 160 Q280 140 200 155" stroke="white" stroke-width="2.5" fill="none"/>
    <line x1="200" y1="20" x2="200" y2="155" stroke="white" stroke-width="3"/>
    <line x1="60" y1="55"  x2="180" y2="48"  stroke="white" stroke-width="1.5" opacity="0.7"/>
    <line x1="60" y1="75"  x2="180" y2="68"  stroke="white" stroke-width="1.5" opacity="0.7"/>
    <line x1="60" y1="95"  x2="180" y2="88"  stroke="white" stroke-width="1.5" opacity="0.7"/>
    <line x1="60" y1="115" x2="180" y2="108" stroke="white" stroke-width="1.5" opacity="0.7"/>
    <line x1="60" y1="135" x2="180" y2="128" stroke="white" stroke-width="1.5" opacity="0.7"/>
    <line x1="220" y1="55"  x2="340" y2="48"  stroke="white" stroke-width="1.5" opacity="0.7"/>
    <line x1="220" y1="75"  x2="340" y2="68"  stroke="white" stroke-width="1.5" opacity="0.7"/>
    <line x1="220" y1="95"  x2="340" y2="88"  stroke="white" stroke-width="1.5" opacity="0.7"/>
    <line x1="220" y1="115" x2="340" y2="108" stroke="white" stroke-width="1.5" opacity="0.7"/>
    <line x1="220" y1="135" x2="340" y2="128" stroke="white" stroke-width="1.5" opacity="0.7"/>
  </svg>

  <!-- Greek Pillars (right) -->
  <svg class="svg-pillar" viewBox="0 0 160 400" fill="none" xmlns="http://www.w3.org/2000/svg">
    <rect x="20" y="20"  width="120" height="16" rx="3" stroke="white" stroke-width="2"/>
    <rect x="10" y="36"  width="140" height="10" rx="2" stroke="white" stroke-width="2"/>
    <rect x="25" y="46"  width="18"  height="290" rx="4" stroke="white" stroke-width="2"/>
    <rect x="71" y="46"  width="18"  height="290" rx="4" stroke="white" stroke-width="2"/>
    <rect x="117" y="46" width="18"  height="290" rx="4" stroke="white" stroke-width="2"/>
    <rect x="8"   y="336" width="144" height="10" rx="2" stroke="white" stroke-width="2"/>
    <rect x="14"  y="346" width="132" height="18" rx="3" stroke="white" stroke-width="2"/>
    <rect x="5"   y="364" width="150" height="14" rx="3" stroke="white" stroke-width="2"/>
  </svg>

  <!-- Scroll / Parchment (left mid) -->
  <svg class="svg-scroll" viewBox="0 0 200 280" fill="none" xmlns="http://www.w3.org/2000/svg">
    <rect x="30" y="30" width="140" height="220" rx="12" stroke="white" stroke-width="2.5"/>
    <ellipse cx="100" cy="30"  rx="40" ry="14" stroke="white" stroke-width="2"/>
    <ellipse cx="100" cy="250" rx="40" ry="14" stroke="white" stroke-width="2"/>
    <line x1="55" y1="70"  x2="145" y2="70"  stroke="white" stroke-width="1.5" opacity="0.7"/>
    <line x1="55" y1="90"  x2="145" y2="90"  stroke="white" stroke-width="1.5" opacity="0.7"/>
    <line x1="55" y1="110" x2="145" y2="110" stroke="white" stroke-width="1.5" opacity="0.7"/>
    <line x1="55" y1="130" x2="120" y2="130" stroke="white" stroke-width="1.5" opacity="0.7"/>
    <line x1="55" y1="150" x2="145" y2="150" stroke="white" stroke-width="1.5" opacity="0.7"/>
    <line x1="55" y1="170" x2="130" y2="170" stroke="white" stroke-width="1.5" opacity="0.7"/>
    <line x1="55" y1="190" x2="145" y2="190" stroke="white" stroke-width="1.5" opacity="0.7"/>
    <line x1="55" y1="210" x2="100" y2="210" stroke="white" stroke-width="1.5" opacity="0.7"/>
  </svg>

  <!-- Quill pen (bottom right) -->
  <svg class="svg-quill" viewBox="0 0 180 260" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M140 20 Q160 40 150 80 Q140 120 100 160 L60 240" stroke="white" stroke-width="2.5" fill="none" stroke-linecap="round"/>
    <path d="M140 20 Q120 30 110 60 Q100 90 100 160" stroke="white" stroke-width="1.5" fill="none" opacity="0.6" stroke-linecap="round"/>
    <line x1="60" y1="240" x2="80" y2="240" stroke="white" stroke-width="3" stroke-linecap="round"/>
  </svg>

  <!-- Blindfolded Justice (top centre, very faint) -->
  <svg class="svg-blindfold" viewBox="0 0 300 200" fill="none" xmlns="http://www.w3.org/2000/svg">
    <circle cx="150" cy="60" r="40" stroke="white" stroke-width="2"/>
    <line x1="110" y1="55" x2="190" y2="55" stroke="white" stroke-width="3" stroke-linecap="round"/>
    <path d="M150 100 L150 180" stroke="white" stroke-width="2"/>
    <path d="M80 130 L220 130" stroke="white" stroke-width="2"/>
  </svg>

</div>

<!-- Floating colour orbs -->
<div class="orb-wrap">
  <div class="orb orb-1"></div>
  <div class="orb orb-2"></div>
  <div class="orb orb-3"></div>
  <div class="orb orb-4"></div>
  <div class="orb orb-5"></div>
  <div class="orb orb-6"></div>
</div>
"""


def inject_styles():
    """Inject global CSS and fixed SVG backgrounds. Call once from app.py."""
    st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)
    st.markdown(SVG_BACKGROUNDS, unsafe_allow_html=True)
