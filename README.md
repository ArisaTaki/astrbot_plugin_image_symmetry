# astrbot_plugin_image_symmetry

将 [nonebot-plugin-image-symmetry](https://github.com/GT-610/nonebot-plugin-image-symmetry) 的核心功能移植到 AstrBot 的插件版本。

[![CI](https://github.com/ArisaTaki/astrbot_plugin_image_symmetry/actions/workflows/ci.yml/badge.svg)](https://github.com/ArisaTaki/astrbot_plugin_image_symmetry/actions/workflows/ci.yml)
[![Release](https://github.com/ArisaTaki/astrbot_plugin_image_symmetry/actions/workflows/release.yml/badge.svg)](https://github.com/ArisaTaki/astrbot_plugin_image_symmetry/actions/workflows/release.yml)

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

## 发布到插件商店

本仓库已补齐 AstrBot 插件市场要求的基础信息：

- `metadata.yaml`
- `requirements.txt`
- GitHub 仓库地址

官方发布流程如下：

1. 将代码推送到 GitHub 仓库。
2. 访问 [AstrBot 插件市场](https://plugins.astrbot.app)。
3. 点击右下角 `+`。
4. 填写插件基础信息、作者信息、仓库信息。
5. 点击 `Submit to GITHUB`，跳转到 AstrBot 官方仓库的 Issue 提交页。
6. 检查信息无误后，点击 `Create` 完成提交流程。

本仓库同时提供：

- `CI`：在推送和 PR 时检查 `metadata.yaml`、`requirements.txt` 和 Python 语法。
- `Release`：在推送版本标签时自动打包插件源码并创建 GitHub Release。

建议发布步骤：

1. 修改 `metadata.yaml` 中的版本号。
2. 提交并推送代码。
3. 创建并推送标签，例如 `v1.0.1`。
4. 等待 GitHub Actions 自动完成 release。
5. 再去插件市场提交该仓库。

## 使用

以下指令需按你的 AstrBot 配置使用对应命令前缀：

- `/对称` 或 `/对称左`
- `/左对称`
- `/对称右` 或 `/右对称`
- `/对称上` 或 `/上对称`
- `/对称下` 或 `/下对称`
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
- 为避免阻塞和内存占用异常，默认限制图片大小不超过 10MB、像素总量不超过 4000 万、GIF 不超过 100 帧。
