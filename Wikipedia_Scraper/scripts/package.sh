rm -rf care-insights-lambda.zip package
mkdir package
pip3 install -r requirements.txt -t ./package
cp -r src/* package
cd package && zip -r ../care-insights-lambda.zip *
cd ..
rm -rf ./package
