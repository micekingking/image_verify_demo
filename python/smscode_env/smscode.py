# 参考 https://www.liaoxuefeng.com/wiki/0014316089557264a6b348958f449949df42a6d3a2e542c000/0014320027235877860c87af5544f25a8deeb55141d60c5000
# python 解析gif图片验证码, 合并为一张图片,并且降噪
# 1. 逐帧保存png图片
# 2. 合并png图片为一张图片
# 3. 去噪点

import PIL
from PIL import Image
import os
import numpy
import os
import random
from PIL import ImageDraw
import re



# 1. 分割图片到指定文件夹
# return 图片切割后的最后一张图片的全路径
def splitImage(targetFileName):
    # 预先创建切割后保存图片的文件夹
    targetDir = os.getcwd() + "/imgsCodeSplit/"
    if os.path.exists(targetDir):
        pass
    else:
        os.mkdir(targetDir)
        pass

    gifFileName = targetFileName
    #使用Image模块的open()方法打开gif动态图像时，默认是第一帧
    im = Image.open(gifFileName)
    pngBaseName = gifFileName[:-4]
    #创建存放每帧图片的文件夹
    # os.mkdir(pngBaseName)

    result = ""
    try:
        while True:
            #保存当前帧图片
            current = im.tell()
            result = targetDir + pngBaseName + '_' + str(current)+'.png'
            im.save(result)
            #获取下一帧图片
            im.seek(current + 1)
    except EOFError:
        pass

    print ("图片切割完毕:" + result)

    return result



# name: transfer
# todo: 将照片转为一样的大小
def transfer(img_path, dst_width,dst_height):
    im = Image.open(img_path)
    if im.mode != "RGBA":
        im = im.convert("RGBA")
    s_w,s_h = im.size
    if s_w < s_h:
        im = im.rotate(90)

    #if dst_width*0.1/s_w > dst_height*0.1/s_h:
    #    ratio = dst_width*0.1/s_w
    #else:
    #    ratio = dst_height*0.1/s_h
    resized_img = im.resize((dst_width, dst_height), Image.ANTIALIAS)
    resized_img = resized_img.crop((0,0,dst_width,dst_height))

    return resized_img



# name: createNevImgMerge
# param 切割后的最后一张图片的全路径
# return: 创建一张新的照片并保存新图片的全路径
def createNevImgMerge(lastSplitImgFullPathName):
    str(lastSplitImgFullPathName)
    (width, height) = Image.open(lastSplitImgFullPathName).size

    # 前缀
    baseImgPathPrefix = lastSplitImgFullPathName[0:lastSplitImgFullPathName.rfind("_") + 1]
    # 后缀
    baseImgPathSuffix = lastSplitImgFullPathName[lastSplitImgFullPathName.rfind("."):]
    # 分割后的最大图片编号
    splitImgCountMaxIndex = lastSplitImgFullPathName[lastSplitImgFullPathName.rfind("_") + 1:lastSplitImgFullPathName.rfind(".")]
    #print (baseImgPathPrefix + " -- " + splitImgCountMaxIndex + "--" + baseImgPathSuffix)

    # 编号默认是从0开始计算,因此此处需要+1
    for i in range(int(splitImgCountMaxIndex) + 1):
        imgFullName = baseImgPathPrefix + str(i) + baseImgPathSuffix
        if i == 0:
            I = numpy.array(transfer(imgFullName, width, height)) * 1.0
        else:
            res = I[0:height, 0:width] * numpy.array(transfer(imgFullName, width, height)) / 255
            I[0:height, 0:width] = res

    # 保存新的图片
    img = Image.fromarray(I.astype(numpy.uint8))
    img = img.point(lambda i : i * 1.5)

    imgMergedName = baseImgPathPrefix[:-1] + baseImgPathSuffix
    img.save(imgMergedName)
    print ("图片合并完毕:" + imgMergedName)

    return imgMergedName




# clearImageWithLineClear
# param: 待处理的图片全路径
# todo: 二值化去噪点,同时清除无用的噪线
# 二值化copy自: http://www.360doc.com/content/12/1006/21/9369336_239836993.shtml
def clearImageWithLineClear(imageFullFilePathName):
    img = Image.open(imageFullFilePathName)
    img = img.convert("RGBA")

    pixdata = img.load()

    # 二值化
    for y in range(img.size[1]):
        for x in range(img.size[0]):
            if pixdata[x, y][0] < 90:
                pixdata[x, y] = (0, 0, 0, 255)

    for y in range(img.size[1]):
        for x in range(img.size[0]):
            if pixdata[x, y][1] < 136:
                pixdata[x, y] = (0, 0, 0, 255)

    for y in range(img.size[1]):
        for x in range(img.size[0]):
            if pixdata[x, y][2] > 0:
                pixdata[x, y] = (255, 255, 255, 0)
    
    # 判断长度是否小于某个阀值,是否需要重置
    # 左右为空,删除
    rangeFlag = 150
    len_x = img.size[0]
    len_y = img.size[1]
    for y in range(len_y):
        for x in range(len_x):
            if x == 0 or x == len_x - 1:
                pixdata[x, y] = (0, 0, 0, 0)
                continue
            if pixdata[x, y][0] < rangeFlag and pixdata[x + 1, y][0] > rangeFlag and pixdata[x - 1, y][0] > rangeFlag:
                pixdata[x, y] = (0, 0, 0, 0)

    # 上下为空,删除
    len_x = img.size[0]
    len_y = img.size[1]
    for x in range(len_x):
        for y in range(len_y):
            if y == 0 or y == len_y - 1:
                pixdata[x, y] = (0, 0, 0, 0)
                continue
            if pixdata[x, y][0] < rangeFlag and pixdata[x, y + 1][0] > rangeFlag and pixdata[x, y - 1][0] > rangeFlag:
                pixdata[x, y] = (0, 0, 0, 0)

    # 保存处理后的图片
    img.save(imageFullFilePathName + ".png")
    print ("图片处理完毕:" + imageFullFilePathName)


# 开始调用方法
imgFullFilePath = splitImage("ms3mdx.gif")
imgFullFilePath = createNevImgMerge(imgFullFilePath)
clearImageWithLineClear(imgFullFilePath)