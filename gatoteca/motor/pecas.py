# -*- coding: utf-8 -*-
"""Pecas da cena da Jaqueira, em <symbol> reutilizavel, com cores por variavel CSS.

Coordenadas herdadas da carta original (540x760): o tronco nasce em (270,606).
Uso: <use href="#arvore" x=".." y=".." width=".." height=".." style="--copa1:#..">
"""
import math, random

# ---------------------------------------------------------------- filtros e gradientes
DEFS = r'''
<filter id="mao" x="-5%" y="-5%" width="110%" height="110%">
  <feTurbulence type="fractalNoise" baseFrequency=".045" numOctaves="2" seed="4" result="n"/>
  <feDisplacementMap in="SourceGraphic" in2="n" scale="1.8" xChannelSelector="R" yChannelSelector="G"/>
</filter>
<filter id="aguada" x="-10%" y="-10%" width="120%" height="120%">
  <feTurbulence type="fractalNoise" baseFrequency=".03" numOctaves="3" seed="9" result="n"/>
  <feDisplacementMap in="SourceGraphic" in2="n" scale="6" xChannelSelector="R" yChannelSelector="G" result="d"/>
  <feTurbulence type="fractalNoise" baseFrequency=".018" numOctaves="2" seed="2" result="m"/>
  <feColorMatrix in="m" type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 -1.5 1.32" result="ma"/>
  <feComposite in="d" in2="ma" operator="in"/>
</filter>
<filter id="contorno" x="-5%" y="-5%" width="110%" height="110%">
  <feMorphology in="SourceAlpha" operator="dilate" radius="1.25" result="dl"/>
  <feComposite in="dl" in2="SourceAlpha" operator="out" result="o"/>
  <feFlood flood-color="#2A1E24"/><feComposite in2="o" operator="in" result="c"/>
  <feTurbulence type="fractalNoise" baseFrequency=".045" numOctaves="2" seed="4" result="n"/>
  <feDisplacementMap in="c" in2="n" scale="1.8" xChannelSelector="R" yChannelSelector="G"/>
</filter>
<filter id="papelrecortado" x="-8%" y="-8%" width="116%" height="116%">
  <feMorphology in="SourceAlpha" operator="dilate" radius="5" result="d"/>
  <feFlood flood-color="#F6EEDC"/><feComposite in2="d" operator="in" result="borda"/>
  <feGaussianBlur in="d" stdDeviation="7" result="sb"/>
  <feOffset in="sb" dx="5" dy="12" result="so"/>
  <feFlood flood-color="#1A0E14" flood-opacity=".45"/><feComposite in2="so" operator="in" result="sombra"/>
  <feMerge><feMergeNode in="sombra"/><feMergeNode in="borda"/><feMergeNode in="SourceGraphic"/></feMerge>
</filter>
<filter id="brilho" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="10"/></filter>
<filter id="brilho2" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="3"/></filter>
<filter id="sombra" x="-20%" y="-20%" width="140%" height="150%"><feDropShadow dx="0" dy="14" stdDeviation="14" flood-color="#14080E" flood-opacity=".5"/></filter>
<radialGradient id="luz" r=".5"><stop offset="0" stop-color="#FFD267" stop-opacity=".85"/><stop offset=".45" stop-color="#F2A93C" stop-opacity=".3"/><stop offset="1" stop-color="#F2A93C" stop-opacity="0"/></radialGradient>
<radialGradient id="luar" r=".5"><stop offset=".55" stop-color="#F2D27E" stop-opacity=".35"/><stop offset="1" stop-color="#F2D27E" stop-opacity="0"/></radialGradient>
<radialGradient id="lunar" cx="42%" cy="40%" r="62%"><stop offset="0" stop-color="#FDF3D6"/><stop offset=".65" stop-color="#F4DC98"/><stop offset="1" stop-color="#E6BF6E"/></radialGradient>
<pattern id="bolinhas" width="6" height="6" patternUnits="userSpaceOnUse"><circle cx="1.5" cy="1.5" r="1.05" fill="#3B2A33" opacity=".5"/><circle cx="4.5" cy="4.5" r="1.05" fill="#3B2A33" opacity=".5"/></pattern>
<pattern id="xadrez" width="14" height="14" patternUnits="userSpaceOnUse" patternTransform="skewX(-18)">
  <rect width="14" height="14" fill="#F6DDE3"/><rect width="7" height="14" fill="#C8324F" opacity=".45"/><rect width="14" height="7" fill="#C8324F" opacity=".45"/></pattern>
<path id="br0" d="M0,-10 Q0,0 10,0 Q0,0 0,10 Q0,0 -10,0 Q0,0 0,-10Z"/>
'''

# circulos da copa: camada de tras e camada da frente
COPA_TRAS = [(118, 328, 50), (422, 328, 50), (178, 270, 56), (362, 270, 56), (270, 240, 62), (220, 246, 44), (320, 246, 44)]
COPA_FRENTE = [(150, 374, 46), (390, 374, 46), (212, 318, 60), (328, 318, 60), (270, 296, 62), (270, 378, 52), (206, 392, 42), (334, 392, 42)]
circ = lambda L: "".join('<circle cx="%d" cy="%d" r="%d"/>' % c for c in L)

TRONCO = ("M222,606 C236,600 244,592 246,580 C244,560 250,500 252,440 C253,420 245,405 232,392 L250,385 C258,398 264,410 270,410 "
          "C276,410 282,398 290,385 L312,392 C297,405 289,420 290,440 C291,452 291,462 291,470 C312,462 334,450 360,436 L363,443 "
          "C338,460 314,476 292,486 C293,520 298,560 296,580 C298,592 304,600 318,606 Z")

L = "style='stroke:var(--linha,#2A1E24)'"

SIMBOLOS = r'''
<symbol id="arvore" viewBox="60 170 420 450" overflow="visible">
  <path d="%(tronco)s" style="fill:var(--tronco,#8A6A62)" opacity=".75" filter="url(#aguada)"/>
  <g filter="url(#mao)" fill="none" %(L)s stroke-width="1.35" stroke-linecap="round" stroke-linejoin="round">
    <path d="M222,606 C236,600 244,592 246,580 C244,560 250,500 252,440 C253,420 245,405 232,392"/>
    <path d="M318,606 C304,600 298,592 296,580 C298,560 293,520 292,486 C314,476 338,460 363,443"/>
    <path d="M360,436 C334,450 312,462 291,470 C291,462 291,452 290,440 C289,420 297,405 312,392"/>
    <path d="M250,385 C258,398 264,410 270,410 C276,410 282,398 290,385"/>
    <path d="M262,592 C259,552 266,505 263,458 M281,582 C283,546 278,512 281,494" stroke-width=".8" opacity=".7"/>
    <path d="M232,606 C238,610 246,610 252,606 M286,607 C294,611 302,611 308,606" stroke-width=".9"/>
  </g>
  <g filter="url(#contorno)">%(tras)s</g>
  <g style="fill:var(--copabase,#ECE0C6)">%(tras)s</g>
  <g style="fill:var(--copa1,#6F8C74)" filter="url(#aguada)">%(tras)s</g>
  <g filter="url(#contorno)">%(frente)s</g>
  <g style="fill:var(--copabase,#ECE0C6)">%(frente)s</g>
  <g style="fill:var(--copa2,#A9C49C)" filter="url(#aguada)">%(frente)s</g>
  <g fill="#1F2A22" opacity=".22" filter="url(#aguada)"><ellipse cx="270" cy="410" rx="150" ry="24"/><ellipse cx="150" cy="400" rx="36" ry="16"/><ellipse cx="390" cy="400" rx="36" ry="16"/></g>
  <g style="fill:var(--copaluz,#E9EFCF)" opacity=".55" filter="url(#aguada)">
    <ellipse cx="252" cy="266" rx="34" ry="15"/><ellipse cx="196" cy="292" rx="24" ry="11"/><ellipse cx="312" cy="290" rx="24" ry="11"/>
    <ellipse cx="146" cy="352" rx="18" ry="8"/><ellipse cx="380" cy="352" rx="18" ry="8"/></g>
  <g fill="none" style="stroke:var(--folha,#3E5A44)" stroke-width="1" stroke-linecap="round" opacity=".6" filter="url(#mao)">
    <path d="M150,300 q4,4 8,0 q4,4 8,0 M160,308 q4,4 8,0 M384,296 q4,4 8,0 q4,4 8,0 M394,304 q4,4 8,0 M240,232 q4,4 8,0 q4,4 8,0 M250,240 q4,4 8,0
             M300,330 q4,4 8,0 q4,4 8,0 M196,350 q4,4 8,0 q4,4 8,0 M206,358 q4,4 8,0 M118,350 q4,4 8,0 q4,4 8,0 M412,350 q4,4 8,0 q4,4 8,0
             M262,394 q4,4 8,0 q4,4 8,0 M340,262 q4,4 8,0 q4,4 8,0"/></g>
  <g filter="url(#mao)" fill="none" %(L)s stroke-width=".9" stroke-linecap="round" opacity=".75">
    <path d="M236,350 C248,358 262,360 274,356 M296,344 C308,352 322,354 334,348 M174,398 C184,404 196,405 206,401 M340,404 C350,408 362,408 372,402"/></g>
  <!-- jacas no tronco -->
  <g fill="#E4DDA0"><ellipse cx="245" cy="482" rx="14" ry="24" transform="rotate(10 245 482)"/><ellipse cx="306" cy="528" rx="15" ry="25" transform="rotate(-10 306 528)"/><ellipse cx="262" cy="560" rx="11" ry="18" transform="rotate(5 262 560)"/></g>
  <g style="fill:var(--jaca,#BDBF6A)" filter="url(#aguada)">
    <ellipse cx="245" cy="482" rx="14" ry="24" transform="rotate(10 245 482)"/><ellipse cx="306" cy="528" rx="15" ry="25" transform="rotate(-10 306 528)"/><ellipse cx="262" cy="560" rx="11" ry="18" transform="rotate(5 262 560)"/></g>
  <g fill="url(#bolinhas)"><ellipse cx="245" cy="482" rx="14" ry="24" transform="rotate(10 245 482)"/><ellipse cx="306" cy="528" rx="15" ry="25" transform="rotate(-10 306 528)"/><ellipse cx="262" cy="560" rx="11" ry="18" transform="rotate(5 262 560)"/></g>
  <g filter="url(#mao)" fill="none" %(L)s stroke-width="1.25" stroke-linecap="round">
    <ellipse cx="245" cy="482" rx="14" ry="24" transform="rotate(10 245 482)"/><path d="M251,459 L253,455"/>
    <ellipse cx="306" cy="528" rx="15" ry="25" transform="rotate(-10 306 528)"/><path d="M297,506 L294,502"/>
    <ellipse cx="262" cy="560" rx="11" ry="18" transform="rotate(5 262 560)"/></g>
  <!-- a jaca-lanterna -->
  <circle cx="350" cy="500" r="96" fill="url(#luz)"/>
  <path d="M350,448 L350,466" %(L)s stroke-width="1.3" filter="url(#mao)"/>
  <ellipse cx="350" cy="498" rx="22" ry="32" style="fill:var(--lanterna,#E2A23E)" filter="url(#aguada)"/>
  <ellipse cx="350" cy="498" rx="22" ry="32" fill="url(#bolinhas)" opacity=".5"/>
  <g fill="#FFF3C6"><path d="M337,486 L346,486 L341.5,476Z"/><path d="M354,486 L363,486 L358.5,476Z"/>
    <path d="M335,500 L339.5,506 L344.5,501 L350,507 L355.5,501 L360.5,506 L365,500 C360,516 340,516 335,500Z"/></g>
  <g fill="#FFE07A" opacity=".55" filter="url(#brilho2)"><circle cx="350" cy="496" r="12"/></g>
  <ellipse cx="350" cy="498" rx="22" ry="32" fill="none" %(L)s stroke-width="1.35" filter="url(#mao)"/>
  <g fill="#FFD267" style="opacity:var(--vagalume,1)"><circle cx="402" cy="452" r="2"/><circle cx="388" cy="560" r="1.6"/><circle cx="312" cy="452" r="1.4"/><circle cx="420" cy="512" r="1.3"/></g>
</symbol>

<symbol id="gato" viewBox="376 540 92 112" overflow="visible">
  <g filter="url(#mao)">
    <path d="M428,644 C452,642 462,622 452,608 C449,603 443,605 445,611 C450,622 442,633 428,636" style="fill:var(--gato,#231820)"/>
    <path d="M391,580 C379,598 379,628 386,646 L426,646 C433,628 432,598 420,580 C412,588 398,588 391,580 Z" style="fill:var(--gato,#231820)"/>
    <path d="M390,577 C387,567 390,557 394,549 L401,560 C405,558 409,558 413,560 L420,549 C424,557 426,567 422,577 C419,590 393,590 390,577 Z" style="fill:var(--gato,#231820)"/>
    <g style="fill:var(--olho,#F2B544)"><ellipse cx="400" cy="571" rx="3.2" ry="2.7"/><ellipse cx="412" cy="571" rx="3.2" ry="2.7"/></g>
    <g style="fill:var(--gato,#231820)"><ellipse cx="399.2" cy="570.6" rx=".9" ry="2.2"/><ellipse cx="411.2" cy="570.6" rx=".9" ry="2.2"/></g>
  </g>
</symbol>

<symbol id="piquenique" viewBox="44 600 182 66" overflow="visible">
  <path d="M62,630 L194,624 L218,654 L48,662 Z" fill="url(#xadrez)" filter="url(#aguada)"/>
  <path d="M62,630 L194,624 L218,654 L48,662 Z" fill="none" %(L)s stroke-width="1.2" stroke-linejoin="round" filter="url(#mao)"/>
  <g filter="url(#mao)" %(L)s stroke-width="1.2" stroke-linejoin="round" stroke-linecap="round">
    <path d="M94,640 C107,629 120,629 131,636 L131,653 C120,646 107,646 94,655 Z" fill="#FBF6EA"/>
    <path d="M131,636 C142,629 155,629 168,640 L168,655 C155,646 142,646 131,653 Z" fill="#FBF6EA"/>
    <path d="M100,642 C108,637 117,637 125,640 M100,647 C108,642 117,642 125,645 M137,640 C145,637 153,637 161,642 M137,645 C145,642 153,642 161,647" fill="none" stroke-width=".7" opacity=".6"/>
    <path d="M176,630 L194,630 L192,646 C190,650 180,650 178,646 Z" fill="#F4ECDC"/>
    <path d="M194,634 C201,634 201,642 193,642" fill="none"/>
    <path d="M182,624 C178,618 186,614 182,606 M189,624 C186,619 192,615 189,609" fill="none" stroke-width=".9" opacity=".75"/>
    <path d="M64,648 L86,640 L88,652 L66,658 Z" fill="#F4DDB0"/><path d="M64,648 L86,640 L86,644 L64,652Z" fill="#D9734E"/>
    <circle cx="80" cy="636" r="2.4" fill="#C8324F"/>
    <circle cx="200" cy="652" r="2.6" fill="#C8324F"/><circle cx="206" cy="648" r="2.4" fill="#7A3E8E"/><circle cx="205" cy="655" r="2.2" fill="#C8324F"/>
  </g>
</symbol>

<symbol id="abobora" viewBox="-24 -26 48 42" overflow="visible">
  <g style="fill:var(--abobora,#E8752F)" filter="url(#aguada)"><ellipse cx="-9" cy="0" rx="12" ry="11"/><ellipse cx="9" cy="0" rx="12" ry="11"/><ellipse cx="0" cy="0" rx="12" ry="12"/></g>
  <g fill="none" %(L)s stroke-width="1.1" filter="url(#mao)"><ellipse cx="-9" cy="0" rx="12" ry="11"/><ellipse cx="9" cy="0" rx="12" ry="11"/><ellipse cx="0" cy="0" rx="9" ry="12"/>
    <path d="M0,-12 C0,-17 2,-19 5,-20" stroke-linecap="round" stroke-width="1.6" style="stroke:var(--talo,#4E6B3A)"/></g>
</symbol>

<symbol id="morcego" viewBox="-12 -7 24 12" overflow="visible">
  <path d="M-11,0 Q-7,-6 -3.5,-1.5 Q-1.5,-4 0,-3 Q1.5,-4 3.5,-1.5 Q7,-6 11,0 Q7,-1.6 4.5,1.8 Q2,0 0,1.6 Q-2,0 -4.5,1.8 Q-7,-1.6 -11,0Z" style="fill:var(--morcego,#231820)"/>
</symbol>
<symbol id="br" viewBox="-10 -10 20 20" overflow="visible"><use href="#br0"/></symbol>
<symbol id="folha" viewBox="-6 -8 12 16" overflow="visible">
  <path d="M0,-7 C5,-3 5,3 0,7 C-5,3 -5,-3 0,-7Z" style="fill:var(--cor,#7DB87A)" %(L)s stroke-width=".8"/><path d="M0,-6 L0,6" %(L)s stroke-width=".6"/>
</symbol>

<!-- icones do que esta incluso -->
<symbol id="ic_ecobag" viewBox="-30 -30 60 60" overflow="visible"><g filter="url(#mao)" %(L)s stroke-width="1.6" stroke-linejoin="round" stroke-linecap="round">
  <path d="M-10,-6 C-10,-22 10,-22 10,-6" fill="none"/><path d="M-17,-6 L17,-6 L15,22 L-15,22 Z" fill="#EAD9B8"/>
  <path d="M-4,8 a6,6 0 1 0 6,-6 a4.6,4.6 0 1 1 -6,6Z" fill="#E8752F" stroke-width="1.1"/></g></symbol>
<symbol id="ic_marcador" viewBox="-30 -30 60 60" overflow="visible"><g filter="url(#mao)" %(L)s stroke-width="1.6" stroke-linejoin="round">
  <path d="M-9,-23 L9,-23 L9,23 L0,15 L-9,23Z" fill="#C8324F"/><use href="#br0" transform="translate(0 -6) scale(.6)" fill="#FBEFD0" stroke="none"/>
  <circle cx="0" cy="-17" r="2.4" fill="#FBEFD0" stroke-width="1"/></g></symbol>
<symbol id="ic_cafe" viewBox="-30 -30 60 60" overflow="visible"><g filter="url(#mao)" %(L)s stroke-width="1.6" stroke-linejoin="round" stroke-linecap="round">
  <path d="M-16,-2 L12,-2 L10,16 C8,22 -12,22 -14,16 Z" fill="#F4ECDC"/><path d="M12,2 C21,2 21,12 10,12" fill="none"/>
  <path d="M-22,22 L18,22" /><path d="M-8,-8 C-11,-13 -5,-16 -8,-22 M0,-8 C-3,-13 3,-16 0,-22" fill="none" stroke-width="1.2"/>
  <path d="M-13,3 L9,3" stroke="#8A5A3A" stroke-width="3" opacity=".7"/></g></symbol>
<symbol id="ic_bolo" viewBox="-30 -30 60 60" overflow="visible"><g filter="url(#mao)" %(L)s stroke-width="1.6" stroke-linejoin="round">
  <path d="M-20,4 L18,-12 L20,14 L-18,20 Z" fill="#F4DDB0"/><path d="M-20,4 L18,-12 L18.6,-4 L-19.4,12 Z" fill="#D9734E"/>
  <path d="M-19,13 L19.4,0" stroke="#FBEFD0" stroke-width="3"/><circle cx="6" cy="-14" r="4.5" fill="#C8324F"/></g></symbol>
<symbol id="ic_frutinhas" viewBox="-30 -30 60 60" overflow="visible"><g filter="url(#mao)" %(L)s stroke-width="1.5">
  <path d="M-2,-10 C4,-24 16,-22 18,-16 C10,-18 2,-14 -2,-10Z" fill="#7DB87A"/>
  <circle cx="-10" cy="4" r="9" fill="#C8324F"/><circle cx="8" cy="6" r="8" fill="#7A3E8E"/><circle cx="-1" cy="17" r="7.5" fill="#C8324F"/>
  <path d="M-2,-10 C-6,-4 -9,-2 -10,-5 M-2,-10 C2,-4 6,-2 8,-2" fill="none" stroke-width="1.1"/></g></symbol>
<symbol id="ic_livro" viewBox="-30 -30 60 60" overflow="visible"><g filter="url(#mao)" %(L)s stroke-width="1.6" stroke-linejoin="round">
  <path d="M-18,-20 L14,-20 L14,20 L-18,20 Z" fill="#3F6E8C"/><path d="M14,-20 L19,-15 L19,24 L-13,24 L-18,20 L14,20Z" fill="#F4ECDC"/>
  <path d="M-12,-20 L-12,20" stroke-width="1"/><use href="#br0" transform="translate(1 0) scale(.75)" fill="#F2B544" stroke="none"/>
  <path d="M8,-20 L8,-6 L11,-9 L14,-6" fill="#C8324F" stroke-width="1"/></g></symbol>
''' % {"tronco": TRONCO, "L": L, "tras": circ(COPA_TRAS), "frente": circ(COPA_FRENTE)}


def defs_svg():
    return '<svg width="0" height="0" style="position:absolute"><defs>%s%s</defs></svg>' % (DEFS, SIMBOLOS)


def lua(cx, cy, r, linha="#2A1E24", raios=True, aneis=True, opac_raios=.55, fill="url(#lunar)"):
    """Lua cheia com aureola de tarot (raios finos e aneis)."""
    s = ['<g transform="translate(%g %g)">' % (cx, cy)]
    s.append('<circle r="%g" fill="url(#luar)"/>' % (r * 1.45))
    if raios:
        s.append('<g stroke="%s" stroke-width="%g" opacity="%g" filter="url(#mao)">' % (linha, max(.8, r / 130), opac_raios))
        a = 0.0
        while a < 360:
            t = math.radians(a)
            l = r * (1.65 if int(a) % 15 == 0 else 1.5)
            s.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f"/>' % (math.cos(t) * r * 1.29, math.sin(t) * r * 1.29, math.cos(t) * l, math.sin(t) * l))
            a += 7.5
        s.append('</g>')
    s.append('<circle r="%g" fill="#F1D88E"/>' % r)
    s.append('<circle r="%g" fill="%s" filter="url(#aguada)"/>' % (r, fill))
    s.append('<g fill="#D9B46A" opacity=".33" filter="url(#aguada)"><circle cx="%g" cy="%g" r="%g"/><circle cx="%g" cy="%g" r="%g"/><circle cx="%g" cy="%g" r="%g"/></g>'
             % (-r * .33, -r * .29, r * .15, r * .21, -r * .46, r * .1, r * .38, -r * .08, r * .125))
    if aneis:
        s.append('<g fill="none" stroke="%s" filter="url(#mao)"><circle r="%g" stroke-width="1.2"/><circle r="%g" stroke-width=".7" opacity=".7"/>'
                 '<circle r="%g" stroke-width=".9" stroke-dasharray="1.5 6" opacity=".7"/></g>' % (linha, r, r * 1.115, r * 1.2))
    s.append('</g>')
    return "".join(s)


def selo(cx, cy, R, rot, fundo, cor, l1, l2, fonte1="Cinzel", tam1=None):
    """Selo recortado (borda ondulada) com o preco."""
    pts = []
    for i in range(361):
        t = math.radians(i)
        rr = R + R * .055 * math.cos(22 * t)
        pts.append("%.1f,%.1f" % (math.cos(t) * rr, math.sin(t) * rr))
    tam1 = tam1 or R * .52
    return ('<g transform="translate(%g %g) rotate(%g)" filter="url(#sombra)">'
            '<path d="M%sZ" fill="%s"/>'
            '<circle r="%g" fill="none" stroke="%s" stroke-width="1.3" stroke-dasharray="2 5" opacity=".8"/>'
            '<text y="%g" text-anchor="middle" font-family="%s" font-weight="700" font-size="%g" fill="%s">%s</text>'
            '<text y="%g" text-anchor="middle" font-family="Cinzel" font-weight="600" font-size="%g" letter-spacing="2" fill="%s">%s</text>'
            '</g>') % (cx, cy, rot, " L".join(pts), fundo, R * .82, cor, tam1 * .32, fonte1, tam1, cor, l1, R * .5, R * .2, cor, l2)


def estrelas(n, w, h, seed=7, cor="#EFE4D0", evitar=None, rmin=.6, rmax=2.0):
    random.seed(seed)
    s = []
    for _ in range(n):
        x, y = random.random() * w, random.random() * h
        if evitar and evitar(x, y):
            continue
        s.append('<circle cx="%.0f" cy="%.0f" r="%.2f" opacity="%.2f"/>' % (x, y, rmin + random.random() * (rmax - rmin), .3 + random.random() * .5))
    return '<g fill="%s">%s</g>' % (cor, "".join(s))


def brilhos(lista, cor):
    return '<g style="fill:%s">%s</g>' % (cor, "".join('<use href="#br0" transform="translate(%g %g) scale(%g)"/>' % t for t in lista))


def morcegos(lista, cor="#231820"):
    return "".join('<use href="#morcego" x="-12" y="-7" width="24" height="12" transform="translate(%g %g) scale(%g) rotate(%g)" style="--morcego:%s"/>' % (x, y, k, r, cor) for x, y, k, r in lista)


def use(simb, x, y, w, h, estilo="", extra=""):
    return '<use href="#%s" x="%g" y="%g" width="%g" height="%g" style="%s" %s/>' % (simb, x, y, w, h, estilo, extra)


# proporcoes dos simbolos (viewBox)
VB = {"arvore": (420, 450), "gato": (92, 112), "piquenique": (182, 66), "abobora": (48, 42)}


def arvore(x_base, y_base, esc, estilo=""):
    """Arvore com o pe do tronco (270,606) caindo em (x_base,y_base)."""
    w, h = 420 * esc, 450 * esc
    return use("arvore", x_base - (270 - 60) * esc, y_base - (606 - 170) * esc, w, h, estilo)


def gato(x, y_chao, esc, estilo="", espelho=False):
    """Gato sentado com o centro do corpo em x e a base em y_chao."""
    w, h = 92 * esc, 112 * esc
    x0, y0 = x - (406 - 376) * esc, y_chao - (646 - 540) * esc
    if espelho:
        return '<g transform="translate(%g 0) scale(-1 1)">%s</g>' % (2 * x, use("gato", x0, y0, w, h, estilo))
    return use("gato", x0, y0, w, h, estilo)


def abobora(cx, cy, esc, estilo=""):
    return use("abobora", cx - 24 * esc, cy - 26 * esc, 48 * esc, 42 * esc, estilo)


def piquenique(x, y, esc):
    return use("piquenique", x, y, 182 * esc, 66 * esc)


ICONES = [("ic_ecobag", "Ecobag"), ("ic_marcador", "Marcador"), ("ic_cafe", "Café"), ("ic_bolo", "Bolo"), ("ic_frutinhas", "Frutinhas"), ("ic_livro", "Sorteio de livro")]


def icones_html(cor_txt, tam=58, gap=26, linha="#2A1E24"):
    itens = "".join('<div class="ic"><svg width="%d" height="%d" viewBox="-30 -30 60 60" style="--linha:%s"><use href="#%s" x="-30" y="-30" width="60" height="60"/></svg><span>%s</span></div>' % (tam, tam, linha, i, n) for i, n in ICONES)
    return '<div class="icones" style="gap:%dpx;color:%s">%s</div>' % (gap, cor_txt, itens)


CSS_BASE = r'''
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:1080px;height:1350px}
.peca{position:relative;width:1080px;height:1350px;overflow:hidden}
.peca::before,.peca::after{content:"";position:absolute;inset:0;pointer-events:none;background-size:1080px 1440px;z-index:50}
.peca::before{background-image:var(--grao-neg);mix-blend-mode:multiply;opacity:.85}
.peca::after{background-image:var(--grao-pos);mix-blend-mode:plus-lighter;opacity:.6}
.peca>*{position:absolute}
svg{overflow:visible}
.marca{display:flex;flex-direction:column;align-items:center}
.marca .sobre{font-family:'Cinzel';font-weight:600;font-size:15px;letter-spacing:.42em;margin-right:-.42em}
.marca .nome{position:relative;margin-top:9px;padding:5px 24px 8px;font-family:'Cormorant';font-style:italic;font-weight:500;font-size:48px;line-height:1}
.marca .nome::before,.marca .nome::after{content:"";position:absolute;left:0;right:0;height:1px;background:linear-gradient(90deg,transparent,currentColor 12%,currentColor 88%,transparent);opacity:.75}
.marca .nome::before{top:0}.marca .nome::after{bottom:0}
.icones{display:flex;justify-content:center;align-items:flex-start}
.ic{display:flex;flex-direction:column;align-items:center;gap:6px;width:112px}
.ic span{font-family:'Cormorant';font-style:italic;font-weight:600;font-size:21px;line-height:1.05;text-align:center}
.gi{position:absolute;-webkit-mask-size:100% 100%;mask-size:100% 100%;-webkit-mask-repeat:no-repeat;mask-repeat:no-repeat}
'''


def marca_html(cor_sobre, cor_nome, extra_style=""):
    return '<div class="marca" style="%s"><div class="sobre" style="color:%s">Clube do livro</div><div class="nome" style="color:%s">Entrelinhas</div></div>' % (extra_style, cor_sobre, cor_nome)


def pagina(titulo, css, corpo):
    return ('<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><title>%s</title>\n<!--ACERVO-->\n<style>%s%s</style></head>'
            '<body>%s<div class="peca">%s</div></body></html>') % (titulo, CSS_BASE, css, defs_svg(), corpo)
