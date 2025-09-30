# PowerShell script to fix DNS resolution issues
# Run this script as Administrator

Write-Host "Fixing DNS resolution issues..." -ForegroundColor Green

# Flush DNS cache
Write-Host "Flushing DNS cache..." -ForegroundColor Yellow
ipconfig /flushdns

# Set DNS servers to Google DNS
Write-Host "Setting DNS servers to Google DNS..." -ForegroundColor Yellow
netsh interface ip set dns "Ethernet" static 8.8.8.8
netsh interface ip add dns "Ethernet" 8.8.4.4 index=2

# Test DNS resolution
Write-Host "Testing DNS resolution..." -ForegroundColor Yellow
nslookup sts.us-east-1.amazonaws.com
nslookup ec2.us-east-1.amazonaws.com

# Test AWS connectivity
Write-Host "Testing AWS connectivity..." -ForegroundColor Yellow
try {
    aws sts get-caller-identity
    Write-Host "AWS connectivity test successful!" -ForegroundColor Green
} catch {
    Write-Host "AWS connectivity test failed. Please check your AWS credentials." -ForegroundColor Red
}

Write-Host "DNS fix completed. Try running terraform commands now." -ForegroundColor Green
