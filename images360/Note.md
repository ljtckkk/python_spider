**实现步骤总结：**
1. 重写start_requests()方法，构建URL
2. 创建一个item容器，用来存储提取的数据
3. 在parse()中提取数据至item
4. 重写ImagePipeline()中实现图片下载，剔除下载失败的图片，将下载成功的item保存至数据库。