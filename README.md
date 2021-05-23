# GN Hackathon#
### A GN project in Hackathon and summarized for learning###


### Hot to integration ###
Google 的GN + ninja绝对是最棒的C++构建系统，没有之一。这个 Demo 提供了自动化扫描工具，以及一些非常有用的构建模版来将代码集成到gn中。


### 目录结构 ###
```
├── README.md # 说明文件
├── build # 编译输出目录
│   └── mac
│       └── x64
├── build_system # 构建核心代码
│   ├── hclient
│   ├── hclient.bat
│   ├── buildcommands.py
│   ├── gn
│   │   ├── bin
│   │   ├── build
│   │   ├── build_overrides
│   │   ├── buildtools
│   │   ├── testing
│   │   └── tools
│   ├── profile
│   │   └── default.conf
│   └── utils.py
├── demo # 简单的demo
│   ├── BUILD.gn
│   ├── README.md
│   ├── hello.cc
│   ├── hello_shared.cc
│   ├── hello_shared.h
│   ├── hello_static.cc
│   └── hello_static.h
```
### How to use ###
```bash
# 以Mac平台为例
./build_system/hclient gen mac x64 release
./build_system/hclient build mac x64 release
# 执行完以后既可在build/mac/x64 目录中找到编译产物hello

# 执行
cd ./build/mac/x64/hello && ./hello
```