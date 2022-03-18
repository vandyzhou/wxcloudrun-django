# 写在最前面：强烈建议先阅读官方教程[Dockerfile最佳实践]（https://docs.docker.com/develop/develop-images/dockerfile_best-practices/）
# 选择构建用基础镜像（选择原则：在包含所有用到的依赖前提下尽可能提及小）。如需更换，请到[dockerhub官方仓库](https://hub.docker.com/_/python?tab=tags)自行选择后替换。

# 选择基础镜像
FROM zenika/alpine-chrome:latest

# 选用国内镜像源以提高下载速度
RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.tencent.com/g' /apk/repositories \
&& apk add --update rpm unzip \
&& apk add --update python3-dev py3-pip \
&& apk add --update libxml2-dev libxslt-dev libffi-dev gcc musl-dev libgcc openssl-dev curl \
&& apk add jpeg-dev zlib-dev freetype-dev lcms2-dev openjpeg-dev tiff-dev tk-dev tcl-dev

# 安装chrome
#RUN wget --no-cache https://dl.google.com/linux/chrome/rpm/stable/x86_64/google-chrome-stable-99.0.4844.51-1.x86_64.rpm && \
#rpm -ivh google-chrome-stable-99.0.4844.51-1.x86_64.rpm

# 安装chromedriver
#RUN wget https://registry.npmmirror.com/-/binary/chromedriver/99.0.4844.51/chromedriver_linux64.zip && \
#unzip -d /usr/bin chromedriver_linux64.zip

# 拷贝当前项目到/app目录下
COPY . /app

# 设定当前的工作目录
WORKDIR /app

# 安装依赖到指定的/install文件夹
# 选用国内镜像源以提高下载速度
RUN pip config set global.index-url http://mirrors.aliyun.com/pypi/simple/ \
&& pip config set global.trusted-host mirrors.aliyun.com \
&& pip install --upgrade pip \
&& pip install --upgrade Pillow \
# pip install scipy 等数学包失败，可使用 apk add py3-scipy 进行， 参考安装 https://pkgs.alpinelinux.org/packages?name=py3-scipy&branch=v3.13
&& pip install --user -r requirements.txt

# 设定对外端口
EXPOSE 80

# 设定启动命令
CMD ["python3", "manage.py", "runserver", "0.0.0.0:80"]
