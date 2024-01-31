# baidupan
百度云盘上传文件

## 成为开发者
https://pan.baidu.com/union/home

## 获取授权码
https://pan.baidu.com/union/doc/al0rwqzzl
注意redirect_uri用oob

## 创建.env文件
```bash
APPID=xxxxxxxxx    # AppKey
APPNAME=xxxxxxx    # 应用名称
SECRET=xxxxxxx     # SecretKey
REDIS_HOST=xxx.xxx.xxx.xxx  # redis地址
REDIS_PORT=xxxx             # redis端口
```

## 创建云盘文件夹
在网盘下的`我的应用数据`文件夹创建一个和应用名称的同名文件夹

## 安装依赖
### python环境
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
### 安装redis
https://www.runoob.com/redis/redis-install.html

## 上传文件
文件会被上传到你的网盘的`我的应用数据/应用名称`文件夹下，每次文件上传不能超过2GB。
```bash
source venv/bin/activate
python upload.py /path/your_file
```
