param(
 [Parameter(Mandatory=$true)][string]$SourceRoot,
 [Parameter(Mandatory=$true)][string]$OutputDir
)
$ErrorActionPreference = 'Stop'
$manifestPath = Join-Path $PSScriptRoot '..\docs\data\images-requested.json'
$manifest = Get-Content -LiteralPath $manifestPath -Raw -Encoding UTF8 | ConvertFrom-Json
$wanted = @{}
foreach ($row in $manifest) { $wanted[$row.imageId] = $true }
$sourceFull = (Resolve-Path -LiteralPath $SourceRoot).Path.TrimEnd('\')
$outputFull = [System.IO.Path]::GetFullPath($OutputDir).TrimEnd('\')
if ($outputFull -eq $sourceFull -or $outputFull.StartsWith($sourceFull + '\', [System.StringComparison]::OrdinalIgnoreCase)) { throw 'Elegí una carpeta de salida fuera del árbol de imágenes original.' }
if (Test-Path -LiteralPath $outputFull) { throw 'La carpeta de salida ya existe. Elegí una nueva para no sobrescribir archivos.' }
$foundFiles = @{}
Get-ChildItem -LiteralPath $sourceFull -File -Recurse | ForEach-Object {
 if ($_.Extension -match '^\.(jpg|jpeg|png|tif|tiff|webp)$' -and $_.BaseName -match '(FO\d{6}_\d+)') {
  $id = $Matches[1].ToUpperInvariant()
  if ($wanted.ContainsKey($id)) {
   if ($foundFiles.ContainsKey($id)) { throw "Hay dos archivos para $id. Usá una carpeta que contenga solo una versión de cada foto." }
   $foundFiles[$id] = $_.FullName
  }
 }
}
New-Item -ItemType Directory -Path $outputFull | Out-Null
foreach ($id in $foundFiles.Keys) {
 $extension = [System.IO.Path]::GetExtension($foundFiles[$id]).ToLowerInvariant()
 Copy-Item -LiteralPath $foundFiles[$id] -Destination (Join-Path $outputFull ($id + $extension))
}
$missing = @($wanted.Keys | Where-Object { -not $foundFiles.ContainsKey($_) } | Sort-Object)
$missing | Set-Content -LiteralPath (Join-Path $outputFull 'faltantes.txt') -Encoding UTF8
Write-Host ("Copiadas: {0}. Pendientes: {1}. Revisá las imágenes antes de compartirlas." -f $foundFiles.Count, $missing.Count)
