# 도커관련

ECR 콘솔주소
```
https://ap-northeast-2.console.aws.amazon.com/ecr/repositories/private/358527653076/rembg-aws-lambda?region=ap-northeast-2
```
<br>

AWS CLI 사용 (초기 1회)
```
aws ecr get-login-password --region ap-northeast-2 | docker login --username AWS --password-stdin 358527653076.dkr.ecr.ap-northeast-2.amazonaws.com
```
<br>

빌드
```
docker build -t rembg-aws-lambda .
```
<br>

태깅
```
docker tag rembg-aws-lambda:latest 358527653076.dkr.ecr.ap-northeast-2.amazonaws.com/rembg-aws-lambda:latest
```
<br>

ECR push
```
docker push 358527653076.dkr.ecr.ap-northeast-2.amazonaws.com/rembg-aws-lambda:latest
```
<br>

이후 rembg-python-docker lambda에서 이미지를 변경해주시면 됩니다.
