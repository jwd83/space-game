# remove the dist directory

rm -r -force ./the-hunt-for-roy-carnassus/

PyInstaller --onefile main.py

cp -r fonts ./dist/
cp -r ships ./dist/
cp -r sounds ./dist/
cp -r sprites ./dist/

rm -force ./the-hunt-for-roy-carnassus-windows.zip

mv ./dist/ ./the-hunt-for-roy-carnassus/

# compress the dist directory into the file windows.zip
Compress-Archive ./the-hunt-for-roy-carnassus/ ./the-hunt-for-roy-carnassus-windows.zip

# clean up the dist folder
rm -r -force ./the-hunt-for-roy-carnassus/
