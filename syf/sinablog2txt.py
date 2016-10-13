# -*- coding: utf-8 -*-
'''
@author: shen
'''
import urllib2
import zlib
from bs4 import BeautifulSoup
import os
import codecs
import sys 
import re
import time
reload(sys) 
sys.setdefaultencoding('utf-8')

class SinaBlog:
    def __getHtml(self, url, referer=None):
        '''获取指定地址的html内容 .'''
        
        request = urllib2.Request(url)

        request.add_header('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8')
        request.add_header('Accept-Encoding', 'gzip, deflate, sdch')
        request.add_header('Accept-Language', 'zh-CN,zh;q=0.8,en;q=0.6')
        request.add_header('Cache-Control', 'max-age=0')
        request.add_header('Connection', 'keep-alive')
        request.add_header('Host', 'blog.sina.com.cn')
        request.add_header('Upgrade-Insecure-Requests', '1')
#         request.add_header('Referer', referer)
        request.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.97 Safari/537.36')
        
        # 尝试5次，如果每次都是timeout，打印提示信息，返回none 
        maxNum = 5
        for i in range(maxNum):
            try:    
                response = urllib2.urlopen(url=request, timeout=15)
                time.sleep(0.5)
                break
            except:
                pass
            
            if i < maxNum - 1:
                continue
            else:
                print 'URLError: <urlopen error timed out> All times is failed '
                return None
        html = response.read()
        gzipped = response.headers.get('Content-Encoding')
        if gzipped:
            html = zlib.decompress(html, 16 + zlib.MAX_WBITS)

#         print html
        return html

    def paraserBlog(self, url):
        self.__getAllBlogs(url)
        
    def __getAllBlogs(self, url):
        '''
        获得给定博客地址的所有目录的链接
        '''
        # 博主名称         
        blogOwner = url.split('/')[3]
        print blogOwner
        
        # 保存的文件夹名称         
        storePath = 'd:\\SinaBlog\\' + blogOwner 
        if not os.path.exists(storePath):
            os.makedirs(storePath)
        
        html = self.__getHtml(url)
        soup = BeautifulSoup(html, "html5lib")
        
        # 获得"博文目录"的url         
        for s in soup.find_all('a', text='博文目录'):
            realBlogContentsURL = s.get('href')
         
        html = self.__getHtml(realBlogContentsURL)
        soup = BeautifulSoup(html, "html5lib")

        # 获得所有目录的url         
        for div in soup.find_all(attrs={'class', "menuCell_main"}):
            # 目录名称             
            contentName = div.contents[0].contents[0].contents[0].encode('utf8')
            print contentName
            
            if div.contents[0].a:
                # 目录的url                 
                contentUrl = div.contents[0].a.get('href')
                print div.contents[0].a.get('href')
                self.getBlogsOfContents(storePath, contentUrl, contentName)
                 
    def getBlogsOfContents(self, storePath, url, contentName):
        '''
        获得给定博客具体目录的所有文章
        '''
#         之所以加这样一句，是因为如果文件名包含中文路径，导致乱码
        fileName = unicode(contentName, "utf8")
        f = codecs.open(storePath + '\\' + fileName + '.txt', 'w+', encoding='utf8')
        
        nextPage = True
        blogURLList = []
        while nextPage:
            html = self.__getHtml(url)
            soup = BeautifulSoup(html, "html5lib")
            
            # 获取博客文章的url
            for div in soup.find_all(attrs={'class', "articleCell SG_j_linedot1"}):
                blogURL = div.contents[1].a.get('href')
                print blogURL
                blogURLList.append(blogURL)
            
            # 获得下一页的url             
            nextPage = soup.find(attrs={'class', 'SG_pgnext'})
            if nextPage:
                url = nextPage.a.get('href')
                print url
        
        # 倒序，时间早的放前面
        blogURLList.reverse()       
        
        for bUrl in blogURLList:
            blogTitle, blogDate, blogArticalContent = self.getArticle(bUrl)
            f.write(blogTitle + '\r\n')
            f.write(blogDate + '\r\n')
            f.write(blogArticalContent.strip() + '\r\n')
            f.write('\r\n')
            
        if not f.closed:
            f.close()
             
    def getArticle(self, url):
        '''
        获取文章的具体内容
        '''
        html = self.__getHtml(url)
        soup = BeautifulSoup(html, "html5lib")
        blogTitle = soup.find(attrs={'class', 'titName SG_txta'}).get_text()
        blogDate = soup.find(attrs={'class', 'time SG_txtc'}).get_text()
        artical = ''
        try:
            artical = soup.find(attrs={'class', "articalContent"})
            blogArticalContent = re.sub('\s+', ' ', artical.get_text())
            
        except:
            blogArticalContent = 'Exception: Cause some reasons, do archive articalContent,url is ' + url
        
        print blogTitle, blogDate
        
        return blogTitle, blogDate, blogArticalContent
        
if __name__ == '__main__':
    a = SinaBlog()
    url = r'http://blog.sina.com.cn/chzhshch'
    url2 = r'http://blog.sina.com.cn/s/articlelist_1070473965_0_1.html'
#     a.paraserBlog(url)
    a.getBlogsOfContents(storePath='d:\\SinaBlog\\chzhshch', url='http://blog.sina.com.cn/s/articlelist_1215172700_2_1.html', contentName='那一夜，他的体液喷了我一身')
