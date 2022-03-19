#!/bin/bash
echo ${1}
cp ${1} ~/Documents/code/myblog/source/_posts/转债/
cd ~/Documents/code/myblog
hexo clean
hexo g
hexo d