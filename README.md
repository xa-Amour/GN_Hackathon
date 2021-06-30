# GN Hackathon
 A GN project in Hackathon and summarized for learning.


## About
Google's GN + Ninja is definitely the best C++ build system out there. This Demo provides automated scanning tools, as well as some very useful build templates for integrating code into the GN.


## Organization structure
```
├── README.md 
├── build  # Compile output directory
│   └── mac
│       └── x64
├── build_system  # Core building code
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
├── demo  # Simple demo(C++/C)
│   ├── BUILD.gn
│   ├── README.md
│   ├── hello.cc
│   ├── hello_shared.cc
│   ├── hello_shared.h
│   ├── hello_static.cc
│   └── hello_static.h
```
## How to use
```bash
# Take the Mac platform for example
./build_system/hclient gen mac x64 release
./build_system/hclient build mac x64 release
# The build product hello can be found in the build/ MAC /x64 directory

# Execute
cd ./build/mac/x64/hello && ./hello
```
