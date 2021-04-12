FROM registry.thunisoft.com:5000/thunisoft/centos-xfce-vnc:1.0
USER 0
RUN yum install -y mesa-libGLU \
 && yum -y install libqt* \ 
 && yum -y install gcc \
 && yum -y install gcc-c++ \
 && yum -y install make \
 && yum -y install libXss* \
 && yum -y install wget \
 && yum -y install python36 \
 && yum clean all \
 && pip3 install python-multipart jinja2 aiofiles fastapi uvicorn apscheduler\
 && pip3 install pywpsrpc -i https://pypi.tuna.tsinghua.edu.cn/simple
RUN cd /home \
 && localedef -c -f UTF-8 -i zh_CN zh_CN.utf8 \
 && curl -O http://172.18.12.223:22062/solo/techgroup/0914/resource-x86.tar.gz \
 && tar zxvf resource-x86.tar.gz \ 
 && tar zxvf fonts-cn.tar.gz \
 && rm -rf /usr/share/fonts/* \
 && mv fonts/* /usr/share/fonts \
 && rpm -ivh /home/wps-office-11.1.0.9662-1.x86_64.rpm \
 && tar zxvf gcc-4.9.3.tar.gz \
#&& cd gcc-4.9.3/ \ 
#&& ./contrib/download_prerequisites \
#&& cd ../ \
 && mkdir build-gcc \
 && cd build-gcc \
 && ../gcc-4.9.3/configure --prefix=/usr --mandir=/usr/share/man --infodir=/usr/share/info --enable-bootstrap --enable-shared --enable-threads=posix --enable-checking=release --with-system-zlib --enable-__cxa_atexit --disable-libunwind-exceptions --enable-gnu-unique-object --enable-linker-build-id --with-linker-hash-style=gnu --enable-languages=c,c++ --enable-plugin --enable-initfini-array --disable-libgcj --enable-gnu-indirect-function --with-tune=generic --disable-multilib \
 && make -j8 \
 && make install \
 && rm -rf /home/*
RUN curl -O http://172.18.12.223:22062/solo/techgroup/0914/code29.tar.gz \ 
 && tar zxvf code29.tar.gz 
RUN  cd .config/ \ 
 && curl -O http://172.18.12.223:22062/solo/techgroup/0914/Kingsoft.tar.gz \
 && rm -rf Kingsoft/ \
 && tar zxvf Kingsoft.tar.gz \
 && rm -rf  Kingsoft.tar.gz
ENV TZ=Asia/Shanghai
ENV VNC_PW=6789@jkl
EXPOSE 5678
CMD uvicorn convert:app --host 0.0.0.0 --port 5678 --log-level error
