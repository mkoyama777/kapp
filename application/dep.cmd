del /F /S /Q upload
del /F /S /Q output
rmdir /S /Q upload
rmdir /S /Q output
mkdir upload
mkdir output
git add .
git commit -m "dummy"
<<<<<<< HEAD
git push origin xserver
=======
git push origin honban
>>>>>>> origin/honban
