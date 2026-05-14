"""
frontend/styles/main.css  (embedded as a Python string)
All global CSS for LexAI — imported by styles/injector.py
"""

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;500;600;700&family=Sora:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

#MainMenu,footer,header{visibility:hidden;}
[data-testid="stToolbar"]{display:none!important;}
.stDeployButton{display:none!important;}

:root{
    --bg:#02060e; --panel:#070f1e; --panel2:#0b1628;
    --border:rgba(56,165,255,0.18); --border2:rgba(56,165,255,0.08);
    --blue:#38a5ff; --blue-b:#1a7fd4;
    --cyan:#00d4ff; --teal:#0ff4c6;
    --orange:#ff8c42; --orange-b:#d4621a; --yellow:#ffd166;
    --purple:#7c5cfc; --pink:#f472b6;
    --text:#d8ecff; --text2:#6fa0cc; --muted:#3a5570;
    --success:#00e5a0; --warn:#ffb547; --danger:#ff5c6a;
}
html,body,[class*="css"]{font-family:'Sora',sans-serif;color:var(--text);background:var(--bg);font-size:17px;}
.stApp{background:var(--bg);overflow-x:hidden;}

/* ANIMATED GRID */
.stApp::before{content:'';position:fixed;inset:0;
    background-image:linear-gradient(rgba(56,165,255,0.04) 1px,transparent 1px),
    linear-gradient(90deg,rgba(56,165,255,0.04) 1px,transparent 1px);
    background-size:72px 72px;pointer-events:none;z-index:0;
    animation:gridDrift 22s linear infinite;}
@keyframes gridDrift{from{background-position:0 0}to{background-position:72px 72px}}
.stApp::after{content:'';position:fixed;inset:0;
    background:radial-gradient(ellipse 85% 55% at 50% 0%,transparent 0%,rgba(2,6,14,0.92) 100%);
    pointer-events:none;z-index:0;}

/* ORBS */
.orb-wrap{position:fixed;inset:0;pointer-events:none;z-index:0;overflow:hidden;}
.orb{position:absolute;border-radius:50%;filter:blur(120px);animation:orbDrift linear infinite;}
.orb-1{width:800px;height:800px;background:radial-gradient(circle,#083580,transparent 65%);top:-18%;left:-12%;opacity:0.22;animation-duration:34s;}
.orb-2{width:600px;height:600px;background:radial-gradient(circle,#007ab5,transparent 65%);top:22%;right:-10%;opacity:0.16;animation-duration:27s;animation-delay:-11s;}
.orb-3{width:500px;height:500px;background:radial-gradient(circle,#6a3fd4,transparent 65%);bottom:-8%;left:24%;opacity:0.14;animation-duration:40s;animation-delay:-22s;}
.orb-4{width:380px;height:380px;background:radial-gradient(circle,#b05010,transparent 65%);top:52%;left:54%;opacity:0.1;animation-duration:24s;animation-delay:-8s;}
.orb-5{width:260px;height:260px;background:radial-gradient(circle,#00d4ff,transparent 65%);bottom:22%;right:28%;opacity:0.08;animation-duration:18s;animation-delay:-4s;}
.orb-6{width:200px;height:200px;background:radial-gradient(circle,#f472b6,transparent 65%);top:35%;left:8%;opacity:0.07;animation-duration:28s;animation-delay:-14s;}
@keyframes orbDrift{0%{transform:translate(0,0) scale(1);}33%{transform:translate(45px,-60px) scale(1.08);}66%{transform:translate(-40px,40px) scale(0.92);}100%{transform:translate(0,0) scale(1);}}

/* LEGAL SVG BG */
.legal-bg{position:fixed;inset:0;pointer-events:none;z-index:0;overflow:hidden;}
.legal-bg svg{position:absolute;opacity:0.045;}
.svg-justice{left:-50px;bottom:6%;width:400px;height:400px;animation:svgFloat 12s ease-in-out infinite;}
.svg-gavel  {right:-30px;top:10%;width:360px;height:360px;animation:svgFloat 15s ease-in-out infinite reverse;}
.svg-book   {left:50%;bottom:-30px;transform:translateX(-50%);width:480px;height:240px;animation:svgFloatH 10s ease-in-out infinite;animation-delay:-5s;}
.svg-pillar {right:6%;top:32%;width:150px;height:380px;animation:svgFloat 18s ease-in-out infinite;animation-delay:-9s;}
.svg-scroll {left:4%;top:20%;width:200px;height:280px;animation:svgFloat 20s ease-in-out infinite;animation-delay:-6s;}
.svg-quill  {right:3%;bottom:18%;width:180px;height:260px;animation:svgFloat 14s ease-in-out infinite reverse;animation-delay:-3s;}
.svg-blindfold{left:50%;top:5%;transform:translateX(-50%);width:300px;height:200px;animation:svgFloatH 16s ease-in-out infinite;animation-delay:-8s;opacity:0.03;}
@keyframes svgFloat{0%,100%{transform:translateY(0);}50%{transform:translateY(-20px);}}
@keyframes svgFloatH{0%,100%{transform:translateX(-50%) translateY(0);}50%{transform:translateX(-50%) translateY(-16px);}}

/* BLOCK CONTAINER */
.block-container{max-width:1320px!important;padding:0 2.5rem 4rem!important;position:relative;z-index:1;}

/* LOGGED-IN BANNER */
.logged-in-banner{display:flex;align-items:center;justify-content:space-between;
    background:linear-gradient(135deg,rgba(0,229,160,0.08),rgba(56,165,255,0.06));
    border:1px solid rgba(0,229,160,0.25);border-radius:16px;padding:18px 28px;
    margin-bottom:30px;animation:fadeDown 0.6s ease both;position:relative;overflow:hidden;z-index:1;}
.logged-in-banner::before{content:'';position:absolute;top:0;left:0;right:0;height:2px;
    background:linear-gradient(90deg,var(--success),var(--cyan),var(--success));
    background-size:200%;animation:bannerShine 3s ease infinite;}
@keyframes bannerShine{0%,100%{background-position:0%;}50%{background-position:100%;}}
.banner-left{display:flex;align-items:center;gap:16px;}
.banner-avatar{width:46px;height:46px;border-radius:12px;
    background:linear-gradient(135deg,rgba(0,229,160,0.2),rgba(56,165,255,0.2));
    border:1px solid rgba(0,229,160,0.3);
    display:flex;align-items:center;justify-content:center;font-size:22px;}
.banner-status{font-family:'JetBrains Mono',monospace;font-size:10px;letter-spacing:2.5px;
    text-transform:uppercase;color:var(--success);margin-bottom:3px;display:flex;align-items:center;gap:8px;}
.banner-pulse{width:7px;height:7px;background:var(--success);border-radius:50%;
    animation:pulse 2s ease infinite;display:inline-block;}
.banner-email{font-size:16px;font-weight:500;color:var(--text);}
.banner-right{display:flex;align-items:center;gap:12px;}

/* EYEBROW */
.land-eyebrow{display:inline-flex;align-items:center;gap:10px;
    background:linear-gradient(90deg,rgba(255,140,66,0.14),rgba(56,165,255,0.14));
    border:1px solid rgba(255,140,66,0.35);border-radius:100px;padding:10px 30px;
    font-family:'JetBrains Mono',monospace;font-size:13px;letter-spacing:3px;
    color:var(--orange);text-transform:uppercase;margin-bottom:36px;
    animation:fadeDown 0.8s ease both;position:relative;overflow:hidden;}
.land-eyebrow::before{content:'';position:absolute;inset:0;
    background:linear-gradient(90deg,transparent,rgba(255,140,66,0.22),transparent);
    transform:translateX(-200%);animation:sweep 2.8s ease infinite;}
@keyframes sweep{to{transform:translateX(300%);}}

/* MEGA TITLE */
.lexai-wrap{text-align:center;position:relative;margin-bottom:6px;line-height:1;}
.lexai-wrap::before{content:'';position:absolute;top:50%;left:50%;
    transform:translate(-50%,-50%);width:min(900px,90vw);height:220px;
    background:radial-gradient(ellipse,rgba(56,165,255,0.2) 0%,rgba(255,140,66,0.14) 40%,transparent 70%);
    filter:blur(40px);animation:haloBreath 5s ease-in-out infinite;z-index:0;pointer-events:none;}
@keyframes haloBreath{0%,100%{opacity:0.7;transform:translate(-50%,-50%) scale(1);}50%{opacity:1;transform:translate(-50%,-50%) scale(1.14);}}
.lexai-title{font-family:'Rajdhani',sans-serif;font-size:clamp(130px,20vw,240px);
    font-weight:700;line-height:0.82;letter-spacing:-6px;display:inline-block;position:relative;z-index:1;
    background:linear-gradient(140deg,#ffffff 0%,#60b8ff 15%,#00d4ff 30%,#ff8c42 50%,#ffd166 65%,#ffffff 80%,#38a5ff 100%);
    background-size:400%;-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
    animation:fadeUp 0.9s 0.1s ease both,megaColorShift 8s ease infinite;
    filter:drop-shadow(0 0 100px rgba(56,165,255,0.6)) drop-shadow(0 0 40px rgba(255,140,66,0.4));}
@keyframes megaColorShift{0%,100%{background-position:0%;}50%{background-position:100%;}}
.lexai-ghost{font-family:'Rajdhani',sans-serif;font-size:clamp(130px,20vw,240px);
    font-weight:700;line-height:0.82;letter-spacing:-6px;
    position:absolute;top:0;left:50%;transform:translateX(-50%);
    -webkit-text-stroke:1px rgba(255,140,66,0.15);color:transparent;
    animation:fadeUp 0.9s 0.1s ease both;pointer-events:none;z-index:0;white-space:nowrap;}
.land-title-sub{font-family:'Rajdhani',sans-serif;font-size:clamp(22px,3.5vw,42px);
    font-weight:500;text-align:center;color:var(--text2);letter-spacing:10px;
    text-transform:uppercase;animation:fadeUp 0.8s 0.3s ease both;margin-bottom:28px;}
.scan-line{height:2px;max-width:500px;
    background:linear-gradient(90deg,transparent,var(--orange),var(--cyan),var(--orange),transparent);
    margin:0 auto 30px;box-shadow:0 0 18px var(--orange),0 0 40px rgba(0,212,255,0.3);
    animation:scanExpand 1.4s 0.5s ease both;}
@keyframes scanExpand{from{max-width:0;opacity:0;}to{max-width:500px;opacity:1;}}
.land-desc{text-align:center;color:var(--text2);font-size:18px;font-weight:300;
    line-height:2;max-width:680px;margin:0 auto 48px;animation:fadeUp 0.8s 0.4s ease both;}

/* STATS */
.land-stats{display:flex;gap:60px;justify-content:center;margin-bottom:52px;animation:fadeUp 0.8s 0.5s ease both;}
.stat-box{text-align:center;position:relative;}
.stat-box::after{content:'';position:absolute;right:-30px;top:15%;height:70%;width:1px;background:rgba(255,140,66,0.15);}
.stat-box:last-child::after{display:none;}
.stat-val{font-family:'Rajdhani',sans-serif;font-size:58px;font-weight:700;color:var(--orange);
    line-height:1;display:block;text-shadow:0 0 32px rgba(255,140,66,0.5);}
.stat-lbl{font-family:'JetBrains Mono',monospace;font-size:12px;letter-spacing:2.5px;
    color:var(--muted);text-transform:uppercase;margin-top:5px;display:block;}

/* FEATURE CARDS */
.feat-card{background:linear-gradient(145deg,rgba(255,140,66,0.05),rgba(7,15,30,0.9));
    border:1px solid rgba(255,140,66,0.12);border-radius:22px;padding:32px 22px;text-align:center;
    position:relative;overflow:hidden;transition:all 0.48s cubic-bezier(0.23,1,0.32,1);
    cursor:default;animation:fadeUp 0.8s 0.65s ease both;min-height:270px;}
.feat-card::before{content:'';position:absolute;top:0;left:0;right:0;height:2px;
    background:linear-gradient(90deg,transparent,var(--orange),var(--cyan),transparent);opacity:0;transition:opacity 0.4s;}
.feat-card::after{content:'';position:absolute;inset:0;
    background:radial-gradient(circle at 50% 100%,rgba(255,140,66,0.07),transparent 70%);opacity:0;transition:opacity 0.4s;}
.feat-card:hover{transform:translateY(-14px);border-color:rgba(255,140,66,0.45);
    box-shadow:0 32px 80px rgba(0,0,0,0.6),0 0 60px rgba(255,140,66,0.12);}
.feat-card:hover::before,.feat-card:hover::after{opacity:1;}
.hex-corner{position:absolute;top:14px;right:14px;width:24px;height:24px;
    border-top:2px solid rgba(255,140,66,0.3);border-right:2px solid rgba(255,140,66,0.3);border-radius:0 6px 0 0;}
.hex-corner-bl{position:absolute;bottom:14px;left:14px;width:24px;height:24px;
    border-bottom:2px solid rgba(56,165,255,0.2);border-left:2px solid rgba(56,165,255,0.2);border-radius:0 0 0 6px;}
.feat-icon{font-size:46px;margin-bottom:16px;display:block;
    filter:drop-shadow(0 0 16px rgba(255,140,66,0.55));animation:iconFloat 4s ease-in-out infinite;}
.feat-card:nth-child(2) .feat-icon{animation-delay:-1.2s;}
.feat-card:nth-child(3) .feat-icon{animation-delay:-2.1s;}
.feat-card:nth-child(4) .feat-icon{animation-delay:-3s;}
@keyframes iconFloat{0%,100%{transform:translateY(0);}50%{transform:translateY(-7px);}}
.feat-title{font-family:'Rajdhani',sans-serif;font-size:22px;font-weight:700;color:var(--orange);margin-bottom:10px;}
.feat-text{font-size:14px;color:var(--text2);line-height:1.9;}

/* TICKER */
.ticker-wrap{overflow:hidden;
    background:linear-gradient(90deg,rgba(255,140,66,0.07),rgba(56,165,255,0.07),rgba(255,140,66,0.07));
    border-top:1px solid rgba(255,140,66,0.18);border-bottom:1px solid rgba(56,165,255,0.18);
    padding:11px 0;margin:0 0 28px;position:relative;z-index:1;}
.ticker-inner{display:flex;width:max-content;animation:tickerScroll 28s linear infinite;gap:70px;align-items:center;}
@keyframes tickerScroll{from{transform:translateX(0)}to{transform:translateX(-50%)}}
.ticker-item{font-family:'JetBrains Mono',monospace;font-size:13px;letter-spacing:2px;
    text-transform:uppercase;white-space:nowrap;display:flex;align-items:center;gap:12px;}
.ticker-dot{width:7px;height:7px;border-radius:50%;display:inline-block;}
.t-blue{color:#38a5ff;}.t-orange{color:#ff8c42;}.t-teal{color:#0ff4c6;}.t-yellow{color:#ffd166;}

/* AUTH PAGE */
.auth-brand-panel{padding:40px 30px;display:flex;flex-direction:column;justify-content:center;animation:fadeUp 0.7s ease both;}
.auth-brand-logo{font-family:'Rajdhani',sans-serif;font-size:clamp(70px,12vw,110px);
    font-weight:700;letter-spacing:-4px;line-height:0.85;
    background:linear-gradient(140deg,#ffffff 0%,#60b8ff 20%,#ff8c42 55%,#ffd166 80%,#38a5ff 100%);
    background-size:300%;-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
    animation:megaColorShift 7s ease infinite;
    filter:drop-shadow(0 0 60px rgba(56,165,255,0.5));margin-bottom:14px;display:block;}
.auth-brand-tagline{font-family:'JetBrains Mono',monospace;font-size:12px;letter-spacing:4px;
    text-transform:uppercase;color:var(--muted);margin-bottom:36px;}
.auth-brand-desc{font-size:16px;color:var(--text2);line-height:1.9;margin-bottom:36px;}
.auth-feat-list{display:flex;flex-direction:column;gap:12px;}
.auth-feat-item{display:flex;align-items:center;gap:14px;
    background:rgba(56,165,255,0.05);border:1px solid rgba(56,165,255,0.1);
    border-radius:14px;padding:14px 18px;transition:all 0.3s;}
.auth-feat-item:hover{background:rgba(255,140,66,0.06);border-color:rgba(255,140,66,0.2);}
.auth-feat-icon{font-size:26px;flex-shrink:0;}
.auth-feat-text{font-size:14px;color:var(--text2);line-height:1.5;}
.auth-feat-text strong{color:var(--orange);font-weight:600;}
.auth-divider-vert{width:1px;
    background:linear-gradient(180deg,transparent,rgba(56,165,255,0.2) 30%,rgba(255,140,66,0.2) 70%,transparent);
    margin:0 20px;flex-shrink:0;align-self:stretch;}
.auth-form-card{width:100%;
    background:linear-gradient(145deg,rgba(10,20,50,0.97),rgba(5,12,28,0.99));
    border:1px solid rgba(56,165,255,0.2);border-radius:28px;
    padding:44px 40px;position:relative;overflow:hidden;
    box-shadow:0 40px 100px rgba(0,0,0,0.6),0 0 0 1px rgba(255,140,66,0.06);
    animation:panelIn 0.6s ease both;}
.auth-form-card::before{content:'';position:absolute;top:0;left:0;right:0;height:3px;
    background:linear-gradient(90deg,var(--orange-b),var(--orange),var(--cyan),var(--blue-b),var(--orange-b));
    background-size:400%;animation:gradSlide 4s ease infinite;}
@keyframes gradSlide{0%,100%{background-position:0%;}50%{background-position:100%;}}
.fc-tl{position:absolute;top:16px;left:16px;width:28px;height:28px;
    border-top:2px solid rgba(255,140,66,0.4);border-left:2px solid rgba(255,140,66,0.4);border-radius:6px 0 0 0;}
.fc-br{position:absolute;bottom:16px;right:16px;width:28px;height:28px;
    border-bottom:2px solid rgba(56,165,255,0.4);border-right:2px solid rgba(56,165,255,0.4);border-radius:0 0 6px 0;}
.auth-form-title{font-family:'Rajdhani',sans-serif;font-size:32px;font-weight:700;color:var(--text);margin-bottom:6px;}
.auth-form-subtitle{font-size:14px;color:var(--muted);margin-bottom:28px;line-height:1.6;}
.method-row{display:flex;gap:10px;margin-bottom:20px;}
.method-chip{flex:1;text-align:center;padding:11px 0;border-radius:12px;
    font-family:'JetBrains Mono',monospace;font-size:11px;letter-spacing:2px;text-transform:uppercase;
    border:1px solid rgba(56,165,255,0.1);color:var(--muted);transition:all 0.3s;cursor:default;}
.method-chip.active{background:rgba(56,165,255,0.1);border-color:rgba(56,165,255,0.4);color:var(--blue);}
.form-label{font-family:'JetBrains Mono',monospace;font-size:11px;letter-spacing:2.5px;
    text-transform:uppercase;color:var(--orange);margin-bottom:6px;display:block;}
.instr-box{background:rgba(56,165,255,0.06);border:1px solid rgba(56,165,255,0.2);
    border-radius:14px;padding:18px 20px;margin:14px 0;font-size:14px;color:var(--text2);line-height:1.9;}
.instr-box ol{margin:10px 0 0 18px;padding:0;}
.instr-box ol li{margin-bottom:6px;}
.success-box{background:rgba(0,229,160,0.07);border:1px solid rgba(0,229,160,0.25);
    border-radius:14px;padding:16px 20px;margin-top:14px;font-size:15px;color:var(--success);line-height:1.7;}
.info-box{background:rgba(56,165,255,0.06);border:1px solid rgba(56,165,255,0.18);
    border-radius:14px;padding:14px 18px;margin-top:10px;font-size:14px;color:var(--text2);line-height:1.7;}
.trust-row{display:flex;gap:12px;margin-top:26px;flex-wrap:wrap;justify-content:center;}
.trust-badge{display:flex;align-items:center;gap:6px;
    background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.06);
    border-radius:100px;padding:6px 14px;
    font-family:'JetBrains Mono',monospace;font-size:10px;letter-spacing:1.5px;
    color:var(--muted);text-transform:uppercase;}

/* TOPBAR */
.topbar{display:flex;align-items:center;justify-content:space-between;
    padding:18px 0;border-bottom:1px solid rgba(255,140,66,0.12);margin-bottom:8px;animation:fadeDown 0.5s ease both;}
.topbar-icon{width:46px;height:46px;background:linear-gradient(135deg,#1052a8,var(--orange-b));
    border-radius:12px;display:flex;align-items:center;justify-content:center;
    font-size:24px;box-shadow:0 0 28px rgba(255,140,66,0.28);}
.topbar-brand-small{font-family:'JetBrains Mono',monospace;font-size:11px;letter-spacing:3px;color:var(--orange);text-transform:uppercase;margin-bottom:2px;}
.topbar-brand-name{font-family:'Rajdhani',sans-serif;font-size:21px;font-weight:700;color:var(--text);}
.main-lexai-mark{position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);
    font-family:'Rajdhani',sans-serif;font-size:clamp(200px,28vw,340px);
    font-weight:700;letter-spacing:-10px;color:transparent;
    -webkit-text-stroke:1px rgba(56,165,255,0.045);pointer-events:none;z-index:0;
    animation:markBreath 10s ease-in-out infinite;white-space:nowrap;user-select:none;}
@keyframes markBreath{0%,100%{opacity:0.5;}50%{opacity:1;}}
.status-pill{display:flex;align-items:center;gap:8px;background:rgba(0,229,160,0.07);
    border:1px solid rgba(0,229,160,0.25);border-radius:100px;padding:8px 20px;
    font-family:'JetBrains Mono',monospace;font-size:12px;letter-spacing:2px;color:var(--success);text-transform:uppercase;}
.pulse-dot{width:9px;height:9px;background:var(--success);border-radius:50%;animation:pulse 2s ease infinite;}
@keyframes pulse{0%,100%{box-shadow:0 0 0 0 rgba(0,229,160,0.55);}50%{box-shadow:0 0 0 10px rgba(0,229,160,0);}}
.hex-badge{display:inline-flex;align-items:center;gap:7px;background:rgba(255,140,66,0.1);
    border:1px solid rgba(255,140,66,0.3);border-radius:8px;padding:6px 16px;
    font-family:'JetBrains Mono',monospace;font-size:11px;letter-spacing:2px;color:var(--orange);text-transform:uppercase;}
.user-badge{display:flex;align-items:center;gap:8px;background:rgba(56,165,255,0.08);
    border:1px solid rgba(56,165,255,0.2);border-radius:100px;padding:6px 16px;
    font-family:'JetBrains Mono',monospace;font-size:11px;color:var(--blue);}

/* SEC LABELS */
.sec-label{font-family:'JetBrains Mono',monospace;font-size:12px;letter-spacing:3px;
    color:var(--orange);text-transform:uppercase;margin-bottom:10px;display:flex;align-items:center;gap:10px;}
.sec-label::before{content:'';display:inline-block;width:20px;height:2px;background:var(--orange);box-shadow:0 0 8px var(--orange);}

/* PANELS */
.panel{background:linear-gradient(145deg,rgba(255,140,66,0.03),rgba(5,12,24,0.94));
    border:1px solid rgba(255,140,66,0.1);border-radius:20px;padding:28px;margin-bottom:18px;
    position:relative;overflow:hidden;transition:border-color 0.3s;animation:panelIn 0.5s ease both;}
.panel::after{content:'';position:absolute;top:0;left:0;right:0;height:1px;
    background:linear-gradient(90deg,transparent,rgba(255,140,66,0.45),transparent);opacity:0.6;}
.panel:hover{border-color:rgba(255,140,66,0.25);}
@keyframes panelIn{from{opacity:0;transform:translateY(22px);}to{opacity:1;transform:translateY(0);}}
.panel-title{font-family:'Rajdhani',sans-serif;font-size:22px;font-weight:700;color:var(--orange);margin-bottom:16px;display:flex;align-items:center;gap:12px;}
.corner-tl{position:absolute;top:14px;left:14px;width:24px;height:24px;
    border-top:2px solid rgba(255,140,66,0.3);border-left:2px solid rgba(255,140,66,0.3);border-radius:4px 0 0 0;}
.corner-br{position:absolute;bottom:14px;right:14px;width:24px;height:24px;
    border-bottom:2px solid rgba(56,165,255,0.3);border-right:2px solid rgba(56,165,255,0.3);border-radius:0 0 4px 0;}

/* PIPELINE */
.pipeline-outer{background:linear-gradient(145deg,rgba(6,16,44,0.97),rgba(4,10,22,0.99));
    border:1px solid rgba(56,165,255,0.22);border-radius:22px;padding:34px;margin:26px 0;
    position:relative;overflow:hidden;}
.pipeline-outer::before{content:'';position:absolute;top:0;left:0;right:0;height:3px;
    background:linear-gradient(90deg,var(--orange-b),var(--orange),var(--cyan),var(--blue-b),var(--orange-b));
    background-size:400%;animation:gradSlide 4s ease infinite;}
.pipe-header-label{font-family:'JetBrains Mono',monospace;font-size:12px;letter-spacing:3px;color:var(--orange);text-transform:uppercase;margin-bottom:8px;}
.pipe-header-title{font-family:'Rajdhani',sans-serif;font-size:32px;font-weight:700;color:var(--text);margin-bottom:34px;}
.pstage{display:flex;flex-direction:column;align-items:center;text-align:center;position:relative;z-index:1;}
.pstage-icon{width:88px;height:88px;border-radius:20px;display:flex;align-items:center;
    justify-content:center;font-size:38px;margin-bottom:16px;
    border:2px solid rgba(56,165,255,0.1);background:rgba(6,16,40,0.9);transition:all 0.4s;}
.pstage.done   .pstage-icon{border-color:var(--success);background:rgba(0,229,160,0.08);box-shadow:0 0 28px rgba(0,229,160,0.28);}
.pstage.active .pstage-icon{border-color:var(--orange);background:rgba(255,140,66,0.1);
    box-shadow:0 0 36px rgba(255,140,66,0.45);animation:activePulse 1.4s ease infinite;}
.pstage.queued .pstage-icon{opacity:0.35;}
@keyframes activePulse{0%,100%{box-shadow:0 0 36px rgba(255,140,66,0.45);}50%{box-shadow:0 0 60px rgba(255,140,66,0.7);}}
.pstage-name{font-family:'JetBrains Mono',monospace;font-size:13px;letter-spacing:2.5px;text-transform:uppercase;margin-bottom:8px;font-weight:500;}
.pstage.done   .pstage-name{color:var(--success);}
.pstage.active .pstage-name{color:var(--orange);}
.pstage.queued .pstage-name{color:var(--muted);}
.pstage-desc{font-size:13px;color:var(--text2);line-height:1.75;max-width:120px;}
.pstage.queued .pstage-desc{opacity:0.4;}
.pstage-badge{margin-top:10px;padding:5px 15px;border-radius:100px;
    font-family:'JetBrains Mono',monospace;font-size:11px;letter-spacing:1.5px;text-transform:uppercase;}
.bd-done  {background:rgba(0,229,160,0.1);border:1px solid rgba(0,229,160,0.38);color:var(--success);}
.bd-active{background:rgba(255,140,66,0.12);border:1px solid rgba(255,140,66,0.48);color:var(--orange);animation:badgeBlink 1.4s ease infinite;}
@keyframes badgeBlink{0%,100%{opacity:1;}50%{opacity:0.45;}}
.bd-queued{background:rgba(8,18,40,0.7);border:1px solid rgba(56,165,255,0.1);color:var(--muted);}
.prog-wrap{margin-top:32px;background:rgba(56,165,255,0.08);border-radius:100px;height:6px;overflow:hidden;}
.prog-fill{height:100%;border-radius:100px;background:linear-gradient(90deg,var(--orange-b),var(--orange),var(--cyan));
    box-shadow:0 0 16px var(--orange);transition:width 0.9s cubic-bezier(0.23,1,0.32,1);}
.live-log{margin-top:22px;background:rgba(0,0,0,0.4);border:1px solid rgba(255,140,66,0.15);
    border-radius:12px;padding:16px 22px;font-family:'JetBrains Mono',monospace;font-size:14px;color:var(--orange);}
.live-log::before{content:'> ';color:var(--cyan);}
.blink-cursor{display:inline-block;width:10px;height:16px;background:var(--orange);
    margin-left:3px;animation:blink 1s step-end infinite;vertical-align:middle;}
@keyframes blink{0%,100%{opacity:1;}50%{opacity:0;}}

/* RESULT */
.result-panel{background:linear-gradient(145deg,rgba(255,140,66,0.05),rgba(4,10,22,0.96));
    border:1px solid rgba(255,140,66,0.3);border-radius:22px;padding:42px;margin-top:30px;
    position:relative;overflow:hidden;animation:resultReveal 0.9s cubic-bezier(0.23,1,0.32,1) both;}
.result-panel::before{content:'';position:absolute;top:0;left:0;right:0;height:3px;
    background:linear-gradient(90deg,var(--orange-b),var(--orange),var(--cyan),var(--blue-b),var(--orange-b));
    background-size:300%;animation:gradSlide 4s ease infinite;}
@keyframes resultReveal{from{opacity:0;transform:translateY(30px) scale(0.97);}to{opacity:1;transform:translateY(0) scale(1);}}
.result-heading{font-family:'Rajdhani',sans-serif;font-size:34px;font-weight:700;
    color:var(--orange);letter-spacing:0.5px;margin-bottom:26px;display:flex;align-items:center;gap:14px;}
.result-body{font-size:18px;line-height:2.1;color:var(--text);white-space:pre-wrap;}
.meta-chips{display:flex;flex-wrap:wrap;gap:12px;margin-top:26px;}
.meta-chip{padding:7px 18px;border-radius:100px;font-family:'JetBrains Mono',monospace;font-size:12px;letter-spacing:1.5px;text-transform:uppercase;}
.chip-orange{background:rgba(255,140,66,0.1);border:1px solid rgba(255,140,66,0.32);color:var(--orange);}
.chip-teal  {background:rgba(15,244,198,0.07);border:1px solid rgba(15,244,198,0.28);color:var(--teal);}
.chip-blue  {background:rgba(56,165,255,0.08);border:1px solid rgba(56,165,255,0.28);color:var(--blue);}
.chip-yellow{background:rgba(255,209,102,0.08);border:1px solid rgba(255,209,102,0.28);color:var(--yellow);}

/* INPUTS */
.stTextArea textarea{background:rgba(4,10,22,0.92)!important;color:var(--text)!important;
    border:1px solid rgba(255,140,66,0.15)!important;border-radius:14px!important;
    padding:20px!important;font-family:'Sora',sans-serif!important;font-size:17px!important;line-height:1.9!important;}
.stTextArea textarea:focus{border-color:rgba(255,140,66,0.5)!important;box-shadow:0 0 0 3px rgba(255,140,66,0.08)!important;}
.stTextInput input{background:rgba(4,10,22,0.92)!important;color:var(--text)!important;
    border:1px solid rgba(56,165,255,0.18)!important;border-radius:12px!important;
    padding:14px 18px!important;font-family:'Sora',sans-serif!important;font-size:16px!important;}
.stTextInput input:focus{border-color:rgba(56,165,255,0.48)!important;box-shadow:0 0 0 3px rgba(56,165,255,0.07)!important;}
.stTextArea label,.stFileUploader label,.stSelectbox label,.stTextInput label{
    font-family:'JetBrains Mono',monospace!important;font-size:11px!important;
    letter-spacing:2px!important;color:var(--orange)!important;text-transform:uppercase!important;}
.stFileUploader{background:rgba(4,10,22,0.75)!important;border:1.5px dashed rgba(255,140,66,0.2)!important;border-radius:14px!important;}
.stSelectbox>div>div{background:rgba(4,10,22,0.92)!important;border:1px solid rgba(255,140,66,0.15)!important;border-radius:12px!important;color:var(--text)!important;font-size:16px!important;}
section[data-testid="stSidebar"]{background:rgba(2,6,14,0.98)!important;border-right:1px solid rgba(255,140,66,0.1)!important;}
section[data-testid="stSidebar"] *{color:var(--text)!important;}

/* BUTTONS */
.stButton>button{font-family:'Rajdhani',sans-serif!important;font-size:18px!important;
    font-weight:700!important;letter-spacing:2px!important;text-transform:uppercase!important;
    border-radius:14px!important;border:none!important;width:100%!important;
    transition:all 0.35s cubic-bezier(0.23,1,0.32,1)!important;}
.stButton>button:hover{transform:translateY(-3px)!important;}
.stButton>button:active{transform:translateY(0) scale(0.97)!important;}
.cta-main .stButton>button{height:70px!important;font-size:22px!important;
    background:linear-gradient(135deg,#a84200,var(--orange),#ffd166)!important;
    background-size:200%!important;color:#06090e!important;animation:ctaGlow 3s ease infinite!important;}
@keyframes ctaGlow{0%,100%{background-position:0%;box-shadow:0 0 55px rgba(255,140,66,0.42),0 8px 36px rgba(0,0,0,0.5);}
    50%{background-position:100%;box-shadow:0 0 90px rgba(255,209,102,0.55),0 14px 48px rgba(0,0,0,0.55);}}
.cta-workspace .stButton>button{height:70px!important;font-size:22px!important;
    background:linear-gradient(135deg,#006b40,var(--success),#00d4a0)!important;
    background-size:200%!important;color:#02060e!important;animation:wsGlow 3s ease infinite!important;}
@keyframes wsGlow{0%,100%{background-position:0%;box-shadow:0 0 55px rgba(0,229,160,0.42),0 8px 36px rgba(0,0,0,0.5);}
    50%{background-position:100%;box-shadow:0 0 90px rgba(0,229,160,0.6),0 14px 48px rgba(0,0,0,0.55);}}
.btn-login .stButton>button{height:58px!important;background:linear-gradient(135deg,#0a1630,#182848)!important;
    color:var(--blue)!important;border:1.5px solid rgba(56,165,255,0.4)!important;}
.btn-login .stButton>button:hover{border-color:rgba(56,165,255,0.75)!important;box-shadow:0 0 36px rgba(56,165,255,0.2)!important;}
.btn-signup .stButton>button{height:58px!important;background:linear-gradient(135deg,#a84200,var(--orange))!important;color:#06090e!important;box-shadow:0 0 32px rgba(255,140,66,0.3)!important;}
.btn-signup .stButton>button:hover{box-shadow:0 0 55px rgba(255,140,66,0.5)!important;}
.btn-otp .stButton>button{height:52px!important;background:linear-gradient(135deg,#0c1830,#182848)!important;
    color:var(--orange)!important;border:1.5px solid rgba(255,140,66,0.38)!important;}
.btn-otp .stButton>button:hover{border-color:rgba(255,140,66,0.75)!important;box-shadow:0 0 36px rgba(255,140,66,0.2)!important;}
.btn-verify .stButton>button{height:52px!important;
    background:linear-gradient(135deg,rgba(0,229,160,0.15),rgba(0,229,160,0.08))!important;
    color:var(--success)!important;border:1.5px solid rgba(0,229,160,0.35)!important;}
.btn-verify .stButton>button:hover{border-color:rgba(0,229,160,0.65)!important;box-shadow:0 0 28px rgba(0,229,160,0.2)!important;}
.analyze-btn .stButton>button{height:60px!important;background:linear-gradient(135deg,#0a1630,#182848)!important;
    color:var(--orange)!important;border:1.5px solid rgba(255,140,66,0.38)!important;}
.analyze-btn .stButton>button:hover{border-color:rgba(255,140,66,0.75)!important;box-shadow:0 0 40px rgba(255,140,66,0.22)!important;}
.voice-btn .stButton>button{height:54px!important;background:rgba(15,244,198,0.07)!important;
    color:var(--teal)!important;border:1.5px solid rgba(15,244,198,0.28)!important;}
.voice-btn .stButton>button:hover{background:rgba(15,244,198,0.14)!important;border-color:rgba(15,244,198,0.58)!important;box-shadow:0 0 34px rgba(15,244,198,0.22)!important;}
.back-btn .stButton>button{height:46px!important;font-size:14px!important;
    background:rgba(56,165,255,0.07)!important;color:var(--blue)!important;
    border:1px solid rgba(56,165,255,0.22)!important;letter-spacing:1.5px!important;}
.back-btn .stButton>button:hover{background:rgba(56,165,255,0.14)!important;border-color:rgba(56,165,255,0.5)!important;}
.logout-btn .stButton>button{height:40px!important;font-size:13px!important;
    background:rgba(255,92,106,0.08)!important;color:var(--danger)!important;
    border:1px solid rgba(255,92,106,0.25)!important;letter-spacing:1px!important;}
.logout-btn .stButton>button:hover{background:rgba(255,92,106,0.15)!important;border-color:rgba(255,92,106,0.5)!important;}

/* MISC */
.tip-card{background:rgba(255,140,66,0.05);border:1px solid rgba(255,140,66,0.14);border-radius:14px;padding:18px 22px;margin-top:16px;}
.tip-label{font-family:'JetBrains Mono',monospace;font-size:11px;letter-spacing:3px;color:var(--yellow);text-transform:uppercase;margin-bottom:8px;}
.tip-text{font-size:15px;color:var(--text2);line-height:1.8;}
.file-confirm{background:rgba(0,229,160,0.06);border:1px solid rgba(0,229,160,0.22);border-radius:12px;padding:14px 18px;margin-top:14px;display:flex;align-items:center;gap:14px;}
.lang-display{display:inline-flex;align-items:center;gap:8px;background:rgba(255,140,66,0.08);border:1px solid rgba(255,140,66,0.22);border-radius:100px;padding:7px 18px;font-family:'JetBrains Mono',monospace;font-size:12px;letter-spacing:2px;color:var(--orange);text-transform:uppercase;margin-top:8px;}
.audio-wrap{background:linear-gradient(135deg,rgba(15,244,198,0.04),rgba(4,10,22,0.93));border:1px solid rgba(15,244,198,0.18);border-radius:18px;padding:28px;margin-top:20px;}
.stSpinner>div{border-color:var(--orange) transparent transparent transparent!important;}
::-webkit-scrollbar{width:5px;}
::-webkit-scrollbar-track{background:var(--bg);}
::-webkit-scrollbar-thumb{background:rgba(255,140,66,0.32);border-radius:3px;}
::-webkit-scrollbar-thumb:hover{background:rgba(255,140,66,0.58);}
@keyframes fadeUp  {from{opacity:0;transform:translateY(34px);}to{opacity:1;transform:translateY(0);}}
@keyframes fadeDown{from{opacity:0;transform:translateY(-24px);}to{opacity:1;transform:translateY(0);}}
"""
