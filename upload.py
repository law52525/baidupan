import os
import argparse
import logging
from dotenv import load_dotenv
from logging.handlers import TimedRotatingFileHandler
from redis_manager import RedisManager
from pan_helper import BaiDuPanHelper


if __name__ == "__main__":
    load_dotenv()

    # 配置 logger
    logger = logging.getLogger("ReportLogger")
    logger.setLevel(logging.INFO)

    # 创建一个TimedRotatingFileHandler并设置level为info
    current_dir_path = os.path.dirname(os.path.realpath(__file__))
    # handler = TimedRotatingFileHandler(os.path.join(current_dir_path, 'logs', 'log.txt'), when='midnight', interval=1, backupCount=30)
    if not os.path.exists(os.path.join(current_dir_path, 'logs')):
        os.mkdir(os.path.join(current_dir_path, 'logs'))
    handler = TimedRotatingFileHandler(os.path.join(current_dir_path, 'logs', 'log.txt'), when='midnight', interval=1, backupCount=30)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    RedisManager.init_config(redis_host=os.getenv("REDIS_HOST"), redis_port=os.getenv("REDIS_PORT"), password=None)

    pan = BaiDuPanHelper(app_id=os.getenv("APPID"), secret=os.getenv("SECRET"), app_name=os.getenv("APPNAME"), logger=logger)
    # 创建参数解析对象
    parser = argparse.ArgumentParser(description="处理命令行文件路径参数")

    # 添加我们想要解析的参数，这里是路径参数
    parser.add_argument("filepath", help="文件路径参数")

    # 使用我们的参数解析对象解析参数
    args = parser.parse_args()

    pan.upload_file(file_path=args.filepath)
