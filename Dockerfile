FROM lambci/lambda:build-python3.6

ENV AWS_DEFAULT_REGION ap-northeast-1

ADD . .

CMD pip3 install -r requirements.txt -t /var/task && \
  zip -9 deploy_package.zip lambda_handler.py && \
  zip -r9 deploy_package.zip *

