#récupération des secrets et autres infos de configuration
Get-Content .env | foreach {
  $name, $value = $_.split('=')
  if ([string]::IsNullOrWhiteSpace($name) -or $name.Contains('#')) {
    # skip empty or comment line in ENV file
    return
  }
  Set-Content env:\$name $value
}

#récupération de la liste des applications
$application_list = Get-WmiObject -Class Win32_Product  | Select-Object Name, Version, Vendor, InstallDate, PackageName, IdentifyingNumber, URLUpdateInfo, ProductID, URLInfoAbout | ConvertTo-Json -Depth 10 -Compress
$application_list = $application_list -replace '\\u0027', "'"
#Ajouter le serial number
$serial_number = (Get-WmiObject -class win32_bios).SerialNumber

#Calcul de la clé de contrôle
# Valeurs d'entrée
$data = $application_list
$key = $Env:SECRET

# Encodage en bytes
$keyBytes = [System.Text.Encoding]::UTF8.GetBytes($Env:SECRET)
$dataBytes = [System.Text.Encoding]::UTF8.GetBytes($data)

# Création de l'objet HMAC
$hmacsha256 = New-Object System.Security.Cryptography.HMACSHA256
$hmacsha256.Key = $keyBytes

# Calcul du hash
$hashBytes = $hmacsha256.ComputeHash($dataBytes)

# Conversion en hexadécimal
$signature = -join ($hashBytes | ForEach-Object { "{0:x2}" -f $_ })


$application_list = $application_list | ConvertFrom-Json


#Création de la structure du JSON
$json = @{
serial_number = $serial_number
os = 'windows'
hmac = $signature
client_id = $Env:CLIENT_ID
device_name = $env:COMPUTERNAME
}

#On ajoute nos applications à notre objet
$json | Add-Member -MemberType NoteProperty -Name "applications" -Value $application_list

$application_list = $json | ConvertTo-Json -Depth 10 -Compress
$application_list = $application_list -replace '\\u0027', "'"

#sous linux : sudo dmidecode -s system-serial-number

#envoi des données pour traitement
#Invoke-WebRequest -Uri $Env:DESTINATION_URL -ContentType "application/json" -Method POST -Body $application_list


#for debug only
Write-Output $application_list