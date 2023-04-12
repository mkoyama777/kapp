del /F /S /Q upload
del /F /S /Q output
rmdir /S /Q upload
rmdir /S /Q output
mkdir upload
mkdir output
git add .
git commit -m "dummy"
git push origin iccard

