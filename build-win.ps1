# remove the dist directory

rm -r -force dist/

PyInstaller --onefile main.py

cp -r ships ./dist/
cp -r sounds ./dist/
cp -r music ./dist/

rm -force windows.zip

# compress the dist directory into the file windows.zip
Compress-Archive dist/ windows.zip
