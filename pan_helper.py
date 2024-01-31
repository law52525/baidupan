import requests
import logging
import json
import os
from redis_manager import RedisManager


class BaiDuPanHelper:
    """
    auth_code 10分钟过期，一次性的
    access_token  30天过期
    refresh_token 10年过期，一次性的
    """

    def __init__(self, app_id, secret, app_name, auth_code=None, logger=logging):
        self.appid = app_id
        self.secret = secret
        self.app_name = app_name
        self.logger = logger
        self.redis_client = RedisManager.get_instance().r
        self.access_token = self.get_token(auth_code)
    
    def get_baidupan_access_token_redis_key(self):
        return "baidupan_access_token_%s" % self.appid
    
    def get_baidupan_refresh_token_redis_key(self):
        return "baidupan_access_refresh_token_%s" % self.appid

    def get_access_token(self):
        access_token = self.redis_client.get(self.get_baidupan_access_token_redis_key())
        if access_token:
            return access_token
        uri = "https://openapi.baidu.com/oauth/2.0/token"
        refresh_token = self.redis_client.get(self.get_baidupan_refresh_token_redis_key())
        params = {
            "grant_type": "refresh_token",
            "client_id": self.appid,
            "client_secret": self.secret,
            "refresh_token": refresh_token,
        }

        response = requests.get(uri, params=params)
        res = response.json()
        if not res.get("access_token"):
            self.logger.error(res)
            raise Exception("Access_token refresh failed.")
        else:
            access_token = res['access_token']
            expires_in = res['expires_in']
            refresh_token = res['refresh_token']
            self.redis_client.setex(self.get_baidupan_access_token_redis_key(), expires_in - 60, access_token)
            self.redis_client.set(self.get_baidupan_refresh_token_redis_key(), refresh_token)
        return access_token
    
    def make_request(self, url, method, **kwargs):
        access_token = self.get_access_token()
        params = {
            "access_token": access_token
        }
        if kwargs.get("params"):
            params.update(kwargs.get("params"))
        self.logger.info("request url: %s with access_token: %s" % (url, access_token))
        if method == "GET":
            response = requests.get(url, params=params)
        else:
            response = requests.post(url, params=params, json=kwargs.get("json"), data=kwargs.get("data"), files=kwargs.get("files"))
        res = response.json()
        self.logger.info("request url: %s response: %s " % (url, json.dumps(res, ensure_ascii=False)))
        return res
    
    def get_token(self, auth_code):
        if auth_code is None:
            return self.get_access_token()
        params = {
            "client_id": self.appid,
            "client_secret": self.secret,
            "grant_type": "authorization_code",
            "code": auth_code,
            "redirect_uri": "oob"
        }
        uri = 'https://openapi.baidu.com/oauth/2.0/token'
        
        response = requests.get(uri, params=params)
        res = response.json()
        if not res.get("access_token"):
            self.logger.error(res)
            raise Exception("Access_token refresh failed.")
        else:
            access_token = res['access_token']
            expires_in = res['expires_in']
            refresh_token = res['refresh_token']
            self.redis_client.setex(self.get_baidupan_access_token_redis_key(), expires_in - 60, access_token)
            self.redis_client.set(self.get_baidupan_refresh_token_redis_key(), refresh_token)
        return access_token
    
    def get_user_info(self):
        """ 获取用户信息 """
        uri = "https://pan.baidu.com/rest/2.0/xpan/nas"
        return self.make_request(uri, "GET", params={"method": "uinfo"})
    
    def upload_file(self, file_path):
        """ 单步上传, 上传文件大小上限为2GB """
        uri = "https://d.pcs.baidu.com/rest/2.0/pcs/file"
        params = {
            "method": "upload",
            "path": f"/apps/{self.app_name}/{os.path.basename(file_path)}",
            "ondup": "overwrite"
        }
        files = {}
        with open(file_path, 'rb') as f:
            files[file_path] = f
            return self.make_request(uri, "POST", files=files, params=params)


if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    from logging.handlers import TimedRotatingFileHandler

    load_dotenv()
    RedisManager.init_config(redis_host=os.getenv("REDIS_HOST"), redis_port=os.getenv("REDIS_PORT"), password=None)

    # 配置 logger
    logger = logging.getLogger("ReportLogger")
    logger.setLevel(logging.INFO)

    # 创建一个TimedRotatingFileHandler并设置level为info
    current_dir_path = os.path.dirname(os.path.realpath(__file__))
    if not os.path.exists(os.path.join(current_dir_path, 'logs')):
        os.mkdir(os.path.join(current_dir_path, 'logs'))
    handler = TimedRotatingFileHandler(os.path.join(current_dir_path, 'logs', 'log.txt'), when='midnight', interval=1, backupCount=30)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    pan = BaiDuPanHelper(app_id=os.getenv("APPID"), secret=os.getenv("SECRET"), app_name=os.getenv("APPNAME"), logger=logger)
    print(pan.get_user_info())
