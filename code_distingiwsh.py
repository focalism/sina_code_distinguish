#!/usr/bin/env python
# -*- codeing:utf-8 -*-

import os
import time
import numpy
import requests
from lxml import etree
from bs4 import BeautifulSoup
from PIL import Image,ImageFilter
from urllib.request import urlretrieve

global session
session = requests.session()

def open_img(giffile):
    img = Image.open(giffile)
    img = img.convert('RGB')
    pixdata = img.load()
    return img,pixdata

def remove_line(giffile,openpath,savepath):
    (img,pixdata) = open_img(openpath+giffile)
    for x in range(img.size[0]):
        for y in range(img.size[1]):
            if pixdata[x,y] ==(4,2,4):
                pixdata[x,y] = (255,255,255)
    img.save(savepath+giffile,'gif')

def two_valued(giffile,openpath,savepath):
    (img, pixdata) = open_img(openpath+giffile)
    for y in range(img.size[1]):  # 二值化处理，这个阈值为R=95，G=95，B=95
        for x in range(img.size[0]):
            if pixdata[x, y][0] < 95 or pixdata[x, y][1] < 136 or pixdata[x, y][2] < 95:
                pixdata[x, y] = (0, 0, 0)
            else:
                pixdata[x, y] = (255, 255, 255)
    img.filter(ImageFilter.EDGE_ENHANCE_MORE)
    img.resize(((img.size[0])*2,(img.size[1])*2),Image.BILINEAR)
    img.save(savepath+giffile,'gif')

def getcoldocnum(giffile,openpath):
    (img,pixdata) = open_img(openpath+giffile)
    dot_num = numpy.zeros(img.size[0])
    for x in range(img.size[0]):
        for y in range(img.size[1]):
            if pixdata[x,y][0] == 0:
                black_dot = 1
            else:
                black_dot = 0
            dot_num[x] = dot_num[x]+black_dot
    return dot_num

def pic_cut(giffile,openpath,savepath,m):
    (img, pixdata) = open_img(openpath+giffile)
    doc_num = getcoldocnum(giffile,openpath)
    #print(doc_num)
    i = 4
    k = 0
    while(i):
        #print(i)
        if k+1>=100:
            break
        if (doc_num[k+1])**2-(doc_num[k])**2>=5:
            x1 = k
            for j in range(10,20):
                if x1+j+1>=100:
                    break
                if (doc_num[x1+j])**2<10 and (doc_num[x1+j+1])**2<10 :
                    x2 = x1+j
                    img.crop((x1, 0, x2, 20)).save(savepath+"%d_%d_old.gif" %(m,5-i))  # 适当的修改
                    k = x2
                    break
            for w in range(1,5):
                if (k+w+1)>99:
                    break
                if (doc_num[k + w]) ** 2 < 10 and (doc_num[k + w + 1]) ** 2 < 10:
                    #print(x1,0,k+w,20)
                    img.crop((x1, 0, k+w, 20)).save(savepath+"%d_%d_old.gif" %(m,5-i))
                    k = k+w
            i = i-1
        else:
            k = k+1
def createwordmodel():
    m=0
    dir = './pic/'
    path = './font1/'
    for f in os.listdir(dir):
        if f.endswith('gif'):
            remove_line(f,'./pic/','./font1/')
            #two_valued(f, './pic/', './font1/')

    for f in os.listdir(path):
        if f.endswith('gif'):
            two_valued(f, './font1/', './font1/')
            pic_cut(f,'./font1/','./model1/',m)
            m = m+1

def createmodeltxt():
    file = open('model1.txt', 'w+')
    for f in os.listdir('./model1/'):
        if f.endswith('gif'):
            file.write(f + '\n')
    file.close
#createwordmodel()
word = []
def getverticode():
    path = './word/'
    for check_pic in os.listdir(path):
        if check_pic.endswith('gif'):
            img1 = Image.open(path+check_pic)
            pixdata = img1.load()
            M = []
            for x in range(img1.size[0]):
                for y in range(img1.size[1]):
                    M.append(pixdata[x,y])

            dir = './model/'
            file = open('model.txt','r')
            lines = file.readlines()
            file_corr = dict()
            for f in os.listdir(dir):
                if f.endswith('gif'):
                    img = Image.open(dir+f)
                    pixdata1 = img.load()
                    N = []
                    for x in range(img.size[0]):
                        for y in range(img.size[1]):
                            N.append(pixdata1[x, y])
                    file_corr[f] = max(numpy.correlate(M,N,'full'))
            file_corr = sorted(file_corr.items(),key = lambda d:d[1],reverse=True)
            for line in lines:
                line = line.strip().split(' ')
                #print(line[0])
                if file_corr[0][0]==line[0]:
                    word.append(line[1])
                    print(line[0])
    word_code = (word[0]+word[1]+word[2]+word[3])
    file.close()
    print(word_code)
    return str(word_code)



#createmodeltxt()

def getvertcodepic():
    url_login = 'http://login.weibo.cn/login/'

    html = requests.get(url_login).content#解析网页
    soup = BeautifulSoup(html,'lxml')
    code_img = str(soup.find('img'))[24:-3]#获取验证码图片地址
    print(code_img)
    urlretrieve(code_img,'captcha.gif')
    #os.system('eog captcha.gif')#显示验证码
    remove_line('captcha.gif','./','./')
    two_valued('captcha.gif','./','./')
    pic_cut('captcha.gif','./','./word/',0)
    k = 0
    for f in os.listdir('./word/'):
        if f.endswith('gif'):
            k = k+1
    return k

def getverticode():
    word = []
    path = './word/'
    for check_pic in os.listdir(path):
        if check_pic.endswith('gif'):
            img1 = Image.open(path+check_pic)
            pixdata = img1.load()
            M = []
            for x in range(img1.size[0]):
                for y in range(img1.size[1]):
                    M.append(pixdata[x,y])

            dir = './model/'
            file = open('model.txt','r')
            lines = file.readlines()
            file_corr = dict()
            for f in os.listdir(dir):
                if f.endswith('gif'):
                    img = Image.open(dir+f)
                    pixdata1 = img.load()
                    N = []
                    for x in range(img.size[0]):
                        for y in range(img.size[1]):
                            N.append(pixdata1[x, y])
                    file_corr[f] = max(numpy.correlate(M,N,'full'))
            file_corr = sorted(file_corr.items(),key = lambda d:d[1],reverse=True)
            for line in lines:
                line = line.strip().split(' ')
                #print(line[0])
                if file_corr[0][0]==line[0]:
                    word.append(line[1])
                    print(line[0])
    word_code = (word[0]+word[1]+word[2]+word[3])
    file.close()
    print(word_code)
    return str(word_code)

def login():
    url_login = 'http://login.weibo.cn/login/'
    html = requests.get(url_login).content  # 解析网页
    soup = BeautifulSoup(html, 'lxml')
    selector = etree.HTML(html)
    code_img = str(soup.find('img'))[24:-3]  # 获取验证码图片地址

    print(code_img)
    urlretrieve(code_img, 'captcha.gif')
    remove_line('captcha.gif','./','./')
    two_valued('captcha.gif','./','./')
    pic_cut('captcha.gif','./','./word/',0)

    choice = input("请输入选择(1程序识别，2手动输入):")
    if choice == str(1):
        code = getverticode()
    else:
        os.system('eog captcha.gif')  # 显示验证码
        code = input('请输入验证码:')
    print(code)

    password = selector.xpath('//input[@type="password"]/@name')[0]  # 解析所要提交的表单内容
    vk = selector.xpath('//input[@name="vk"]/@value')[0]
    action = selector.xpath('//form[@method="post"]/@action')[0]
    capId = selector.xpath('//input[@name="capId"]/@value')[0]

    new_url = url_login + action
    data = {'mobile': '250682744@qq.com',  # 构造数据
            password: 'xzg.1990924',
            'code': code,
            'remember': 'on',
            'backURL': 'http://weibo.cn/search/?tf=5_012&vt=4',
            'backTitle': u'微博',
            'tryCount': '',
            'vk': vk,
            'capId': capId,
            'submit': u'登录'
            }
    resp = session.post(new_url, data=data)  # 提交
    url = 'http://weibo.cn/'
    html = session.get(url).content
    bsobj = BeautifulSoup(html, 'html.parser')

    thetime = bsobj.find_all("div", {"class": "b"})
    if thetime == []:
        print("log failed")
        pos = -1
    else:
        pos = 1
        print(thetime)
        print("log sucess")
        return  pos
if __name__ == '__main__':
    for i in range(3):
        pos = login()
        if(pos):
            break
        else:
            print(u'验证码输入错误，请重新输入：')
            time.sleep(10)


