#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import os
import sys
import json
import shlex
import subprocess
import uuid
import utils as command
sys.path.append(os.path.join(
    os.path.dirname(os.path.realpath(__file__)), ".."))

script_path = os.path.dirname(os.path.realpath(__file__))
root_path = os.path.join(script_path, "..")
root_path = os.path.abspath(root_path)
demo_path = os.path.join(script_path, "..", "demo")
demo_path = os.path.abspath(demo_path)
gn_bin_path = os.path.join(script_path, "gn", "bin")
ninja_bin_path = os.path.join(script_path, "gn", "bin")
ccache_bin_path = os.path.join(script_path, "gn", "bin")
if command.IS_WINDOWS:
    gn_bin_path = os.path.join(gn_bin_path, "win", "gn.exe")
    ninja_bin_path = os.path.join(ninja_bin_path, "win", "ninja.exe")
    ccache_bin_path = os.path.join(ccache_bin_path, "win", "ccache.exe")
elif command.IS_MAC:
    gn_bin_path = os.path.join(gn_bin_path, "mac", "gn")
    ninja_bin_path = os.path.join(ninja_bin_path, "mac", "ninja")
    ccache_bin_path = os.path.join(ccache_bin_path, "mac", "ccache")
else:
    gn_bin_path = os.path.join(gn_bin_path, "linux", "gn")
    ninja_bin_path = os.path.join(ninja_bin_path, "linux", "ninja")
    ccache_bin_path = os.path.join(ccache_bin_path, "linux", "ccache")
gn_bin_path = os.path.abspath(gn_bin_path).replace("\\", "/")
ninja_bin_path = os.path.abspath(ninja_bin_path).replace("\\", "/")
ccache_bin_path = os.path.abspath(ccache_bin_path).replace("\\", "/")

target_os = ""
target_cpu = ""
profile = ""
is_debug = "false"
build_dir = ""
build_command = ""
build_target = ""
generator = "default"
android_build_tools_ver = ""
has_vs2019 = False
has_vs2017 = False
enable_sanitizer = False
enable_fastlink = False
verbos_build = False
enable_ccache = False
ccache_in_server = False
ccache_command = ""
enable_sauron = "true"
enable_fuzzer = "false"
sysroot = ""
gn_args_config = {}

valid_build_commands = ["prepare", "gen", "build", "rebuild", "clean", "info"]
valid_target_os = ["win", "mac", "linux", "ios", "android"]
valid_target_cpu = {
    "win": ["x86", "x64"],
    "mac": ["x64"],
    "linux": ["x64", "arm", "arm64"],
    "ios": ["x86", "x64", "arm", "arm64"],
    "android": ["x86", "x64", "arm", "arm64"],
}
valid_build_config = ["debug", "release"]
ccache_locations = ["ip_address:/mnt/cache"]

PREDEFINED_GN_ARGS = {
    "mac": [
        'target_os = "mac"',
        'is_component_build = false',
        'clang_base_path = ""',
        'clang_use_chrome_plugins = false',
        'use_xcode_clang = false',
        'mac_deployment_target = "10.10"'
    ],
    "linux": [
        'target_os = "linux"',
        'is_component_build = false',
        'clang_base_path = "/usr"',
        'clang_use_chrome_plugins = false',
        'use_custom_libcxx = false',
        'use_gold = false',
    ],
    "ios": [
        'target_os = "ios"',
        'is_component_build = false',
        'clang_base_path = ""',
        'clang_use_chrome_plugins = false',
        'use_xcode_clang = true',
        'ios_deployment_target = "9.0"'
    ],
    "win": [
        'target_os = "win"',
        'is_component_build = false',
        'clang_base_path = ""',
        'clang_use_chrome_plugins = false',
        'feature_enable_chromium_module = true'
    ],
    "android": [
        'target_os = "android"',
        'is_component_build = false',
        'clang_use_chrome_plugins = false',
        'use_sysroot = false',
        'use_allocator_shim = false',
        'use_custom_libcxx = false',
        'clang_base_path = "{0}/toolchains/llvm/prebuilt/{1}-x86_64"'.format(os.environ.get("ANDROID_NDK", "").replace("\\", "/"),
                                                                             get_platform_name()),
        'android_ndk_root = "{}"'.format(
            os.environ.get("ANDROID_NDK", "").replace("\\", "/")),
        'android_sdk_root = "{}"'.format(
            os.environ.get("ANDROID_SDK", "").replace("\\", "/")),
        'lint_android_sdk_root = "{}"'.format(
            os.environ.get("ANDROID_SDK", ""))
    ]
}

SANITIZERS = {
    "win": {
        "x86": {
            "debug": [],
            "release": ["is_msvc_asan"]
        },
        "x64": {
            "debug": [],
            "release": []
        }
    },
    "linux": {
        "x64": {
            "debug": ["is_asan", "is_lsan", "use_cfi_cast"],
            "release": ["is_asan", "use_cfi_cast"]
        },
        "arm": {
            "debug": ["is_asan", "is_lsan", "use_cfi_cast"],
            "release": ["is_asan", "use_cfi_cast"]
        },
        "arm64": {
            "debug": ["is_asan", "is_lsan", "use_cfi_cast"],
            "release": ["is_asan", "use_cfi_cast"]
        }
    },
    "mac": {
        "x64": {
            "debug": ["is_asan"],
            "release": ["is_asan"]
        }
    },
    "android": {
        "x86": {
            "debug": ["is_asan"],
            "release": ["is_asan"]
        },
        "x64": {
            "debug": ["is_asan"],
            "release": ["is_asan"]
        },
        "arm": {
            "debug": ["is_asan"],
            "release": ["is_asan"]
        },
        "arm64": {
            "debug": ["is_asan"],
            "release": ["is_asan"]
        }
    },
    "ios": {
        "x86": {
            "debug": ["is_asan"],
            "release": ["is_asan"]
        },
        "x64": {
            "debug": ["is_asan"],
            "release": ["is_asan"]
        },
        "arm": {
            "debug": ["is_asan"],
            "release": ["is_asan"]
        },
        "arm64": {
            "debug": ["is_asan"],
            "release": ["is_asan"]
        }
    }
}

# trickies in windows:
# vs2017 will crash when build //base:base, vs2019 is fine
# so if no vs2019 is installed, we will use clang in windows, otherwise use vs2019
def use_clang():
    if target_os != "win":
        # in linux/mac/ios/android: we use clang
        return "true"

    if not has_vs2019:
        # if no vs2019 installed: use clang because vs2017 crashes in build
        return "true"

    if os.environ.get('GYP_MSVS_VERSION', None) != "2019":
        return "true"

    return "false"


def run_or_die(cmd, show_output=True):
    if command.run_cmd(cmd, show_output) != 0:
        print("CMD: {} fail".format(cmd))
        sys.exit(-1)


def run_anyway(cmd, show_output=True):
    command.run_cmd(cmd, show_output)


def get_local_ccache_location():
    if command.IS_WINDOWS:
        return ""
    mount_points = []
    try:
        output = subprocess.check_output("df", shell=True)
        mount_points = output.splitlines()
    except:
        return ""

    local_ccache_location = ""
    for mount_point in mount_points:
        items = mount_point.split()
        if len(items) < 2:
            continue
        filesystem = items[0].strip()
        mounted_on = items[-1].strip()
        if filesystem not in ccache_locations:
            continue
        local_ccache_location = mounted_on
        break
    return local_ccache_location

def prepare_ccache():
    global ccache_command
    ccache_command = ""
    if not enable_ccache:
        return

    if not ccache_in_server:
        local_ccache_location = get_local_ccache_location()
        if local_ccache_location != "":
            run_anyway("sudo umount {}".format(local_ccache_location))
        else:
            local_ccache_location = os.path.abspath(os.path.join(os.getenv("HOME"), ".ccache")).replace("\\", "/")
            run_anyway("sudo umount {}".format(local_ccache_location))
        ccache_command = ccache_bin_path
        return


    path_patten = os.path.relpath(root_path, os.getcwd())
    if path_patten != "../sdk_folder" and not os.getenv('IS_CI'):
        print("No ccache enable. Make sure your working dir (gn_out) is in the same path as sdk_folder")
        return

    local_ccache_location = get_local_ccache_location()
    if local_ccache_location == "":
        local_ccache_location = os.path.abspath(os.path.join(os.getenv("HOME"), ".ccache")).replace("\\", "/")
        os.makedirs(local_ccache_location)
        ccache_location = ccache_locations[int(uuid.getnode()) % len(ccache_locations)]
        run_anyway("sudo umount {}".format(local_ccache_location))
        run_anyway("sudo mount -t nfs {0} {1}".format(ccache_location, local_ccache_location))
        local_ccache_location = get_local_ccache_location()

    if local_ccache_location == "":
        return

    os.environ["CCACHE_BASEDIR"] = root_path
    ccache_command = ccache_bin_path



def prepare_linux():
    """
    Linux need those tools:
        python, python3, clang
    """
    tools = {
        "python": "--version",
        "python3": "--version",
        "clang": "--version",
    }

    command.prepare_tools(tools)
    packages = [
        'libasound2-dev',
        'libgtk2.0-dev',
        'libX11-dev',
        'libpulse-dev',
        'libgl1-mesa-dev',
        'libc++-7-dev',
        'libc++abi-7-dev',
        'libxtst-dev',
        'libgtk-3-dev',
        "nfs-common"
    ]
    for p in packages:
        status, output = command.get_cmd_output(
            "dpkg -s {} | grep Status".format(p))
        if output.find("ok installed") == -1:
            print("please install {} by hclient prepare linux x64 debug".format(p))


def prepare_mac():
    """
    Mac need those tools:
        python, python3
    """
    tools = {
        "python": "--version",
        "python3": "--version",
    }
    command.prepare_tools(tools)
    # prepare xcode command line tools
    command.run_cmd("xcode-select --install", False)


def prepare_windows():
    """
    Windows need those tools:
        python, vs2017, sdk10
        clang(nice to have)
    Obviously python is already installed (otherwise can not run this script)
    but we have to check whether it's in PATH variable or not
    We requires both  python 2 and python 3, and put python (version 2.X) in PATH
    """
    tools = {
        "python": "--version"
    }
    not_installed_tools = command.check_tools(tools)
    if len(not_installed_tools) != 0:
        print("Please put python into PATH variable")
        sys.exit(-1)

    global has_vs2019
    has_vs2019 = False
    for driver_letter in ["c", "d", "e", "f", "g", "h", "i"]:
        vs_path = driver_letter + \
            ":\\Program Files (x86)\\Microsoft Visual Studio\\2019"
        if os.path.exists(vs_path):
            has_vs2019 = True
            break

    global has_vs2017
    has_vs2017 = False
    for driver_letter in ["c", "d", "e", "f", "g", "h", "i"]:
        vs_path = driver_letter + \
            ":\\Program Files (x86)\\Microsoft Visual Studio\\2017"
        if os.path.exists(vs_path):
            has_vs2017 = True
            break

    if not has_vs2019 and not has_vs2017:
        print("Please install Visual Studio 2017/2019 first")
        sys.exit(-1)

    has_sdk10 = False
    for driver_letter in ["c", "d", "e", "f", "g", "h", "i"]:
        sdk_path = driver_letter + ":\\Program Files (x86)\\Windows Kits\\10"
        if os.path.exists(sdk_path):
            has_sdk10 = True
            break
    if not has_sdk10:
        print("Please install Windows SDK 10 version 10.0.17134.0 first")
        sys.exit(-1)
    if not os.path.exists(os.path.join(sdk_path, 'include', '10.0.17134.0')):
        print("Windows SDK 10 detected but not version 10.0.17134.0")
        print("Please install Windows SDK 10 version 10.0.17134.0 first")
        sys.exit(-1)
    if not os.path.exists(os.path.join(sdk_path, 'Debuggers')):
        print("Please install Windbg")
        print("Tips: If the Windows SDK is already installed, open Settings, \
            navigate to Apps & features, select Windows Software Development Kit, \
                and then click Modify to change the installation to add Debugging \
                    Tools for Windows.")
        sys.exit(-1)
    if "PYTHON3_PATH" not in os.environ:
        print("Please set PYTHON3_PATH environment variable")
        sys.exit(-1)
    if not 'GYP_MSVS_VERSION' in os.environ:
        if has_vs2019 and target_os == "win":
            os.environ["GYP_MSVS_VERSION"] = "2019"
        else:
            os.environ["GYP_MSVS_VERSION"] = "2017"
    os.environ["DEPOT_TOOLS_WIN_TOOLCHAIN"] = '0'
    os.environ['WINDOWSSDKDIR'] = sdk_path


def prepare_android():
    """
        Android NDK must be installed
        Oracle JDK must be installed
    """
    global android_build_tools_ver
    ndk_path = os.environ.get("ANDROID_NDK", None)
    sdk_path = os.environ.get("ANDROID_SDK", None)
    if not ndk_path or not sdk_path:
        if not ndk_path:
            print("Please set ANDROID_NDK environment variable")
        if not sdk_path:
            print("Please set ANDROID_SDK environment variable")
        sys.exit(-1)
    if command.IS_MAC:
        run_or_die("/usr/libexec/java_home -v 1.8", False)
    else:
        java_home = os.environ.get("JAVA_HOME", None)
        if not java_home:
            print("Please set JAVA_HOME to Oracle JDK, and add $JAVA_HOME/bin to PATH")
            sys.exit(-1)
        run_or_die("javac -version", False)
    android_tools = os.path.join(demo_path, "third_party", "android_tools")
    if not os.path.exists(android_tools):
        os.makedirs(android_tools)
    cwd = os.getcwd()
    os.chdir(android_tools)
    conf = {}
    conf["ndk"] = ndk_path
    conf["sdk"] = sdk_path
    for item in conf.keys():
        if command.IS_WINDOWS:
            if os.path.isdir(item):
                run_or_die("rd /s /q {}".format(item), False)
            elif os.path.islink(item):
                run_or_die("rmdir {}".format(item), False)
            elif os.path.isfile(item):
                run_or_die("del /F /Q {}".format(item), False)
            elif not os.path.exists(item):
                pass
            else:
                print("{0} in {1} are not support".format(item, os.getcwd()))
                exit(-1)
            run_or_die("mklink /d {0} \"{1}\"".format(item, conf[item]), False)
        else:
            run_or_die("rm -f {}".format(item), False)
            run_or_die("ln -s \"{0}\" {1}".format(conf[item], item), False)
    os.chdir(cwd)
    # find android build tool
    build_tool_path = os.path.join(sdk_path, "build-tools")
    build_tool_path = os.path.abspath(build_tool_path)
    dirs = [p for p in os.listdir(build_tool_path) if p != '.' and p != '..' and os.path.isdir(
        os.path.join(build_tool_path, p))]
    if len(dirs) == 0:
        print("No Android build tool found under {}!".format(build_tool_path))
        sys.exit(-1)
    android_build_tools_ver = select_build_tools(build_tool_path, dirs)


def main(argv):
    pass


if __name__ == "__main__":
    main(sys.argv[1:])
