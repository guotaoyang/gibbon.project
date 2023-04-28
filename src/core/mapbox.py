#-*- coding:utf-8 -*-


import os
import json

import System
from System.Net import WebClient  # 网络数据下载


class Mapbox(object):
    def __init__(self, token=None):
        self._token = token
        self.client = WebClient(Encoding=System.Text.Encoding.GetEncoding("UTF-8"))

    @property
    def token(self):
        if self._token is None:
            # 打开根目录下的 data\key.json 文件，获取 Mapbox 的 token：
            CORE_PATH = os.path.dirname(__file__)
            SRC_PATH = os.path.dirname(CORE_PATH)
            ROOT_PATH = os.path.dirname(SRC_PATH)

            file_path = os.path.join(ROOT_PATH, "data", "key.json")

            with open(file_path, 'r') as f:
                data = json.loads(f.read())
                self._token = data['mapbox']

        return self._token

    def download_image(self, xyz, style_index, folder):
        """
        """
        # 获得当前格式化的文件名：
        urls = [
            "https://api.mapbox.com/v4/mapbox.terrain-rgb",
            "https://api.mapbox.com/v4/mapbox.satellite"
        ]

        style = 'terrian' if style_index == 0 else 'satellite'
        file_name = "%s-%d-%d-%d.png"%(style, xyz.x, xyz.y, xyz.z)
        file_path = os.path.join(folder, file_name)

        # 如果这个文件已经下载过了，直接返回这个文件 Bitmap：
        if os.path.exists(file_path):
            return file_path

        # 获取标准的图片申请链接：
        url = urls[style_index]
        url += "/{}/{}/{}@2x.png?access_token={}".format(xyz.z, xyz.x, xyz.y, self.token)

        # self.client.DownloadFlie(url, file_path)
        data = self.client.DownloadData(url)

        # 保存文件：
        with open(file_path, 'wb') as f:
            f.write(data)

        return file_path


if __name__ == '__main__':
    file_path = os.path.join(os.path.dirname(__file__), "..", "data", "key.json")
    print(file_path)
