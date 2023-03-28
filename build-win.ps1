# remove the dist directory

rm -r -force dist/

PyInstaller --onefile main.py

cp -r fonts ./dist/
cp -r ships ./dist/
cp -r sounds ./dist/
cp -r sprites ./dist/

rm -force the-hunt-for-roy-carnassus-windows.zip

# compress the dist directory into the file windows.zip
Compress-Archive dist/ the-hunt-for-roy-carnassus-windows.zip
