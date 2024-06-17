import AWS from 'aws-sdk';
import fs from 'fs';
import path from 'path';
import { spawn } from 'child_process';

const REGION = "ap-northeast-2";
const BUCKET = 'vplate-s3';
const tempPath = '/tmp/';

export const handler = async (event, context) => {

  try {
    const video_path = event.video_path;    
    const extension = path.extname(video_path);
    const filename = path.basename(video_path);
    const basename = path.basename(video_path, extension);
    const dirName = path.dirname(video_path);
    
    const parsedUrl = new URL(video_path);
    const pathWithoutDomain = parsedUrl.pathname.replace(/^\/|\/[^\/]+$/g, '');
    
    const s3 = new AWS.S3({ region: REGION });
    
    let targetPath = '';
    if (pathWithoutDomain === filename) {
      targetPath = filename;
    } else {
      targetPath = pathWithoutDomain + '/' + filename;
    }
  
    const video = await s3.getObject({
      Bucket: BUCKET,
      Key: targetPath,
    }).promise();
    
    // 비디오 버퍼를 로컬 파일로 저장
    const videoFilePath = tempPath + filename;
    
    await fs.writeFileSync(videoFilePath, video.Body);
        
    const thumbnailFile = tempPath + basename + '.png';
    
    // Process video
    await generateThumbnail(videoFilePath, thumbnailFile);
    
    const result = await fs.readdirSync('/tmp')
  
    let final_path = '';
    if (dirName !== 'https://vplate-s3.s3.ap-northeast-2.amazonaws.com') {
      final_path = pathWithoutDomain + '/';
    }
    
    // 파일 읽기
    const fileContent = fs.readFileSync(tempPath + basename + '.png');
    
    const s3_params = {
      Bucket: BUCKET,
      Key: final_path + basename +'.png',
      Body: fileContent,
      ContentType: "image/png",
    };

    await s3.putObject(s3_params).promise();
  
    const response = {
      statusCode: 200,
      // body: JSON.stringify('Hello from Lambda!'),
      isSuccess: true,
    };
    return response;
  } catch (error) {
    console.info('catch error =', error);
    // callback(err);
    return {
      isSuccess: false,
    };
  }
    
};

async function generateThumbnail(videoPath, thumbnailPath) {
  return new Promise((resolve, reject) => {
    const ffmpeg = spawn('/opt/ffmpeg', [
      '-i', videoPath, 
      '-ss', '00:00:01.000', // 첫 번째 프레임을 캡쳐
      '-vframes', '1',
      thumbnailPath,
    ]);

    ffmpeg.stderr.on('data', (data) => {
      console.log('Thumbnail ERR:', data);
    });
    
    ffmpeg.on('error', (error) => {
      console.error('Error while running ffmpeg:', error);
      reject('Error while running ffmpeg');
    });

    ffmpeg.on('close', (code) => {
      if (code === 0) {
        console.log('썸네일 생성 완료');
        resolve();
      } else {
        console.error('썸네일 생성 중 오류 발생:', code);
        reject('썸네일 생성 중 오류 발생');
      }
    });
  });
}