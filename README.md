# openeda
kicad , pcb  design ,   AI

![pcb_design_flow](https://github.com/user-attachments/assets/ea3c3e9a-de3a-489c-b206-856430502a23)


![Upl<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 520">
  <defs>
    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#1a1a2e"/>
      <stop offset="100%" style="stop-color:#16213e"/>
    </linearGradient>
    <linearGradient id="arrowGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:#3B82F6"/>
      <stop offset="50%" style="stop-color:#10B981"/>
      <stop offset="100%" style="stop-color:#F59E0B"/>
    </linearGradient>
    <linearGradient id="node1Grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#3B82F6;stop-opacity:0.8"/>
      <stop offset="100%" style="stop-color:#1D4ED8;stop-opacity:0.6"/>
    </linearGradient>
    <linearGradient id="node2Grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#10B981;stop-opacity:0.8"/>
      <stop offset="100%" style="stop-color:#059669;stop-opacity:0.6"/>
    </linearGradient>
    <linearGradient id="node3Grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#F59E0B;stop-opacity:0.9"/>
      <stop offset="100%" style="stop-color:#D97706;stop-opacity:0.7"/>
    </linearGradient>
    <linearGradient id="node4Grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#8B5CF6;stop-opacity:0.8"/>
      <stop offset="100%" style="stop-color:#7C3AED;stop-opacity:0.6"/>
    </linearGradient>
    <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="4" result="coloredBlur"/>
      <feMerge>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
    <filter id="shadow" x="-10%" y="-10%" width="120%" height="120%">
      <feDropShadow dx="0" dy="4" stdDeviation="6" flood-opacity="0.3"/>
    </filter>
    <marker id="arrowHead" markerWidth="10" markerHeight="10" refX="9" refY="5" orient="auto">
      <path d="M0,0 L10,5 L0,10 L2,5 Z" fill="#64748B"/>
    </marker>
    <pattern id="grid" width="30" height="30" patternUnits="userSpaceOnUse">
      <path d="M 30 0 L 0 0 0 30" fill="none" stroke="#334155" stroke-width="0.5" opacity="0.3"/>
    </pattern>
  </defs>

  <rect width="100%" height="100%" fill="url(#bgGrad)"/>
  <rect width="100%" height="100%" fill="url(#grid)"/>

  <rect x="20" y="20" width="80" height="60" rx="8" fill="none" stroke="#3B82F6" stroke-width="1" opacity="0.3"/>
  <path d="M30 50 L50 30 L70 50" fill="none" stroke="#3B82F6" stroke-width="1.5" opacity="0.5"/>
  <circle cx="50" cy="40" r="6" fill="none" stroke="#3B82F6" stroke-width="1.5" opacity="0.5"/>

  <rect x="900" y="440" width="80" height="60" rx="8" fill="none" stroke="#8B5CF6" stroke-width="1" opacity="0.3"/>
  <rect x="910" y="450" width="60" height="40" rx="4" fill="none" stroke="#8B5CF6" stroke-width="1.5" opacity="0.5"/>

  <g filter="url(#shadow)">
    <rect x="50" y="80" width="180" height="120" rx="16" fill="url(#node1Grad)" stroke="#60A5FA" stroke-width="1"/>
    <text x="140" y="115" text-anchor="middle" fill="#F8FAFC" font-size="22" font-weight="bold">原理图</text>
    <text x="140" y="140" text-anchor="middle" fill="#BFDBFE" font-size="12">Schematic</text>
    <g transform="translate(100, 155)">
      <path d="M0 0 L5 10 L15 10 L10 20 L15 30 L5 30 L0 40" fill="none" stroke="#93C5FD" stroke-width="2"/>
      <path d="M40 0 L40 40" fill="none" stroke="#93C5FD" stroke-width="2"/>
      <circle cx="20" cy="20" r="4" fill="#93C5FD"/>
    </g>
  </g>

  <g filter="url(#shadow)">
    <rect x="270" y="80" width="180" height="120" rx="16" fill="url(#node2Grad)" stroke="#34D399" stroke-width="1"/>
    <text x="360" y="115" text-anchor="middle" fill="#F8FAFC" font-size="22" font-weight="bold">网表</text>
    <text x="360" y="140" text-anchor="middle" fill="#A7F3D0" font-size="12">Netlist</text>
    <g transform="translate(320, 155)">
      <circle cx="0" cy="15" r="4" fill="#6EE7B7"/>
      <circle cx="30" cy="0" r="4" fill="#6EE7B7"/>
      <circle cx="60" cy="15" r="4" fill="#6EE7B7"/>
      <circle cx="30" cy="30" r="4" fill="#6EE7B7"/>
      <path d="M0 15 L30 0 L60 15 L30 30 Z" fill="none" stroke="#6EE7B7" stroke-width="1.5"/>
      <text x="15" y="45" fill="#A7F3D0" font-size="9">NET1</text>
      <text x="45" y="45" fill="#A7F3D0" font-size="9">NET2</text>
    </g>
  </g>

  <g filter="url(#shadow)">
    <rect x="490" y="80" width="200" height="120" rx="16" fill="url(#node3Grad)" stroke="#FBBF24" stroke-width="1"/>
    <text x="590" y="115" text-anchor="middle" fill="#F8FAFC" font-size="20" font-weight="bold">KiCad PCB</text>
    <text x="590" y="140" text-anchor="middle" fill="#FEF3C7" font-size="12">PCB Layout + RL</text>
    <g transform="translate(530, 150)">
      <rect x="0" y="0" width="120" height="40" rx="4" fill="none" stroke="#FCD34D" stroke-width="1.5"/>
      <path d="M10 20 L40 20 L50 10 L80 10" fill="none" stroke="#FCD34D" stroke-width="1.5"/>
      <path d="M20 30 L60 30 L70 20 L100 20" fill="none" stroke="#FCD34D" stroke-width="1.5"/>
      <rect x="40" y="8" width="10" height="6" rx="1" fill="#FCD34D" opacity="0.6"/>
      <rect x="60" y="28" width="10" height="6" rx="1" fill="#FCD34D" opacity="0.6"/>
    </g>
    <rect x="630" y="85" width="50" height="20" rx="10" fill="#EF4444">
      <animate attributeName="opacity" values="0.7;1;0.7" dur="2s" repeatCount="indefinite"/>
    </rect>
    <text x="655" y="99" text-anchor="middle" fill="#FFFFFF" font-size="10" font-weight="bold">AI/RL</text>
  </g>

  <g filter="url(#shadow)">
    <rect x="730" y="80" width="180" height="120" rx="16" fill="url(#node4Grad)" stroke="#A78BFA" stroke-width="1"/>
    <text x="820" y="115" text-anchor="middle" fill="#F8FAFC" font-size="22" font-weight="bold">Gerber</text>
    <text x="820" y="140" text-anchor="middle" fill="#DDD6FE" font-size="12">Gerber / Manufacturing</text>
    <g transform="translate(785, 150)">
      <rect x="0" y="0" width="70" height="45" rx="4" fill="none" stroke="#C4B5FD" stroke-width="1.5"/>
      <line x1="10" y1="12" x2="60" y2="12" stroke="#C4B5FD" stroke-width="1"/>
      <line x1="10" y1="22" x2="50" y2="22" stroke="#C4B5FD" stroke-width="1"/>
      <line x1="10" y1="32" x2="40" y2="32" stroke="#C4B5FD" stroke-width="1"/>
      <circle cx="55" cy="35" r="6" fill="none" stroke="#C4B5FD" stroke-width="1.5"/>
      <circle cx="55" cy="35" r="2" fill="#C4B5FD"/>
    </g>
  </g>

  <g opacity="0.6">
    <path d="M230 140 Q250 120 270 140" fill="none" stroke="#64748B" stroke-width="2" marker-end="url(#arrowHead)"/>
    <path d="M450 140 Q480 120 490 140" fill="none" stroke="#64748B" stroke-width="2" marker-end="url(#arrowHead)"/>
    <path d="M690 140 Q710 120 730 140" fill="none" stroke="#64748B" stroke-width="2" marker-end="url(#arrowHead)"/>
  </g>

  <g>
    <circle cx="250" cy="135" r="4" fill="#60A5FA">
      <animate attributeName="cx" values="240;260;240" dur="3s" repeatCount="indefinite"/>
    </circle>
    <circle cx="480" cy="135" r="4" fill="#34D399">
      <animate attributeName="cx" values="470;490;470" dur="3s" repeatCount="indefinite" begin="0.5s"/>
    </circle>
    <circle cx="710" cy="135" r="4" fill="#FBBF24">
      <animate attributeName="cx" values="700;720;700" dur="3s" repeatCount="indefinite" begin="1s"/>
    </circle>
  </g>

  <rect x="50" y="230" width="860" height="260" rx="12" fill="#1e293b" stroke="#334155" stroke-width="1" opacity="0.8"/>
  <text x="70" y="260" fill="#F8FAFC" font-size="16" font-weight="bold">🤖 强化学习奖励项 (RL Rewards)</text>
  <text x="290" y="260" fill="#94A3B8" font-size="12">— PCB自动布线优化目标</text>

  <rect x="70" y="280" width="820" height="2" fill="#334155"/>

  <g transform="translate(80, 300)">
    <rect x="0" y="0" width="120" height="22" rx="4" fill="#166534" opacity="0.3"/>
    <text x="60" y="15" text-anchor="middle" fill="#22C55E" font-size="11" font-weight="bold">R_completion</text>
    <text x="140" y="15" fill="#22C55E" font-size="11" font-weight="bold">+100</text>
    <text x="200" y="15" fill="#A7F3D0" font-size="10">完成所有网络连接</text>

    <rect x="420" y="0" width="120" height="22" rx="4" fill="#166534" opacity="0.3"/>
    <text x="480" y="15" text-anchor="middle" fill="#22C55E" font-size="11" font-weight="bold">R_clock_priority</text>
    <text x="560" y="15" fill="#22C55E" font-size="11" font-weight="bold">+50</text>
    <text x="620" y="15" fill="#A7F3D0" font-size="10">时钟网络优先布线</text>

    <rect x="0" y="28" width="120" height="22" rx="4" fill="#991B1B" opacity="0.3"/>
    <text x="60" y="43" text-anchor="middle" fill="#EF4444" font-size="11" font-weight="bold">R_overlap</text>
    <text x="140" y="43" fill="#EF4444" font-size="11" font-weight="bold">-100</text>
    <text x="200" y="43" fill="#FCA5A5" font-size="10">走线重叠（硬约束）</text>

    <rect x="420" y="28" width="120" height="22" rx="4" fill="#991B1B" opacity="0.3"/>
    <text x="480" y="43" text-anchor="middle" fill="#EF4444" font-size="11" font-weight="bold">R_antenna</text>
    <text x="560" y="43" fill="#EF4444" font-size="11" font-weight="bold">-200</text>
    <text x="620" y="43" fill="#FCA5A5" font-size="10">天线效应（硬约束）</text>

    <rect x="0" y="56" width="120" height="22" rx="4" fill="#991B1B" opacity="0.3"/>
    <text x="60" y="71" text-anchor="middle" fill="#EF4444" font-size="11" font-weight="bold">R_drc</text>
    <text x="140" y="71" fill="#EF4444" font-size="11" font-weight="bold">-50</text>
    <text x="200" y="71" fill="#FCA5A5" font-size="10">进入 DRC 禁区域</text>

    <rect x="420" y="56" width="120" height="22" rx="4" fill="#991B1B" opacity="0.3"/>
    <text x="480" y="71" text-anchor="middle" fill="#EF4444" font-size="11" font-weight="bold">R_timing</text>
    <text x="560" y="71" fill="#F87171" font-size="11" font-weight="bold">-0.05×</text>
    <text x="620" y="71" fill="#FCA5A5" font-size="10">时序约束惩罚</text>

    <rect x="0" y="84" width="120" height="22" rx="4" fill="#991B1B" opacity="0.3"/>
    <text x="60" y="99" text-anchor="middle" fill="#EF4444" font-size="11" font-weight="bold">R_clearance</text>
    <text x="140" y="99" fill="#EF4444" font-size="11" font-weight="bold">-20</text>
    <text x="200" y="99" fill="#FCA5A5" font-size="10">与其他网络间距不足</text>

    <rect x="420" y="84" width="120" height="22" rx="4" fill="#991B1B" opacity="0.3"/>
    <text x="480" y="99" text-anchor="middle" fill="#EF4444" font-size="11" font-weight="bold">R_differential</text>
    <text x="560" y="99" fill="#F87171" font-size="11" font-weight="bold">-15×</text>
    <text x="620" y="99" fill="#FCA5A5" font-size="10">差分对长度不匹配</text>

    <rect x="0" y="112" width="120" height="22" rx="4" fill="#B45309" opacity="0.3"/>
    <text x="60" y="127" text-anchor="middle" fill="#F59E0B" font-size="11" font-weight="bold">R_length</text>
    <text x="140" y="127" fill="#F59E0B" font-size="11" font-weight="bold">-0.1×</text>
    <text x="200" y="127" fill="#FDE68A" font-size="10">走线长度惩罚</text>

    <rect x="420" y="112" width="120" height="22" rx="4" fill="#B45309" opacity="0.3"/>
    <text x="480" y="127" text-anchor="middle" fill="#F59E0B" font-size="11" font-weight="bold">R_power_width</text>
    <text x="560" y="127" fill="#F59E0B" font-size="11" font-weight="bold">-0.5×</text>
    <text x="620" y="127" fill="#FDE68A" font-size="10">电源轨宽度不足</text>

    <rect x="0" y="140" width="120" height="22" rx="4" fill="#B45309" opacity="0.3"/>
    <text x="60" y="155" text-anchor="middle" fill="#F59E0B" font-size="11" font-weight="bold">R_via</text>
    <text x="140" y="155" fill="#F59E0B" font-size="11" font-weight="bold">-10</text>
    <text x="200" y="155" fill="#FDE68A" font-size="10">每个过孔惩罚</text>

    <rect x="420" y="140" width="120" height="22" rx="4" fill="#B45309" opacity="0.3"/>
    <text x="480" y="155" text-anchor="middle" fill="#F59E0B" font-size="11" font-weight="bold">R_layer_penalty</text>
    <text x="560" y="155" fill="#F59E0B" font-size="11" font-weight="bold">-5</text>
    <text x="620" y="155" fill="#FDE68A" font-size="10">切换层（额外过孔成本）</text>

    <rect x="0" y="168" width="120" height="22" rx="4" fill="#B45309" opacity="0.3"/>
    <text x="60" y="183" text-anchor="middle" fill="#F59E0B" font-size="11" font-weight="bold">R_angle</text>
    <text x="140" y="183" fill="#F59E0B" font-size="11" font-weight="bold">-20</text>
    <text x="200" y="183" fill="#FDE68A" font-size="10">非 45°/90° 转弯</text>

    <rect x="420" y="168" width="120" height="22" rx="4" fill="#B45309" opacity="0.3"/>
    <text x="480" y="183" text-anchor="middle" fill="#F59E0B" font-size="11" font-weight="bold">R_crossing</text>
    <text x="560" y="183" fill="#F59E0B" font-size="11" font-weight="bold">-30</text>
    <text x="620" y="183" fill="#FDE68A" font-size="10">线对交叉惩罚</text>

    <rect x="0" y="196" width="120" height="22" rx="4" fill="#075985" opacity="0.3"/>
    <text x="60" y="211" text-anchor="middle" fill="#38BDF8" font-size="11" font-weight="bold">R_symmetry</text>
    <text x="140" y="211" fill="#38BDF8" font-size="11" font-weight="bold">-0.5×</text>
    <text x="200" y="211" fill="#BAE6FD" font-size="10">OSC 对称性</text>

    <rect x="420" y="196" width="120" height="22" rx="4" fill="#075985" opacity="0.3"/>
    <text x="480" y="211" text-anchor="middle" fill="#38BDF8" font-size="11" font-weight="bold">R_step</text>
    <text x="560" y="211" fill="#38BDF8" font-size="11" font-weight="bold">-0.01</text>
    <text x="620" y="211" fill="#BAE6FD" font-size="10">每步探索小惩罚</text>
  </g>

  <g transform="translate(80, 490)">
    <circle cx="0" cy="0" r="4" fill="#64748B"/>
    <circle cx="15" cy="0" r="3" fill="#64748B"/>
    <circle cx="28" cy="0" r="2" fill="#64748B"/>
    <text x="40" y="4" fill="#94A3B8" font-size="12">等 20+ 项奖励项...</text>
  </g>
</svg>oading pcb_design_flow.svg…]()


<img width="3200" height="2000" alt="截图 2026-03-06 11-29-08" src="https://github.com/user-attachments/assets/a5c043f9-1538-4221-b71a-424246c3e8f4" />
