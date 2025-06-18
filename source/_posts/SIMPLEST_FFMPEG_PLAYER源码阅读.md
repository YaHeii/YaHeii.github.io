---
title: SIMPLEST_FFMPEG_PLAYER源码阅读
date: 2025-06-10
tags: 音视频技术
cover: ../pic/音视频传输/封面.png
label: 
---

对于FFmpeg的使用中，理解各个结构体的作用至关重要。

---
1. 解协议（http,rtsp,rtmp,mms）

AVIOContext，URLProtocol，URLContext主要存储视音频使用的协议的类型以及状态。URLProtocol存储输入视音频使用的封装格式。每种协议都对应一个URLProtocol结构。（注意：FFMPEG中文件也被当做一种协议“file”）

>1. AVIOContext是FFmpeg中用于执行输入输出操作的抽象层，提供协议层之上的抽象接口，它负责处理数据流的读写和定位，而不需要知道底层数据的来源，因此可以处理本地，网络，内存缓冲区多个流来源。这个结构体包含了读写缓冲区的指针，缓冲区的大小，当前读写位置，和读写位置的指针（这些具体的指针指向集体的协议实现）等
>2. 在古早版本的FFmpeg中UP用于定义和注册不同的底层协议（如file\http\rtp\tcp\udp等），每个这样的结构体中都包含了针对该协议的一组回调函数（如url_open\url_read\url_read\url_write\url_seek\url_close等）。但是在现代的FFmpeg中这个东嗯那个已经更多的整合和抽象进入AC中了。
>3. 同样的在古早版本中，UC是UP的一个具体实例，用于存贮某个已经打开协议连接的上下文信息。但是在新版的FFmpeg中这个结构也已经被整合到了AC中
---

2. 解封装（flv,avi,rmvb,mp4）

AVFormatContext主要存储视音频封装格式中包含的信息；AVInputFormat存储输入视音频使用的封装格式。每种视音频封装格式都对应一个AVInputFormat 结构。

>1.  在阅读雷博士写的播放器的时候能够轻易地发现这个结构体是一个很重要的结构体，它不仅是用于解封装到解码中间，在其他地方也是可以看到的。但是在这个结构体中实际上并没有什么很复杂的信息。只有类似音视频流的个数，音视频流，时长，比特率之类的东西。以及显示音视频流（文件）的源信息

---


3. 解码（h264,mpeg2,aac,mp3）

每个AVStream存储一个视频/音频流的相关数据；每个AVStream对应一个AVCodecContext，存储该视频/音频流使用解码方式的相关数据；每个AVCodecContext中对应一个AVCodec，包含该视频/音频对应的解码器。每种解码器都对应一个AVCodec结构。
>AVStream
>1. 这个结构体可以理解成为媒体文件中的轨道信息。
>AVCodecContex
>1. 这个结构体在编码和解码中都有应用，用于存储编解码器的上下文实例
>2. 解码过程，用于存储和接收编码器配置，打开一个媒体文件时候FFmpeg会从文件头部解析出视频流的编码参数，包括像视频宽度高度，像素格式，时间基准，音视频采样率等。另外配置编码器选项，跳帧策略，线程数，错误隐藏策略，是否允许多线程解码。传递压缩数据和接收原始数据： 会把压缩后的 AVPacket （例如一个H.264 NALU）传递给 AVCodecContext 对应的解码器（通过 avcodec_send_packet）。解码器处理后，会从 AVCodecContext 对应的解码器中读取解码后的 AVFrame （例如YUV像素数据或PCM采样数据，通过 avcodec_receive_frame）。
>3. 编码过程。首先还是设置编码参数，包括输入原始视频的尺寸和格式，编码器的时间基准，B帧最大数量等。配置编码选项，例如一些预设和调优，编码速度，编码模式等。传递原始数据和接收压缩数据： 你会把原始的 AVFrame （例如YUV像素数据或PCM采样数据）传递给 AVCodecContext 对应的编码器（通过 avcodec_send_frame）。编码器处理后，你会从 AVCodecContext 对应的编码器中读取压缩后的 AVPacket （例如H.264 NALU或AAC帧，通过 avcodec_receive_packet）。
>4. 这个接口一般是应用程序和底层编解码算法之间的桥梁，FFmpeg由此提供了统一的接口来配置不同的编解码器。有关于其他参数的解析还是看一下雷博士的[博客](https://blog.csdn.net/leixiaohua1020/article/details/14214859)。
>AVCodec
>1. AVCodec代表了一个具体的已经注册的编码器算法，它是一个只读的结构体，包含着这个编码器本身的静态通用信息，和能力。以及只想内部实现函数的指针。一般通过avcodec_find_decoder或者avcodec_find_encoder来获取这样一个指针。可以理解这是一个解码算法所提供的指针。
>2. 要注意AC的存储是以一个全局的注册列表形式（可能是一个链表或是其他的数据结构）实现的。由于FFmpeg时支持多种音视频编解码的这些编解码器在编译时可以被静态链接，作为共享库进行动态加载，允许 FFmpeg 在运行时动态地查找和选择合适的编解码器。
>3. AVCodec 定义了编解码器的抽象接口（例如 decode, encode, init, close 等函数指针）。具体的编解码器实现（例如 libx264、libvpx、libfdk_aac 等第三方库或 FFmpeg 内部实现）则通过 AVCodec 结构体将自己注册到 FFmpeg 中。这种设计使得 FFmpeg 核心库无需知道所有编解码器的具体实现细节，只需通过统一的 AVCodec 接口来调用它们。
---
4. 存数据

视频的话，每个结构一般是存一帧；音频可能有好几帧

解码前数据：AVPacket
>1. 这个结构体比较简单，都是一些时间戳，大小之类的数据，
解码后数据：AVFrame
> 1. AF中包含了多个码流参数，其中又以data数组为核心，主要是存储原始数据。在data数组中对于packed和planar数据的存储格式是不一样的。
>  2. 在AVPictureType结构体中IBP较为常见，但是要注意S\SI\BI\BP帧类型，S 帧是一种特殊的编码帧，它本身是帧间预测的（像 P 帧），但它的预测信息（运动矢量、残差）可以被后续的 I 帧或 P 帧作为参考。SI 帧是一种特殊的 I 帧。它所有的宏块都是帧内编码的（像 I 帧一样），所以它是一个独立的帧，不依赖其他帧进行预测。 它的主要作用也是提供随机访问点，但它通常是为了更快速、更鲁棒的切换而设计。与普通的 I 帧相比，SI 帧可能在编码方式或解码端处理上有一些特定优化，以确保在它这里可以立即开始一个新的解码序列。BI 帧是一种非常特殊的帧，它包含的宏块全部是帧内编码的（就像 I 帧），但它却像 B 帧一样，既可以被向前参考，也可以被向后参考。SP 帧是一种特殊的 P 帧。它的大部分宏块都是帧间预测的（像 P 帧），但它的预测信息（运动矢量、残差）可以被后续的 I 帧或 P 帧作为参考。
> 3. qscale_table，网上绝大部分关于这个结构体的论述都是搬得雷博士的，需要注意宏块在视频帧指的是一个矩形块，而QP值其实是QP_step的一个索引，规定了宏块的采样步数，这个索引表是可以被查到的。
> 4. 另外以及像运动矢量和运动估计参考帧都比较容易理解
---
接下来是以雷博士做的SIMPLEST_FFMPEG_PLAYER为例（注意是第一版），在上面添加注释，详细分析每个语句的作用，以及视频播放器的工作流程。

```C++
/** 
**核心流程：**
**FFmpeg 部分：**
* 初始化 FFmpeg 库。
* 打开视频文件并查找视频流。
* 查找并打开视频解码器。
* 分配用于存储解码帧和转换后YUV帧的内存。
* 初始化 SWS_Scaler (用于图像格式转换)。

**SDL 部分：**
* 初始化 SDL 库。
* 创建 SDL 窗口、渲染器和纹理。

**主循环：**
* 从视频文件中读取数据包 (`AVPacket`)。
* 将数据包发送给解码器 (`avcodec_decode_video2`)。
* 如果解码器成功解码出图像 (`got_picture` 为真)，则：
* 使用 SWS_Scaler 将解码后的帧转换为 YUV420P 格式。
* （可选）将 YUV420P 数据写入文件。
* 使用 SDL 更新纹理、清空渲染器、复制纹理到渲染器并呈现，从而显示视频帧。
* 延时一小段时间以控制播放速度。
* 刷新解码器（处理剩余的帧）。
* 释放所有分配的资源并退出。
**/


/**
 * 最简单的FFmpeg播放器 2
 * Simplest FFmpeg Player 2
 *
 * 作者：雷霄骅 Lei Xiaohua.注释作者：yahei

 * 版本2：使用SDL 2.0取代了版本1中的SDL 1.2。
 * Version 2 use SDL 2.0 instead of SDL 1.2 in version 1.
 *
 * 本程序实现了一个视频文件的解码和显示（支持HEVC, H.264, MPEG2等）。
 * 这是一个最简单的FFmpeg视频解码方法。
 * 通过学习这个示例可以初步了解FFmpeg的解码流程。
 * This software is a simplest video player based on FFmpeg.
 * Suitable for beginner of FFmpeg.
 *
 */
#include <cstddef>

#include <stdio.h>

// 宏定义，确保stdint.h中的常量宏可用，例如UINT64_C
#define __STDC_CONSTANT_MACROS

// 根据操作系统类型包含不同的头文件路径
#ifdef _WIN32
// Windows 平台
extern "C" // 声明为C风格链接，因为FFmpeg和SDL库是C语言编写的
{
#include "include/libavcodec/avcodec.h"   // 包含FFmpeg编解码器库头文件
#include "include/libavformat/avformat.h" // 包含FFmpeg封装格式库头文件
#include "include/libswscale/swscale.h"   // 包含FFmpeg图像缩放/格式转换库头文件
#include "SDL2/SDL.h"             // 包含SDL2库头文件
};
#else
// Linux 或其他类Unix平台
#ifdef __cplusplus // 如果是C++编译器，使用extern "C"
extern "C"
{
#endif
#include <libavcodec/avcodec.h>
#include <libavformat/avformat.h>
#include <libswscale/swscale.h>
#include <SDL2/SDL.h>
#ifdef __cplusplus
};
#endif
#endif

// 宏定义：是否将YUV420P数据输出到文件
// 如果定义为1，则会将解码并转换后的YUV420P数据写入output.yuv文件
// 如果定义为0，则不写入文件
#define OUTPUT_YUV420P 0

int main(int argc, char* argv[])
{
    // FFmpeg 相关的结构体指针
    AVFormatContext *pFormatCtx; // 封装格式上下文，包含了文件的整体信息（如流的数量、时长等）
    int              i, videoindex; // i用于循环，videoindex用于存储视频流的索引
    AVCodecContext  *pCodecCtx;    // 编解码器上下文，包含了编解码器操作所需的所有参数（如宽度、高度、像素格式等）
    AVCodec         *pCodec;       // 编解码器，代表一个具体的编解码器（如H.264解码器）
    AVFrame *pFrame, *pFrameYUV; // pFrame用于存储解码前的数据包（原始数据），pFrameYUV用于存储解码后并转换为YUV420P格式的帧
    uint8_t *out_buffer; // 用于存储转换后YUV420P数据的缓冲区
    AVPacket *packet;    // 数据包，存储从文件中读取的压缩数据（如H.265或H.264帧）
    int y_size; // Y分量的大小，用于计算YUV数据的总大小和写入YUV文件
    int ret, got_picture; // ret用于接收函数返回值，got_picture指示是否解码出一张完整的图片

    // SWS_Scaler 上下文，用于图像格式转换（例如从解码器的原生像素格式转换为YUV420P）
    struct SwsContext *img_convert_ctx;

    // 输入文件路径
    char filepath[] = "bigbuckbunny_480x272.h265"; // 要播放的视频文件路径

    // SDL 相关变量
    int screen_w = 0, screen_h = 0; // 屏幕（窗口）的宽度和高度
    SDL_Window *screen;             // SDL 窗口对象
    SDL_Renderer* sdlRenderer;      // SDL 渲染器，用于在窗口上绘图
    SDL_Texture* sdlTexture;        // SDL 纹理，用于存储YUV数据并渲染到屏幕
    SDL_Rect sdlRect;               // SDL 矩形，定义纹理在窗口上的显示区域

    FILE *fp_yuv; // 用于输出YUV文件时的文件指针

    // FFmpeg 初始化
    av_register_all();     // 注册所有可用的编解码器、复用器/解复用器等组件
    avformat_network_init(); // 初始化网络模块，如果需要处理网络流（例如HTTP, RTSP等）

    pFormatCtx = avformat_alloc_context(); // 分配一个AVFormatContext结构体
    // 打开输入流（文件或网络流）
    // avformat_open_input 负责打开媒体文件并读取其头部信息
    if (avformat_open_input(&pFormatCtx, filepath, NULL, NULL) != 0) {
        printf("Couldn't open input stream.\n"); // 如果文件无法打开，打印错误信息
        return -1;
    }

    // 查找输入流信息
    // avformat_find_stream_info 负责读取媒体文件的一部分，填充pFormatCtx中的流信息（nb_streams, streams等）
    if (avformat_find_stream_info(pFormatCtx, NULL) < 0) {
        printf("Couldn't find stream information.\n"); // 如果无法找到流信息，打印错误信息
        return -1;
    }

    // 找到视频流的索引
    videoindex = -1; // 视频流索引初始化为-1（未找到）
    for (i = 0; i < pFormatCtx->nb_streams; i++) { // 遍历所有流
        // 检查当前流的类型是否为视频流
        if (pFormatCtx->streams[i]->codec->codec_type == AVMEDIA_TYPE_VIDEO) {
            videoindex = i; // 找到视频流，记录其索引
            break;          // 退出循环
        }
    }
    if (videoindex == -1) {
        printf("Didn't find a video stream.\n"); // 如果没有找到视频流，打印错误信息
        return -1;
    }

    // 获取视频流的编解码器上下文
    pCodecCtx = pFormatCtx->streams[videoindex]->codec; // 从视频流中获取其对应的AVCodecContext
    // 找到视频解码器
    // avcodec_find_decoder 根据编解码器ID（pCodecCtx->codec_id）找到对应的解码器
    pCodec = avcodec_find_decoder(pCodecCtx->codec_id);
    if (pCodec == NULL) {
        printf("Codec not found.\n"); // 如果没有找到解码器，打印错误信息
        return -1;
    }
    // 打开解码器
    // avcodec_open2 负责打开解码器，并为它分配必要的资源
    if (avcodec_open2(pCodecCtx, pCodec, NULL) < 0) {
        printf("Could not open codec.\n"); // 如果无法打开解码器，打印错误信息
        return -1;
    }

    // FFmpeg 内存分配
    pFrame = av_frame_alloc();     // 分配一个AVFrame结构体，用于存储解码后的原始帧数据
    pFrameYUV = av_frame_alloc();  // 分配一个AVFrame结构体，用于存储转换为YUV420P格式后的帧数据
    // 计算YUV420P格式的图像数据所需的大小，并分配缓冲区
    out_buffer = (uint8_t *)av_malloc(avpicture_get_size(PIX_FMT_YUV420P, pCodecCtx->width, pCodecCtx->height));
    // 将分配的缓冲区与pFrameYUV关联起来，avpicture_fill会设置pFrameYUV->data和pFrameYUV->linesize
    // 注意：在FFmpeg 4.0+版本中，PIX_FMT_YUV420P 已被 AV_PIX_FMT_YUV420P 取代
    avpicture_fill((AVPicture *)pFrameYUV, out_buffer, PIX_FMT_YUV420P, pCodecCtx->width, pCodecCtx->height);
    packet = (AVPacket *)av_malloc(sizeof(AVPacket)); // 分配一个AVPacket结构体，用于存储从文件中读取的压缩数据包

    // 输出文件信息
    printf("--------------- File Information ----------------\n");
    av_dump_format(pFormatCtx, 0, filepath, 0); // 打印媒体文件的详细信息到控制台
    printf("-------------------------------------------------\n");

    // 初始化SWS_Scaler上下文，用于图像格式转换
    // 从解码器输出的原始像素格式（pCodecCtx->pix_fmt）转换为YUV420P格式
    // SWS_BICUBIC 是一个常用的缩放算法
    img_convert_ctx = sws_getContext(pCodecCtx->width, pCodecCtx->height, pCodecCtx->pix_fmt,
                                     pCodecCtx->width, pCodecCtx->height, AV_PIX_FMT_YUV420P, SWS_BICUBIC, NULL, NULL, NULL);

// 如果定义了OUTPUT_YUV420P宏，则打开YUV文件
#if OUTPUT_YUV420P
    fp_yuv = fopen("output.yuv", "wb+"); // 以二进制写模式打开output.yuv文件
#endif

    // SDL 初始化
    // 初始化SDL视频、音频和定时器子系统
    if (SDL_Init(SDL_INIT_VIDEO | SDL_INIT_AUDIO | SDL_INIT_TIMER)) {
        printf("Could not initialize SDL - %s\n", SDL_GetError()); // 初始化失败，打印错误信息
        return -1;
    }

    screen_w = pCodecCtx->width;  // 设置窗口宽度为视频宽度
    screen_h = pCodecCtx->height; // 设置窗口高度为视频高度
    // 创建SDL窗口
    // SDL_WINDOWPOS_UNDEFINED 表示窗口位置由系统决定
    // SDL_WINDOW_OPENGL 提示使用OpenGL渲染
    screen = SDL_CreateWindow("Simplest ffmpeg player's Window", SDL_WINDOWPOS_UNDEFINED, SDL_WINDOWPOS_UNDEFINED,
                              screen_w, screen_h,
                              SDL_WINDOW_OPENGL);

    if (!screen) {
        printf("SDL: could not create window - exiting:%s\n", SDL_GetError()); // 窗口创建失败，打印错误信息
        return -1;
    }

    // 创建SDL渲染器
    sdlRenderer = SDL_CreateRenderer(screen, -1, 0);
    // 创建SDL纹理
    // SDL_PIXELFORMAT_IYUV 指定纹理的像素格式为IYUV (即YUV420P)
    // SDL_TEXTUREACCESS_STREAMING 表示纹理数据会频繁更新
    sdlTexture = SDL_CreateTexture(sdlRenderer, SDL_PIXELFORMAT_IYUV, SDL_TEXTUREACCESS_STREAMING, pCodecCtx->width, pCodecCtx->height);

    // 设置SDL矩形，定义纹理在窗口上的显示区域
    sdlRect.x = 0;
    sdlRect.y = 0;
    sdlRect.w = screen_w;
    sdlRect.h = screen_h;

    // SDL 初始化结束----------------------

    // 主循环：读取、解码和显示视频帧
    // av_read_frame 从输入流中读取一个AVPacket
    while (av_read_frame(pFormatCtx, packet) >= 0) {
        // 检查当前数据包是否属于视频流
        if (packet->stream_index == videoindex) {
            // 解码视频包
            // avcodec_decode_video2 将压缩的AVPacket解码为AVFrame（原始帧）
            // got_picture 会在成功解码出完整图像时设置为非0
            ret = avcodec_decode_video2(pCodecCtx, pFrame, &got_picture, packet);
            if (ret < 0) {
                printf("Decode Error.\n"); // 解码错误
                return -1;
            }
            if (got_picture) { // 如果成功解码出了一张完整的图片
                // 图像格式转换
                // sws_scale 将pFrame中的图像数据转换为YUV420P格式，并存储到pFrameYUV中
                // pFrame->data 和 pFrame->linesize 包含原始帧的像素数据和行步长
                // 0 表示从图像的第0行开始转换
                // pCodecCtx->height 是图像的高度
                // pFrameYUV->data 和 pFrameYUV->linesize 接收转换后的YUV数据和行步长
                sws_scale(img_convert_ctx, (const uint8_t* const*)pFrame->data, pFrame->linesize, 0, pCodecCtx->height,
                          pFrameYUV->data, pFrameYUV->linesize);

            // 如果定义了OUTPUT_YUV420P宏，则将YUV数据写入文件
            #if OUTPUT_YUV420P
                y_size = pCodecCtx->width * pCodecCtx->height; // Y分量大小
                fwrite(pFrameYUV->data[0], 1, y_size, fp_yuv);     // 写入Y分量数据
                fwrite(pFrameYUV->data[1], 1, y_size / 4, fp_yuv); // 写入U分量数据 (YUV420P中U/V是Y的1/4大小)
                fwrite(pFrameYUV->data[2], 1, y_size / 4, fp_yuv); // 写入V分量数据
            #endif

                // SDL 渲染部分---------------------------
            #if 0 // 这是一个旧的SDL_UpdateTexture用法，通常用于YUV数据的更新
                SDL_UpdateTexture( sdlTexture, NULL, pFrameYUV->data[0], pFrameYUV->linesize[0] );
            #else // 使用SDL_UpdateYUVTexture更新YUV纹理，更适合YUV420P三平面格式
                SDL_UpdateYUVTexture(sdlTexture, &sdlRect,
                                     pFrameYUV->data[0], pFrameYUV->linesize[0], // Y分量数据和行步长
                                     pFrameYUV->data[1], pFrameYUV->linesize[1], // U分量数据和行步长
                                     pFrameYUV->data[2], pFrameYUV->linesize[2]); // V分量数据和行步长
            #endif

                SDL_RenderClear( sdlRenderer );   // 清空渲染器
                // 将纹理复制到渲染器，NULL表示复制整个纹理到整个sdlRect定义的区域
                SDL_RenderCopy( sdlRenderer, sdlTexture, NULL, &sdlRect);
                SDL_RenderPresent( sdlRenderer ); // 更新屏幕显示

                // SDL 渲染部分结束-----------------------
                
                // 延时以控制播放速度，这里简单固定延时40ms，约每秒25帧（1000ms / 40ms = 25帧）
                SDL_Delay(40); 
            }
        }
        av_free_packet(packet); // 释放当前AVPacket的内存，准备读取下一个
    }

    // 刷新解码器（处理解码器中剩余的帧）
    // 在文件末尾，解码器内部可能还缓存了一些帧，需要通过不断调用解码函数直到没有更多帧输出
    // 此时packet参数可以设置为NULL或一个空packet
    while (1) {
        ret = avcodec_decode_video2(pCodecCtx, pFrame, &got_picture, NULL); // 注意这里 packet 为 NULL
        if (ret < 0) // 解码错误或没有更多数据
            break;
        if (!got_picture) // 没有解码出新的图像
            break;
        // 对剩余的帧进行格式转换和显示
        sws_scale(img_convert_ctx, (const uint8_t* const*)pFrame->data, pFrame->linesize, 0, pCodecCtx->height,
                  pFrameYUV->data, pFrameYUV->linesize);
        
    #if OUTPUT_YUV420P
        int y_size=pCodecCtx->width*pCodecCtx->height; // 重新计算y_size，虽然这里应该和之前一样
        fwrite(pFrameYUV->data[0],1,y_size,fp_yuv);     // Y
        fwrite(pFrameYUV->data[1],1,y_size/4,fp_yuv);   // U
        fwrite(pFrameYUV->data[2],1,y_size/4,fp_yuv);   // V
    #endif
        // SDL 显示剩余帧
        SDL_UpdateTexture( sdlTexture, &sdlRect, pFrameYUV->data[0], pFrameYUV->linesize[0] ); // 修正，这里应该用 SDL_UpdateYUVTexture
        SDL_RenderClear( sdlRenderer );
        SDL_RenderCopy( sdlRenderer, sdlTexture, NULL, &sdlRect);
        SDL_RenderPresent( sdlRenderer );
        SDL_Delay(40);
    }

    // 释放资源
    sws_freeContext(img_convert_ctx); // 释放SWS_Scaler上下文

#if OUTPUT_YUV420P
    fclose(fp_yuv); // 关闭YUV输出文件
#endif

    SDL_Quit(); // 退出SDL子系统

    av_frame_free(&pFrameYUV); // 释放YUV帧的内存
    av_frame_free(&pFrame);     // 释放原始帧的内存
    avcodec_close(pCodecCtx);   // 关闭编解码器上下文
    avformat_close_input(&pFormatCtx); // 关闭输入流上下文

    return 0; // 程序成功退出
}

```