param([switch]$SemEditor)

$ErrorActionPreference = 'Stop'
$Repo = $PSScriptRoot
$Utf8 = New-Object System.Text.UTF8Encoding($false)

Write-Host '[1/6] Conferindo git, python, node e ffmpeg...'
$Py = $null
if (Get-Command python -ErrorAction SilentlyContinue) { $Py = 'python' }
elseif (Get-Command py -ErrorAction SilentlyContinue) { $Py = 'py' }
$falta = @()
if (-not (Get-Command git -ErrorAction SilentlyContinue)) { $falta += 'git: winget install -e --id Git.Git' }
if (-not $Py) { $falta += 'python: winget install -e --id Python.Python.3.12' }
if (-not (Get-Command node -ErrorAction SilentlyContinue)) { $falta += 'node: winget install -e --id OpenJS.NodeJS.LTS' }
if (-not (Get-Command ffmpeg -ErrorAction SilentlyContinue)) { $falta += 'ffmpeg: winget install -e --id Gyan.FFmpeg' }
if ($falta.Count -gt 0) {
    Write-Host 'Faltam programas. Instale com os comandos abaixo, reabra o terminal e rode de novo:'
    foreach ($f in $falta) { Write-Host "  $f" }
    exit 1
}

Write-Host '[2/6] Instalando dependencias Python e o Chromium do Playwright...'
& $Py -m pip install -r (Join-Path $Repo 'requirements.txt')
& $Py -m playwright install chromium

if (-not $SemEditor) {
    Write-Host '[3/6] Instalando o editor por referencia (clone, branch edicao-iara, patches)...'
    $Ed = Join-Path $HOME 'editor-por-referencia'
    if (-not (Test-Path $Ed)) {
        git clone https://github.com/nextwork-projects/ai-video-editor-cooked.git $Ed
    }
    $existe = git -C $Ed branch --list edicao-iara
    if (-not $existe) {
        git -C $Ed checkout -b edicao-iara e56fad2c46ed0998dfa74ecd414d81aa3dc53b59
        $patches = Get-ChildItem -Path (Join-Path $Repo 'edicao-iara\editor-patch') -Filter '*.patch' | Sort-Object Name | ForEach-Object { $_.FullName }
        git -C $Ed -c user.name=edicao-iara -c user.email=edicao-iara@local am @patches
    } else {
        Write-Host '  Branch edicao-iara ja existe; pulando patches.'
        git -C $Ed checkout edicao-iara
    }
    & $Py (Join-Path $Ed 'plugins\ai-editor\skills\setup\scripts\setup.py') bootstrap
    $cfg = Join-Path $HOME '.ai-video-editor'
    if (-not (Test-Path $cfg)) { New-Item -ItemType Directory -Path $cfg -Force | Out-Null }
    $json = ConvertTo-Json -InputObject @{ path = (Join-Path $Repo 'edicao-iara') }
    [IO.File]::WriteAllText((Join-Path $cfg 'library.json'), $json, $Utf8)
    $edits = Join-Path $Repo 'edicao-iara\edits'
    if (-not (Test-Path $edits)) { New-Item -ItemType Directory -Path $edits -Force | Out-Null }
} else {
    Write-Host '[3/6] Pulando o editor por referencia (-SemEditor).'
}

Write-Host '[4/6] Copiando skills para Gemini/Antigravity e Claude...'
$destinos = @((Join-Path $HOME '.gemini\antigravity\skills'), (Join-Path $HOME '.claude\skills'))
foreach ($d in $destinos) {
    if (-not (Test-Path $d)) { New-Item -ItemType Directory -Path $d -Force | Out-Null }
    foreach ($s in Get-ChildItem -Path (Join-Path $Repo 'skills') -Directory) {
        Copy-Item -Path $s.FullName -Destination $d -Recurse -Force
    }
}

Write-Host '[5/6] Gravando memoria global (GEMINI.md e CLAUDE.md)...'
$Marca = '<!-- gatoteca-e-edicao-iara -->'
$Fim = '<!-- /gatoteca-e-edicao-iara -->'
$agentes = [IO.File]::ReadAllText((Join-Path $Repo 'AGENTS.md'), $Utf8)
$memorias = @((Join-Path $HOME '.gemini\GEMINI.md'), (Join-Path $HOME '.claude\CLAUDE.md'))
foreach ($m in $memorias) {
    $pasta = Split-Path $m -Parent
    if (-not (Test-Path $pasta)) { New-Item -ItemType Directory -Path $pasta -Force | Out-Null }
    $atual = ''
    if (Test-Path $m) { $atual = [IO.File]::ReadAllText($m, $Utf8) }
    $bloco = $Marca + "`r`nRepositório gatoteca-e-edicao-iara instalado em: " + $Repo + "`r`n" + $agentes + "`r`n" + $Fim
    $i = $atual.IndexOf($Marca)
    if ($i -ge 0) {
        # ja instalado antes: troca o bloco antigo pelo novo (assim uma atualizacao vale)
        $j = $atual.IndexOf($Fim, $i)
        if ($j -ge 0) { $depois = $atual.Substring($j + $Fim.Length) } else { $depois = '' }
        $novo = $atual.Substring(0, $i) + $bloco + $depois
    } else {
        $novo = $atual + "`r`n" + $bloco + "`r`n"
    }
    [IO.File]::WriteAllText($m, $novo, $Utf8)
}

Write-Host "[6/6] Pronto. Abra o agente na pasta $Repo e peça: edita meu vídeo no estilo Iara / faz um post da Gatoteca."
