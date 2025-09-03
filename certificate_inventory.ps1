<#
.SYNOPSIS
    Fetches certificate information from Windows Certificate Stores (CurrentUser and LocalMachine)
    and stores it in a CSV file.

.DESCRIPTION
    This script enumerates certificates from specified stores (My, Root, CA, TrustedPeople, 
    TrustedPublisher, AuthRoot) in both CurrentUser and LocalMachine locations.

    For each certificate, it extracts detailed information including Subject, Issuer,
    validity dates, thumbprint, serial number, and more.

    The script then aggregates all the certificate information and exports it to a single
    CSV file, creating a comprehensive inventory.

.PARAMETER CsvOutputPath
    The full path where the output CSV file will be saved.
    Example: "C:\Temp\CertificateInventory.csv"

.EXAMPLE
    .\certificate_inventory.ps1 -CsvOutputPath "C:\Temp\WindowsCerts.csv"

    This command runs the script and saves the certificate inventory to a CSV file
    named 'WindowsCerts.csv' in the 'C:\Temp' directory.
#>
param(
    [Parameter(Mandatory = $true)]
    [string]$CsvOutputPath
)

# --- 1. DEFINE STORES TO QUERY ---

$storeLocations = @("CurrentUser", "LocalMachine")
$storeNames = @("My", "Root", "CA", "TrustedPeople", "TrustedPublisher", "AuthRoot")

# --- 2. HELPER FUNCTION TO PARSE DISTINGUISHED NAMES ---

function Parse-DistinguishedName {
    param (
        [string]$DNString
    )
    $result = @{
        CN = $null
        O  = $null
        OU = $null
    }
    if ([string]::IsNullOrWhiteSpace($DNString)) {
        return $result
    }
    $parts = $DNString.Split(',') | ForEach-Object { $_.Trim() }
    foreach ($part in $parts) {
        $keyValue = $part.Split('=', 2)
        if ($keyValue.Length -eq 2) {
            $key = $keyValue[0].Trim().ToUpper()
            $value = $keyValue[1].Trim()
            if ($result.ContainsKey($key) -and $result[$key] -eq $null) {
                $result[$key] = $value
            }
        }
    }
    return $result
}


# --- 3. MAIN PROCESSING LOGIC ---

try {
    Write-Host "Starting certificate discovery..."
    $allCertificatesData = @() # Array to hold all certificate objects
    $totalCertsProcessed = 0

    # Iterate over each store location and name
    foreach ($location in $storeLocations) {
        foreach ($name in $storeNames) {
            $storePath = "Cert:\$location\$name"
            Write-Host "`nProcessing store: $storePath" -ForegroundColor Cyan

            # Check if the certificate store path exists
            if (-not (Test-Path $storePath)) {
                Write-Warning "Store path '$storePath' not found. Skipping."
                continue
            }
            
            $certificates = Get-ChildItem -Path $storePath
            if ($null -eq $certificates) {
                Write-Host "No certificates found in $storePath."
                continue
            }

            Write-Host "Found $($certificates.Count) certificates."

            # Process each certificate in the store
            foreach ($cert in $certificates) {
                $subjectDetails = Parse-DistinguishedName -DNString $cert.Subject
                $issuerDetails = Parse-DistinguishedName -DNString $cert.Issuer

                $certData = @{
                    StorePath               = "$($location)\$($name)"
                    Thumbprint              = $cert.Thumbprint
                    StoreLocation           = $location
                    StoreName               = $name
                    FriendlyName            = $cert.FriendlyName
                    Subject                 = $cert.Subject
                    SubjectCN               = $subjectDetails.CN
                    SubjectO                = $subjectDetails.O
                    SubjectOU               = $subjectDetails.OU
                    Issuer                  = $cert.Issuer
                    IssuerCN                = $issuerDetails.CN
                    IssuerO                 = $issuerDetails.O
                    IssuerOU                = $issuerDetails.OU
                    IssuedOn_NotBefore      = $cert.NotBefore
                    ExpiresOn_NotAfter      = $cert.NotAfter
                    SerialNumber            = $cert.SerialNumber
                    HasPrivateKey           = $cert.HasPrivateKey
                    PublicKeyAlgorithm      = $cert.PublicKey.Oid.FriendlyName
                    KeySize                 = if ($cert.PublicKey.Key) { $cert.PublicKey.Key.KeySize } else { 0 }
                    SignatureAlgorithm      = $cert.SignatureAlgorithm.FriendlyName
                    RawDataBase64           = if ($null -ne $cert.RawData.RawData) { [System.Convert]::ToBase64String($cert.RawData.RawData) } else { [string]::Empty }
                    LastScanned             = (Get-Date).ToUniversalTime().ToString("o") # ISO 8601 format
                }
                
                # Add the certificate data as a custom object to our array
                $allCertificatesData += [PSCustomObject]$certData
                $totalCertsProcessed++
            }
        }
    }
    
    # --- 4. EXPORT TO CSV ---
    
    Write-Host "`n----------------------------------------" -ForegroundColor Green
    if ($allCertificatesData.Count -gt 0) {
        Write-Host "Exporting $totalCertsProcessed certificates to CSV..." -ForegroundColor Green
        # Ensure the directory exists before exporting
        $CsvDirectory = Split-Path -Path $CsvOutputPath -Parent
        if (-not (Test-Path $CsvDirectory)) {
            Write-Host "Creating directory: $CsvDirectory"
            New-Item -ItemType Directory -Path $CsvDirectory | Out-Null
        }
        
        $allCertificatesData | Export-Csv -Path $CsvOutputPath -NoTypeInformation -Encoding UTF8
        Write-Host "Successfully exported certificate data to:" -ForegroundColor Green
        Write-Host $CsvOutputPath -ForegroundColor White
    }
    else {
        Write-Host "No certificates found to export." -ForegroundColor Yellow
    }
    Write-Host "----------------------------------------"

}
catch {
    Write-Error "An error occurred: $_"
    Write-Error "Stack Trace: $($_.ScriptStackTrace)"
}