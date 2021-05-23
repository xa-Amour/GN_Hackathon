import os
import platform
import sys

# Distinguish slashes for different platforms
if platform.system() == "Windows":  # IS_WINDOWS
    slash = '\\'
elif platform.system() == "Darwin":  # IS_MAC
    slash = '/'
elif platform.system() == "Linux":  # IS_LINUX
    slash = '/'

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__))))
sys.path.append(os.path.join(os.path.dirname(os.getcwd())))
suffix = ['.cc','.mm','.cpp','.h']


def __get_src_file(src_folder):
    src_file_lst = []
    for root, dirs, files in os.walk(src_folder):
        for file in files:
            src_file_lst.append(root + slash + file)
    return src_file_lst


def __get_file_with_suffix(src_folder):
    src_file_lst = __get_src_file(src_folder)
    file_with_suffix = []
    for file in src_file_lst:
        if os.path.splitext(file)[1] in tuple(suffix):
            file_with_suffix.append(file)
    print(('There are {0} files, '
           'suffix called {1}').format(len(file_with_suffix), suffix))
    return file_with_suffix


def gen_gn_template(_target_file_lst, target_folder):
    sources_lst = []
    BUILD_gn_location = os.path.join(
        os.path.dirname(
            os.getcwd()),
        target_folder,
        'BUILD.gn')
    if os.path.exists(BUILD_gn_location):
        os.remove(BUILD_gn_location)
    with open(str(BUILD_gn_location), 'w') as fileWriter:
        for item in _target_file_lst:
            sources_lst.append(item.split(slash)[-1])
        sources = ''
        for source in sources_lst:
            sources += '     "{0}",\n'.format(source)
        payload = '# Avatar SDK\n# Copyright (c) 2020 Avatar IO. All rights reserved.\n\n' + \
                  'static_library("hello_static") {{ \n  sources = [\n{0}  ]\n}}'.format(sources)
        fileWriter.write(payload)
    print('SUCCESS!')


def has_file_with_suffix(foler):
    for root, dirs, files in os.walk(foler):
        for file in files:
            if os.path.splitext(file)[1] in tuple(suffix):
                return os.getcwd()
    return False


def main():
    gen_gn_template(__get_file_with_suffix(r'../demo', ), 'demo')
    gen_gn_template(__get_file_with_suffix(r'demo/subtalk', ),'demo/subtalk')


if __name__ == '__main__':
    main()
