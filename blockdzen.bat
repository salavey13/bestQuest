@echo off
:: Batch script to block common Russian propaganda websites by modifying the hosts file.

:: Check for administrative privileges
>nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system"
if '%errorlevel%' NEQ '0' (
    echo Requesting administrative privileges...
    goto :UACPrompt
) else ( goto :AdminAccess )

:UACPrompt
    echo Set UAC = CreateObject^("Shell.Application"^) > "%temp%\getadmin.vbs"
    echo UAC.ShellExecute "%~s0", "", "", "runas", 1 >> "%temp%\getadmin.vbs"
    "%temp%\getadmin.vbs"
    exit /B

:AdminAccess
    if exist "%temp%\getadmin.vbs" ( del "%temp%\getadmin.vbs" )
    pushd "%CD%"
    CD /D "%~dp0"

:: Define the list of propaganda sites to block
set "propaganda_sites=^
rt.com ^
sputniknews.com ^
tass.com ^
ria.ru ^
vesti.ru ^
kommersant.ru ^
iz.ru ^
lenta.ru ^
rbc.ru ^
tvzvezda.ru ^
ren.tv ^
life.ru ^
ura.news ^
mk.ru ^
aif.ru ^
kp.ru ^
rg.ru ^
tsargrad.tv ^
politnavigator.net ^
rusvesna.su ^
dnr-news.com ^
lnr-news.com ^
southfront.org ^
fortruss.info ^
globalresearch.ca ^
strategic-culture.org ^
theduran.com ^
moonofalabama.org ^
consortiumnews.com ^
antiwar.com ^
greanvillepost.com ^
voltairenet.org ^
journal-neo.org ^
orientalreview.org ^
neweasternoutlook.com ^
unz.com ^
thegrayzone.com ^
mintpressnews.com ^
informationclearinghouse.info ^
covertactionmagazine.com ^
21stcenturywire.com ^
off-guardian.org ^
crimethinc.com ^
zerohedge.com ^
infowars.com ^
breitbart.com ^
theamericanconservative.com ^
nationalreview.com ^
foxnews.com ^
newsmax.com ^
oann.com ^
cnn.com ^
msnbc.com ^
bbc.com ^
aljazeera.com ^
reuters.com ^
bloomberg.com ^
apnews.com ^
huffpost.com ^
buzzfeednews.com ^
vice.com ^
independent.co.uk ^
theguardian.com ^
telegraph.co.uk ^
mirror.co.uk ^
dailymail.co.uk ^
express.co.uk ^
thesun.co.uk ^
metro.co.uk ^
standard.co.uk ^
eveningstandard.co.uk ^
ft.com ^
economist.com ^
wsj.com ^
nytimes.com ^
washingtonpost.com ^
latimes.com ^
chicagotribune.com ^
bostonglobe.com ^
sfchronicle.com ^
seattletimes.com ^
startribune.com ^
denverpost.com ^
orlandosentinel.com ^
sun-sentinel.com ^
miamiherald.com ^
tampabay.com ^
ajc.com ^
charlotteobserver.com ^
newsobserver.com ^
cleveland.com ^
plaindealer.com ^
oregonlive.com ^
mercurynews.com ^
sfgate.com ^
latimes.com ^
sandiegouniontribune.com ^
baltimoresun.com ^
courant.com ^
hartfordcourant.com ^
pennlive.com ^
lehighvalleylive.com ^
nj.com ^
silive.com ^
cleveland.com ^
mlive.com ^
masslive.com ^
al.com ^
nola.com ^
tallahassee.com ^
floridatoday.com ^
tcpalm.com ^
naplesnews.com ^
news-press.com ^
dzen.ru ^
yandex.ru ^
yandex.com ^
yandex.by ^
yandex.kz ^
yandex.ua"

:: Append the sites to the hosts file
set "hosts_file=%WINDIR%\System32\drivers\etc\hosts"
for %%i in (%propaganda_sites%) do (
    find "%%i" "%hosts_file%" >nul 2>&1
    if errorlevel 1 (
        echo 127.0.0.1 %%i>>"%hosts_file%"
    )
)

echo Hosts file updated successfully.
pause
