# -*- coding: utf-8 -*-
"""例句、图片、音频获取模块 - 有道词典API"""

import requests
import logging
import re
from typing import Dict, Optional, Tuple


class ExampleFetcher:
    """从有道词典获取例句、下载图片和音频"""
    
    def __init__(self):
        self.youdao_api = "https://dict.youdao.com/jsonapi"
        self.logger = logging.getLogger(__name__)
    
    def fetch_word_data(self, word: str) -> Dict:
        """
        获取单词的完整数据：例句、图片、音频（转为base64 data URI）
        
        Args:
            word: 单词
            
        Returns:
            包含example_en, example_zh, image_base64, audio_base64的字典
        """
        result = {
            'example_en': None,
            'example_zh': None,
            'image_base64': None,  # data:image/jpeg;base64,xxx
            'audio_base64': None   # data:audio/mpeg;base64,xxx
        }
        
        # 1. 获取例句
        example = self.fetch_example(word)
        if example:
            result.update(example)
        
        # 2. 下载图片并转为base64
        image_base64 = self.download_image_as_base64(word)
        if image_base64:
            result['image_base64'] = image_base64
        
        # 3. 下载音频并转为base64
        audio_base64 = self.download_audio_as_base64(word)
        if audio_base64:
            result['audio_base64'] = audio_base64
        
        return result
    
    def fetch_example(self, word: str) -> Optional[Dict[str, str]]:
        """
        从有道词典获取例句
        
        Args:
            word: 单词
            
        Returns:
            包含example_en和example_zh的字典，失败返回None
        """
        try:
            params = {'q': word}
            response = requests.get(self.youdao_api, params=params, timeout=5)
            
            if response.status_code != 200:
                self.logger.warning(f"例句API请求失败: {word}, status={response.status_code}")
                return None
            
            data = response.json()
            
            # 尝试从有道返回数据中提取例句
            # 有道API返回格式：blng_sents_part 包含双语例句
            blng_sents = data.get('blng_sents_part', {}).get('sentence-pair', [])
            
            if blng_sents and len(blng_sents) > 0:
                first_example = blng_sents[0]
                example_en = first_example.get('sentence', '')
                example_zh = first_example.get('sentence-translation', '')
                
                # 清理HTML标签
                example_en = re.sub(r'<[^>]+>', '', example_en).strip()
                example_zh = re.sub(r'<[^>]+>', '', example_zh).strip()
                
                if example_en and example_zh:
                    self.logger.debug(f"获取例句成功: {word}")
                    return {
                        'example_en': example_en,
                        'example_zh': example_zh
                    }
            
            # 备用：从 web_trans 获取网络释义作为例句
            web_trans = data.get('web_trans', {}).get('web-translation', [])
            if web_trans and len(web_trans) > 0:
                first_trans = web_trans[0]
                key = first_trans.get('key', '')
                trans = first_trans.get('trans', [])
                if key and trans:
                    trans_text = trans[0].get('value', '') if trans else ''
                    if trans_text:
                        self.logger.debug(f"使用网络释义: {word}")
                        return {
                            'example_en': key,
                            'example_zh': trans_text
                        }
            
            self.logger.warning(f"未找到例句: {word}")
            return None
            
        except requests.Timeout:
            self.logger.warning(f"例句API请求超时: {word}")
            return None
        except Exception as e:
            self.logger.error(f"获取例句失败: {word}, error={str(e)}")
            return None
    
    def download_audio_as_base64(self, word: str) -> Optional[str]:
        """
        下载有道词典发音并转为base64 data URI
        
        Args:
            word: 单词
            
        Returns:
            data URI 字符串 (data:audio/mpeg;base64,xxx) 或 None
        """
        try:
            import base64
            
            audio_url = f"https://dict.youdao.com/dictvoice?audio={word}&type=1"
            response = requests.get(audio_url, timeout=5)
            
            if response.status_code != 200:
                self.logger.warning(f"音频下载失败: {word}, status={response.status_code}")
                return None
            
            audio_data = response.content
            mime_type = response.headers.get('Content-Type', 'audio/mpeg')
            
            if len(audio_data) > 0:
                # 转为base64
                audio_base64 = base64.b64encode(audio_data).decode('utf-8')
                data_uri = f"data:{mime_type};base64,{audio_base64}"
                
                self.logger.debug(f"音频下载成功: {word}, size={len(audio_data)} bytes, base64={len(audio_base64)}")
                return data_uri
            
            return None
            
        except requests.Timeout:
            self.logger.warning(f"音频下载超时: {word}")
            return None
        except Exception as e:
            self.logger.error(f"音频下载失败: {word}, error={str(e)}")
            return None
    
    def download_image_as_base64(self, word: str) -> Optional[str]:
        """
        下载单词配图并转为base64 data URI
        优先使用必应图片搜索获取与单词相关的图片
        
        Args:
            word: 单词
            
        Returns:
            data URI 字符串 (data:image/jpeg;base64,xxx) 或 None
        """
        import base64
        import json
        
        # 方案1：尝试从必应图片搜索获取第一张图片
        try:
            # 必应图片搜索API（无需key，通过HTML解析）
            bing_search_url = f"https://www.bing.com/images/search?q={word}&first=1"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(bing_search_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                # 从HTML中提取图片URL（必应会在页面中嵌入JSON数据）
                import re
                # 查找图片URL模式
                pattern = r'"murl":"([^"]+)"'
                matches = re.findall(pattern, response.text)
                
                if matches:
                    # 尝试下载前3张图片（有些可能失效）
                    for img_url in matches[:3]:
                        try:
                            img_url = img_url.replace('\\u0026', '&')
                            img_response = requests.get(img_url, timeout=8, headers=headers)
                            
                            if img_response.status_code == 200:
                                image_data = img_response.content
                                mime_type = img_response.headers.get('Content-Type', 'image/jpeg')
                                
                                if len(image_data) > 1000 and mime_type.startswith('image/'):
                                    image_base64 = base64.b64encode(image_data).decode('utf-8')
                                    data_uri = f"data:{mime_type};base64,{image_base64}"
                                    self.logger.debug(f"必应图片下载成功: {word}, size={len(image_data)} bytes")
                                    return data_uri
                        except:
                            continue
        except Exception as e:
            self.logger.debug(f"必应图片搜索失败: {word}, error={str(e)}")
        
        # 方案2：使用Pixabay API（免费，无需注册）
        try:
            pixabay_url = f"https://pixabay.com/api/?key=9656065-a4094594c34f9ac14c7fc4c39&q={word}&image_type=photo&per_page=3"
            response = requests.get(pixabay_url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                hits = data.get('hits', [])
                
                if hits:
                    # 获取第一张图片的中等尺寸
                    img_url = hits[0].get('webformatURL') or hits[0].get('previewURL')
                    if img_url:
                        img_response = requests.get(img_url, timeout=8)
                        if img_response.status_code == 200:
                            image_data = img_response.content
                            mime_type = img_response.headers.get('Content-Type', 'image/jpeg')
                            
                            if len(image_data) > 1000:
                                image_base64 = base64.b64encode(image_data).decode('utf-8')
                                data_uri = f"data:{mime_type};base64,{image_base64}"
                                self.logger.debug(f"Pixabay图片下载成功: {word}, size={len(image_data)} bytes")
                                return data_uri
        except Exception as e:
            self.logger.debug(f"Pixabay图片搜索失败: {word}, error={str(e)}")
        
        # 方案3：使用LoremFlickr（带关键词的随机图片）
        try:
            image_url = f"https://loremflickr.com/400/300/{word}"
            response = requests.get(image_url, timeout=10, allow_redirects=True)
            
            if response.status_code == 200:
                image_data = response.content
                mime_type = response.headers.get('Content-Type', 'image/jpeg')
                
                if len(image_data) > 1000:
                    image_base64 = base64.b64encode(image_data).decode('utf-8')
                    data_uri = f"data:{mime_type};base64,{image_base64}"
                    self.logger.debug(f"LoremFlickr图片下载成功: {word}, size={len(image_data)} bytes")
                    return data_uri
        except Exception as e:
            self.logger.debug(f"LoremFlickr失败: {word}, error={str(e)}")
        
        self.logger.warning(f"所有图片源都失败: {word}")
        return None
        return None
