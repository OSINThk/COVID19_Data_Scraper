rm -rf wikipedia-scraper.zip package
mkdir package
pip3 install -r requirements.txt -t ./package
cp -r *.py package
cp -r *.csv package
cp -r *.geojson package
cp -r final package
cp -r output package
cd package && zip -qr ../wikipedia-scraper.zip *
cd ..
rm -rf ./package
aws s3 cp wikipedia-scraper.zip s3://outbreak-asia/lambda_builds/wikipedia-scraper.zip