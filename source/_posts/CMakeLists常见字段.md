---
title:CMakeLists中的常见字段
date: 2025-06-07
tags: CMake
cover: 
label: 
---

`CMakeLists.txt` 中的核心是一系列的命令（commands）和变量（variables）。通过这些命令，我们向 CMake 声明项目的各种特性和构建规则。

以下是一些 `CMakeLists.txt` 中最常见和重要的“字段”（或者说，命令和变量）：

### 核心项目配置命令

1.  **`cmake_minimum_required(VERSION <major>.<minor> [FATAL_ERROR])`**
    * **作用：** 指定项目所需的最低 CMake 版本。这是每个 `CMakeLists.txt` 文件的第一行。它确保你的项目不会在旧版本的 CMake 上编译，旧版本可能不支持你使用的某些命令或特性。
    * **示例：** `cmake_minimum_required(VERSION 3.10)`

2.  **`project(<PROJECT_NAME> [LANGUAGES <language>...] [VERSION <major>[.<minor>[.<patch>[.<tweak>]]]])`**
    * **作用：** 定义项目的名称。这是顶级 `CMakeLists.txt` 中仅次于 `cmake_minimum_required` 的第二条命令。它也可能指定项目支持的语言（如 CXX, C, Fortran）和版本。
    * **示例：** `project(simplest_ffmpeg_player CXX VERSION 1.0)`

### 源文件、目标和依赖管理

3.  **`add_executable(<target_name> [source1] [source2] ...)`**
    * **作用：** 定义一个可执行目标。这是最常见的命令之一，它告诉 CMake 将指定的源文件编译并链接成一个可执行程序。
    * **示例：** `add_executable(my_app main.cpp helper.cpp)`

4.  **`add_library(<target_name> [STATIC | SHARED | MODULE] [source1] [source2] ...)`**
    * **作用：** 定义一个库目标。你可以指定它是静态库 (`STATIC`)、动态库 (`SHARED`) 还是模块库 (`MODULE`)。
    * **示例：**
        * `add_library(my_static_lib STATIC static_func.cpp)`
        * `add_library(my_shared_lib SHARED shared_func.cpp)`

5.  **`target_sources(<target> [PRIVATE|PUBLIC|INTERFACE] <source1> [source2] ...)`**
    * **作用：** 向一个已存在的 `target` 添加源文件。当源文件很多或需要根据条件添加时，这个命令比直接在 `add_executable`/`add_library` 中列出更灵活。
    * **示例：** `target_sources(my_app PRIVATE main.cpp)`

6.  **`target_include_directories(<target> [PRIVATE|PUBLIC|INTERFACE] [dir1] [dir2] ...)`**
    * **作用：** 指定某个目标（可执行文件或库）的头文件搜索路径。
        * `PRIVATE`：只影响当前目标本身的编译。
        * `PUBLIC`：影响当前目标本身的编译，也影响链接到此目标的任何其他目标。
        * `INTERFACE`：只影响链接到此目标的任何其他目标。
    * **示例：** `target_include_directories(my_app PUBLIC ${CMAKE_SOURCE_DIR}/include)`

7.  **`target_link_libraries(<target> [PRIVATE|PUBLIC|INTERFACE] [item1] [item2] ...)`**
    * **作用：** 指定某个目标需要链接的库。这可以是其他 CMake 目标，也可以是外部库。链接顺序在某些情况下很重要。
    * **示例：** `target_link_libraries(my_app PRIVATE my_shared_lib Qt5::Widgets)`

8.  **`add_subdirectory(<source_dir> [binary_dir] [EXCLUDE_FROM_ALL])`**
    * **作用：** 包含另一个子目录中的 `CMakeLists.txt` 文件。这对于组织大型项目结构非常有用。
    * **示例：** `add_subdirectory(src)`

### 变量和属性设置

9.  **`set(<variable> <value> [CACHE <type> <docstring> [FORCE]])`**
    * **作用：** 设置 CMake 变量的值。变量在 CMake 脚本内部使用，可以存储路径、选项等。`CACHE` 选项用于创建用户可以在 CMake GUI 或命令行中配置的缓存变量。
    * **示例：**
        * `set(SOURCE_FILES main.cpp)`
        * `set(CMAKE_CXX_STANDARD 17)` (设置C++标准，这是一个重要的内置变量)
        * `set(BUILD_SHARED_LIBS ON CACHE BOOL "Build shared libraries" FORCE)`

10. **`option(<variable> "Help string" [initial value])`**
    * **作用：** 创建一个布尔选项，用户可以在 CMake 配置时启用或禁用。
    * **示例：** `option(BUILD_TESTS "Build unit tests" ON)`

### 查找包和依赖

11. **`find_package(<PackageName> [version] [REQUIRED] [COMPONENTS <comp1> <comp2>...] [OPTIONAL_COMPONENTS <comp3>...] [NO_MODULE] [NO_CONFIG])`**
    * **作用：** 查找并加载外部依赖包（如 Boost, OpenCV, Qt 等）。如果找到，它会设置一些变量（如 `<PackageName>_FOUND`，`<PackageName>_INCLUDE_DIRS`，`<PackageName>_LIBRARIES`）或导入目标（如 `Qt5::Widgets`）。
    * **示例：** `find_package(SDL2 REQUIRED)`

### 条件和循环控制流

12. **`if (...) ... elseif (...) ... else (...) ... endif()`**
    * **作用：** 条件语句，根据条件执行不同的命令。
    * **示例：**
        ```cmake
        if(WIN32)
            message("Building on Windows")
        elseif(UNIX)
            message("Building on Unix-like system")
        endif()
        ```

13. **`foreach(<loop_var> <item1> [<item2> ...] ) ... endforeach()`**
    * **作用：** 循环遍历列表。
    * **示例：**
        ```cmake
        set(MY_SOURCES a.cpp b.cpp c.cpp)
        foreach(src_file ${MY_SOURCES})
            message("Processing ${src_file}")
        endforeach()
        ```

### 其他常用命令

14. **`message([STATUS|WARNING|AUTHOR_WARNING|FATAL_ERROR|CHECK_START|CHECK_DONE|CHECK_FAIL] "message to display")`**
    * **作用：** 在 CMake 配置过程中输出信息到控制台。对于调试和用户提示非常有用。
    * **示例：** `message(STATUS "Configuring ${PROJECT_NAME} project...")`

15. **`file(GLOB <variable> [LIST_DIRECTORIES true|false] [RELATIVE <path>] [pattern1] [pattern2] ...)`**
    * **作用：** 查找匹配给定模式的文件，并将结果存储到变量中。常用于收集源文件。
    * **示例：** `file(GLOB SOURCE_FILES "src/*.cpp" "src/*.c")`
        * **注意：** 虽然方便，但 `file(GLOB)` 在某些情况下可能不是最佳实践，因为它不处理文件删除的情况（需要重新运行 CMake）。更推荐显式列出源文件或使用 `target_sources`。

16. **`install(...)`**
    * **作用：** 定义项目的安装规则，例如将可执行文件、库、头文件安装到系统目录或指定目录。
    * **示例：**
        ```cmake
        install(TARGETS my_app DESTINATION bin)
        install(DIRECTORY include/ DESTINATION include)
        ```

