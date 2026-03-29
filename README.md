# astrbot_plugin_image_symmetry

将 [nonebot-plugin-image-symmetry](https://github.com/GT-610/nonebot-plugin-image-symmetry) 的核心功能移植到 AstrBot 的插件版本。

## 来源与致谢

- 原始项目：[`GT-610/nonebot-plugin-image-symmetry`](https://github.com/GT-610/nonebot-plugin-image-symmetry)
- 本项目基于原项目的图像对称处理思路与功能设计，适配为 AstrBot 插件实现。

## 功能

- 对称左：将图片左半部分镜像到右半部分
- 对称右：将图片右半部分镜像到左半部分
- 对称上：将图片上半部分镜像到下半部分
- 对称下：将图片下半部分镜像到上半部分
- 支持静态图片和 GIF
- 支持“指令和图片同发”以及“回复图片消息后发送指令”

## 安装

按 AstrBot 插件标准放入插件目录后，安装依赖：

```bash
pip install -r requirements.txt
```

其中本插件额外依赖：

- `Pillow>=10.4.0`

AstrBot 插件开发规范参考：

- [AstrBot 插件开发文档](https://docs.astrbot.app/dev/star/plugin-new.html)

## 使用

以下指令需按你的 AstrBot 配置使用对应命令前缀：

- `/对称` 或 `/对称左`
- `/对称右`
- `/对称上`
- `/对称下`
- `/对称帮助`

### 用法一

直接发送图片和指令，例如：

```text
/对称左
```

并与图片同一条消息发送。

### 用法二

回复一条带图片的消息，再发送指令，例如：

```text
/对称上
```

## 说明

- 插件在内存中处理图片，不做额外缓存。
- 返回结果直接以图片消息发送。
