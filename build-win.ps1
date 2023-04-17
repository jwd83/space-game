# remove the dist directory

# check if the the-hunt-for-roy-carnassus directory exists
# and if it does, remove it
if (Test-Path ./the-hunt-for-roy-carnassus) {
    # print out a message that we are deleting the old build directory
    Write-Host "Deleting old build directory"
    # remove the directory
    rm -r -force ./the-hunt-for-roy-carnassus/
}

# check if the the-hunt-for-roy-carnassus directory exists
# and if it does, remove it
if (Test-Path ./dist) {
    # print out a message that we are deleting the old build directory
    Write-Host "Deleting old dist directory"
    # remove the directory
    rm -r -force ./dist/
}


# check if the the-hunt-for-roy-carnassus-windows.zip file exists
# and if it does, remove it
if (Test-Path ./the-hunt-for-roy-carnassus-windows.zip) {
    # print out a message that we are deleting the old zip file
    Write-Host "Deleting old zip file"

    # remove the file
    rm -force ./the-hunt-for-roy-carnassus-windows.zip
}

PyInstaller --onefile main.py

cp -r fonts ./dist/
cp -r ships ./dist/
cp -r sounds ./dist/
cp -r sprites ./dist/

mv ./dist/main.exe ./dist/roy-carnassus.exe
mv ./dist/ ./the-hunt-for-roy-carnassus/

# compress the dist directory into the file windows.zip
Compress-Archive ./the-hunt-for-roy-carnassus/ ./the-hunt-for-roy-carnassus-windows.zip

# clean up the dist folder
rm -r -force ./the-hunt-for-roy-carnassus/
