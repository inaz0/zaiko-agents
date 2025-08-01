#récupération des secrets et autres infos de configuration
Get-Content C:\ProgramData\CyberFacile\Zaiko\.env | foreach {
  $name, $value = $_.split('=')
  if ([string]::IsNullOrWhiteSpace($name) -or $name.Contains('#')) {
    # skip empty or comment line in ENV file
    return
  }
  Set-Content env:\$name $value
}

$secret = $Env:SECRET
# 1. Récupération des applications, conversion explicite en objets simples
$applications = @()

$registryPaths = @(
    "HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall",
    "HKLM:\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall",
    "HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall"
)

foreach ($path in $registryPaths) {
    if (Test-Path $path) {
        Get-ChildItem $path | ForEach-Object {
            $app = Get-ItemProperty $_.PSPath
            if ($app.DisplayName) {
                $applications += [PSCustomObject]@{
                    Name              = $app.DisplayName
                    Version           = $app.DisplayVersion
                    Vendor            = $app.Publisher
                    InstallDate       = $app.InstallDate
                    PackageName       = ''
                    IdentifyingNumber = ''
                    URLUpdateInfo     = ''
                    ProductID         = ''
                    URLInfoAbout      = $app.URLInfoAbout
                }
            }
        }
    }
}

# 2. JSON brut compressé pour la signature
$app_json_raw = $applications | ConvertTo-Json -Depth 10 -Compress

$app_json_raw = $app_json_raw -replace '\\u0027', "'"

# 3. Calcul de la signature
$key = [System.Text.Encoding]::UTF8.GetBytes($Env:SECRET)
$data = [System.Text.Encoding]::UTF8.GetBytes($app_json_raw)

$hmac = New-Object System.Security.Cryptography.HMACSHA256
$hmac.Key = $key
$signature = -join ($hmac.ComputeHash($data) | ForEach-Object { "{0:x2}" -f $_ })

# 4. Récupération du numéro de série
$serial_number = (Get-WmiObject -Class Win32_BIOS).SerialNumber

# 5. Création de l’objet final
$json = @{
    serial_number = $serial_number
    os            = 'windows'
    hmac          = $signature
    client_id     = $Env:CLIENT_ID
    device_name   = $env:COMPUTERNAME
    applications  = @{
        value = $applications
        Count = $applications.Count
    }
}

# 6. Encodage JSON final
$final_json = $json | ConvertTo-Json -Depth 10 -Compress

$final_json = $final_json -replace '\\u0027', "'"
# 7. Envoi
$utf8NoBOM = New-Object System.Text.UTF8Encoding $False
Invoke-WebRequest -Uri $Env:DESTINATION_URL `
  -Method POST `
  -ContentType "application/json; charset=utf-8" `
  -Body $utf8NoBOM.GetBytes($final_json)
#Write-Output $final_json